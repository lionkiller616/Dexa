"""
Daxa Core Language Package (V3 - Unified Block Language).

Handles the fundamental parsing, validation, schema management, data representation,
and serialization for the Daxa language and its various block types.
"""
# flake8: noqa: F401 (import all for easy access by other Daxa modules)

from .common import (
    DaxaError, DaxaParsingError, DaxaValidationError, DaxaSchemaError,
    DaxaIOError, DaxaInternalError, DaxaBlockTypeEnum, # New enum for block types
    DaxaTypeEnum, SourceLocation, DAXA_VERSION,
    DAXA_MAIN_FILE_MAGIC_COMMENT, # For .daxa general files
    DAXA_BINARY_MAGIC_NUMBER, DAXA_BINARY_FORMAT_VERSION,
    # ... other constants from common if needed
)
from .daxa_value import (
    DaxaValue, DaxaObject, DaxaArray, PYTHON_TO_DAXA_TYPE_MAP, PythonNative
)
# diagram.py and math_equation.py primarily define the *definition* classes
# that hold raw content and potentially an AST passed from specialized parsers.
from .diagram import DiagramDefinition # Will mostly be for DXD (new V2 syntax from your spec)
# math_equation.py might not be needed in core if MathBlock in document.model stores raw Math only.
# Or it could define MathEquationDefinition similar to DiagramDefinition. Let's assume basic for now.
# from .math_equation import MathEquationDefinition # (Conceptual - create this file if needed)

from .schema import (
    Schema, DaxaType, Field,
    StructDefinition, EnumDefinition, TypeAliasDefinition, ConstantDefinition, # These are Daxa type system defs
    Constraint, LengthConstraint, RangeConstraint, RegexConstraint
)
# The main parser for .daxa documents that understand blocks
from .parser_main import DaxaMainParser
# The main writer for .daxa documents
from .writer_main import DaxaMainWriter

from .validator import DaxaValidator

# Binary format (less emphasis in V3 doc-centric model, but still for data sections)
from .parser_binary import DaxaBinaryParser
from .writer_binary import DaxaBinaryWriter


__all__ = [
    # Common
    "DaxaError", "DaxaParsingError", "DaxaValidationError", "DaxaSchemaError",
    "DaxaIOError", "DaxaInternalError", "DaxaBlockTypeEnum",
    "DaxaTypeEnum", "SourceLocation", "DAXA_VERSION", "DAXA_MAIN_FILE_MAGIC_COMMENT",
    "DAXA_BINARY_MAGIC_NUMBER", "DAXA_BINARY_FORMAT_VERSION",
    # Daxa Value
    "DaxaValue", "DaxaObject", "DaxaArray", "PYTHON_TO_DAXA_TYPE_MAP", "PythonNative",
    # Diagram/Math (Definition holders)
    "DiagramDefinition", # "MathEquationDefinition", (if created)
    # Schema Components (Type System)
    "Schema", "DaxaType", "Field",
    "StructDefinition", "EnumDefinition", "TypeAliasDefinition", "ConstantDefinition",
    "Constraint", "LengthConstraint", "RangeConstraint", "RegexConstraint",
    # Main Parser/Writer for .daxa documents
    "DaxaMainParser", "DaxaMainWriter",
    # Validator
    "DaxaValidator",
    # Binary Data Codec
    "DaxaBinaryParser", "DaxaBinaryWriter",
]