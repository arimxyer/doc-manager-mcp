# MkDocs Formatting Guide

Reference for MkDocs and Material for MkDocs formatting.

## Admonitions

### Basic Syntax

```markdown
!!! note
    This is a note admonition.

!!! warning
    This is a warning.

!!! danger
    This is a danger alert.

!!! tip
    This is a helpful tip.

!!! info
    This is informational.
```

### With Custom Title

```markdown
!!! note "Custom Title"
    Content with custom title.
```

### Collapsible

```markdown
??? note "Click to expand"
    Hidden content here.

???+ note "Expanded by default"
    Visible content here.
```

### Available Types

| Type | Use For |
|------|---------|
| `note` | General information |
| `info` | Informational context |
| `tip` | Helpful suggestions |
| `success` | Positive outcomes |
| `question` | FAQ items |
| `warning` | Caution notices |
| `danger` | Critical warnings |
| `bug` | Known issues |
| `example` | Usage examples |
| `quote` | Citations |

---

## Code Blocks

### Basic

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### With Title

````markdown
```python title="example.py"
def hello():
    print("Hello, World!")
```
````

### With Line Numbers

````markdown
```python linenums="1"
def hello():
    print("Hello, World!")
```
````

### Highlighting Lines

````markdown
```python hl_lines="2 3"
def hello():
    message = "Hello"  # highlighted
    print(message)     # highlighted
```
````

### Annotations

````markdown
```python
def hello():
    print("Hello")  # (1)!
```

1. This is an annotation explaining the line.
````

---

## Tabs

### Content Tabs

```markdown
=== "Python"

    ```python
    print("Hello")
    ```

=== "JavaScript"

    ```javascript
    console.log("Hello");
    ```

=== "Go"

    ```go
    fmt.Println("Hello")
    ```
```

---

## Tables

### Basic Table

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
```

### Aligned Columns

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| L    |   C    |     R |
```

---

## Links

### Internal Links

```markdown
[Link to page](../folder/page.md)
[Link to heading](page.md#heading-id)
[Link to heading on same page](#heading-id)
```

### Reference Links

```markdown
See the [API reference][api-ref] for details.

[api-ref]: ../api/reference.md
```

---

## Images

### Basic Image

```markdown
![Alt text](../assets/image.png)
```

### With Caption

```markdown
<figure markdown>
  ![Alt text](../assets/image.png)
  <figcaption>Image caption here</figcaption>
</figure>
```

### Sized Image

```markdown
![Alt text](../assets/image.png){ width="300" }
```

---

## Special Features

### Keys (Keyboard)

```markdown
Press ++ctrl+c++ to copy.
Press ++cmd+v++ to paste on Mac.
```

### Buttons

```markdown
[Click Me](#){ .md-button }
[Primary](#){ .md-button .md-button--primary }
```

### Abbreviations

```markdown
The HTML specification is maintained by the W3C.

*[HTML]: Hyper Text Markup Language
*[W3C]: World Wide Web Consortium
```

### Footnotes

```markdown
This needs clarification[^1].

[^1]: Here's the clarification.
```

---

## Best Practices

1. **Use admonitions** for callouts, not blockquotes
2. **Add titles** to code blocks for context
3. **Use tabs** for multi-language examples
4. **Include line numbers** for longer code blocks
5. **Add annotations** for complex code
6. **Use relative links** for internal references
7. **Always add alt text** to images
