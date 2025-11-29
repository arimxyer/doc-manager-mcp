# Docusaurus Formatting Guide

Reference for Docusaurus MDX formatting.

## Admonitions

### Basic Syntax

```mdx
:::note
This is a note.
:::

:::tip
This is a helpful tip.
:::

:::info
This is informational.
:::

:::warning
This is a warning.
:::

:::danger
This is a danger alert.
:::
```

### With Custom Title

```mdx
:::note Custom Title
Content with custom title.
:::
```

### Nested Content

```mdx
:::tip Pro Tip

You can include:
- Lists
- **Formatting**
- `code`

```python
# Even code blocks
print("Hello")
```

:::
```

---

## Code Blocks

### Basic

````mdx
```python
def hello():
    print("Hello, World!")
```
````

### With Title

````mdx
```python title="example.py"
def hello():
    print("Hello, World!")
```
````

### Line Highlighting

````mdx
```python {2-3}
def hello():
    message = "Hello"  // highlighted
    print(message)     // highlighted
```
````

### Show Line Numbers

````mdx
```python showLineNumbers
def hello():
    print("Hello, World!")
```
````

### Live Code Editor

````mdx
```jsx live
function Hello() {
  return <div>Hello, World!</div>;
}
```
````

---

## Tabs

### Basic Tabs

```mdx
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
  <TabItem value="python" label="Python" default>

```python
print("Hello")
```

  </TabItem>
  <TabItem value="js" label="JavaScript">

```javascript
console.log("Hello");
```

  </TabItem>
</Tabs>
```

### Synced Tabs

```mdx
<Tabs groupId="language">
  <TabItem value="python" label="Python">
    Python content
  </TabItem>
  <TabItem value="js" label="JavaScript">
    JavaScript content
  </TabItem>
</Tabs>
```

---

## Front Matter

### Basic

```mdx
---
id: my-doc
title: My Document
sidebar_label: My Doc
---

# My Document

Content here.
```

### Full Options

```mdx
---
id: unique-id
title: Document Title
sidebar_label: Sidebar Label
sidebar_position: 1
description: SEO description
keywords: [keyword1, keyword2]
tags: [tag1, tag2]
image: /img/social-card.png
hide_title: false
hide_table_of_contents: false
---
```

---

## Links

### Internal Links

```mdx
[Link to doc](./other-doc.md)
[Link to doc](./folder/doc.md)
[Link with heading](./doc.md#heading-id)
```

### Using Slug

```mdx
[Link to doc](/docs/category/doc-id)
```

### Asset Links

```mdx
![Alt text](./img/image.png)
[Download PDF](./files/document.pdf)
```

---

## Images

### Basic

```mdx
![Alt text](/img/screenshot.png)
```

### With Import

```mdx
import screenshot from './img/screenshot.png';

<img src={screenshot} alt="Screenshot" width="400" />
```

### Themed Images

```mdx
import ThemedImage from '@theme/ThemedImage';

<ThemedImage
  alt="Diagram"
  sources={{
    light: '/img/diagram-light.png',
    dark: '/img/diagram-dark.png',
  }}
/>
```

---

## MDX Components

### Details/Collapsible

```mdx
<details>
  <summary>Click to expand</summary>

  Hidden content here.

  - Can include lists
  - And other content

</details>
```

### Custom Components

```mdx
import CustomComponent from '@site/src/components/CustomComponent';

<CustomComponent prop="value">
  Content inside
</CustomComponent>
```

### Inline JSX

```mdx
<div style={{backgroundColor: '#f0f0f0', padding: '1rem'}}>
  Styled content
</div>
```

---

## Tables

### Standard Markdown

```mdx
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
```

### With Alignment

```mdx
| Left | Center | Right |
|:-----|:------:|------:|
| L    |   C    |     R |
```

---

## Special Features

### TOC (Table of Contents)

```mdx
import TOCInline from '@theme/TOCInline';

<TOCInline toc={toc} />
```

### Code Block Metadata

````mdx
```bash npm2yarn
npm install package-name
```
````

### BrowserWindow

```mdx
import BrowserWindow from '@site/src/components/BrowserWindow';

<BrowserWindow url="https://example.com">
  Content shown in browser frame
</BrowserWindow>
```

---

## Best Practices

1. **Use admonitions** for callouts (:::note, :::tip, etc.)
2. **Add front matter** with id, title, sidebar_label
3. **Use tabs** for multi-language/platform examples
4. **Set sidebar_position** for ordering
5. **Add descriptions** for SEO
6. **Use relative links** for internal docs
7. **Import images** for better optimization
8. **Use details** for optional/advanced content
