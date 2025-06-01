# Dexa Diagrams (`.dxd`) — Enhanced Detailed Syntax Specification

---

## 1. Overview

`.dxd` is a declarative, human-readable language for describing diagrams and graphs with:

* Nodes
* Edges
* Clusters (subgraphs)
* Styles & attributes
* Labels & annotations
* Directed and undirected edges
* Multiple graph types (flowcharts, trees, networks, state machines, etc.)

---

## 2. Basic Structure

A Dexa diagram file or block begins with a `graph` declaration and is enclosed in `{ }`.

```dxd
graph [graph_type] {
    // Diagram elements here
}
```

* `graph_type` is optional, defines layout type: `directed`, `undirected`, `flowchart`, `tree`, `network`, `state`, `mindmap`, etc.
* Default is `directed` if omitted.

---

## 3. Comments

* Line comments: `# this is a comment`
* Inline comments allowed after elements

---

## 4. Nodes

Declare nodes by name or with attributes.

```dxd
node NodeName
```

### Node with attributes:

```dxd
node NodeName {
    label: "User Login"
    shape: circle | rectangle | ellipse | diamond | hexagon | trapezoid
    color: #hexcode or color_name
    style: filled | dashed | dotted | bold
    fill: #hexcode
    font: {
      size: 14
      color: #333333
      family: "Arial"
      weight: bold | normal
    }
    tooltip: "Tooltip text"
}
```

### Node examples:

```dxd
node Start {
  label: "Start"
  shape: ellipse
  color: green
}

node Decision {
  label: "Is Valid?"
  shape: diamond
  color: orange
  style: dashed
}
```

---

## 5. Edges

Edges connect nodes.

```dxd
NodeA -> NodeB [attributes]
NodeA -- NodeB [attributes]
```

* `->` indicates directed edge
* `--` indicates undirected edge

### Edge Attributes:

```dxd
[
  label: "Yes"
  style: solid | dashed | dotted | bold | invisible
  color: #hexcode or color_name
  arrowhead: normal | vee | none | diamond | dot | box
  arrowtail: normal | vee | none | diamond | dot | box
  penwidth: number (thickness)
  font: {
    size: 12
    color: #555555
    family: "Courier New"
    weight: normal
  }
  tooltip: "Edge tooltip"
]
```

### Example:

```dxd
Start -> Decision [label: "Begin", color: green, style: bold]
Decision -> End [label: "No", color: red, arrowhead: vee]
Decision -> Process [label: "Yes", color: blue]
```

---

## 6. Clusters (Subgraphs)

Clusters group nodes visually.

```dxd
cluster ClusterName {
  label: "Cluster Label"
  style: filled | dashed | dotted
  color: #hexcode
  fill: #hexcode
  nodes: [Node1, Node2, Node3]
}
```

Or nested declaration:

```dxd
cluster Backend {
  label: "Backend Systems"
  color: blue
  node DB
  node API
  DB -> API
}
```

---

## 7. Graph Attributes

Set graph-wide properties:

```dxd
graph {
  layout: dot | neato | fdp | sfdp | circo | twopi
  rankdir: TB | LR | BT | RL  # direction: top-bottom, left-right, etc.
  bgcolor: #hexcode
  margin: number
  nodesep: number
  ranksep: number
}
```

Example:

```dxd
graph flowchart {
  layout: dot
  rankdir: LR
  bgcolor: #fefefe
  margin: 20
}
```

---

## 8. Special Diagram Types & Syntax

### Flowcharts

* Use `node` with decision shapes (diamond)
* Directed edges with conditional labels ("Yes", "No")

### State Machines

* States are nodes with shape `circle` or `ellipse`
* Transitions are directed edges with event labels

```dxd
graph state {
  node Idle { shape: ellipse }
  node Running { shape: ellipse }
  node Error { shape: ellipse, color: red }

  Idle -> Running [label: "start"]
  Running -> Idle [label: "stop"]
  Running -> Error [label: "fail"]
}
```

### Mindmaps

* Tree-like structure
* Root node at center, child nodes connected

```dxd
graph mindmap {
  node Root { shape: ellipse }
  Root -> Idea1
  Root -> Idea2
  Idea1 -> Subidea1
}
```

---

## 9. Stylesheets

Define reusable styles:

```dxd
style NodeStyle1 {
  shape: rectangle
  color: blue
  style: filled
}

style EdgeStyle1 {
  color: gray
  style: dashed
  arrowhead: vee
}
```

Apply styles:

```dxd
node Task1 [style: NodeStyle1]
Task1 -> Task2 [style: EdgeStyle1]
```

---

## 10. Variables and Macros

* Support for variables to reuse values

```dxd
let mainColor = "#3498db"

node A {
  color: mainColor
}
```

---

## 11. Full Example

```dxd
graph flowchart {
  layout: dot
  rankdir: TB
  bgcolor: #fff

  node Start {
    label: "Start"
    shape: ellipse
    color: green
  }

  node Decision {
    label: "Check Value"
    shape: diamond
    color: orange
  }

  node Process {
    label: "Process Data"
    shape: rectangle
  }

  node End {
    label: "End"
    shape: ellipse
    color: red
  }

  Start -> Decision [label: "Begin"]
  Decision -> Process [label: "Yes"]
  Decision -> End [label: "No"]
  Process -> End
}
```

---

## 12. Summary of Elements

| Element    | Syntax Example                     | Description                        |
| ---------- | ---------------------------------- | ---------------------------------- |
| Graph      | `graph flowchart { ... }`          | Container for diagram              |
| Node       | `node Name { label: "text" }`      | Nodes/entities                     |
| Edge       | `A -> B [label: "Yes"]`            | Connect nodes, directed/undirected |
| Cluster    | `cluster GroupName { node A ... }` | Group nodes visually               |
| Styles     | `style MyStyle { ... }`            | Reusable styles                    |
| Variables  | `let color = "#abc"`               | Reusable values                    |
| Comments   | `# comment`                        | Inline or line comments            |
| Attributes | `[label: "text", color: "#123"]`   | Customize nodes/edges              |

---
