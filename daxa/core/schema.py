"""
daxa.core.schema (V4) - Defines Daxa schema elements: DaxaTypeV4, FieldV4,
                        StructDefinitionV4, EnumDefinitionV4, etc., and the
                        SchemaV4 container for type system management.
                        Aligns with V4 syntax (top-level struct, enum, type, const).
"""
from __future__ import annotations # For cleaner forward references
import re
from typing import List, Dict, Optional, Union, Any, Set, cast, TYPE_CHECKING, Tuple, Type

from .common import ( # V4 versions
    DaxaTypeEnumV4, DaxaSchemaError, DaxaInternalError, DaxaValidationError,
    SourceLocation, MAX_RECURSION_DEPTH_V4, DaxaNameError, DaxaBlockTypeEnumV4,
    PYTHON_TO_DAXA_TYPE_MAP_V4 # For default value type check (conceptual)
)

if TYPE_CHECKING:
    from .daxa_value import DaxaValue, PythonNativeV4 # V4 versions

# --- Constraints V4 (Largely similar in structure, using DaxaTypeEnumV4) ---
class ConstraintV4:
    __slots__ = ('source_attribute',)
    def __init__(self, source_attribute: str): self.source_attribute: str = source_attribute
    def validate(self, value_to_check: Any, daxa_type_enum: DaxaTypeEnumV4, ctx_name: str, loc: Optional[SourceLocation]) -> None: raise NotImplementedError
    def to_daxa_attribute_str(self) -> str: return self.source_attribute # For writing back to Daxa text
    def __eq__(self, other: object) -> bool: return isinstance(other, self.__class__) and self.source_attribute == other.source_attribute
    def __hash__(self) -> int: return hash((self.__class__.__name__, self.source_attribute))
    def __repr__(self) -> str: return f"{self.__class__.__name__}(attr='{self.source_attribute}')"

class LengthConstraintV4(ConstraintV4):
    __slots__ = ('min_length', 'max_length')
    def __init__(self, sa: str, min_l: Optional[int]=None, max_l: Optional[int]=None):
        super().__init__(sa)
        if min_l is not None and min_l < 0: raise DaxaSchemaError("Min length must be non-negative.")
        if max_l is not None and max_l < 0: raise DaxaSchemaError("Max length must be non-negative.")
        if min_l is not None and max_l is not None and min_l > max_l: raise DaxaSchemaError(f"Min length {min_l} > max length {max_l}.")
        self.min_length, self.max_length = min_l, max_l
    def validate(self, val: Any, type_enum: DaxaTypeEnumV4, name: str, loc: Optional[SourceLocation]):
        # V4 types: STRING, BYTES (if it's a distinct type), ARRAY
        if type_enum not in (DaxaTypeEnumV4.STRING, DaxaTypeEnumV4.BYTES, DaxaTypeEnumV4.ARRAY): return
        l = len(val)
        if self.min_length is not None and l < self.min_length: raise DaxaValidationError(f"Length of '{name}' ({l}) < min {self.min_length}.", loc)
        if self.max_length is not None and l > self.max_length: raise DaxaValidationError(f"Length of '{name}' ({l}) > max {self.max_length}.", loc)
    # __eq__, __hash__ need to compare min_length, max_length too

class RangeConstraintV4(ConstraintV4): # For INT, FLOAT
    __slots__ = ('min_value', 'max_value', 'exclusive_min', 'exclusive_max')
    def __init__(self, sa: str, min_v:Optional[Union[int,float]]=None, max_v:Optional[Union[int,float]]=None, excl_min:bool=False, excl_max:bool=False):
        super().__init__(sa); self.min_value, self.max_value, self.exclusive_min, self.exclusive_max = min_v, max_v, excl_min, excl_max
    def validate(self, val: Any, type_enum: DaxaTypeEnumV4, name: str, loc: Optional[SourceLocation]):
        if type_enum not in (DaxaTypeEnumV4.INT, DaxaTypeEnumV4.FLOAT) or not isinstance(val, (int, float)): return
        # ... (validation logic as before) ...
    # __eq__, __hash__

