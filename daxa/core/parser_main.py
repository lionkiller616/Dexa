"""
daxa.core.parser_main - Main Daxa Document Parser (.daxa files).
Parses V3 block-oriented syntax: prose, type, data, dxd, math, config, table, code.
Outputs a sequence of block representations for a DaxaDocument model.
"""
import re
import io
import os
from typing import Dict, List, Any, Tuple, Optional, Union, Callable, cast

from .common import (
    DaxaTypeEnum, DaxaError, DaxaParsingError, DaxaSchemaError, DaxaInternalError,
    SourceLocation, DaxaBlockTypeEnum, DAXA_MAIN_FILE_MAGIC_COMMENT
)
from .schema import ( # For parsing type/const/data definitions within their blocks
    Schema, DaxaType, Field, StructDefinition, EnumDefinition,
    TypeAliasDefinition, ConstantDefinition
)
from .daxa_value import DaxaValue # For parsing data literals
# Placeholder for actual block objects from daxa.document.model
# from daxa.document.model import (
#     DaxaDocument, ProseBlock, TypeDefBlock, DataInstanceBlock, TableBlock,
#     DxdBlock, MathBlock, ConfigBlock, GenericCodeBlock, HorizontalRuleBlock, HeadingBlock
# )

# Re-import and potentially rename the _ParserState helper if needed
from core import _ParserState as DaxaParserState # Assuming prior robust _ParserState

# Regexes for block identification (simplified)
RE_HEADING = re.compile(r"^(#{1,6})\s+(.*)") # Markdown headings
RE_HR = re.compile(r"^(?:-{3,}|_{3,}|={3,})\s*$") # Horizontal Rules (using '=' too for TOML-like section breaks)

# Keywords for explicit Daxa blocks (case-sensitive)
# Note: Your spec used "type", "struct", "enum", "const" for definitions.
# Let's assume `type MyStruct { ... }` becomes `struct MyStruct { ... }` for directness here.
# Or, a `definitions:` block that then contains struct/enum/type/const.
# For now, using the direct keywords as top-level block indicators as per your last spec:
# type UserID = int; struct User {...} enum Status {...} const PI = 3.14;
# data User john_doe {...}
# table Planets {...} = [...]
# dxd opt_subtype { meta } { content }
# math { meta } { content }
# config MyConfig { key=val }
# code lang { content }
# Prose is anything else.

BLOCK_KEYWORDS = [
    "type", "enum", "struct", "const", # Schema definition related
    "data", "table",                   # Data instance / tabular data
    "dxd", "math",                     # Embedded DSLs
    "config",                          # Configuration blocks
    "code"                             # Generic code blocks
]
# Regex to find any of these keywords at the start of a line (ignoring leading whitespace)
RE_BLOCK_KEYWORD_START = re.compile(r"^\s*(" + "|".join(BLOCK_KEYWORDS) + r")\b")


# Represents the output of this parser (conceptually, list of Block Objects for DaxaDocument)
# For this generation, will be List[Dict[str, Any]] or List[Tuple[DaxaBlockTypeEnum, Any, SourceLocation]]
ParsedBlock = Dict[str, Any] # e.g. {"block_type": DaxaBlockTypeEnum, "content": ..., "loc": ...}


