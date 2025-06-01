.
├── assets/                     # GUI assets
│   ├── icons/                  # General UI, diagram, math icons (SVG preferred)
│   │   ├── open.svg, save.svg, settings.svg, validate.svg, render_html.svg
│   │   ├── dxd_icon.svg, math_icon.svg, config_icon.svg, data_icon.svg, type_icon.svg
│   │   ├── (and other common UI action icons: cut, copy, paste, zoom, etc.)
│   ├── daxa_style_dark.qss
│   ├── daxa_style_light.qss
│   ├── icon.ico, icon.png, logo.png # Application branding
├── daxa/
│   ├── __init__.py             # Top-level package exports
│   ├── cli/                    # Command-Line Interface
│   │   ├── __init__.py
│   │   ├── main.py             # Main CLI entry point using argparse
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── base_command.py # Base class for CLI commands
│   │       ├── convert_cmd.py  # Converts Daxa docs/data to JSON, HTML, potentially MD
│   │       ├── dxd_cmd.py      # NEW: CLI specifically for .dxd files (render, validate)
│   │       ├── info_cmd.py     # Info about .daxa, .dx, .dxc files
│   │       ├── init_cmd.py     # NEW: Create boilerplate .daxa, .dx, .dxc files
│   │       ├── math_cmd.py     # NEW: CLI specifically for .maths content (render, validate)
│   │       ├── render_cmd.py   # Renders a full Daxa document (.daxa) to HTML/PDF
│   │       └── validate_cmd.py # Validates .daxa, .dx, .dxc files
│   ├── core/                   # Core Daxa language elements
│   │   ├── __init__.py
│   │   ├── common.py           # Base exceptions, enums (DaxaBlockType), SourceLocation
│   │   ├── daxa_value.py       # Runtime Daxa data representation
│   │   ├── parser_main.py      # RENAMED from parser_text.py: Main Daxa Document Parser (.daxa files)
│   │   ├── schema.py           # Struct, Enum, Type Alias, Const definitions (used by parser_main)
│   │   ├── validator.py        # Validates schema integrity and data instances
│   │   ├── writer_main.py      # RENAMED from writer_text.py: Serializes DaxaDocument to text
│   │   ├── parser_binary.py    # Parser for compiled .dex data sections
│   │   └── writer_binary.py    # Writer for compiled .dex data sections
│   ├── dxd/                    # Native DXD (Diagrams V2 - Graphviz-like) Processing
│   │   ├── __init__.py
│   │   ├── dxd_ast.py          # AST node definitions for parsed DXD (Node, Edge, Cluster, GraphAttr)
│   │   ├── dxd_parser.py       # Parser for the NEW .dxd syntax (graph {}, node, edge, cluster)
│   │   ├── dxd_renderer_svg.py # Renders DXD AST to SVG (includes layout logic)
│   │   └── dxd_renderer_png.py # (Optional) Renders DXD AST to PNG (likely via SVG)
│   ├── maths/                  # Native DaxaMath (Math Equations V2 - LaTeX-inspired) Processing
│   │   ├── __init__.py
│   │   ├── maths_ast.py        # AST node definitions for parsed math expressions
│   │   ├── maths_parser.py     # Parser for the NEW DaxaMath syntax (∫, d/dx, matrices)
│   │   └── maths_renderer_svg.py # Renders Math AST to SVG (or MathML)
│   ├── config/                 # DaxaConfig (`.dxc`) Processing
│   │   ├── __init__.py
│   │   ├── dxc_ast.py          # AST for config sections, key-values, env refs, consts
│   │   ├── dxc_parser.py       # Parser for .dxc files or `config` blocks in .daxa
│   │   └── dxc_evaluator.py    # Evaluates config (resolves consts, env vars)
│   ├── data_lang/              # Daxa Data Language (`.dx` specific + `data`, `table` blocks)
│   │   ├── __init__.py
│   │   ├── dx_model.py         # Representation for `table` blocks if different from generic DaxaValue array
│   │   ├── dx_parser.py        # Handles `data TypeName instanceName {}` and `table Name {} = []` blocks.
│   │   └── dx_query_engine.py  # (Future/Conceptual Stub) For querying .dx data
│   ├── document/               # Daxa Document Object Model and Full Document Rendering
│   │   ├── __init__.py
│   │   ├── doc_model.py        # Defines DaxaDocument and its block types (Prose, DaxaDef, Data, Dxd, Math, Config, Table, Code)
│   │   ├── prose_parser.py     # Markdown-like parser for prose blocks (might use a library)
│   │   ├── doc_renderer_html.py# Renders DaxaDocument to HTML
│   │   └── doc_renderer_pdf.py # (Conceptual Stub) Renders DaxaDocument to PDF
│   ├── gui/                    # Graphical User Interface (based on Editor/Preview model)
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window with editor/preview
│   │   ├── resources.py        # Icon/asset management
│   │   ├── style.py            # QSS theme management
│   │   ├── threads.py          # QThread helpers
│   │   ├── view_model.py       # Manages DaxaDocument state for GUI
│   │   ├── dialogs/            # Error, Preferences dialogs
│   │   │   ├── __init__.py, error_dialog.py, preferences_dialog.py
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── console_widget.py       # For app logs
│   │       ├── daxa_editor_widget.py   # Advanced Daxa source text editor (syntax highlighting for all blocks)
│   │       ├── daxa_preview_widget.py  # Live preview pane (renders HTML from doc_renderer_html)
│   │       ├── outline_widget.py       # NEW: Tree view of document structure (headings, named blocks)
│   │       └── property_editor.py      # Contextual properties (e.g. for selected diagram node in future editor)
│   ├── utils/                  # General utilities
│   │   ├── __init__.py
│   │   ├── compression.py      # For .dex format
│   │   ├── db_utils.py         # For exporting .dx data to SQL DDL, CSV (schema.py now more for struct/enum)
│   │   ├── encryption.py       # For .dex format
│   │   └── misc_utils.py       # Other small helper functions
│   └── daxa_settings.py        # QSettings management for GUI
├── examples/                   # Updated example files reflecting new syntaxes
│   ├── main_document.daxa      # Master example with prose, data, dxd, math, config blocks
│   ├── my_app_config.dxc       # Dedicated .dxc configuration file example
│   ├── product_catalog.dx      # Dedicated .dx data file example (schema + data instances)
│   ├── simple_flowchart.dxd    # Standalone .dxd diagram file example (Graphviz-like)
│   ├── complex_equations.maths # Standalone .maths file example (LaTeX-like)
│   ├── old_person_data.daxa    # Example using only type/const/data blocks for simpler data-only cases
├── tests/                      # Test suite structure
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   ├── test_cli_commands.py    # Tests for info, validate, convert, render CLI
│   ├── test_core_parser_main.py# Tests for the main .daxa document parser
│   ├── test_core_schema.py     # Tests for struct/enum/type/const definitions
│   ├── test_core_daxa_value.py
│   ├── test_core_validator.py
│   ├── test_dxd_parser.py      # Tests for the new DXD (Graphviz-like) parser
│   ├── test_dxd_renderer_svg.py# Conceptual tests for DXD SVG rendering
│   ├── test_maths_parser.py    # Tests for the new DaxaMath parser
│   ├── test_maths_renderer_svg.py# Conceptual tests for DaxaMath SVG rendering
│   ├── test_dxc_parser.py      # Tests for .dxc / config: block parsing
│   ├── test_dx_data_parser.py  # Tests for data: and table: block parsing
│   ├── test_doc_model.py       # Tests for DaxaDocument and its block structure
│   └── test_doc_renderer_html.py# Tests for HTML rendering of DaxaDocument
├── .gitignore
├── LICENSE                     # e.g., MIT
├── README.md                   # Significantly updated to reflect new unified language vision
├── requirements.txt            # Python dependencies (PyQt6, PyQt6-WebEngine, PyYAML, markdown, etc.)
└── setup.py                    # For `pip install daxa-system`, defining CLI/GUI entry points