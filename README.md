# Daxa - Python Edition

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- Add build status, coverage badges etc. once CI is set up -->
<!-- ![Build Status](...) -->

![Daxa Logo](./assets/logo.png) <!-- Assuming logo.png is in assets -->

**Daxa: One Language for Documents, Data, Diagrams, Math, and Configuration.**

Developed for Lion ([@lionxlover](https://github.com/lionxlover), Telegram: @lionxlover, Instagram: @lionxlover).

---

## 🌟 Overview

Daxa is a next-generation, **unified language ecosystem** designed to replace the complexity of juggling multiple formats like Markdown, JSON/YAML, Mermaid/DOT, LaTeX, and TOML/INI. It provides a **single, elegant, human-friendly `.daxa` format** that seamlessly integrates:

*   **Rich Prose:** Markdown-inspired text for beautiful documentation.
*   **Typed Schemas & Data:** Define and instantiate structured data with robust type safety.
*   **Native DXD Diagrams:** A powerful, declarative symbolic language (`.dxd` syntax embedded in `dxd{}`) for creating diverse diagrams (flowcharts, class diagrams, mind maps, etc.) rendered natively.
*   **Native DaxaMath:** An intuitive syntax (`.maths` logic embedded in `math{}`) for both block and inline mathematical equations, rendered natively to high-quality SVG.
*   **Type-Safe Configuration:** Manage application and system settings (`.dxc` style via `config{}`) with the clarity and safety of the Daxa type system.
*   **Structured Tables:** Define and populate tabular data directly.
*   **Code Embedding:** Include syntax-highlighted code snippets from various languages.

Daxa is built to be **extensible, secure by design, and efficient**, aiming for a user experience where creating complex, interconnected information is "easier and faster than Markdown."

---

## 🧩 Core Daxa Block Types ( Syntax in `.daxa` files)

A Daxa file is a sequence of these blocks:

*   **Prose (Markdown-like):** Any text not recognized as another block type.
    *   Supports: `# H1-H6`, `**bold**`, `*italic*`, `` `code` ``, ```` ```lang ... ````, `> quote`, lists, links, images.
    *   Inline Math: `` `∫ DaxaMath Expression` ``.
    *   Inline Data/Enum Refs: `` `MyStructInstance.field` ``, `` `MyEnum.VALUE` ``.
*   **Type Definitions (Schema):**
    *   `type AliasName = TargetType;`
    *   `enum EnumName { VALUE_A; VALUE_B @description("Desc"); }`
    *   `struct StructName @desc("...") { field: Type @attr; ... }`
*   **Constant Definitions:**
    *   `const CONST_NAME: Type = Value;`
*   **Data Instance Blocks:**
    *   `data StructTypeName instanceName { field1 = value1; ... }`
*   **Table Blocks:**
    *   `table TableName { col1: Type1; ... } = [ [row1val1,...], [row2val1,...] ];`
*   **DXD Diagram Blocks:**
    *   `dxd <optional_subtype_keyword> { <optional_metadata_struct> \n ...DXD_V2_Content... \n}`
    *   DXD V2 Content (within the block) uses `graph [type] { node Name {attr}; Edge A -> B [attr]; ... }` syntax.
*   **Math Equation Blocks:**
    *   `math { <optional_metadata_struct> \n ...DaxaMath_Content... \n}`
    *   DaxaMath Content (within the block) uses a simplified, LaTeX-inspired syntax for `E=mc^2`, fractions, calculus, etc.
*   **Configuration Blocks:**
    *   `config ConfigBlockName: OptionalTypeName { key1 = value1; section.key2 = val2; ... }`
    *   Can also use TOML-like `[Section.Name]` syntax if within a dedicated `.dxc` file or a top-level Daxa block `config MyAppConfig { [Section] ... }`.
*   **Generic Code Blocks:**
    *   `code language_identifier { \n ...raw code... \n}`

---

## 🚀 Key Features & Tooling

*   **Unified `.daxa` Format:** The master file type.
*   **Specialized File Types (Optional):**
    *   `.dxc`: For dedicated configuration files.
    *   `.dx`: For data-centric files (schemas + data instances, "Daxa Databases").
    *   `.dxd`: Standalone native DXD diagram files (Graphviz DOT-like syntax).
    *   `.maths`: Standalone DaxaMath files (LaTeX-inspired syntax).
*   **Native DXD Engine:** Parses and renders `.dxd` syntax to SVG. Supports various diagram types (flow, class, mindmap, state, etc.) through layout hints and element semantics.
*   **Native DaxaMath Engine:** Parses and renders DaxaMath syntax to SVG (or MathML).
*   **Document Object Model:** Parses `.daxa` files into a structured `DaxaDocument` for processing and rendering.
*   **HTML Renderer:** Converts `DaxaDocument` objects into self-contained HTML files, embedding rendered SVGs for diagrams and math.
*   **Command-Line Interface (`daxa`):**
    *   `info`, `validate`: For Daxa files.
    *   `convert`: To JSON/YAML (data), HTML (documents).
    *   `render`: Renders `.daxa` documents to HTML (PDF future).
    *   `dxd`: CLI for standalone `.dxd` file operations (render, validate).
    *   `math`: CLI for standalone `.maths` content operations.
    *   `init`: Create boilerplate Daxa files.
*   **Graphical User Interface (`daxa-gui`):** "Ultimate UI/UX"
    *   **Real-time Editor & Preview:** Split-pane view with Daxa source editor (advanced syntax highlighting for all block types) and a live-updating rendered preview.
    *   **Modern & Configurable:** Dockable tool windows (Console, Document Outline, Property Inspector), light/dark themes, persistent settings.
    *   **Native Diagram & Math Display:** Renders DXD and Math content directly in the preview.
*   **Binary Format (`.dex`):** Conceptual for compiled, efficient storage of data sections (compressed, optionally encrypted).

---

## 🛠️ Installation & Usage (Linux First)

(Installation instructions will be detailed here, similar to previous README but updated for new dependencies if any.)

**CLI Examples:**
```bash
# Validate and get info on a Daxa document
daxa validate examples/main_document.daxa
daxa info examples/main_document.daxa

# Render the Daxa document to HTML
daxa render examples/main_document.daxa -o output.html

# Render a specific standalone DXD diagram file to SVG
daxa dxd render examples/simple_flowchart.dxd -o flowchart.svg
```

# Convert a data block from a .daxa file to JSON
# (CLI for this needs to specify which data block if many)
# daxa convert examples/main_document.daxa --dataset my_data_instance -t json

GUI:
```bash
daxa-gui
```

(Open .daxa, .dx, or .dxc files. Enjoy live preview and editing.)

## 🔮 Future Roadmap

Advanced DXD layout engines and styling.

Comprehensive DaxaMath symbol and structure support.

Full PDF document rendering.

Query engine for .dx data files.

Plugin system for custom Daxa block types.

Git-aware binary storage for .dex.

Cross-language parsers (Rust, JS/WASM).

Full native application bundles for Windows and macOS.

## 🎯 Why Daxa?

Daxa offers a paradigm shift from fragmented tooling to a single, coherent, and powerful language platform for all aspects of technical documentation, data management, configuration, and visual communication. It's designed for human clarity and machine efficiency.

(License, Acknowledgements, Contributing sections remain similar)