class DaxaMainParser:
    """
    Parses a full Daxa document string, identifying and processing various
    Daxa V3 block types (prose, schema, data, diagrams, math, config, etc.).
    Produces a list of block objects representing the document structure.
    """

    def __init__(self, file_path: Optional[str] = None):
        self.file_path: Optional[str] = file_path
        self._state: DaxaParserState = None  # type: ignore Initialized in parse()
        self.schema_context: Schema = Schema(source_file_path=file_path) # Aggregates all type defs
        self.parsed_blocks: List[ParsedBlock] = []

    def _init_parse_state(self, text_content: str):
        self._state = DaxaParserState(text_content, self.file_path)
        self.schema_context = Schema(name=f"Schema_{os.path.basename(self.file_path or 'untitled')}",
                                     source_file_path=self.file_path)
        self.parsed_blocks = []

    def _add_block(self, block_type: DaxaBlockTypeEnum, content: Any, loc: SourceLocation,
                   metadata: Optional[Dict[str, Any]] = None, lang: Optional[str]=None):
        block_data: ParsedBlock = {"block_type": block_type, "content": content, "loc": loc}
        if metadata: block_data["metadata"] = metadata
        if lang: block_data["language"] = lang
        self.parsed_blocks.append(block_data)


    def _parse_optional_metadata_struct_literal(self) -> Optional[DaxaValue]:
        """
        Tries to parse an optional Daxa struct literal like `{key: "val", ...}`
        often used for block-level metadata after a block keyword and before content.
        Returns DaxaValue if parsed, else None. Assumes metadata ends before a newline if on same line as keyword,
        or is on its own line. For `dxd/math/config { metadata } { content }` syntax, parser needs to be specific.

        Your new spec like `dxd optional_subtype { metadata_struct } { content }`
        is parsed where `DaxaMainParser` gets `optional_subtype` and `metadata_struct`,
        then gives `content` to a specialized parser.
        """
        current_ptr = self._state.ptr
        self._state.skip_space_and_line_comments() # skip space after keyword or sub-keyword
        
        if self._state.peek() == '{':
            try:
                # This needs the value literal parser from previous DaxaTextParser (or integrated here)
                # For now, this is a major placeholder for parsing a DaxaValue map object.
                # This requires a sub-parser instance for values or that logic to be here.
                # meta_dv = DaxaTextParser._parse_value_literal() <--- need that capability
                # For stub:
                loc_meta = self._state.get_loc()
                self._state.expect_and_consume("{") # type:ignore
                # ... parse key-value pairs ...
                metadata_content = {} # placeholder
                # This logic is extremely simplified and incorrect for a full map.
                if self._state.match_and_consume(r"[^}]+"): # type:ignore
                    # Dummy read until }
                    pass
                self._state.expect_and_consume("}") # type:ignore
                # Actual DaxaValue of type MAP with metadata_content would be returned
                meta_dv = DaxaValue(metadata_content, DaxaTypeEnum.MAP, source_loc=loc_meta)
                return meta_dv
            except DaxaParsingError:
                self._state.ptr = current_ptr # Backtrack if not a valid metadata struct literal
                return None
        self._state.ptr = current_ptr # Backtrack
        return None

    def _parse_fenced_content(self, opening_fence: str, closing_fence: str, block_name: str) -> Tuple[str, SourceLocation]:
        """
        Parses content between an opening and closing fence (e.g., ```` ``` ```` or `$$ $$` or `{}`).
        Handles simple fences. Does not handle nested fences of the same type.
        """
        loc_content_start = self._state.get_loc()
        try:
            # Assume fence already consumed or next char is start of fence
            if not self._state.content[self._state.ptr:].startswith(opening_fence):
                self._state.expect_and_consume(opening_fence, f"Expected opening '{opening_fence}' for {block_name} block content.") # type: ignore

            # Adjust pointer based on if expect_and_consume ate the fence or just checked it
            # Assuming expect_and_consume DOES eat it. If not, self._state.advance(len(opening_fence))

            content_start_ptr_after_fence = self._state.ptr
            
            # Find the end fence. This is tricky if content can contain the end fence (e.g. escaped)
            # For `dxd/math/config { content }` blocks, closing `}` is the fence.
            # For ```code```, ``` is fence.
            
            end_fence_pos = self._state.content.find(closing_fence, content_start_ptr_after_fence)
            if end_fence_pos == -1:
                raise DaxaParsingError(f"Unterminated {block_name} block. Expected closing '{closing_fence}'.", loc_content_start)

            content = self._state.content[content_start_ptr_after_fence : end_fence_pos]
            self._state.advance_to(end_fence_pos + len(closing_fence)) # Advance past content and closing fence
            return content.strip('\r\n'), loc_content_start # Remove leading/trailing newlines typically
        
        except DaxaParsingError:
            raise # Re-raise if expect_and_consume or other errors
        except Exception as e:
            raise DaxaParsingError(f"Error parsing content for {block_name} block: {e}", self._state.get_loc()) from e


    # --- Block Parsing Methods ---

    def _parse_type_definition_statement(self) -> bool:
        """Parses `type Alias = ...;`, `enum Name {...}`, `struct Name {...}`."""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        
        # This logic will be complex based on your "V3 Spec" for how these are written
        # e.g., `type UserID = int;` vs `type User { ... }` vs `type Status enum { ... }`
        # Needs careful tokenizing and dispatch. This is a simplified approach.
        # The original parser_text.py had more detailed sub-parsers for these; that logic
        # needs to be adapted to be called when these keywords are found.

        # For simplicity, let's assume these start with the keyword
        # `struct Name {...}`
        # `enum Name {...}`
        # `type Name = ...;`
        
        # --- TODO: Integrate refined parsing logic for struct/enum/alias ---
        # This section is a major placeholder requiring logic from the old DaxaTextParser._parse_..._definition methods,
        # adapted to fit into this block-parsing loop and to add results to self.schema_context
        # and a TypeDefinitionBlock to self.parsed_blocks.
        
        # Example structure:
        # if self._state.match_and_consume(re.compile(r"struct\b")):
        #     struct_name = self._parse_identifier(...)
        #     # ... parse fields into a StructDefinition object ...
        #     struct_def = StructDefinition(...)
        #     self.schema_context.add_definition(struct_def)
        #     self._add_block(DaxaBlockTypeEnum.TYPE_DEFINITION, struct_def, loc_start)
        #     return True
        # elif self._state.match_and_consume(re.compile(r"enum\b")): ...
        # elif self._state.match_and_consume(re.compile(r"type\b")): ... # This is TypeAlias
        
        # For now, this is a very coarse "skip" if these keywords are found, as full parsing here is too verbose.
        # A real implementation integrates the detailed parsing logic here.
        
        matched_keyword = False
        for kw in ["struct", "enum", "type "]: # Space after "type " for "type Name ="
            if self._state.content[self._state.ptr:].startswith(kw):
                # This means a definition starts here.
                # Find the end of this definition (complex: ; for alias, } for struct/enum)
                # This is a HACK to consume the line/block for the stub.
                line_end = self._state.content.find('\n', self._state.ptr)
                if line_end == -1: line_end = self._state.length
                
                # If it's a block like struct/enum, find closing brace
                if kw in ["struct", "enum"] and "{" in self._state.content[self._state.ptr:line_end]:
                    # Very naive brace finding. Needs proper balancing.
                    open_brace = self._state.content.find('{', self._state.ptr)
                    if open_brace != -1:
                        # This logic is placeholder for robust brace matching
                        # Example: Scan until matching '}' (needs depth counting for nested)
                        # For now, just assume definition ends at some point.
                        print(f"Parser stub: Found '{kw}' definition. Full parsing not stubbed here.")
                        # A real parser consumes token by token using the state.
                        # For now, skip to a sensible seeming end or error
                        end_of_def = self._state.content.find('}', open_brace)
                        if end_of_def == -1: end_of_def = line_end
                        else: end_of_def +=1

                        self._state.advance_to(end_of_def) 
                        self._add_block(DaxaBlockTypeEnum.TYPE_DEFINITION,
                                       f"Placeholder for {kw} def at {loc_start}", loc_start)

                else: # Likely type alias or const
                    self._state.advance_to(line_end)
                    self._add_block(DaxaBlockTypeEnum.TYPE_DEFINITION,
                                   f"Placeholder for {kw} def at {loc_start}", loc_start)

                return True # Consumed a type definition line/block
        return False # Not a recognized type definition starting token


    def _parse_const_definition_statement(self) -> bool:
        """Parses `const NAME: Type = Value;`"""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        if self._state.match_and_consume(re.compile(r"const\b")):
            # --- TODO: Integrate full const parsing from DaxaTextParser ---
            # This is a placeholder skip for the stub.
            print(f"Parser stub: Found 'const' definition. Full parsing not stubbed here.")
            line_end = self._state.content.find(';', self._state.ptr)
            if line_end == -1: line_end = self._state.content.find('\n', self.ptr) # type: ignore
            if line_end == -1: line_end = self._state.length
            else: line_end +=1 # Include semicolon

            const_content_str = self._state.content[loc_start.column-1 : line_end] # Rough content
            self._state.advance_to(line_end)
            self._add_block(DaxaBlockTypeEnum.CONSTANT_DEFINITION, f"Const: {const_content_str.strip()}", loc_start)
            return True
        return False

    def _parse_data_instance_block(self) -> bool:
        """Parses `data TypeName instanceName { field = value; ... }`"""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        if self._state.match_and_consume(re.compile(r"data\b")):
            # --- TODO: Integrate full data instance parsing ---
            # Requires parsing TypeName, instanceName, then key-value pairs for fields
            # against the TypeName's struct definition from self.schema_context.
            print(f"Parser stub: Found 'data' block. Full parsing not stubbed here.")
            # Placeholder: consume until potential closing brace or sensible end
            end_of_block = self._find_matching_brace(self._state.content, self._state.ptr, '{', '}')
            if end_of_block == -1 : end_of_block = self._state.content.find('\n', self.ptr) #type:ignore
            if end_of_block == -1 : end_of_block = self._state.length
            else: end_of_block +=1

            data_content_str = self._state.content[loc_start.column-1 : end_of_block]
            self._state.advance_to(end_of_block)
            self._add_block(DaxaBlockTypeEnum.DATA_INSTANCE, f"Data: {data_content_str.strip()}", loc_start)
            return True
        return False


    def _parse_table_block(self) -> bool:
        """Parses `table TableName { colName: colType; ... } = [ [rows...] ];`"""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        if self._state.match_and_consume(re.compile(r"table\b")):
            # --- TODO: Integrate full table parsing ---
            # 1. Parse TableName.
            # 2. Parse inline column schema { colName: colType @attr; ... }. Store this.
            # 3. Expect "=".
            # 4. Parse data: array of arrays literal `[ [val,...], [val,...] ]`.
            #    Values in inner arrays should conform to column types.
            print(f"Parser stub: Found 'table' block. Full parsing not stubbed here.")
            # Placeholder consumption
            end_of_block = self._state.content.find(';', self._state.ptr) # End of table block is after data literal's semicolon
            if end_of_block == -1 : end_of_block = self._state.content.find('\n', self.ptr) #type:ignore
            if end_of_block == -1 : end_of_block = self._state.length
            else: end_of_block +=1
            
            table_content_str = self._state.content[loc_start.column-1 : end_of_block]
            self._state.advance_to(end_of_block)
            self._add_block(DaxaBlockTypeEnum.TABLE_DATA, f"Table: {table_content_str.strip()}", loc_start)
            return True
        return False

    def _parse_dxd_block(self) -> bool:
        """Parses `dxd optional_subtype { metadata } { content }`"""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        if self._state.match_and_consume(re.compile(r"dxd\b")):
            subtype_keyword: Optional[str] = None
            # Try to parse optional subtype keyword
            subtype_match = self._state.match_and_consume(RE_DXD_IDENTIFIER) # type:ignore
            if subtype_match:
                subtype_keyword = subtype_match.group(0) if isinstance(subtype_match, re.Match) else subtype_match # type:ignore

            # Try to parse optional metadata struct literal
            block_metadata = self._parse_optional_metadata_struct_literal()

            # Expect opening { for DXD content
            self._state.expect_and_consume("{", "Expected '{' to start DXD block content.") # type: ignore
            
            # Content for DxdParser: the raw string content of the diagram itself
            # The content uses your new Graphviz-like DXD syntax (`graph type {} node A; A->B;`)
            # This content will be passed to `daxa.dxd.dxd_parser.DxdParser`.
            dxd_content_str, _ = self._parse_fenced_content("", "}", "DXD content") # Opening { already consumed by metadata or above expect.
                                                                                  # Fences "" and "}" mean read until next "}".

            self._add_block(DaxaBlockTypeEnum.DXD_DIAGRAM, dxd_content_str, loc_start,
                           metadata={"subtype": subtype_keyword, "block_meta_dv": block_metadata})
            return True
        return False

    def _parse_math_block(self) -> bool:
        """Parses `math { metadata } { content }` (block equations)"""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        if self._state.match_and_consume(re.compile(r"math\b")):
            block_metadata = self._parse_optional_metadata_struct_literal()
            self._state.expect_and_consume("{", "Expected '{' to start Math block content.") #type:ignore
            math_content_str, _ = self._parse_fenced_content("", "}", "Math content")
            # Content is DaxaMath syntax (e.g. E = mc^2)
            # This will be passed to `daxa.math.math_parser.MathParser`.
            self._add_block(DaxaBlockTypeEnum.MATH_EQUATION, math_content_str, loc_start,
                           metadata={"block_meta_dv": block_metadata})
            return True
        return False


    def _parse_config_block(self) -> bool:
        """Parses `config ConfigName: OptionalType { key = val; ... }`"""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        if self._state.match_and_consume(re.compile(r"config\b")):
            # --- TODO: Integrate full config block parsing ---
            # 1. ConfigBlockName (identifier)
            # 2. Optional : TypeName (DaxaType annotation for the whole config block)
            # 3. { key = value; sections [SubSection] { key = val } ... }
            #    Values are DaxaValueLiterals. `env("VAR", default)` needs special parsing.
            #    This requires its own specialized parser in `daxa.config.dxc_parser.py`.
            print(f"Parser stub: Found 'config' block. Full parsing not stubbed here.")
            # Placeholder consumption
            end_of_block = self._find_matching_brace(self._state.content, self._state.ptr, '{', '}')
            if end_of_block == -1 : end_of_block = self._state.content.find('\n', self.ptr) #type:ignore
            if end_of_block == -1 : end_of_block = self._state.length
            else: end_of_block +=1

            config_content_str = self._state.content[loc_start.column-1 : end_of_block] #type:ignore
            self._state.advance_to(end_of_block) #type:ignore
            self._add_block(DaxaBlockTypeEnum.CONFIG_DATA, f"Config: {config_content_str.strip()}", loc_start)
            return True
        return False

    def _parse_generic_code_block(self) -> bool:
        """Parses ``` ```lang { content } or ```lang \n content \n ```"""
        self._state.skip_space_and_line_comments()
        loc_start = self._state.get_loc()
        if self._state.match_and_consume(re.compile(r"code\b")):
            lang_identifier_match = self._state.match_and_consume(RE_DXD_IDENTIFIER) #type:ignore
            lang_identifier = lang_identifier_match.group(0) if isinstance(lang_identifier_match, re.Match) else lang_identifier_match #type:ignore
            if not lang_identifier:
                 raise DaxaParsingError("Expected language identifier after 'code' keyword.", self._state.get_loc())

            self._state.expect_and_consume("{", f"Expected '{{' to start code block for language '{lang_identifier}'.") # type:ignore
            # Content parsing is raw until matching '}'
            code_content, _ = self._parse_fenced_content("", "}", f"code {lang_identifier}") # Raw content
            self._add_block(DaxaBlockTypeEnum.GENERIC_CODE, code_content, loc_start, lang=lang_identifier)
            return True
        return False

    def _find_matching_brace(self, text:str, start_pos:int, open_char:str, close_char:str) -> int:
        """Helper to find matching closing brace, respecting nesting. Very basic."""
        balance = 0
        initial_open_found = False
        for i in range(start_pos, len(text)):
            if text[i] == open_char:
                balance += 1
                if not initial_open_found: initial_open_found = True
            elif text[i] == close_char:
                balance -= 1
            if initial_open_found and balance == 0:
                return i # Position of closing brace
        return -1 # Not found or unbalanced


    def _parse_prose_or_implicit_blocks(self) -> bool:
        """
        Parses Markdown-like prose, headings, or horizontal rules.
        This is called if no other Daxa keyword block is identified.
        It collects lines until a Daxa keyword block starts or EOF.
        """
        self._state.skip_space_and_line_comments() # Should be called before entering this.
        loc_start_prose = self._state.get_loc()
        prose_buffer = io.StringIO()
        start_ptr_prose_block = self._state.ptr

        while self._state.ptr < self._state.length:
            line_start_ptr = self._state.ptr
            # Find end of current line
            line_end_ptr = self._state.content.find('\n', self._state.ptr)
            if line_end_ptr == -1: line_end_ptr = self._state.length # Last line
            
            current_line_text = self._state.content[self._state.ptr : line_end_ptr].strip() # Current line stripped

            # Check if this line starts a new Daxa keyword block
            if RE_BLOCK_KEYWORD_START.match(self._state.content[line_start_ptr:]): # Check from actual line start
                break # End of current prose block

            # Check for Markdown Heading or HR
            heading_match = RE_HEADING.match(current_line_text)
            hr_match = RE_HR.match(current_line_text)

            if heading_match or hr_match:
                # If prose_buffer has content, finalize that first
                if prose_buffer.tell() > 0:
                    self._add_block(DaxaBlockTypeEnum.PROSE, prose_buffer.getvalue().strip(), loc_start_prose)
                    prose_buffer = io.StringIO(); start_ptr_prose_block = self._state.get_loc() # Reset for next
                
                if heading_match:
                    level = len(heading_match.group(1))
                    text = heading_match.group(2).strip()
                    self._add_block(DaxaBlockTypeEnum.PROSE, # Or specific HEADING type
                                   {"level": level, "text": text}, # Store as dict for heading
                                   SourceLocation(self._state.current_line, 1, self._state.file_path) )
                elif hr_match:
                    self._add_block(DaxaBlockTypeEnum.PROSE, # Or specific HR type
                                   "---HR---", # Special content for HR
                                   SourceLocation(self._state.current_line, 1, self._state.file_path) )
                
                self._state.advance_to(line_end_ptr) # Consume the heading/hr line
                if self._state.ptr < self._state.length and self._state.content[self._state.ptr] == '\n': self._state.advance() # Consume newline
                return True # Parsed an implicit block


            # Not a keyword block, not a heading/hr -- append to prose buffer
            # Append the original line including leading/trailing whitespace within the line
            # (but not file-level leading whitespace which skip_... already handled)
            prose_buffer.write(self._state.content[self._state.ptr : line_end_ptr] + '\n')
            self._state.advance_to(line_end_ptr)
            if self._state.ptr < self._state.length and self._state.content[self._state.ptr] == '\n':
                 self._state.advance() # Consume the newline character itself
            
            self._state.skip_space_and_line_comments() # For next line check (e.g. blank lines end paragraphs)

        # After loop, if prose_buffer has content, it's the last prose block
        final_prose = prose_buffer.getvalue().strip()
        if final_prose:
            self._add_block(DaxaBlockTypeEnum.PROSE, final_prose, loc_start_prose)
            return True
        return False # No prose was actually accumulated


    def parse(self, text_content: str) -> List[ParsedBlock]: # Returns List of "Block Objects"
        """
        Main Daxa document parsing method.
        Iteratively parses top-level blocks until EOF.

        Returns:
            A list of dictionaries, where each dictionary represents a parsed block
            (e.g., {"block_type": DaxaBlockTypeEnum.PROSE, "content": "...", "loc": ...}).
            This list forms the basis of a `DaxaDocument` object.
        """
        self._init_parse_state(text_content)

        # Optional: Check for Daxa magic comment
        self._state.skip_space_and_line_comments()
        if self._state.match_and_consume(DAXA_MAIN_FILE_MAGIC_COMMENT):
            # Could add a "metadata" block for file-level comments or pragmas.
            pass
        self._state.skip_space_and_line_comments()


        # Main parsing loop - identify and parse blocks
        while self._state.ptr < self._state.length:
            self._state.skip_space_and_line_comments()
            if self._state.ptr >= self._state.length: break

            start_of_loop_ptr = self._state.ptr

            # Try parsing keyword-led blocks first (most specific)
            if self._parse_type_definition_statement(): continue
            if self._parse_const_definition_statement(): continue
            if self._parse_data_instance_block(): continue
            if self._parse_table_block(): continue
            if self._parse_dxd_block(): continue
            if self._parse_math_block(): continue
            if self._parse_config_block(): continue
            if self._parse_generic_code_block(): continue
            
            # If none of the above, try to parse prose (which includes headings, HRs)
            if self._parse_prose_or_implicit_blocks(): continue

            # If parser didn't advance but not EOF, there's an unrecognized syntax
            if self._state.ptr == start_of_loop_ptr and self._state.ptr < self._state.length:
                context_end = min(self._state.length, self._state.ptr + 30)
                err_context = self._state.content[self._state.ptr : context_end]
                raise DaxaParsingError(f"Unrecognized Daxa syntax or unexpected token near: '{err_context}...'",
                                       self._state.get_loc())
        
        # Schema context populated during parsing of type/const definitions should be validated
        try:
            self.schema_context.validate_schema_integrity()
        except DaxaSchemaError as e:
             raise DaxaParsingError(f"Schema integrity error in document: {e.message}", e.location or self._state.get_loc())

        # For a full DaxaDocument, you'd also pass self.schema_context with parsed_blocks
        # return DaxaDocument(blocks=self.parsed_blocks, global_schema=self.schema_context)
        return self.parsed_blocks