class RegexConstraintV4(ConstraintV4): # For STRING
    __slots__ = ('pattern', '_regex_compiled')
    def __init__(self, sa: str, pattern_str: str):
        super().__init__(sa); self.pattern = pattern_str
        try: self._regex_compiled = re.compile(pattern_str)
        except re.error as e: raise DaxaSchemaError(f"Invalid regex '{pattern_str}': {e}")
    def validate(self, val: Any, type_enum: DaxaTypeEnumV4, name: str, loc: Optional[SourceLocation]):
        if type_enum != DaxaTypeEnumV4.STRING or not isinstance(val, str): return
        if not self._regex_compiled.fullmatch(val): raise DaxaValidationError(f"Value '{val[:50]}' for '{name}' doesn't match pattern '{self.pattern}'.", loc)
    # __eq__, __hash__


# --- DaxaTypeV4 ---
class DaxaTypeV4: # Represents a type reference or definition in the schema. Immutable once fully resolved.
    __slots__ = (
        '_type_enum_kind', # What kind of definition this refers to if named (STRUCT_DEF, ENUM_DEF, ALIAS_DEF) or direct type (INT, ARRAY)
        '_name',           # Name of the struct/enum/alias being referred to, or primitive name like "int"
        '_element_type',   # For ARRAY
        '_key_type', '_value_type', # For MAP
        '_is_optional', '_constraints', '_default_value_native', '_description',
        '_attributes_raw', '_source_loc', '_schema_context',
        '_is_resolved_structurally', '_syntax_flavor' # e.g. "shorthand_array" for `[string]`
    )

    def __init__(self, type_enum_kind: DaxaTypeEnumV4, name: Optional[str] = None,
                 element_type: Optional[DaxaTypeV4] = None, key_type: Optional[DaxaTypeV4] = None, value_type: Optional[DaxaTypeV4] = None,
                 is_optional: bool = False, constraints: Optional[List[ConstraintV4]] = None,
                 default_value_native: Optional[PythonNativeV4] = None, description: Optional[str] = None,
                 attributes_raw: Optional[Dict[str, Any]] = None, source_loc: Optional[SourceLocation] = None,
                 schema_context: Optional[SchemaV4] = None, _is_resolved_structurally: bool = False,
                 _syntax_flavor: Optional[str] = None):
        
        self._type_enum_kind: DaxaTypeEnumV4 = type_enum_kind
        self._name: Optional[str] = name
        self._element_type: Optional[DaxaTypeV4] = element_type
        self._key_type: Optional[DaxaTypeV4] = key_type
        self._value_type: Optional[DaxaTypeV4] = value_type
        self._is_optional: bool = is_optional
        self._constraints: Tuple[ConstraintV4, ...] = tuple(sorted(constraints,key=lambda c:c.source_attribute)) if constraints else tuple()
        self._default_value_native: Optional[PythonNativeV4] = default_value_native
        self._description: Optional[str] = description
        self._attributes_raw: Dict[str, Any] = dict(attributes_raw) if attributes_raw else {}
        self._source_loc: Optional[SourceLocation] = source_loc
        self._schema_context: Optional[SchemaV4] = schema_context
        self._is_resolved_structurally: bool = _is_resolved_structurally
        self._syntax_flavor: Optional[str] = _syntax_flavor

        # Basic validations (more in SchemaV4.parse_type_string which is the main entry point)
        if self._type_enum_kind == DaxaTypeEnumV4.ARRAY and self._element_type is None:
            raise DaxaSchemaError("ARRAY DaxaTypeV4 must have an element_type.", source_loc)
        if self._type_enum_kind == DaxaTypeEnumV4.MAP: # `map[K,V]`
            if self._key_type is None or self._value_type is None:
                raise DaxaSchemaError("MAP DaxaTypeV4 must have key_type and value_type (key_type defaults to string if not specified).", source_loc)
            if self._key_type.type_enum != DaxaTypeEnumV4.STRING: # Enforce string keys
                 raise DaxaSchemaError("Daxa MAP keys must be 'string'.", self._key_type._source_loc)

        if self._name is None and self._type_enum_kind.is_primitive():
             self._name = self._type_enum_kind.value # Use enum value as name for primitives
             if not self._is_resolved_structurally : self._is_resolved_structurally = True


    # --- Properties to access internal state ---
    @property
    def type_enum_kind(self) -> DaxaTypeEnumV4: return self._type_enum_kind
    @property
    def name(self) -> Optional[str]: return self._name
    @property
    def is_optional(self) -> bool: return self._is_optional
    # ... (other properties: element_type, key_type, value_type, constraints, etc.)

    def is_alias_reference(self) -> bool:
        """True if this refers to a TypeAliasDefinitionV4 by name."""
        return self._type_enum_kind == DaxaTypeEnumV4.SCHEMA_ALIAS_DEF and bool(self._name)

    def get_instance_type_enum(self) -> DaxaTypeEnumV4:
        """Returns the DaxaTypeEnumV4 for *instances* of this type (resolves aliases and definition kinds)."""
        resolved_self = self.get_resolved_type_fully() # Resolve to base definition or primitive
        if resolved_self._type_enum_kind == DaxaTypeEnumV4.SCHEMA_STRUCT_DEF: return DaxaTypeEnumV4.STRUCT_INSTANCE
        if resolved_self._type_enum_kind == DaxaTypeEnumV4.SCHEMA_ENUM_DEF: return DaxaTypeEnumV4.ENUM_INSTANCE
        if resolved_self._type_enum_kind.is_primitive() or \
           resolved_self._type_enum_kind in (DaxaTypeEnumV4.ARRAY, DaxaTypeEnumV4.MAP, DaxaTypeEnumV4.ANY,
                                             DaxaTypeEnumV4.DXD_SOURCE_CONTENT, DaxaTypeEnumV4.MATH_SOURCE_CONTENT):
            return resolved_self._type_enum_kind # Already an instance type
        raise DaxaInternalError(f"Cannot determine instance type for resolved DaxaTypeV4 kind: {resolved_self._type_enum_kind}")


    def get_resolved_type_fully(self, _visited_aliases: Optional[Set[str]] = None) -> DaxaTypeV4:
        """Resolves aliases fully. Requires _schema_context. Returns a new, resolved DaxaTypeV4."""
        # ... (Robust alias resolution logic as in previous DaxaType.get_resolved_type_fully)
        # This method is critical and complex. It will:
        # 1. Check if already structurally resolved and not an alias. If so, resolve children if any and return.
        # 2. If an alias, look up TypeAliasDefinitionV4 in _schema_context.
        # 3. Recursively call get_resolved_type_fully on the alias's target_type.
        # 4. Detect alias cycles using _visited_aliases.
        # 5. Merge properties (optionality, constraints, desc, default) from the alias chain onto the base resolved type.
        # 6. Return a *new* DaxaTypeV4 instance that is fully resolved.
        # For STUB:
        if self._type_enum_kind != DaxaTypeEnumV4.SCHEMA_ALIAS_DEF or self._is_resolved_structurally:
            # Simplified: if not alias, or marked resolved, assume it's good for stub
            # TODO: Need recursive child resolution for array/map elements to be truly "fully" resolved.
            return self
        if not self._schema_context or not self._name:
            raise DaxaInternalError("Cannot resolve alias without schema context or name.", self._source_loc)
        
        target_def = self._schema_context.get_definition(self._name) #type: ignore
        if isinstance(target_def, TypeAliasDefinitionV4):
             # This is where merging of optionality, constraints, etc. happens.
             base_resolved = target_def.target_type.get_resolved_type_fully(_visited_aliases) #type: ignore
             # Return a new DaxaTypeV4 combining this alias's modifiers with base_resolved.
             # Placeholder for complex merging:
             return base_resolved._clone_with_changes(is_optional=self.is_optional or base_resolved.is_optional, #type: ignore
                                                     _is_resolved_structurally=True)
        raise DaxaSchemaError(f"Alias '{self._name}' cannot be resolved.", self._source_loc)


    def _clone_with_changes(self, **kwargs) -> DaxaTypeV4:
        """Creates a new DaxaTypeV4 by copying current and overriding specified fields."""
        # ... (Implementation as before, ensuring all V4 __slots__ are handled) ...
        current_attrs = {slot[1:]: getattr(self, slot) for slot in self.__slots__ if hasattr(self, slot)}
        current_attrs.update(kwargs)
        if isinstance(current_attrs.get('_constraints'), tuple):
            current_attrs['_constraints'] = list(current_attrs['_constraints'])
        return DaxaTypeV4(**current_attrs) # type: ignore


    def to_string(self, short: bool = True, include_attributes: bool = True) -> str:
        """Generates Daxa V4 type string, e.g., "[string]?", "MyStruct", "map[string, int] @attr"."""
        # ... (Implementation as before, adapting to V4 syntax like `[ElementType]` for arrays,
        #      `map[KeyType,ValueType]`, and how named types/primitives are represented) ...
        # Must accurately reflect Daxa V4 spec's textual type representation.
        # Placeholder:
        name_part = self._name or self._type_enum_kind.value
        opt_part = "?" if self.is_optional else ""
        attr_part = ""
        if include_attributes and self._constraints: # Simplified attr string
            attr_part = " " + " ".join(c.to_daxa_attribute_str() for c in self._constraints) #type: ignore
        if self._type_enum_kind == DaxaTypeEnumV4.ARRAY:
            el_str = self._element_type.to_string(True, False) if self._element_type else "any" #type:ignore
            # Use [...] V4 syntax for arrays
            if self._syntax_flavor == "shorthand_array" or short:
                 name_part = f"[{el_str}]"
            else: # Full form `array<T>` if specified
                 name_part = f"array<{el_str}>"


        return f"{name_part}{opt_part}{attr_part}".strip()

    # ... (__repr__, __eq__, __hash__ adapted for V4 attributes) ...

