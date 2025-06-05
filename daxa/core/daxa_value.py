"""
daxa.core.daxa_value (V4) - Defines DaxaValue, the runtime representation of Daxa data.
Aligns with Daxa V4 type system (int, float, string, bool, datetime, uuid, bytes,
enum instances, struct instances, arrays, any, and potentially DXD/Math source).
"""
from __future__ import annotations # For cleaner forward references
import datetime
import uuid
import base64 # For bytes to/from base64 string if string representation used for bytes
from typing import Any, Dict, List, Union, Optional, TYPE_CHECKING, cast, Type

from .common import ( # V4 versions
    DaxaTypeEnumV4, DaxaError, DaxaInternalError, DaxaValidationError, DaxaTypeError,
    SourceLocation, PYTHON_TO_DAXA_TYPE_MAP_V4, DaxaSchemaError
)
# Definition classes for Diagram/Math might be held by DaxaValue if type is DXD_SOURCE/MATH_SOURCE
from .diagram import DiagramDefinitionV4
from maths import MathEquationDefinitionV4


if TYPE_CHECKING:
    from .schema import DaxaTypeV4, SchemaV4, StructDefinitionV4, EnumDefinitionV4 # V4 versions

# PythonNativeV4 for type hints of values easily convertible to/from DaxaValue
# These are types DaxaValue.from_python_native directly understands.
DaxaPrimitiveNativeV4 = Union[None, bool, int, float, str, bytes, datetime.datetime, uuid.UUID]
# Diagram/Math definitions can also be native Python objects that DaxaValue can wrap.
PythonNativeV4 = Union[
    DaxaPrimitiveNativeV4, List[Any], Dict[str, Any],
    DiagramDefinitionV4, MathEquationDefinitionV4
]


