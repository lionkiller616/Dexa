# Dexa Database Format (`.dx`) — Enhanced Detailed Syntax Specification

---

## 1. Overview

`.dx` files are designed to act as:

* Lightweight, schema-aware, human-editable database files.
* Support complex nested data, relations, and constraints.
* Provide a unified, extensible, typed, self-documenting DB file format.
* Integrate naturally with Daxa language components.

---

## 2. File Structure

A `.dx` file consists of:

* **Schema declarations** (`type`, `struct`, `enum`, `const`)
* **Dataset blocks** (`data`)
* **Index & metadata** (optional)
* **Query/logic blocks** (optional future extension)

---

## 3. Syntax Elements

### 3.1 Schema Declarations

Define structured types and constraints to shape your data.

```daxa
type UserID = int;
enum Status { Active, Inactive, Pending };
struct User {
  id: UserID;
  name: string;
  email: string;
  status: Status;
  tags: [string];
}
```

---

### 3.2 Dataset Blocks

Holds actual data instances matching the declared schema.

```daxa
data Users = [
  {
    id: 1;
    name: "Alice";
    email: "alice@example.com";
    status: Active;
    tags: ["admin", "beta"];
  },
  {
    id: 2;
    name: "Bob";
    email: "bob@example.com";
    status: Pending;
    tags: [];
  }
];
```

---

### 3.3 Nested Data & Relations

Support nested objects and arrays.

```daxa
struct Post {
  id: int;
  author: UserID;
  content: string;
  comments: [Comment];
}

struct Comment {
  id: int;
  user: UserID;
  message: string;
}
```

---

### 3.4 Index and Metadata (Optional)

```daxa
index Users.id;        // declare indexed field
meta created_at = "2025-06-01T10:00:00Z";
```

---

### 3.5 Query / Logic Blocks (Future)

Reserved for embedded query syntax or logic rules (planned).

---

## 4. Data Types Supported

| Type            | Description                    |
| --------------- | ------------------------------ |
| `int`           | Integer numbers                |
| `float`         | Floating-point numbers         |
| `string`        | Unicode text                   |
| `bool`          | Boolean (true/false)           |
| `enum`          | Enumerations                   |
| `struct`        | Custom records                 |
| `[type]`        | Arrays (homogeneous lists)     |
| `map[key, val]` | Maps / dictionaries (optional) |

---

## 5. Example `.dx` File

```daxa
type UserID = int;

enum Status { Active, Inactive, Pending };

struct User {
  id: UserID;
  name: string;
  email: string;
  status: Status;
  tags: [string];
}

data Users = [
  {
    id: 1;
    name: "Alice";
    email: "alice@example.com";
    status: Active;
    tags: ["admin", "beta"];
  },
  {
    id: 2;
    name: "Bob";
    email: "bob@example.com";
    status: Pending;
    tags: [];
  }
];

index Users.id;
meta created_at = "2025-06-01T10:00:00Z";
```

---

## 6. Comments

* Single line comments: `// this is a comment`
* Multi-line comments: `/* multi-line comment */`

---

## 7. Notes

* Semicolons `;` terminate fields and statements.
* Arrays use square brackets `[ ]`.
* Strings are enclosed in double quotes `" "`.
* Enum values and identifiers are case-sensitive.
* Structs allow optional fields by marking with `?` (future).
* Designed for easy parsing and validation.

---
