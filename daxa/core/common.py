"""
daxa.core.common (V4) - Common constants, enums, and custom exceptions
                         for the Daxa unified language.
"""
import sys # For sys.byteorder, though we're fixing endianness
from enum import Enum, auto # auto for DaxaBlockTypeEnumV4 if values don't matter
from typing import Optional, NamedTuple, Dict, Type, Any
import datetime # Needed for PYTHON_TO_DAXA_TYPE_MAP_V4
import uuid     # Needed for PYTHON_TO_DAXA_TYPE_MAP_V4

# --- Daxa System and Language Versioning ---
DAXA_VERSION_V4: str = "4.0.0-alpha.1" # Version for the Daxa Language Specification this codebase targets

# --- File Type Markers ---
DAXA_FILE_MAGIC_COMMENT_V4: str = "# DAXA Document" # Recommended first line for .daxa files
# Specific magic comments/markers could exist for .dx, .dxc, .dxd, .maths if they have unique top-level needs
# DAXA_DX_MAGIC_COMMENT_V4: str = "# DAXA Data File"
# DAXA_DXC_MAGIC_COMMENT_V4: str = "# DAXA Config File"
# (For now, a general Daxa file parser might look for these if handling different dedicated file types)

# --- Binary Format Constants (for .dex compiled data sections/full docs) ---
DAXA_BINARY_MAGIC_NUMBER_V4: bytes = b"DEXA" # Identifies a Daxa compiled binary file
DAXA_BINARY_FORMAT_VERSION_V4: int = 4    # Version of the binary format itself
DAXA_BINARY_ENDIANNESS_V4: str = "!"      # Big-endian ('network') for struct pack/unpack

# Compression/Encryption type IDs for binary format (shared with daxa.utils)
COMPRESSION_TYPE_NONE_V4: int = 0
COMPRESSION_TYPE_ZSTD_V4: int = 1
COMPRESSION_TYPE_LZ4_V4: int = 2

ENCRYPTION_TYPE_NONE_V4: int = 0
ENCRYPTION_TYPE_AES_256_GCM_V4: int = 1


# --- Parser and Validator Configuration ---
MAX_RECURSION_DEPTH_V4: int = 100 # For parsing nested structures and validation to prevent stack overflows

# --- Source Location Tracking ---
class SourceLocation(NamedTuple):
    """Represents a location (line, column, file path) in a Daxa source file."""
    line: int    # 1-indexed line number
    column: int  # 1-indexed column number
    path: Optional[str] = None # File path, if available
    # Optional: add length or end_line/end_column for spans

    def __str__(self) -> str:
        path_str = f" in '{self.path}'" if self.path else ""
        return f"(L{self.line}:C{self.column}{path_str})"


# --- Base Daxa Exception ---
class DaxaError(Exception):
    """Base class for all Daxa-specific errors, incorporating source location."""
    def __init__(self, message: str, location: Optional[SourceLocation] = None,
                 hint: Optional[str] = None):
        self.message: str = message
        self.location: Optional[SourceLocation] = location
        self.hint: Optional[str] = hint # Optional hint for user
        super().__init__(self.formatted_message())

    def formatted_message(self) -> str:
        """Returns the error message, including source location and hint if available."""
        msg = f"{self.message}"
        if self.location:
            msg += f" {self.location}"
        if self.hint:
            msg += f"\n  Hint: {self.hint}"
        return msg


# --- Specific Daxa Exceptions (V4) ---
class DaxaParsingError(DaxaError): """Error during parsing of Daxa text."""
class DaxaSyntaxError(DaxaParsingError): """More specific parsing error for syntax violations."""
class DaxaValidationError(DaxaError): """Error during Daxa data or schema validation against defined rules."""
class DaxaSchemaError(DaxaError): """Error related to schema definitions (e.g., invalid struct, unresolved type)."""
class DaxaTypeError(DaxaError): """Error related to type mismatches or invalid type operations at runtime or validation."""
class DaxaNameError(DaxaError): """Error related to undefined or duplicate names/identifiers (e.g., for variables, types, datasets)."""
class DaxaIOError(DaxaError): """Error related to file input/output operations for Daxa files."""
class DaxaRenderingError(DaxaError): """Error occurring during the rendering of DXD diagrams or DaxaMath equations."""
class DaxaConfigError(DaxaError): """Error specific to processing Daxa configuration (`.dxc` or `config:`) blocks."""
class DaxaPermissionsError(DaxaError): """Error related to permissions (e.g., for `include` directives, file access)."""
class DaxaInternalError(DaxaError): """Indicates an unexpected internal Daxa system logic error. Should ideally not be user-facing."""


