"""
daxa.core.validator (V4) - Validates DaxaValue instances against DaxaTypeV4 definitions
                           and ensures schema-level consistency for constants and defaults.
                           Aligns with Daxa V4 language specification.
"""
from typing import Any, Optional, Set, cast, List, Union, Dict

from .common import ( # V4 versions
    DaxaTypeEnumV4, DaxaError, DaxaValidationError, DaxaSchemaError, DaxaInternalError, DaxaTypeError,
    SourceLocation, MAX_RECURSION_DEPTH_V4
)
from .daxa_value import DaxaValue # V4 by module context
from .schema import ( # V4 versions
    SchemaV4, DaxaTypeV4, StructDefinitionV4, EnumDefinitionV4, FieldV4, ConstantDefinitionV4
)


class DaxaValidatorV4:
    """
    Validates Daxa data against a V4 schema.
    It operates on a SchemaV4 instance that should have already passed its own
    internal integrity checks.
    """

    def __init__(self, schema: SchemaV4, strict_field_checking: bool = True):
        """
        Args:
            schema: The Daxa SchemaV4 to validate against. It's assumed this schema
                    has already passed its own `validate_schema_integrity()`.
            strict_field_checking: If True, struct instances must not have fields
                                   not defined in their StructDefinitionV4.
        """
        if not schema._validated_integrity: # Use internal flag if SchemaV4 has it
            # Or, for safety, re-validate, but this might be redundant if parser guarantees it.
            try:
                schema.validate_schema_integrity()
            except DaxaSchemaError as e:
                raise DaxaValidationError(
                    f"Cannot initialize validator: Schema '{schema.name}' failed integrity check: {e.message}",
                    e.location or (schema.source_file_path and SourceLocation(1,1,schema.source_file_path))
                ) from e
        self.schema: SchemaV4 = schema
        self.strict_fields: bool = strict_field_checking


    def validate_value(
        self,
        daxa_val: DaxaValue, # The value to validate
        expected_daxa_type: DaxaTypeV4, # The schema type it should conform to
        path_context: Optional[List[Union[str, int]]] = None, # For error reporting path
        recursion_depth: int = 0
    ) -> None:
        """
        Validates a single DaxaValue against an expected DaxaTypeV4.

        Args:
            daxa_val: The DaxaValue instance to validate.
            expected_daxa_type: The DaxaTypeV4 (from schema, should be fully resolved) it must conform to.
            path_context: Current path for error messages during recursive validation.
            recursion_depth: Current recursion depth.

        Raises:
            DaxaValidationError: If validation fails.
        """
        if recursion_depth > MAX_RECURSION_DEPTH_V4:
            path_str = ".".join(map(str, path_context or []))
            raise DaxaValidationError(f"Max recursion depth hit at '{path_str}'. Possible cycle or deep data.", daxa_val.source_location)

        current_path_str = ".".join(map(str, path_context or ["<root>"]))
        loc = daxa_val.source_location # Location from the DaxaValue itself if parsed

        # 1. Ensure expected_daxa_type is fully resolved (critical)
        # Caller should ensure this, but defensively resolve if possible.
        # DaxaTypeV4 needs its schema_context to be this validator's schema.
        if expected_daxa_type.schema_context is not self.schema and expected_daxa_type.schema_context is not None:
            print(f"Warning (Validator): Validating value for type '{expected_daxa_type.to_string()}' which has a different schema context.") # Dev warning
        
        type_to_validate_against = expected_daxa_type._clone_with_changes(schema_context=self.schema) # type: ignore #Ensure context
        try:
            resolved_expected_type = type_to_validate_against.get_resolved_type_fully()
        except DaxaSchemaError as e:
            raise DaxaValidationError(f"Invalid expected type for '{current_path_str}': {e.message}", loc or e.location) from e

        # 2. Handle optionality vs null value
        if daxa_val.daxa_type_enum == DaxaTypeEnumV4.NULL:
            if resolved_expected_type.is_optional:
                return # Null is valid for an optional type
            else:
                raise DaxaValidationError(f"Null value at '{current_path_str}' but type '{resolved_expected_type.to_string()}' is not optional.", loc)
        
        # 3. Primary Type Kind Check
        # Compare DaxaValue's actual runtime type enum with the expected instance type enum from schema type.
        value_instance_enum = daxa_val.daxa_type_enum
        expected_instance_enum = resolved_expected_type.get_instance_type_enum()

        if expected_instance_enum == DaxaTypeEnumV4.ANY:
            # If schema expects 'any', any valid DaxaValue is accepted here.
            # Constraints on the 'any' type itself are applied below.
            pass # Value is some DaxaValue, 'any' accepts it.
        elif value_instance_enum == DaxaTypeEnumV4.ANY:
            # If value is 'any' but schema expects a specific type:
            # Validate the *inner value* of the 'any' DaxaValue.
            if isinstance(daxa_val.value, DaxaValue): # DaxaValue stored inside 'any'
                self.validate_value(daxa_val.value, resolved_expected_type, path_context, recursion_depth + 1)
                # If inner validation passes, apply constraints of the *outer* 'any' type if this DV represents that usage.
                # This path implies `daxa_val` itself is the schema field type that was `any`,
                # but its content (daxa_val.value) is being matched to `resolved_expected_type`.
                # This is an unusual validation path for 'any'.
                # Usually, if expected_type is 'any', then any DaxaValue passes.
                # If value's runtime type is 'any', and expected is concrete:
                # -> if value._value is DaxaValue, validate value._value against concrete.
                # -> if value._value is opaque Python, type error.
            else: # Opaque Python object within 'any' cannot conform to a specific Daxa type
                raise DaxaTypeError(f"Opaque 'any' value (Python type '{type(daxa_val.value).__name__}') at '{current_path_str}' "
                                     f"cannot satisfy expected Daxa type '{resolved_expected_type.to_string()}'.", loc)
        # Allow INT value for FLOAT type (implicit promotion)
        elif expected_instance_enum == DaxaTypeEnumV4.FLOAT and value_instance_enum == DaxaTypeEnumV4.INT:
            pass
        elif value_instance_enum != expected_instance_enum:
            raise DaxaTypeError(f"Type mismatch at '{current_path_str}'. Expected instance of '{expected_instance_enum}' "
                                 f"but got '{value_instance_enum}'. (Value: {daxa_val.value!r:.50})", loc)

        # 4. Apply Constraints from the resolved_expected_type
        # Constraints operate on the Python native value part of the DaxaValue
        # or the collection structure itself (for list/map length constraints).
        value_for_constraints: Any
        if value_instance_enum.is_primitive() or value_instance_enum == DaxaTypeEnumV4.ENUM_INSTANCE:
            value_for_constraints = daxa_val.value # Direct Python primitive or string for enum
        elif value_instance_enum.is_collection() or value_instance_enum == DaxaTypeEnumV4.STRUCT_INSTANCE:
            value_for_constraints = daxa_val.value # The list/dict of DaxaValues
        elif value_instance_enum == DaxaTypeEnumV4.ANY:
            value_for_constraints = daxa_val.value # Could be DaxaValue or Python primitive
            # If value is DaxaValue, constraints may need to operate on its py_value or DV itself.
            # Let constraint.validate handle this based on `value_instance_enum` if passed as ANY
        else: # DXD_SOURCE, MATH_SOURCE - constraints usually not applicable or custom
            value_for_constraints = daxa_val.value

        for constraint in resolved_expected_type.constraints:
            try:
                # Pass the DaxaTypeEnum of the value for the constraint to do its own applicability check
                constraint.validate(value_for_constraints, value_instance_enum, current_path_str, loc)
            except DaxaValidationError as e_constr: # Re-raise with path if not already set fully
                raise DaxaValidationError(f"Constraint failed for '{current_path_str}': {e_constr.message}",
                                          e_constr.location or loc) from e_constr


        # 5. Recursive Validation for Complex Types
        if value_instance_enum == DaxaTypeEnumV4.ARRAY:
            daxa_array_items = cast(List[DaxaValue], daxa_val.value)
            if resolved_expected_type.element_type is None:
                raise DaxaInternalError(f"ARRAY type '{resolved_expected_type.to_string()}' has no element_type for validation.", loc)
            expected_el_type = resolved_expected_type.element_type
            for i, item_val in enumerate(daxa_array_items):
                self.validate_value(item_val, expected_el_type, (path_context or []) + [i], recursion_depth + 1)

        elif value_instance_enum == DaxaTypeEnumV4.STRUCT_INSTANCE: # Map or Struct instance
            daxa_map_items = cast(Dict[str, DaxaValue], daxa_val.value)

            if resolved_expected_type.type_enum_kind == DaxaTypeEnumV4.MAP: # Generic map[K,V] from schema
                if resolved_expected_type.value_type is None:
                    raise DaxaInternalError(f"MAP type '{resolved_expected_type.to_string()}' has no value_type.", loc)
                exp_val_type = resolved_expected_type.value_type
                for key, item_val in daxa_map_items.items():
                    # Key type check (DaxaValue for MAP should have string keys) implicitly handled
                    self.validate_value(item_val, exp_val_type, (path_context or []) + [key], recursion_depth + 1)
            
            elif resolved_expected_type.type_enum_kind == DaxaTypeEnumV4.SCHEMA_STRUCT_DEF: # Struct instance
                struct_name = resolved_expected_type.name
                if not struct_name: raise DaxaInternalError(f"Schema struct type has no name at '{current_path_str}'.", loc)
                
                struct_def = self.schema.get_definition(struct_name, StructDefinitionV4)
                if not struct_def: raise DaxaSchemaError(f"Struct definition '{struct_name}' not found in schema (for validating instance at '{current_path_str}').", loc)

                # Check for missing required fields & validate present fields
                defined_field_names = {f.name for f in struct_def.fields}
                for field_def in struct_def.fields:
                    if field_def.name in daxa_map_items:
                        field_dv = daxa_map_items[field_def.name]
                        self.validate_value(field_dv, field_def.daxa_type, (path_context or []) + [field_def.name], recursion_depth + 1)
                    else: # Field not in data instance
                        is_opt = field_def.daxa_type.get_resolved_type_fully().is_optional
                        has_def = field_def.daxa_type.get_resolved_type_fully().default_value_native is not None
                        if not is_opt and not has_def:
                            raise DaxaValidationError(f"Required field '{field_def.name}' missing in struct '{struct_name}' at '{current_path_str}'.", loc)
                
                # Check for extraneous fields if in strict mode
                if self.strict_fields:
                    for data_key in daxa_map_items.keys():
                        if data_key not in defined_field_names:
                            raise DaxaValidationError(f"Extraneous field '{data_key}' found in struct '{struct_name}' instance at '{current_path_str}'.", loc)
            # Else: MAP instance but schema type was not map or struct_def - should be caught by type mismatch

        elif value_instance_enum == DaxaTypeEnumV4.ENUM_INSTANCE:
            # Value is string. Expected type should be a resolved SCHEMA_ENUM_DEF DaxaTypeV4.
            if resolved_expected_type.type_enum_kind != DaxaTypeEnumV4.SCHEMA_ENUM_DEF:
                 raise DaxaInternalError(f"Value is ENUM_INSTANCE but expected schema type kind is '{resolved_expected_type.type_enum_kind}'. Inconsistency.", loc)
            enum_name = resolved_expected_type.name
            if not enum_name: raise DaxaInternalError(f"Expected enum type has no definition name.", loc)
            
            enum_def = self.schema.get_definition(enum_name, EnumDefinitionV4)
            if not enum_def: raise DaxaSchemaError(f"Enum definition '{enum_name}' not found for value at '{current_path_str}'.", loc)

            if cast(str, daxa_val.value) not in enum_def.values:
                raise DaxaValidationError(f"Value '{daxa_val.value}' at '{current_path_str}' is not a valid member of enum '{enum_name}'. "
                                          f"Allowed: {', '.join(enum_def.values)}.", loc)

        # DXD_SOURCE_CONTENT / MATH_SOURCE_CONTENT: Value is Diagram/MathEquationDefinitionV4.
        # No further validation here unless specific constraints are on these types.

    def validate_constant_definition(self, const_def: ConstantDefinitionV4) -> None:
        """Validates a ConstantDefinitionV4: value vs declared type."""
        loc = const_def.source_loc or (self.schema.source_file_path and SourceLocation(0,0,f"const {const_def.name}"))
        if const_def.declared_type:
            # Constant's declared_type must use this validator's schema context to resolve.
            decl_type_in_context = const_def.declared_type._clone_with_changes(schema_context=self.schema) #type:ignore
            resolved_decl_type = decl_type_in_context.get_resolved_type_fully()
            try:
                self.validate_value(const_def.daxa_value, resolved_decl_type, path_context=[f"const {const_def.name}"])
            except (DaxaValidationError, DaxaTypeError) as e_val:
                raise DaxaValidationError(
                    f"Value of constant '{const_def.name}' does not match its declared type '{resolved_decl_type.to_string()}'. "
                    f"Detail: {e_val.message}", const_def.daxa_value.source_location or loc or e_val.location
                ) from e_val
        # If no declared type, DaxaValue must be self-consistent (constructor ensures). Value itself is accepted.


    def validate_field_default_value(self, field: FieldV4, containing_struct_name: str) -> None:
        """
        Validates a field's default_value_native against the field's DaxaTypeV4.
        Called by SchemaV4.validate_schema_integrity().
        """
        if field.daxa_type.default_value_native is None: return

        loc = field.source_loc or field.daxa_type._source_loc #type:ignore
        field_type_in_context = field.daxa_type._clone_with_changes(schema_context=self.schema) #type:ignore
        resolved_field_type = field_type_in_context.get_resolved_type_fully()

        try:
            # Default value is PythonNative. Convert to DaxaValue for validation.
            # The DaxaType's default_value_native attribute must be Python values that
            # from_python_native can handle correctly for the resolved_field_type.
            default_daxa_val = DaxaValue.from_python_native(
                field.daxa_type.default_value_native,
                resolved_field_type, # Hint with the field's fully resolved type
                self.schema,
                source_loc=loc # Approximate location
            )
            self.validate_value(default_daxa_val, resolved_field_type,
                                path_context=[f"struct {containing_struct_name}", f"field {field.name}", "default"])
        except (DaxaValidationError, DaxaTypeError, DaxaSchemaError, DaxaInternalError) as e:
            raise DaxaSchemaError( # Schema error because default value defined in schema is bad
                f"Default value for field '{containing_struct_name}.{field.name}' (type '{resolved_field_type.to_string()}') "
                f"is invalid: {e.message}", loc or e.location
            ) from e