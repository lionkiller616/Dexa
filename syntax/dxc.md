# Dexa Config Format (`.dxc`) — Enhanced Detailed Syntax Specification

---

## 1. Overview

`.dxc` files provide:

* Typed, schema-aware, human-readable configuration.
* Full integration with Daxa types, constants, and structs.
* Support for hierarchical settings with sections and subsections.
* Unified syntax compatible with the rest of the Daxa ecosystem.
* Easy parsing and validation.
* Support for environment variables, defaults, and overrides.

---

## 2. File Structure

A `.dxc` config file consists of:

* **Section headers**
* **Typed key-value pairs**
* **Constants and references**
* **Comments**
* **Imports / includes** (optional)
* **Overrides / environment injection** (optional)

---

## 3. Syntax Elements

### 3.1 Section Headers

Use square brackets `[SectionName]` to declare config sections.

Supports nested subsections using dot notation.

```dxc
[Database]
host = "localhost";
port = 5432;

[Database.Credentials]
username = "admin";
password = "secret";
```

---

### 3.2 Key-Value Pairs

Key-value pairs inside sections, with explicit or inferred types.

Basic types supported:

* `int` (e.g., `max_connections = 100;`)
* `float` (e.g., `timeout = 30.5;`)
* `string` (e.g., `url = "http://example.com";`)
* `bool` (e.g., `enabled = true;`)
* Arrays (e.g., `servers = ["srv1", "srv2", "srv3"];`)

Example:

```dxc
max_connections = 100;
debug = true;
allowed_hosts = ["localhost", "127.0.0.1"];
```

---

### 3.3 Type Annotation (Optional)

You can explicitly annotate types for clarity or enforcement:

```dxc
timeout: float = 15.0;
retries: int = 5;
feature_enabled: bool = false;
```

---

### 3.4 Constants and References

Supports defining constants and referencing them inside the config:

```dxc
const DefaultPort = 8080;

[Server]
port = DefaultPort;
```

---

### 3.5 Environment Variable Injection (Optional)

Allows injecting environment variables, with optional defaults:

```dxc
db_password = env("DB_PASS", "default_password");
```

Here `env()` fetches an environment variable or falls back to the default.

---

### 3.6 Includes / Imports (Optional)

Support for including other config files to modularize config:

```dxc
@include "common.dxc";
```

---

### 3.7 Comments

* Single line: `// comment`
* Multi-line: `/* comment */`

---

## 4. Example `.dxc` File

```dxc
// Global constants
const MaxUsers = 500;
const TimeoutSeconds: int = 30;

[General]
app_name = "DexaApp";
debug_mode = true;
max_users = MaxUsers;

[Database]
host = "db.example.com";
port: int = 5432;
timeout: float = TimeoutSeconds;

[Database.Credentials]
username = "dex_user";
password = env("DB_PASS", "fallback_secret");

[Logging]
level = "info";
files = ["app.log", "error.log"];
```

---

## 5. Notes

* Semicolons `;` terminate key-value pairs (optional if line breaks are unambiguous).
* Section names are case-insensitive but recommended camel-case or Pascal-case.
* Arrays use square brackets `[ ]`.
* Strings must use double quotes `" "`.
* Supports extensible custom types from `.daxa` schemas.
* Environment injection is a runtime feature to support secure configs.
* Constants allow reuse and easier updates.
* Designed to replace TOML, YAML, and INI with stronger typing and integration.

---

## 6. Advanced Features (Future)

* Validation rules on keys (ranges, regex)
* Computed values or expressions
* Encrypted secrets support
* Profiles (dev, staging, prod) with overrides
* Dynamic reload support