# --- Daxa Document Block Type Enumeration (V4) ---
class DaxaBlockTypeEnumV4(Enum):
    """Identifies the type of a top-level block in a Daxa V4 document."""
    # Based on your V3 syntax spec block keywords/types
    PROSE = auto()                  # Markdown-like text content
    HEADING = auto()                # Parsed from prose: # H1 ... ###### H6
    HORIZONTAL_RULE = auto()        # Parsed from prose: --- / *** / ___
    LIST_BLOCK = auto()             # Parsed from prose: *,-,+, 1. lists
    QUOTE_BLOCK = auto()            # Parsed from prose: > quote
    GENERIC_CODE_BLOCK = auto()     # `code lang { ... }` or ```lang ... ```

    TYPE_ALIAS_DEFINITION = auto()  # `type Name = ...;`
    ENUM_DEFINITION = auto()        # `enum Name { VAL1; VAL2; }`
    STRUCT_DEFINITION = auto()      # `struct Name { field: Type; ... }`
    CONSTANT_DEFINITION = auto()    # `const NAME: Type = ...;`
    
    DATA_INSTANCE = auto()          # `data StructTypeName instanceName { ... }`
    TABLE_DATA = auto()             # `table TableName {cols_schema} = [rows_data];`
    
    DXD_DIAGRAM = auto()            # `dxd optional_subtype {metadata} { DXD_V2_Content }`
    MATH_EQUATION = auto()          # `math {metadata} { DaxaMath_Content }` (block equations)
                                    # Inline math `∫...∫` becomes part of ProseBlock's rich text structure

    CONFIG_BLOCK = auto()           # Top-level `config ConfigBlockName: OptType { ... }`
    # For `.dxc` files, parser might also produce finer-grained config block types:
    # CONFIG_SECTION_HEADER = auto()  # `[Section.Name]` in .dxc
    # CONFIG_KEY_VALUE = auto()       # `key = value;` in .dxc section
    # CONFIG_CONST_DEF = auto()       # `const NAME = val;` in .dxc scope
    # CONFIG_INCLUDE = auto()         # `@include "path";` in .dxc
    
    # For `.dx` "database" files (beyond regular DATA_INSTANCE and TABLE_DATA)
    INDEX_DIRECTIVE = auto()        # `index TableName.fieldName;`
    META_DIRECTIVE = auto()         # `meta key = value;` (file-level metadata for .dx)

    COMMENT_BLOCK = auto()          # If parser treats `/* ... */` as distinct structural blocks
    UNKNOWN_BLOCK = auto()          # For content the main parser couldn't categorize

    def __str__(self) -> str: # User-friendly name
        return self.name.lower().replace("_definition", "").replace("_v4", "")


