Here is the **enhanced complete syntax specification** for the main `.daxa` file format — the **primary format** in the Dexa Language ecosystem. This format is **Markdown-inspired**, but **fully typed**, **programmable**, and **unified** with data, diagrams, math, config, and schema.

---

# 📘 `.daxa` — Dexa Language Master Format Specification

---

## 🔹 1. Purpose

The `.daxa` file format is:

* A **superset** of Markdown
* A **unified platform** for:

  * Rich prose
  * Typed data and schemas
  * Structured datasets
  * Diagrams (`.dxd`)
  * Math (`.maths`)
  * Config (`.dxc`)
  * DB-like logic (`.dx`)
* Both **human-friendly** and **machine-readable**
* Ideal for **apps**, **docs**, **APIs**, **databases**, **dashboards**, and more

---

## 🔹 2. Block Types

| Block Type     | Syntax Prefix     | Purpose                               |
| -------------- | ----------------- | ------------------------------------- |
| Prose          | Plain Markdown    | Rich human-readable text              |
| Data Structs   | `struct` / `type` | Define reusable data types and shapes |
| Constants      | `const`           | Declare fixed values                  |
| Typed Datasets | `data`            | Assign data entries with type         |
| Diagrams       | `dxd`             | Embedded diagrams (like Mermaid++)    |
| Math           | `math` / `∫`      | Inline or block math expressions      |
| Config         | `config` / `dxc`  | Define runtime or app configuration   |
| Table/Matrix   | `table`           | Visual tables with type awareness     |
| Scripts/Logic  | `code`            | Executable or logical code (optional) |
| Sections       | `#` - `######`    | Markdown-style headings               |
| Comments       | `//` or `/* */`   | Ignored by parser                     |

---

## 🔹 3. Prose Blocks

Standard Markdown-style:

```markdown
# Welcome to My Daxa File

This document is powered by Dexa Language.

- Supports **bold**, _italic_, `code`, and [links](#).
```

---

## 🔹 4. Constants

```daxa
const Pi = 3.1415;
const SiteName = "Dexa Docs";
const Debug: bool = false;
```

---

## 🔹 5. Types and Structs

### Basic Types

```daxa
type UserID = int;
type URL = string;
type Enabled = bool;
```

### Structs

```daxa
struct User {
  id: UserID;
  name: string;
  email: string;
  active: Enabled;
}
```

### Enums

```daxa
enum Status {
  Active;
  Inactive;
  Suspended;
}
```

---

## 🔹 6. Data Blocks

```daxa
data User john_doe {
  id = 1;
  name = "John Doe";
  email = "john@example.com";
  active = true;
}
```

---

## 🔹 7. Tables

```daxa
table Planets {
  name: string;
  distance_from_sun: float;
  has_rings: bool;
} = [
  ["Earth", 149.6, false],
  ["Saturn", 1427.0, true],
  ["Neptune", 4495.1, true]
];
```

---

## 🔹 8. Diagrams (`dxd` block)

```daxa
dxd {
  flow {
    start --> login --> dashboard;
    dashboard --> settings;
  }
}
```

More detail: [See full `.dxd` syntax ➤](https://chat.openai.com/share/e/f1de5e0a...)

---

## 🔹 9. Math Blocks

### Inline

```daxa
The area is `∫ r²π`.
```

### Block

```daxa
math {
  E = mc^2
  F = ma
}
```

---

## 🔹 10. Config Blocks (`dxc`-style inline)

```daxa
config AppSettings {
  debug = true;
  max_users = 500;
  api_url = "https://api.example.com";
}
```

---

## 🔹 11. Code Blocks

```daxa
code python {
  def greet():
      print("Hello, Dexa!")
}
```

Supports multi-language or typed code (Python, JS, SQL, etc.)

---

## 🔹 12. Inline Types & Math

Mix inline data with prose:

```daxa
User `john_doe` is currently `Status.Active` with score ∫ 89.5.
```

---

## 🔹 13. File Organization Best Practices

```plaintext
project/
├── README.daxa       ← Main index document
├── data.daxa         ← Structured data
├── types.daxa        ← Types, enums, constants
├── config.daxa       ← App configs
├── diagrams.dxd      ← Visual models
├── formulas.maths    ← Math logic
├── storage.dx        ← Structured database
├── config.dxc        ← Runtime config
```

---

## 🔹 14. Features Summary

| Feature            | Supported in `.daxa` |
| ------------------ | -------------------- |
| Markdown (prose)   | ✅                    |
| Typed structs/data | ✅                    |
| Math & Diagrams    | ✅                    |
| Config logic       | ✅                    |
| One-file docs/data | ✅                    |
| Extensible types   | ✅                    |
| DB integration     | ✅ (`.dx`)            |
| Compiler-ready     | ✅ Future-ready       |

---

## ✅ Conclusion

`.daxa` is not just a Markdown replacement — it is a **unified human-readable programming, documentation, and database format**, bridging prose, math, config, diagrams, and structured data under one language.

Would you like:

* A **live interactive parser** in Python?
* An **official Daxa linter or formatter**?
* A **compiler** that turns `.daxa` into `.dx` files?

Let me know and I can help you build it.
