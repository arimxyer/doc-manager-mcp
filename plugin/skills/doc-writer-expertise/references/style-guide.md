# Documentation Style Guide

Writing principles for clear, consistent documentation.

## Voice and Tone

### Use Active Voice

```
❌ "The configuration file is read by the system."
✓ "The system reads the configuration file."

❌ "An error will be thrown if the input is invalid."
✓ "The function throws an error if the input is invalid."
```

### Use Second Person

Address the reader directly:

```
❌ "Users can configure the settings..."
✓ "You can configure the settings..."

❌ "One should always validate input..."
✓ "Always validate your input..."
```

### Use Imperative Mood for Instructions

```
❌ "You should click the button."
✓ "Click the button."

❌ "The user needs to enter their password."
✓ "Enter your password."
```

### Be Direct

```
❌ "In order to start the server, you will need to..."
✓ "To start the server:"

❌ "It is important to note that..."
✓ "Note:"
```

---

## Clarity

### Use Simple Words

| Instead of | Use |
|------------|-----|
| utilize | use |
| implement | add, create |
| leverage | use |
| facilitate | help, enable |
| commence | start, begin |
| terminate | end, stop |
| subsequently | then, after |
| prior to | before |

### One Idea Per Sentence

```
❌ "The function processes the data, validates it, transforms the result,
   and then returns the output while logging any errors that occur."

✓ "The function processes and validates the data. It transforms the result
   and returns the output. Any errors are logged automatically."
```

### Define Acronyms

```
❌ "Configure the API using JWT tokens."

✓ "Configure the API using JWT (JSON Web Token) tokens."
   (Define on first use, then use acronym)
```

### Avoid Jargon Without Explanation

```
❌ "The function uses memoization for performance."

✓ "The function caches results (memoization) to avoid repeated calculations."
```

---

## Structure

### Use Headings Hierarchically

```
❌
## Topic
#### Subtopic (skipped h3)

✓
## Topic
### Subtopic
#### Detail
```

### Lead with the Most Important Information

```
❌ "After considering various options and evaluating the trade-offs,
   you should use method A for best performance."

✓ "Use method A for best performance."
   (Details can follow if needed)
```

### Use Lists for Multiple Items

```
❌ "The function accepts a data parameter, an options parameter,
   and an optional callback parameter."

✓ "The function accepts:
   - `data` - Input data
   - `options` - Configuration options
   - `callback` (optional) - Completion handler"
```

### Group Related Information

```
❌ Parameters scattered throughout text

✓ **Parameters**:
  - `param1`: Description
  - `param2`: Description

  **Returns**:
  - Description of return value

  **Example**:
  ```code block```
```

---

## Code Examples

### Make Examples Complete and Runnable

```
❌
```python
result = process(data)
```

✓
```python
from mypackage import process

data = {"key": "value"}
result = process(data)
print(result)  # Output: {"processed": True}
```
```

### Show Expected Output

```python
result = calculate(10, 5)
print(result)
# Output: 15
```

### Use Realistic Data

```
❌
user = {"name": "foo", "id": 123}

✓
user = {"name": "Alice Chen", "id": "user_abc123"}
```

### Include Error Cases

```python
# Valid input
result = process(valid_data)

# Invalid input - shows error handling
try:
    result = process(invalid_data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

## Formatting Conventions

### Code References

- Use backticks for: `function_names`, `variable_names`, `file.py`, `command`
- Use code blocks for multi-line code
- Specify language for syntax highlighting

### File Paths

```
❌ config.yaml
✓ `config.yaml`

❌ /path/to/file
✓ `/path/to/file`
```

### UI Elements

Use bold for UI elements:

```
Click **Settings** > **Advanced** > **Save**.
```

### Keyboard Shortcuts

```
Press **Ctrl+C** to copy.
Press **Cmd+V** (Mac) or **Ctrl+V** (Windows) to paste.
```

---

## Parameter Documentation

### Standard Format

```
- `parameter_name` (type): Description of what it does.
- `optional_param` (type, optional): Description. Defaults to `value`.
```

### Include Types

```
❌ - `data`: The input data

✓ - `data` (dict): Input data containing user information
```

### Document Defaults

```
❌ - `timeout` (int, optional): Request timeout.

✓ - `timeout` (int, optional): Request timeout in seconds. Defaults to `30`.
```

### Document Constraints

```
- `port` (int): Server port number. Must be between 1 and 65535.
- `name` (str): User name. Maximum 100 characters.
```

---

## Common Patterns

### Prerequisites Section

```markdown
## Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher
- pip package manager
- An API key ([get one here](https://...))
```

### Warning/Note Patterns

Use platform-appropriate admonitions for:
- **Note**: Additional helpful information
- **Tip**: Suggestions for better usage
- **Warning**: Potential issues to avoid
- **Danger**: Critical warnings about data loss or security

### Version Information

```markdown
> Available since version 2.0

> **Deprecated** in version 2.5. Use `new_function()` instead.
```

### See Also Sections

```markdown
## See Also

- [Related Topic](./related.md) - Brief description
- [API Reference](./api.md) - Full API documentation
```

---

## Checklist

Before submitting documentation:

- [ ] Active voice used
- [ ] Second person ("you") for instructions
- [ ] Imperative mood for steps
- [ ] No unexplained jargon
- [ ] Code examples are complete and runnable
- [ ] Parameters documented with types
- [ ] Headings are hierarchical
- [ ] Links are working
- [ ] Platform formatting is correct