# --- Daxa Type System Enumeration (V4) ---
class DaxaTypeEnumV4(Enum):
    """Fundamental Daxa data types used in schemas, variables, and values."""
    # Based on your ".dx File Structure - Data Types Supported" and common needs
    NULL = "null"
    INT = "int"                   # Typically platform's standard int, consider 64-bit for binary
    FLOAT = "float"               # Typically IEEE 754 double
    STRING = "string"             # UTF-8 text
    BOOL = "bool"                 # true/false
    
    # Complex Types / Instances
    ENUM_INSTANCE = "enum_instance"     # Value is a string, type refers to an EnumDefinitionV4
    STRUCT_INSTANCE = "struct_instance" # Value is a DaxaObject, type refers to a StructDefinitionV4
    ARRAY = "array"                     # Value is a List[DaxaValue], typed `[ElementType]` or `array<ElementType>`
    MAP = "map"                       # `map[KeyType, ValueType]`. KeyType usually string. If this syntax is used.
                                      # Otherwise, struct_instance covers general object needs.

    # Schema Definition Keywords (used by parser when identifying definitions)
    # These are NOT runtime types of DaxaValue instances directly.
    SCHEMA_STRUCT_KEYWORD = "struct_keyword"  # e.g., when parsing `struct User {...}`
    SCHEMA_ENUM_KEYWORD = "enum_keyword"
    SCHEMA_TYPE_ALIAS_KEYWORD = "type_alias_keyword" # e.g., when parsing `type UserID = int;`

    # Semantic types that might have specific DaxaValue representations or handling
    DATETIME = "datetime"         # Represented as ISO8601 string by default for text format
    UUID = "uuid"                 # Represented as standard UUID string
    BYTES = "bytes"               # Raw byte sequence. Represented as hex `0x...` or `b"..."` in text.
                                  # If not in `.dx` primitive list, string fields need `@format("bytes")` attribute.
                                  # For clarity, let's include it as a distinct type system enum.

    # Special semantic types for fields/values if needed by Daxa tooling directly
    DXD_SOURCE_CONTENT = "dxd_source_content"   # Field contains raw DXD string (e.g., `my_diag_field: dxd_source;`)
    MATH_SOURCE_CONTENT = "math_source_content" # Field contains raw DaxaMath string

    ANY = "any"                     # Can hold any DaxaValue; use sparingly
    UNKNOWN_TYPE = "unknown_type"   # If a declared type name cannot be resolved by schema

    def __str__(self) -> str: return self.value.replace("_", "-")

    @classmethod
    def from_string(cls, s: str) -> "DaxaTypeEnumV4":
        s_lower = s.lower().replace("-", "_") # Allow "enum-instance"
        for member in cls:
            if member.value.replace("_", "-") == s.lower() or member.name.lower() == s_lower :
                return member
        # Aliases from typical programming languages
        if s_lower in ["integer", "long"]: return cls.INT
        if s_lower in ["number", "double", "decimal"]: return cls.FLOAT
        if s_lower == "boolean": return cls.BOOL
        if s_lower in ["object", "dict", "dictionary"]: return cls.STRUCT_INSTANCE # Or MAP if that syntax used
        if s_lower in ["list", "vector"]: return cls.ARRAY
        if s_lower in ["timestamp"]: return cls.DATETIME # For semantic alias
        if s_lower in ["guid"]: return cls.UUID
        if s_lower in ["blob", "binary"]: return cls.BYTES

        raise ValueError(f"Unknown DaxaTypeEnumV4 identifier: '{s}'")

    def is_primitive(self) -> bool:
        """Checks if this enum represents a Daxa primitive data type value."""
        return self in (
            DaxaTypeEnumV4.NULL, DaxaTypeEnumV4.INT, DaxaTypeEnumV4.FLOAT,
            DaxaTypeEnumV4.STRING, DaxaTypeEnumV4.BOOL, DaxaTypeEnumV4.DATETIME,
            DaxaTypeEnumV4.UUID, DaxaTypeEnumV4.BYTES
        )

    def is_instance_type(self) -> bool:
        """Checks if this enum represents a type that can be an instance in a DaxaValue."""
        return self.is_primitive() or self in (
            DaxaTypeEnumV4.ENUM_INSTANCE, DaxaTypeEnumV4.STRUCT_INSTANCE,
            DaxaTypeEnumV4.ARRAY, DaxaTypeEnumV4.MAP, DaxaTypeEnumV4.ANY,
            DaxaTypeEnumV4.DXD_SOURCE_CONTENT, DaxaTypeEnumV4.MATH_SOURCE_CONTENT
        )


# Mapping Python types to DaxaTypeEnumV4 for DaxaValue.from_python_native()
PYTHON_TO_DAXA_TYPE_MAP_V4: Dict[Type, DaxaTypeEnumV4] = {
    type(None): DaxaTypeEnumV4.NULL,
    bool: DaxaTypeEnumV4.BOOL,
    int: DaxaTypeEnumV4.INT,
    float: DaxaTypeEnumV4.FLOAT,
    str: DaxaTypeEnumV4.STRING,
    bytes: DaxaTypeEnumV4.BYTES, # Direct mapping now that BYTES is a DaxaTypeEnum
    list: DaxaTypeEnumV4.ARRAY,
    dict: DaxaTypeEnumV4.STRUCT_INSTANCE, # Python dicts become struct instances or maps
    datetime.datetime: DaxaTypeEnumV4.DATETIME,
    uuid.UUID: DaxaTypeEnumV4.UUID,
    # DiagramDefinitionV4/MathEquationDefinitionV4 might map to DXD_SOURCE_CONTENT / MATH_SOURCE_CONTENT
    # if passed to from_python_native.
}