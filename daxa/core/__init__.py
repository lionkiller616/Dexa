"""
Daxa Core Language Package (V4 - Unified Document & Data Language).

Handles the fundamental parsing of Daxa documents, schema definitions, data
representation, validation, and serialization. It forms the bedrock for processing
.daxa, .dx (data-focused), and .dxc (config-focused) files.
"""
# flake8: noqa: F401

from .common import (
    DaxaError, DaxaParsingError, DaxaValidationError, DaxaSchemaError,
    DaxaIOError, DaxaInternalError, DaxaRenderingError, DaxaBlockTypeEnumV4,
    DaxaTypeEnumV4, SourceLocation, DAXA_VERSION_V4,
    DAXA_FILE_MAGIC_COMMENT_V4,
    DAXA_BINARY_MAGIC_NUMBER_V4, DAXA_BINARY_FORMAT_VERSION_V4,
)
from .daxa_value import ( # V4: Mostly stable but used by new parser logic
    DaxaValue, DaxaObject, DaxaArray, PYTHON_TO_DAXA_TYPE_MAP_V4, PythonNativeV4
)
from .diagram import DiagramDefinitionV4 # V4: Holds raw DXD v2 (DOT-like) content
from .math_equation import MathEquationDefinitionV4 # V4: Holds raw DaxaMath v2 content

from .schema import ( # V4: Schema definitions as parsed from `struct/enum/type/const` keywords
    SchemaV4, DaxaTypeV4, FieldV4,
    StructDefinitionV4, EnumDefinitionV4, TypeAliasDefinitionV4, ConstantDefinitionV4,
    ConstraintV4, LengthConstraintV4, RangeConstraintV4, RegexConstraintV4
)
# Main parser for .daxa, .dx, .dxc documents
from .parser_main import DaxaMainParserV4
# Main writer for these document types
from .writer_main import DaxaMainWriterV4

from .validator import DaxaValidatorV4

# Binary format for .dex data sections
from .parser_binary import DaxaBinaryParserV4
from .writer_binary import DaxaBinaryWriterV4

__all__ = [
    "DaxaError", "DaxaParsingError", "DaxaValidationError", "DaxaSchemaError",
    "DaxaIOError", "DaxaInternalError", "DaxaRenderingError", "DaxaBlockTypeEnumV4",
    "DaxaTypeEnumV4", "SourceLocation", "DAXA_VERSION_V4",
    "DAXA_FILE_MAGIC_COMMENT_V4", "DAXA_BINARY_MAGIC_NUMBER_V4", "DAXA_BINARY_FORMAT_VERSION_V4",

    "DaxaValue", "DaxaObject", "DaxaArray", "PYTHON_TO_DAXA_TYPE_MAP_V4", "PythonNativeV4",
    
    "DiagramDefinitionV4", "MathEquationDefinitionV4",
    
    "SchemaV4", "DaxaTypeV4", "FieldV4",
    "StructDefinitionV4", "EnumDefinitionV4", "TypeAliasDefinitionV4", "ConstantDefinitionV4",
    "ConstraintV4", "LengthConstraintV4", "RangeConstraintV4", "RegexConstraintV4",
    
    "DaxaMainParserV4", "DaxaMainWriterV4",
    "DaxaValidatorV4",
    "DaxaBinaryParserV4", "DaxaBinaryWriterV4",
]