# --- V4 Schema Definition Classes (using DaxaTypeV4) ---
# Your V4 spec uses top-level keywords: `struct Name {...}`, `enum Name {...}`, `type Alias = ...;`
# These are parsed into the following definition objects.

class SchemaDefinitionBaseV4: # Base for named definitions
    __slots__ = ('_name', '_description', '_source_loc', '_schema_context_ref')
    def __init__(self, name: str, description: Optional[str]=None, loc:Optional[SourceLocation]=None, schema_context:Optional[SchemaV4]=None):
        self._name, self._description, self._source_loc = name, description, loc
        self._schema_context_ref = schema_context # weakref recommended for real impl
    @property
    def name(self) -> str: return self._name
    @property
    def description(self) -> Optional[str]: return self._description
    @property
    def source_loc(self) -> Optional[SourceLocation]: return self._source_loc
    @property
    def schema_context(self) -> Optional[SchemaV4]: return self._schema_context_ref


class FieldV4: # Field within a StructDefinitionV4
    __slots__ = ('_name', '_daxa_type', '_description_direct', '_source_loc')
    def __init__(self, name: str, daxa_type: DaxaTypeV4, description_direct: Optional[str]=None, loc:Optional[SourceLocation]=None):
        # Basic name validation (e.g., valid identifier)
        if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
             raise DaxaSchemaError(f"Invalid field name '{name}'.", loc)
        self._name, self._daxa_type, self._description_direct, self._source_loc = name, daxa_type, description_direct, loc
    @property
    def name(self) -> str: return self._name
    @property
    def daxa_type(self) -> DaxaTypeV4: return self._daxa_type
    @property
    def description(self) -> Optional[str]: return self._description_direct or self.daxa_type._description # Field desc overrides type desc
    @property
    def source_loc(self) -> Optional[SourceLocation]: return self._source_loc
    # ... delegating properties: is_optional, default_value_native, constraints from self.daxa_type ...
    def __repr__(self) -> str: return f"FieldV4(name='{self.name}', type='{self.daxa_type.to_string()}')"


