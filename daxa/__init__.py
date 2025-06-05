"""
Daxa System Root Package (V4 - Unified Document & Data Language).

The Daxa System provides a comprehensive suite for working with the Daxa unified
language, including parsing, validation, serialization, native diagram (DXD) and
math rendering, a Command-Line Interface (CLI), and a Graphical User Interface (GUI).

Key components accessible from this top-level package:

Core Language & Document Processing:
  - `daxa.DaxaMainParserV4`: Parses .daxa, .dx, .dxc document files.
  - `daxa.DaxaMainWriterV4`: Serializes Daxa documents back to text.
  - `daxa.SchemaV4`, `daxa.DaxaValue`, `daxa.DaxaTypeV4`: Core type system and data representation.
  - `daxa.DaxaValidatorV4`: Validates data against schemas.
  - `daxa.doc_model.DaxaDocument`: The primary in-memory representation of a parsed Daxa file.
  - `daxa.doc_model.DaxaBlockBase` and its subclasses (TextBlock, DataInstanceBlock, etc.).
  - `daxa.doc_renderer_html.HtmlDocumentRendererV4`: Renders a DaxaDocument to HTML.

Native DXD Diagrams:
  - `daxa.dxd.DxdParserV4`: Parses the DXD (DOT-like) diagram syntax.
  - `daxa.dxd.DxdRendererSvgV4`: Renders DXD AST to SVG.
  - `daxa.core.DiagramDefinitionV4`: Holds raw DXD source.

Native DaxaMath:
  - `daxa.maths.MathsParserV4`: Parses the DaxaMath (LaTeX-inspired) syntax.
  - `daxa.maths.MathsRendererSvgV4`: Renders Math AST to SVG.
  - `daxa.core.MathEquationDefinitionV4`: Holds raw DaxaMath source.

Specialized File Parsers (primarily used internally by DaxaMainParserV4 or dedicated CLIs):
  - `daxa.config.DxcParserV4`: For .dxc configuration files/blocks.
  - `daxa.data_lang.DxParserV4`: For `data:` and `table:` blocks.

Utilities:
  - `daxa.utils.compress_data`, `daxa.utils.decompress_data`
  - `daxa.utils.encrypt_data`, `daxa.utils.decrypt_data`

For CLI usage: `python -m daxa.cli.main --help` or `daxa --help` (if installed)
For GUI usage: `python -m daxa.gui.main_window` or `daxa-gui` (if installed)
"""

# --- Versioning and Metadata ---
# Version of the Daxa System package itself
__version__ = "4.0.0-alpha.1"
# Version of the Daxa Language Specification this code implements
DAXA_LANGUAGE_VERSION = "4.0.0" # Could be same as package or independent

__author__ = "Lion (@lionxlover) & AI Collaborator"
__license__ = "MIT" # As per LICENSE file
from typing import Optional


# --- Expose Key Elements from Submodules for Convenience ---

# Core Language Parsing, Schema, Data, Validation
from .core import (
    DaxaError, DaxaParsingError, DaxaSyntaxError, DaxaValidationError,
    DaxaSchemaError, DaxaTypeError, DaxaNameError, DaxaIOError, DaxaRenderingError,
    DaxaConfigError, DaxaInternalError,
    SourceLocation, DaxaBlockTypeEnumV4, DaxaTypeEnumV4,
    DaxaValue, DaxaObject, DaxaArray, PythonNativeV4,
    SchemaV4, DaxaTypeV4, FieldV4,
    StructDefinitionV4, EnumDefinitionV4, TypeAliasDefinitionV4, ConstantDefinitionV4,
    ConstraintV4, LengthConstraintV4, RangeConstraintV4, RegexConstraintV4,
    DaxaMainParserV4, DaxaMainWriterV4,
    DaxaValidatorV4,
    DiagramDefinitionV4, MathEquationDefinitionV4,
    # DAXA_FILE_MAGIC_COMMENT_V4 # Constant, usually not directly used by lib consumers
)

# Document Object Model (Key Classes)
from .document.doc_model import (
    DaxaDocumentV4, DaxaBlockBaseV4, ProseTextBlockV4, HeadingBlockV4,
    TypeDefinitionBlockV4, DataInstanceBlockV4, TableBlockV4, DxdBlockV4,
    MathBlockV4, ConfigBlockV4, GenericCodeBlockV4
)

# Primary Document Renderer
from .document.doc_renderer_html import HtmlDocumentRendererV4

