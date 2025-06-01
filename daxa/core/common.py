"""
daxa.core.common - Common constants, enums, and custom exceptions for the Daxa language.
V3: Unified Block Language Focus.
"""
import sys
from enum import Enum
from typing import Optional, NamedTuple

# --- Constants ---
DAXA_VERSION: str = "3.0.0-alpha" # Version for the Daxa Language Specification V3
DAXA_MAIN_FILE_MAGIC_COMMENT: str = "# DAXA Document" # For general .daxa files

# Binary Format Constants (for .dex compiled data sections, if used)
DAXA_BINARY_MAGIC_NUMBER: bytes = b"DXB2" # Daxa Binary v2 (update if format changes)
DAXA_BINARY_FORMAT_VERSION: int = 2
DAXA_BINARY_ENDIANNESS: str = "!" # Big-endian

# --- Source Location ---
class SourceLocation(NamedTuple):
    """Represents a location in a Daxa source file."""
    line: int
    column: int
    path: Optional[str] = None # File path, if available

    def __str__(self) -> str:
        path_str = f" in '{self.path}'" if self.path else ""
        return f"(Line {self.line}, Col {self.column}{path_str})"

# --- Daxa Base Exception ---
class DaxaError(Exception):
    """Base class for all Daxa-specific errors."""
    def __init__(self, message: str, location: Optional[SourceLocation] = None):
        self.message = message
        self.location = location
        super().__init__(self.formatted_message())

    def formatted_message(self) -> str:
        if self.location:
            return f"{self.message} {self.location}"
        return self.message

# --- Specific Daxa Exceptions ---
class DaxaParsingError(DaxaError): """Error during parsing of Daxa text."""
class DaxaValidationError(DaxaError): """Error during Daxa data/schema validation."""
class DaxaSchemaError(DaxaError): """Error related to Daxa schema definition or resolution."""
class DaxaIOError(DaxaError): """Error related to file I/O for Daxa files."""
class DaxaInternalError(DaxaError): """Indicates an unexpected internal Daxa system error."""
class DaxaRenderingError(DaxaError): """Error during rendering of DXD or Math."""

# --- Daxa Block Type Enumeration (NEW for V3) ---
class DaxaBlockTypeEnum(Enum):
    """Identifies the type of a top-level block in a Daxa document."""
    PROSE = "prose"                 # Markdown-like text content
    TYPE_DEFINITION = "type_definition" # Encompasses struct, enum, type alias defined with `type:` or keywords
    CONSTANT_DEFINITION = "constant_definition" # `const:` block or `const NAME = ...;`
    DATA_INSTANCE = "data_instance"     # `data TypeName instanceName { ... }`
    TABLE_DATA = "table_data"         # `table TableName {cols} = [rows];`
    DXD_DIAGRAM = "dxd_diagram"       # `dxd subtype? {meta} { content }` block
    MATH_EQUATION = "math_equation"     # `math {meta} { content }` block (for display math)
    CONFIG_DATA = "config_data"         # `config ConfigName { ... }` block
    GENERIC_CODE = "generic_code"     # `code lang { ... }` block
    # Potentially others like COMMENT_BLOCK if comments are treated as structural elements by parser

    def __str__(self) -> str:
        return self.value

# --- Daxa Type System Enumeration (for schema fields and data values) ---
class DaxaTypeEnum(Enum):
    """Enumeration of fundamental Daxa data types within the type system."""
    NULL = "null"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BYTES = "bytes"
    DATETIME = "datetime"
    UUID = "uuid"
    ARRAY = "array"       # `array<ElementType>`
    MAP = "map"         # `map<KeyType, ValueType>` (Daxa typically string keys)
    STRUCT = "struct"     # Represents a struct *definition* keyword/concept
    ENUM = "enum"       # Represents an enum *definition* keyword/concept
    ALIAS = "alias"       # Represents a type alias *definition* keyword/concept
    ANY = "any"         # Can hold any DaxaValue
    DIAGRAM = "diagram"   # Data type for holding a DiagramDefinition (DXD content)
    MATH = "math"       # Data type for holding a MathEquationDefinition (DaxaMath content)
    # Custom named types (StructName, EnumName, AliasName) are resolved to these base kinds + name.

    def __str__(self) -> str: return self.value
    @classmethod
    def from_string(cls, s: str) -> "DaxaTypeEnum": # (implementation same as before)
        s_lower = s.lower()
        for member in cls:
            if member.value == s_lower: return member
        if s_lower == "integer": return cls.INT
        if s_lower == "number": return cls.FLOAT # Or INT
        if s_lower == "boolean": return cls.BOOL
        if s_lower == "object": return cls.MAP
        raise ValueError(f"Unknown DaxaTypeEnum identifier: '{s}'")
    def is_primitive(self) -> bool:
        return self in (DaxaTypeEnum.NULL, DaxaTypeEnum.BOOL, DaxaTypeEnum.INT, DaxaTypeEnum.FLOAT,
                         DaxaTypeEnum.STRING, DaxaTypeEnum.BYTES, DaxaTypeEnum.DATETIME, DaxaTypeEnum.UUID)
    def is_collection(self) -> bool: return self in (DaxaTypeEnum.ARRAY, DaxaTypeEnum.MAP)


MAX_RECURSION_DEPTH: int = 50 # For parsing & validation