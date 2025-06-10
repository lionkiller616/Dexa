# Vector Dexa (`.vdx`) â€” Enhanced Vector Graphics Format

---

## 1. Overview

`.vdx` is a declarative, human-readable vector graphics language for drawing scalable illustrations, icons, UI mockups, and data visualizations. It offers a cleaner, more expressive alternative to SVG with:

* Intuitive syntax
* Named styles and reusability
* Shapes, text, paths, groups, and layers
* Variables, animations, and interactivity
* Layout support (grids, alignment)
* Fully extendable

---

## 2. Basic Structure

A `.vdx` file begins with a `vector` block:

```vdx
vector {
  // shapes, groups, layers, styles, animations
}
```

---

## 3. Comments

* Line comments: `# comment`
* Inline comments allowed

---

## 4. Shapes

### 4.1 Rectangle

```vdx
rect Box {
  x: 10
  y: 20
  width: 120
  height: 60
  fill: "#fafafa"
  stroke: "#222"
  radius: 4       # Rounded corners
}
```

### 4.2 Circle

```vdx
circle Sun {
  cx: 80
  cy: 80
  r: 40
  fill: yellow
}
```

### 4.3 Ellipse

```vdx
ellipse {
  cx: 100
  cy: 60
  rx: 50
  ry: 20
  fill: "#00aaff"
}
```

### 4.4 Line

```vdx
line {
  x1: 0
  y1: 0
  x2: 100
  y2: 100
  stroke: black
  strokeWidth: 2
}
```

### 4.5 Polygon

```vdx
polygon {
  points: [(10, 10), (60, 20), (40, 60)]
  fill: "#f00"
}
```

### 4.6 Path

```vdx
path {
  d: "M10 10 H90 V90 H10 Z"
  fill: none
  stroke: #333
}
```

---

## 5. Text

```vdx
text Label {
  x: 50
  y: 100
  content: "Hello Dexa"
  font: {
    size: 14
    family: "Sans"
    color: "#222"
    weight: bold
  }
}
```

---

## 6. Groups and Layers

### Group

```vdx
group Buttons {
  transform: translate(10, 10)
  rect Btn1 { ... }
  rect Btn2 { x: 150 }
}
```

### Layer

```vdx
layer Background {
  zIndex: 0
  rect {
    x: 0
    y: 0
    width: 400
    height: 400
    fill: "#f0f0f0"
  }
}
```

---

## 7. Styles

```vdx
style ButtonBase {
  fill: "#0099ff"
  stroke: "#003366"
  radius: 6
  font: {
    color: white
    size: 12
  }
}
```

Apply style:

```vdx
rect SubmitBtn [style: ButtonBase]
```

---

## 8. Variables

```vdx
let baseX = 20

rect {
  x: baseX
  y: baseX * 2
}
```

---

## 9. Animation

```vdx
animate Spin {
  target: Sun
  property: rotate
  from: 0deg
  to: 360deg
  duration: 2s
  loop: true
}
```

---

## 10. Gradients and Patterns

### Gradient

```vdx
gradient BlueFade {
  type: linear
  stops: [
    (0%, "#0000ff"),
    (100%, "#00ffff")
  ]
}
```

Apply gradient:

```vdx
circle { fill: BlueFade }
```

---

## 11. Interactivity

```vdx
rect Btn {
  label: "Click"
  onClick: "alert('Clicked!')"
}
```

---

## 12. Full Example

```vdx
vector {
  let bg = "#eeeeee"
  let red = "#ff0000"

  style TitleText {
    font: {
      size: 18
      weight: bold
      color: "#333"
    }
  }

  layer Background {
    rect {
      x: 0
      y: 0
      width: 400
      height: 300
      fill: bg
    }
  }

  text Title [style: TitleText] {
    x: 150
    y: 40
    content: "Welcome to .vdx"
  }

  group Shapes {
    circle { cx: 100, cy: 150, r: 30, fill: red }
    rect { x: 160, y: 120, width: 80, height: 60, fill: "#00f" }
  }

  animate Pulse {
    target: Title
    property: opacity
    from: 1
    to: 0.4
    duration: 1.5s
    loop: true
  }
}
```

---

## 13. Summary of Elements

| Element     | Syntax Example                        | Description                        |
|-------------|----------------------------------------|------------------------------------|
| `vector`    | `vector { ... }`                      | Root block for a vector graphic    |
| `rect`      | `rect Box { ... }`                    | Rectangle                         |
| `circle`    | `circle Sun { ... }`                  | Circle                             |
| `path`      | `path { d: "..." }`                   | Custom path shape                  |
| `text`      | `text { content: "..." }`             | Text with styling                  |
| `group`     | `group Name { ... }`                  | Logical grouping of elements       |
| `layer`     | `layer Name { zIndex: 0 ... }`        | Visual stacking/layering           |
| `style`     | `style MyStyle { ... }`               | Reusable visual style              |
| `animate`   | `animate Name { ... }`                | Time-based animation               |
| `let`       | `let name = value`                    | Variable definition                |
| `gradient`  | `gradient Name { ... }`               | Fill gradients (linear/radial)     |
| `onClick`   | `onClick: "..."`                      | Interactivity (optional support)   |

---

## 14. Future Extensions

* Layout engines (flex/grid alignment)
* Embedded icons or images
* Conditional rendering (if/else)
* Programmatic drawing (loops/functions)

---