# Native DXD Processing (Key Classes - Parsers/Renderers often used via higher levels)
from .dxd import (
    DxdParserV4, DxdRendererSvgV4,
    # DxdAstNodeV4 and its specific subclasses from dxd_ast are usually for internal use by renderer
)

# Native DaxaMath Processing (Key Classes)
from .maths import (
    MathsParserV4, MathsRendererSvgV4,
    # MathsAstNodeV4 and subclasses are usually for internal use
)

# Configuration Processing (Key Classes - typically used via DaxaMainParserV4)
# from .config import DxcParserV4, DxcEvaluatorV4 # Less likely for direct top-level use

# Data Language Block Processing (Key Classes - typically used via DaxaMainParserV4)
# from .data_lang import DxParserV4 # Less likely for direct top-level use

# General Utilities (Selective exports)
from .utils import (
    compress_data, decompress_data,
    encrypt_data, decrypt_data, generate_encryption_key,
    daxa_schema_to_sql_ddl, export_daxa_dataset_to_csv, export_daxa_dataset_to_jsonl
)


# --- Define __all__ for `from daxa import *` ---
# It's good practice to be explicit. List what users should typically import.
__all__ = [
    # Metadata
    "__version__", "DAXA_LANGUAGE_VERSION", "__author__", "__license__",
    # Core Exceptions & Common
    "DaxaError", "DaxaParsingError", "DaxaSyntaxError", "DaxaValidationError",
    "DaxaSchemaError", "DaxaTypeError", "DaxaNameError", "DaxaIOError",
    "DaxaRenderingError", "DaxaConfigError", "DaxaInternalError",
    "SourceLocation", "DaxaBlockTypeEnumV4", "DaxaTypeEnumV4",
    # Core Language Components
    "DaxaValue", "DaxaObject", "DaxaArray", "PythonNativeV4",
    "DiagramDefinitionV4", "MathEquationDefinitionV4",
    "SchemaV4", "DaxaTypeV4", "FieldV4",
    "StructDefinitionV4", "EnumDefinitionV4", "TypeAliasDefinitionV4", "ConstantDefinitionV4",
    "ConstraintV4", "LengthConstraintV4", "RangeConstraintV4", "RegexConstraintV4",
    "DaxaMainParserV4", "DaxaMainWriterV4",
    "DaxaValidatorV4",
    # Document Model
    "DaxaDocumentV4", "DaxaBlockBaseV4", "ProseTextBlockV4", "HeadingBlockV4",
    "TypeDefinitionBlockV4", "DataInstanceBlockV4", "TableBlockV4", "DxdBlockV4",
    "MathBlockV4", "ConfigBlockV4", "GenericCodeBlockV4",
    "HtmlDocumentRendererV4",
    # Native Diagram & Math (primary interfaces if users want to parse/render fragments)
    "DxdParserV4", "DxdRendererSvgV4",
    "MathsParserV4", "MathsRendererSvgV4",
    # Key Utilities
    "compress_data", "decompress_data",
    "encrypt_data", "decrypt_data", "generate_encryption_key",
    "daxa_schema_to_sql_ddl", "export_daxa_dataset_to_csv", "export_daxa_dataset_to_jsonl",
]


# Optional top-level convenience functions to parse a .daxa file string or path
def parse_daxa_document(content: str, file_path: Optional[str] = None) -> DaxaDocumentV4:
    """Parses a Daxa document string and returns the DaxaDocumentV4 object."""
    parser = DaxaMainParserV4(file_path=file_path)
    # The DaxaMainParserV4.parse() method is expected to return a list of block objects (dicts)
    # and the aggregated schema. We need a step to construct DaxaDocumentV4 from these.
    # For now, assume parser.parse() directly returns the DaxaDocumentV4 instance or raises DaxaParsingError
    parsed_block_structs, schema_ctx = parser.parse_to_block_structs(content)
    return DaxaDocumentV4(blocks_data=parsed_block_structs, global_schema=schema_ctx, source_path=file_path)

def load_daxa_document(file_path: str) -> DaxaDocumentV4:
    """Loads and parses a Daxa document from a file path."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return parse_daxa_document(content, file_path=file_path)
    except FileNotFoundError:
        raise DaxaIOError(f"Daxa file not found: '{file_path}'.", location=None) from None
    except IOError as e:
        raise DaxaIOError(f"Error reading Daxa file '{file_path}': {e}", location=None) from e

if "parse_daxa_document" not in __all__: __all__.append("parse_daxa_document") # type: ignore
if "load_daxa_document" not in __all__: __all__.append("load_daxa_document") # type: ignore