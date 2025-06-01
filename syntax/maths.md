Here’s a detailed enhanced syntax specification for **`.maths`**, the Dexa Math language — designed for easy, clean, human-friendly inline and block math expressions, fully integrated with Daxa.

---

# Dexa Math Language (`.maths`) — Enhanced Detailed Syntax Specification

---

## 1. Overview

`.maths` supports:

* Inline math (within prose)
* Block math (standalone)
* Algebraic expressions
* Calculus (derivatives, integrals, limits)
* Matrices and vectors
* Logical and set notation
* Custom functions and variables
* Unicode math symbols
* Easy-to-read syntax without heavy LaTeX-style complexity

---

## 2. Basic Usage

### Inline math

Delimited by `∫` symbols:

```
This is an inline math example: ∫ x^2 + 3x + 2 ∫ within text.
```

---

### Block math

Delimited by triple backticks with `math` or `∫∫∫`:

```math
∫
f(x) = x^2 + 3x + 2
lim_{x→∞} f(x)
∫
```

Or

```
∫∫∫
∂f/∂x = 2x + 3
∫∫∫
```

---

## 3. Supported Syntax Elements

### Arithmetic operators

| Symbol | Meaning        |
| ------ | -------------- |
| `+`    | Addition       |
| `-`    | Subtraction    |
| `*`    | Multiplication |
| `/`    | Division       |
| `^`    | Exponentiation |
| `%`    | Modulus        |

---

### Grouping and precedence

* Parentheses `( )` for grouping
* Square brackets `[ ]` and braces `{ }` can also be used for matrices, sets, or function arguments

---

### Functions

Common math functions (syntax is simple):

```
sin(x), cos(x), tan(x)
log(x), ln(x)
sqrt(x)
abs(x)
max(a,b), min(a,b)
```

User-defined functions:

```
f(x) = x^2 + 3
g(x,y) = x*y + 2
```

---

### Calculus

* Derivatives:

```
d/dx f(x)
∂/∂x f(x,y)
f'(x), f''(x)
```

* Integrals:

```
∫ f(x) dx
∫_a^b f(x) dx
```

* Limits:

```
lim_{x→∞} f(x)
lim_{h→0} (f(x+h)-f(x))/h
```

---

### Matrices and Vectors

Use brackets and semicolons or new lines for rows:

```
Matrix A = [
  1, 2, 3;
  4, 5, 6;
  7, 8, 9
]

Vector v = [1, 2, 3]
```

---

### Logical and Set Notation

* Logical operators:

```
∧ (and), ∨ (or), ¬ (not), ⇒ (implies), ⇔ (iff)
```

* Set notation:

```
{ x | x > 0 }
∈ (element of)
⊂ (subset)
∅ (empty set)
```

---

### Greek Letters and Symbols

Direct unicode or shortcuts:

| Unicode | Shortcut | Meaning     |
| ------- | -------- | ----------- |
| α       | alpha    | alpha       |
| β       | beta     | beta        |
| γ       | gamma    | gamma       |
| δ       | delta    | delta       |
| π       | pi       | pi constant |
| Σ       | Sigma    | summation   |
| ∑       | sum      | summation   |
| ∞       | inf      | infinity    |

---

## 4. Examples

### Simple expression

```
∫ (x^2 + 2x + 1) dx
```

### Derivative

```
d/dx (sin(x)) = cos(x)
```

### Integral with limits

```
∫_0^1 x^2 dx = 1/3
```

### Matrix

```
Matrix M = [
  1, 0;
  0, 1
]
```

### Logical expression

```
(x > 0) ∧ (y < 5) ⇒ z = 1
```

---

## 5. Summary of Syntax Elements

| Syntax           | Description                    |  
| ---------------- | ------------------------------ | 
| `+ - * / ^ %`    | Arithmetic operators           | 
| `( ) [ ] { }`    | Grouping                       |      
| `f(x)`           | Functions                      |         
| `d/dx f(x)`      | Derivative                     |             
| `∫ f(x) dx`      | Integral                       |                      
| `lim_{x→a} f(x)` | Limit                          |                      
| `[a,b; c,d]`     | Matrix                         |                      
| `∧ ∨ ¬ ⇒ ⇔`      | Logic operators                |                      
| \`{ x condition }\`    | Set builder notation          |
| Unicode Greek    | Greek letters and math symbols |                      

---

If you want, I can also help you with:

* Formal grammar (EBNF) for `.maths`
* Parser example in Python or another language
* Math expression evaluator or renderer
* Integration examples with `.daxa` or `.dxd`

Would you like me to proceed with any of these?