class DaxaValue: # Name kept as DaxaValue; module context makes it DaxaValue for V4
    """
    Represents a single Daxa value at runtime (V4). It holds the actual Python value
    and its Daxa type information, ensuring type consistency.

    The `_value` attribute stores:
    - Primitives (NULL, BOOL, INT, FLOAT, STRING, BYTES, DATETIME, UUID): Direct Python objects.
    - ENUM_INSTANCE: The string value of the enum member.
    - ARRAY: A Python `list` of `DaxaValue` instances.
    - STRUCT_INSTANCE (or MAP): A Python `dict` of `str` to `DaxaValue`.
    - DXD_SOURCE_CONTENT: A `DiagramDefinitionV4` instance.
    - MATH_SOURCE_CONTENT: A `MathEquationDefinitionV4` instance.
    - ANY: Either another `DaxaValue` instance or an opaque Python object.
    """
    __slots__ = ('_value', '_daxa_type_info', '_source_loc')

    def __init__(self,
                 value: Any, # See class docstring for what this holds per type
                 daxa_type_info: Union[DaxaTypeEnumV4, DaxaTypeV4], # Resolved DaxaTypeV4 or base DaxaTypeEnumV4
                 source_loc: Optional[SourceLocation] = None):
        self._daxa_type_info: Union[DaxaTypeEnumV4, DaxaTypeV4] = daxa_type_info
        self._source_loc: Optional[SourceLocation] = source_loc

        effective_enum = self.daxa_type_enum # Gets the *instance* type enum

        # Validate and store the value based on the effective DaxaTypeEnum
        # This now uses DaxaTypeEnumV4
        if effective_enum == DaxaTypeEnumV4.NULL:
            if value is not None: raise DaxaInternalError(f"Value for DaxaTypeEnumV4.NULL must be None, got {type(value).__name__}")
            self._value = None
        elif effective_enum == DaxaTypeEnumV4.BOOL:
            if not isinstance(value, bool): raise DaxaInternalError(f"Value for DaxaTypeEnumV4.BOOL must be bool, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.INT:
            if not isinstance(value, int) or isinstance(value, bool): # bool is subclass of int
                raise DaxaInternalError(f"Value for DaxaTypeEnumV4.INT must be true int, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.FLOAT:
            if not isinstance(value, float): raise DaxaInternalError(f"Value for DaxaTypeEnumV4.FLOAT must be float, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.STRING: # Used for raw strings
            if not isinstance(value, str): raise DaxaInternalError(f"Value for DaxaTypeEnumV4.STRING must be str, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.BYTES:
            if not isinstance(value, bytes): raise DaxaInternalError(f"Value for DaxaTypeEnumV4.BYTES must be bytes, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.DATETIME:
            if not isinstance(value, datetime.datetime): raise DaxaInternalError(f"Value for DaxaTypeEnumV4.DATETIME must be datetime, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.UUID:
            if not isinstance(value, uuid.UUID): raise DaxaInternalError(f"Value for DaxaTypeEnumV4.UUID must be uuid.UUID, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.ENUM_INSTANCE: # Stored as string, validated by schema_type (EnumDefinitionV4)
            if not isinstance(value, str): raise DaxaInternalError(f"Value for DaxaTypeEnumV4.ENUM_INSTANCE must be str, got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.ARRAY:
            if not isinstance(value, list) or not all(isinstance(item, DaxaValue) for item in value):
                raise DaxaInternalError(f"Value for DaxaTypeEnumV4.ARRAY must be List[DaxaValue], got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.STRUCT_INSTANCE: # Map or Struct instance
            if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, DaxaValue) for k,v in value.items()):
                raise DaxaInternalError(f"Value for DaxaTypeEnumV4.STRUCT_INSTANCE must be Dict[str, DaxaValue], got {type(value).__name__}")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.DXD_SOURCE_CONTENT:
            if not isinstance(value, DiagramDefinitionV4): raise DaxaInternalError("Value for DXD_SOURCE_CONTENT must be DiagramDefinitionV4.")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.MATH_SOURCE_CONTENT:
            if not isinstance(value, MathEquationDefinitionV4): raise DaxaInternalError("Value for MATH_SOURCE_CONTENT must be MathEquationDefinitionV4.")
            self._value = value
        elif effective_enum == DaxaTypeEnumV4.ANY:
            self._value = value # ANY can hold another DaxaValue or an opaque Python object
        else: # Should not be SCHEMA_*_KEYWORD or UNKNOWN_TYPE types
            raise DaxaInternalError(f"Unhandled or invalid DaxaTypeEnumV4 '{effective_enum}' for DaxaValue instance construction.")

    @property
    def value(self) -> Any: return self._value

    @property
    def daxa_type_enum(self) -> DaxaTypeEnumV4:
        """Returns the effective runtime DaxaTypeEnumV4 of this DaxaValue instance."""
        if isinstance(self._daxa_type_info, DaxaTypeEnumV4):
            return self._daxa_type_info # Already a base enum
        
        # If _daxa_type_info is a DaxaTypeV4 object from schema, get its instance enum
        schema_type_obj = cast(DaxaTypeV4, self._daxa_type_info)
        return schema_type_obj.get_instance_type_enum()

    @property
    def schema_type(self) -> Optional[DaxaTypeV4]:
        """The DaxaTypeV4 object from schema if this value is schema-typed, else None."""
        return self._daxa_type_info if isinstance(self._daxa_type_info, DaxaTypeV4) else None

    @property
    def source_location(self) -> Optional[SourceLocation]: return self._source_loc

    def get_py_value(self) -> PythonNativeV4:
        """Recursively converts DaxaValue to native Python types (primitives, list, dict)."""
        dt_enum = self.daxa_type_enum
        val = self._value

        if dt_enum.is_primitive(): return cast(PythonNativeV4, val)
        if dt_enum == DaxaTypeEnumV4.ENUM_INSTANCE: return cast(str, val) # Enum value is string

        if dt_enum == DaxaTypeEnumV4.ARRAY:
            return [item.get_py_value() for item in cast(List[DaxaValue], val)]
        if dt_enum == DaxaTypeEnumV4.STRUCT_INSTANCE: # Map / Struct instance
            return {k: v.get_py_value() for k, v in cast(Dict[str, DaxaValue], val).items()}
        
        if dt_enum == DaxaTypeEnumV4.DXD_SOURCE_CONTENT and isinstance(val, DiagramDefinitionV4):
            return val # Or val.to_dict_representation() if PythonNativeV4 implies JSON-like
        if dt_enum == DaxaTypeEnumV4.MATH_SOURCE_CONTENT and isinstance(val, MathEquationDefinitionV4):
            return val # Or val.to_dict_representation()

        if dt_enum == DaxaTypeEnumV4.ANY:
            return val.get_py_value() if isinstance(val, DaxaValue) else cast(PythonNativeV4, val)
        
        raise DaxaTypeError(f"Cannot get Python native value for DaxaTypeEnumV4: {dt_enum} (Value: {val!r})")

    @classmethod
    def from_python_native(
        cls, py_native_value: PythonNativeV4,
        target_daxa_type_hint: Optional[Union[DaxaTypeV4, DaxaTypeEnumV4, str]] = None,
        schema_context: Optional[SchemaV4] = None,
        source_loc: Optional[SourceLocation] = None
    ) -> DaxaValue:
        """Creates DaxaValue from Python value, inferring or using hinted Daxa type (V4)."""
        final_type_info: Union[DaxaTypeV4, DaxaTypeEnumV4]
        element_type_for_array: Optional[DaxaTypeV4] = None
        value_type_for_map: Optional[DaxaTypeV4] = None # For map[K,V] syntax
        struct_def_for_obj: Optional[StructDefinitionV4] = None

        if target_daxa_type_hint:
            # ... (resolve target_daxa_type_hint to DaxaTypeV4 or DaxaTypeEnumV4, as in prev version) ...
            # This resolution is complex and involves schema_context.
            # Let `resolved_hint_type_obj` be the DaxaTypeV4 resulting from hint resolution.
            # Let `instance_enum_from_hint` be resolved_hint_type_obj.get_instance_type_enum().
            if isinstance(target_daxa_type_hint, DaxaTypeV4):
                final_type_info = target_daxa_type_hint.get_resolved_type_fully() if schema_context else target_daxa_type_hint # Resolve if possible
                if final_type_info.type_enum == DaxaTypeEnumV4.ARRAY : element_type_for_array = final_type_info.element_type
                if final_type_info.type_enum == DaxaTypeEnumV4.MAP : value_type_for_map = final_type_info.value_type # type: ignore
                if final_type_info.type_enum == DaxaTypeEnumV4.SCHEMA_STRUCT_DEF and final_type_info.name and schema_context:
                     struct_def_for_obj = schema_context.get_definition(final_type_info.name, StructDefinitionV4)
            elif isinstance(target_daxa_type_hint, DaxaTypeEnumV4):
                final_type_info = target_daxa_type_hint
            elif isinstance(target_daxa_type_hint, str): # type name
                if not schema_context: raise DaxaSchemaError("Schema context needed for type name hint.")
                resolved_hint_obj = schema_context.resolve_type(target_daxa_type_hint)
                if not resolved_hint_obj : raise DaxaSchemaError(f"Hint type '{target_daxa_type_hint}' not in schema.")
                final_type_info = resolved_hint_obj
                if final_type_info.type_enum == DaxaTypeEnumV4.ARRAY : element_type_for_array = final_type_info.element_type
                if final_type_info.type_enum == DaxaTypeEnumV4.MAP : value_type_for_map = final_type_info.value_type # type: ignore
                if final_type_info.type_enum == DaxaTypeEnumV4.SCHEMA_STRUCT_DEF and final_type_info.name :
                     struct_def_for_obj = schema_context.get_definition(final_type_info.name, StructDefinitionV4)

            else: raise DaxaTypeError(f"Unsupported target_daxa_type_hint: {type(target_daxa_type_hint)}")
        else: # Infer from Python type
            py_type = type(py_native_value)
            inferred_enum = PYTHON_TO_DAXA_TYPE_MAP_V4.get(py_type)
            if inferred_enum is None: final_type_info = DaxaTypeEnumV4.ANY # Fallback
            else: final_type_info = inferred_enum

        # Get instance enum (e.g. STRUCT_DEF becomes STRUCT_INSTANCE)
        instance_enum = final_type_info.get_instance_type_enum() if isinstance(final_type_info, DaxaTypeV4) else final_type_info

        # Construct value part based on instance_enum
        if instance_enum.is_primitive():
            # Ensure py_native_value type matches (or can be coerced to) inferred/hinted primitive
            # (Constructor will do strict check based on final_type_info)
            return cls(py_native_value, final_type_info, source_loc)
        elif instance_enum == DaxaTypeEnumV4.ENUM_INSTANCE: # Value should be string
            if not isinstance(py_native_value, str): DaxaValidationError("Enum instance value must be string.")
            # Final validation happens with validator against EnumDefinitionV4 in schema_type.
            return cls(py_native_value, final_type_info, source_loc)
        elif instance_enum == DaxaTypeEnumV4.ARRAY:
            if not isinstance(py_native_value, list): raise DaxaValidationError("Expected Python list for ARRAY type.")
            el_type_hint_for_items = element_type_for_array or (DaxaTypeEnumV4.ANY if isinstance(final_type_info, DaxaTypeEnumV4) else final_type_info.element_type) # type: ignore
            items = [cls.from_python_native(item, el_type_hint_for_items, schema_context) for item in py_native_value]
            return cls(items, final_type_info, source_loc)
        elif instance_enum == DaxaTypeEnumV4.STRUCT_INSTANCE: # Map or Struct
            if not isinstance(py_native_value, dict): raise DaxaValidationError("Expected Python dict for STRUCT_INSTANCE type.")
            obj_items: DaxaObject = {} #type: ignore
            for k, v_py in py_native_value.items():
                if not isinstance(k, str): raise DaxaValidationError("Struct/Map keys must be strings.")
                
                field_type_hint_for_value: Optional[Union[DaxaTypeV4, DaxaTypeEnumV4]] = None #Type Change
                if struct_def_for_obj: # If a specific struct is expected
                    field_def = struct_def_for_obj.get_field(k)
                    if field_def: field_type_hint_for_value = field_def.daxa_type
                    # Else: field not in struct, behavior depends on strictness (validator handles this)
                    # For from_python_native, if no field_def, treat as ANY or infer.
                    elif not field_def : field_type_hint_for_value = DaxaTypeEnumV4.ANY # Assume ANY if field unknown for this context
                elif value_type_for_map: # If it's map[K,V] type
                    field_type_hint_for_value = value_type_for_map
                # else: general dict, infer value types or use ANY

                obj_items[k] = cls.from_python_native(v_py, field_type_hint_for_value, schema_context)
            return cls(obj_items, final_type_info, source_loc)
        elif instance_enum == DaxaTypeEnumV4.DXD_SOURCE_CONTENT:
            if not isinstance(py_native_value, DiagramDefinitionV4): raise DaxaValidationError("Expected DiagramDefinitionV4 for DXD_SOURCE_CONTENT")
            return cls(py_native_value, final_type_info, source_loc)
        elif instance_enum == DaxaTypeEnumV4.MATH_SOURCE_CONTENT:
            if not isinstance(py_native_value, MathEquationDefinitionV4): raise DaxaValidationError("Expected MathEquationDefinitionV4 for MATH_SOURCE_CONTENT")
            return cls(py_native_value, final_type_info, source_loc)
        elif instance_enum == DaxaTypeEnumV4.ANY:
            # If value itself is DaxaValue, wrap it directly.
            # Else, try to make it a DaxaValue of specific type then wrap in ANY DaxaValue.
            # Or just store raw if no obvious conversion and from_python_native with None hint defaults to ANY
            # The DaxaValue constructor for ANY takes the value directly.
            return cls(py_native_value, DaxaTypeEnumV4.ANY, source_loc) # Simplest: value becomes an ANY

        raise DaxaTypeError(f"Cannot create DaxaValue for Python value '{py_native_value!r}' with inferred/hinted type '{final_type_info}'.")


    @classmethod
    def from_json_compatible( # JSON (from Python dicts/lists/primitives) to DaxaValue
        cls, json_data: Any, # JsonValue compatible (usually primitive, list, dict)
        target_daxa_type: Union[DaxaTypeV4, DaxaTypeEnumV4, str], # Type Changed to V4
        schema_context: Optional[SchemaV4] = None, #Type Changed to V4
        source_loc: Optional[SourceLocation] = None
    ) -> DaxaValue:
        # ... (Similar extensive logic as before, adapted for DaxaTypeV4 and DaxaTypeEnumV4)
        # This method is crucial for converting raw parsed data (like from config blocks or initial data literals)
        # into type-checked DaxaValues when a schema or type hint is available.
        # Main changes:
        # - Uses SchemaV4, DaxaTypeV4, DaxaTypeEnumV4.
        # - Handles ENUM_INSTANCE creation: json_data (string) is validated against EnumDefinitionV4.
        # - Handles STRUCT_INSTANCE creation: json_data (dict) keys/values validated against StructDefinitionV4 fields.
        # - If json_data is string, but target DaxaType is DATETIME, UUID, BYTES, performs conversion
        #   (ISO string to datetime obj, UUID string to uuid obj, base64 string to bytes obj).
        # - Needs robust error handling (DaxaValidationError, DaxaTypeError, DaxaSchemaError).
        # For STUB:
        if target_daxa_type == DaxaTypeEnumV4.INT: return cls(int(json_data), target_daxa_type, source_loc)
        if target_daxa_type == DaxaTypeEnumV4.STRING: return cls(str(json_data), target_daxa_type, source_loc)
        # Highly simplified - real implementation is very long.
        print(f"Warning: DaxaValue.from_json_compatible STUB called for {target_daxa_type}")
        return cls(json_data, DaxaTypeEnumV4.ANY, source_loc) # Fallback to ANY for stub.

    def to_json_compatible(self, for_daxa_literal: bool = False) -> Any: # Python type ready for json.dumps or Daxa writer
        """Converts DaxaValue to JSON-compatible Python types or Daxa literal string."""
        # ... (Logic similar to previous version, adapted for DaxaTypeEnumV4)
        # - If for_daxa_literal:
        #   - BYTES -> "0xHEX..." or "b\"...\""
        #   - DATETIME -> "ISO8601_string"
        #   - UUID -> "uuid_string"
        #   - DXD_SOURCE_CONTENT -> DiagramDefinitionV4 obj (writer handles actual ```dxd...```)
        #   - MATH_SOURCE_CONTENT -> MathEquationDefinitionV4 obj (writer handles actual ```math...```)
        # - If not for_daxa_literal (standard JSON):
        #   - BYTES -> base64 string
        #   - DATETIME -> ISO8601 string
        #   - UUID -> uuid string
        #   - DXD_SOURCE_CONTENT -> dict representation of DiagramDefinitionV4
        #   - MATH_SOURCE_CONTENT -> dict representation of MathEquationDefinitionV4
        # For STUB:
        if for_daxa_literal: return str(self.get_py_value()) # Very crude literal
        return self.get_py_value() # Crude JSON compatible

    # ... (__repr__, __eq__, convenience accessors as_int, as_str etc. as before, adapted for V4 types) ...
    def __repr__(self) -> str:
        # ... (as before, show value preview and type info) ...
        type_str = self.schema_type.to_string(short=True) if self.schema_type else self.daxa_type_enum.value
        return f"DaxaValue({self._value!r:.50}, type='{type_str}')"


# Type aliases for V4 DaxaValue collections (internal representation)
DaxaObject = Dict[str, DaxaValue] # type:ignore # Underlying dict for STRUCT_INSTANCE DaxaValue
DaxaArray = List[DaxaValue]     # type:ignore # Underlying list for ARRAY DaxaValue