class StructDefinitionV4(SchemaDefinitionBaseV4):
    __slots__ = ('_fields', '_field_map')
    def __init__(self, name:str, fields:List[FieldV4], desc:Optional[str]=None, loc:Optional[SourceLocation]=None, schema_ctx:Optional[SchemaV4]=None):
        if not re.fullmatch(r"[A-Z][a-zA-Z0-9_]*", name): raise DaxaSchemaError(f"Struct name '{name}' must be PascalCase.", loc) # V4 convention
        super().__init__(name, desc, loc, schema_ctx)
        self._fields = tuple(fields)
        self._field_map = {f.name: f for f in fields}
        if len(self._fields) != len(self._field_map): raise DaxaSchemaError(f"Duplicate field names in struct '{name}'.", loc)
        if schema_ctx: [f.daxa_type._clone_with_changes(schema_context=schema_ctx) for f in self._fields if not f.daxa_type.schema_context] # Propagate
    @property
    def fields(self) -> Tuple[FieldV4,...]: return self._fields
    def get_field(self, field_name:str) -> Optional[FieldV4]: return self._field_map.get(field_name)


class EnumDefinitionV4(SchemaDefinitionBaseV4):
    __slots__ = ('_values_with_desc',) # Dict[str_value, Optional[str_description]]
    def __init__(self, name:str, values_data: List[Union[str, Tuple[str, Optional[str]]]], desc:Optional[str]=None, loc:Optional[SourceLocation]=None, schema_ctx:Optional[SchemaV4]=None):
        if not re.fullmatch(r"[A-Z][a-zA-Z0-9_]*", name): raise DaxaSchemaError(f"Enum name '{name}' must be PascalCase.", loc)
        super().__init__(name, desc, loc, schema_ctx)
        if not values_data: raise DaxaSchemaError(f"Enum '{name}' must have values.", loc)
        self._values_with_desc: Dict[str, Optional[str]] = {}
        for item in values_data:
            val_name, val_desc = (item[0], item[1]) if isinstance(item, tuple) else (item, None)
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", val_name): raise DaxaSchemaError(f"Enum value '{val_name}' in '{name}' must be UPPER_SNAKE_CASE.", loc) # V4 convention
            if val_name in self._values_with_desc: raise DaxaSchemaError(f"Duplicate enum value '{val_name}' in '{name}'.", loc)
            self._values_with_desc[val_name] = val_desc
    @property
    def values(self) -> List[str]: return list(self._values_with_desc.keys())
    def get_value_description(self, val_name:str) -> Optional[str]: return self._values_with_desc.get(val_name)


