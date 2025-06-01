"""
daxa.core.diagram - Defines DiagramDefinition to hold diagram source code.
The actual parsing and AST for DXD diagrams (new DOT-like syntax) is in daxa.dxd.
"""
from enum import Enum
from typing import Dict, Any, Optional, Union, List

from .common import DaxaError, SourceLocation
from daxa.core import DaxaTypeEnum, DaxaValue  # Import DaxaTypeEnum and DaxaValue for type checking

class DiagramType(Enum):
    """Defines the type of diagram content. Focus on DXD for native support."""
    DXD = "dxd" # Daxa's native diagramming language (NEW DOT-like syntax)
    # Legacy/Import support (conceptual)
    MERMAID = "mermaid"
    GRAPHVIZ_DOT = "graphviz_dot"
    PLANTUML = "plantuml"
    UNKNOWN = "unknown"

    def __str__(self) -> str: return self.value

    @classmethod
    def from_string(cls, s: str) -> "DiagramType":
        # ... (implementation for from_string as before, prioritizing "dxd") ...
        s_lower = s.lower().strip()
        if s_lower == "dxd": return cls.DXD
        # ... other types for compatibility/import ...
        return cls.UNKNOWN


class DiagramDefinition:
    """
    Represents a diagram definition found within a Daxa document.
    It primarily stores the raw source code of the diagram.
    Parsing into an AST is handled by specialized parsers (e.g., DxdParser).
    """
    __slots__ = ('diagram_type', 'content', 'title', 'attributes',
                 'source_loc', 'block_subtype_keyword', 'block_metadata')

    def __init__(self,
                 diagram_type: Union[DiagramType, str],
                 content: str,
                 title: Optional[str] = None, # From DXD metadata or inferred
                 attributes: Optional[Dict[str, Any]] = None, # General renderer attributes
                 source_loc: Optional[SourceLocation] = None, # Location in .daxa file
                 # New fields for block-level info from `dxd subtype {meta} {content}`
                 block_subtype_keyword: Optional[str] = None, # e.g., "flow", "mindmap" from `dxd flow {...}`
                 block_metadata: Optional[DaxaValue] = None): # Parsed DaxaValue (map) from `{...}` metadata

        if isinstance(diagram_type, str):
            self.diagram_type: DiagramType = DiagramType.from_string(diagram_type)
        else:
            self.diagram_type: DiagramType = diagram_type

        self.content: str = content # Raw diagram source (e.g., content inside DXD's `graph {}`)
        self.title: Optional[str] = title
        self.attributes: Dict[str, Any] = attributes or {} # For renderer hints not in DXD content
        self.source_loc: Optional[SourceLocation] = source_loc
        self.block_subtype_keyword: Optional[str] = block_subtype_keyword
        self.block_metadata: Optional[DaxaValue] = block_metadata
        
        if self.block_metadata and self.title is None: # Infer title from block metadata if possible
            if isinstance(self.block_metadata.value, dict):
                title_from_meta = self.block_metadata.value.get("title")
                if isinstance(title_from_meta, DaxaValue) and title_from_meta.daxa_type_enum == DaxaTypeEnum.STRING:
                    self.title = title_from_meta.value


    def get_parsed_dxd_ast(self) -> Optional[List[Any]]: # Return type from dxd_ast.py
        """
        If this is a DXD diagram, parses its content using DxdParser and returns the AST.
        Caches the result. (Conceptual: parser needs to be robustly implemented)
        """
        if self.diagram_type != DiagramType.DXD: return None
        # if hasattr(self, '_cached_dxd_ast'): return self._cached_dxd_ast
        try:
            from daxa.dxd.dxd_parser import DxdParser # Lazy import to avoid cycles at init
            # The DxdParser should handle the `graph [type] {}` wrapper now
            parser = DxdParser(self.content, file_path=self.source_loc.path if self.source_loc else None)
            # The 'block_subtype_keyword' might be passed to DxdParser or used by renderer directly
            ast = parser.parse_full_diagram_content() # New method in parser to expect graph block
            # setattr(self, '_cached_dxd_ast', ast)
            return ast
        except ImportError: print("Warning: DxdParser not found, cannot parse DXD AST."); return None
        except Exception as e:
            if e.__class__.__name__ == "DaxaParsingError":
                print(f"Warning: Failed to parse DXD AST: {e}")
                return None
            print(f"Unexpected error parsing DXD AST: {e}")
            return None

    # ... to_dict_for_daxa, from_json_compatible, __repr__, __eq__ as before,
    # but ensure they handle new block_subtype_keyword and block_metadata if serializing DiagramDefinition itself.
    # Typically, these are attributes of the DiagramBlock in document model, not the DiagramDefinition content holder.