class TypeAliasDefinitionV4(SchemaDefinitionBaseV4):
    __slots__ = ('_target_type',)
    def __init__(self, name:str, target_type:DaxaTypeV4, desc:Optional[str]=None, loc:Optional[SourceLocation]=None, schema_ctx:Optional[SchemaV4]=None):
        if not re.fullmatch(r"[A-Z][a-zA-Z0-9_]*", name): raise DaxaSchemaError(f"Type alias name '{name}' must be PascalCase.", loc)
        super().__init__(name, desc, loc, schema_ctx)
        self._target_type = target_type
        if schema_ctx and not self._target_type.schema_context: self._target_type = self._target_type._clone_with_changes(schema_context=schema_ctx)
    @property
    def target_type(self) -> DaxaTypeV4: return self._target_type


class ConstantDefinitionV4(SchemaDefinitionBaseV4):
    __slots__ = ('_daxa_value', '_declared_type') # DaxaValue holds the constant's runtime value
    def __init__(self, name:str, daxa_value:DaxaValue, declared_type:Optional[DaxaTypeV4]=None, desc:Optional[str]=None, loc:Optional[SourceLocation]=None, schema_ctx:Optional[SchemaV4]=None):
        if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", name): raise DaxaSchemaError(f"Constant name '{name}' must be UPPER_SNAKE_CASE.", loc)
        super().__init__(name, desc, loc, schema_ctx)
        self._daxa_value, self._declared_type = daxa_value, declared_type
    @property
    def daxa_value(self) -> DaxaValue: return self._daxa_value
    @property
    def declared_type(self) -> Optional[DaxaTypeV4]: return self._declared_type


SchemaDefObjectV4 = Union[StructDefinitionV4, EnumDefinitionV4, TypeAliasDefinitionV4]

# --- SchemaV4 Container --- (Manages a collection of definitions)
class SchemaV4:
    __slots__ = ('_name', '_source_file_path', '_definitions', '_constants', '_type_parse_cache', '_validated_integrity')
    def __init__(self, name: str = "_DaxaGlobalSchema", source_file_path: Optional[str] = None):
        self._name, self._source_file_path = name, source_file_path
        self._definitions: Dict[str, SchemaDefObjectV4] = {} # Name -> Struct/Enum/Alias Def
        self._constants: Dict[str, ConstantDefinitionV4] = {}
        self._type_parse_cache: Dict[str, DaxaTypeV4] = {} # For SchemaV4.parse_type_string
        self._validated_integrity: bool = False

    # ... add_definition (for types or consts), get_definition, get_constant,
    #     get_all_definitions, get_all_constants methods (similar to Schema from before)
    #     Must handle name collisions robustly and set _schema_context_ref on added defs.

    def parse_type_string(self, type_str: str, loc: Optional[SourceLocation]=None) -> DaxaTypeV4:
        """
        CRITICAL: Parses a Daxa V4 type string (e.g., "[string]?", "MyStruct @attr") into DaxaTypeV4.
        Needs full recursive descent parser logic (as sketched in prev Schema.parse_type_string)
        adapted for V4 syntax (esp. array `[T]`), V4 enums, and context of this SchemaV4.
        Attributes (`@desc`, `@default`, constraints) are parsed and attached to DaxaTypeV4.
        Sets `schema_context=self` on created DaxaTypeV4 objects.
        Uses `self._type_parse_cache`.
        """
        # STUB for V4 type string parsing. This is a placeholder for a complex parser.
        # It must correctly handle: [ElementType]?, NamedType?, map[Key,Value]?, attributes.
        cache_key = type_str # Simple cache key, may need loc if errors are cached too
        if cache_key in self._type_parse_cache: return self._type_parse_cache[cache_key].copy() # Return copy if types mutable

        is_optional = type_str.endswith("?")
        base_type_str = type_str[:-1] if is_optional else type_str
        attributes_str = "" # TODO: extract attributes string here

        # Super simplified logic:
        dt: DaxaTypeV4
        if base_type_str == "int": dt = DaxaTypeV4(DaxaTypeEnumV4.INT, name="int", is_optional=is_optional)
        elif base_type_str == "string": dt = DaxaTypeV4(DaxaTypeEnumV4.STRING, name="string", is_optional=is_optional)
        elif base_type_str.startswith("[") and base_type_str.endswith("]"):
            el_str = base_type_str[1:-1]
            el_type = self.parse_type_string(el_str, loc) # Recursive
            dt = DaxaTypeV4(DaxaTypeEnumV4.ARRAY, element_type=el_type, is_optional=is_optional, _syntax_flavor="shorthand_array")
        else: # Assume named type
            # Look up if `base_type_str` is a known primitive DaxaTypeEnumV4 value first.
            try:
                primitive_enum = DaxaTypeEnumV4.from_string(base_type_str)
                dt = DaxaTypeV4(primitive_enum, name=base_type_str, is_optional=is_optional)
            except ValueError: # Not a primitive name, so it's a user-defined named type
                # The `_type_enum_kind` for such a reference is SCHEMA_ALIAS_DEF (if unknown) or STRUCT/ENUM_DEF if resolved
                dt = DaxaTypeV4(DaxaTypeEnumV4.SCHEMA_ALIAS_DEF, name=base_type_str, is_optional=is_optional)

        dt._schema_context = self # Link back to this schema for resolution
        # TODO: Parse `attributes_str` and populate dt.constraints, description, default_value_native
        # dt = self._apply_attributes_to_type(dt, attributes_str, loc)
        self._type_parse_cache[cache_key] = dt
        return dt


    def resolve_type(self, type_name_or_obj: Union[str, DaxaTypeV4]) -> Optional[DaxaTypeV4]:
        """Resolves type name string or DaxaTypeV4 to its fundamental DaxaTypeV4 (handles aliases)."""
        # ... (Logic similar to previous Schema.resolve_type, but uses self.parse_type_string for strings
        #      and DaxaTypeV4.get_resolved_type_fully for DaxaTypeV4 objects. Ensures context is self.)
        # STUB:
        if isinstance(type_name_or_obj, str):
            parsed = self.parse_type_string(type_name_or_obj)
            return parsed.get_resolved_type_fully()
        elif isinstance(type_name_or_obj, DaxaTypeV4):
            return type_name_or_obj.get_resolved_type_fully()
        return None

    def validate_schema_integrity(self) -> None:
        """Validates all definitions for resolvable types, no bad cycles, valid defaults/constraints."""
        # ... (Logic as before: iterate all defs, resolve types, check consts/defaults. Crucial step.)
        # Uses DaxaValidatorV4 for defaults/consts against their types.
        if self._validated_integrity: return
        # Basic pass for stub
        for name, defn in self._definitions.items():
            if isinstance(defn, TypeAliasDefinitionV4):
                if not self.resolve_type(defn.target_type): raise DaxaSchemaError(f"Unresolvable target for alias {name}")
            elif isinstance(defn, StructDefinitionV4):
                for field in defn.fields:
                    if not self.resolve_type(field.daxa_type): raise DaxaSchemaError(f"Unresolvable type for field {field.name} in struct {name}")
        self._validated_integrity = True

    def __repr__(self): return f"SchemaV4(name='{self._name}', defs={len(self._definitions)}, consts={len(self._constants)})"