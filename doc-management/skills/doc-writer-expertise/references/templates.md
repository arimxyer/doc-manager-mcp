# Documentation Templates

Ready-to-use templates for common documentation types.

## Function Documentation

### Basic Function

```markdown
## function_name

Brief description of what the function does.

**Parameters**:
- `param1` (type): Description of parameter
- `param2` (type, optional): Description. Defaults to `default_value`.

**Returns**:
- `ReturnType`: Description of return value

**Example**:
```python
result = function_name(arg1, arg2)
print(result)
```
```

### Function with Exceptions

```markdown
## function_name

Brief description.

**Parameters**:
- `data` (dict): Input data dictionary
- `validate` (bool, optional): Whether to validate input. Defaults to `True`.

**Returns**:
- `Result`: Processed result object

**Raises**:
- `ValueError`: If data is empty or malformed
- `TypeError`: If data is not a dictionary
- `ProcessingError`: If processing fails

**Example**:
```python
try:
    result = function_name({"key": "value"})
except ValueError as e:
    print(f"Invalid data: {e}")
```
```

### Async Function

```markdown
## async function_name

Brief description of async operation.

**Parameters**:
- `url` (str): Target URL
- `timeout` (float, optional): Request timeout in seconds. Defaults to `30.0`.

**Returns**:
- `Response`: HTTP response object

**Raises**:
- `TimeoutError`: If request exceeds timeout
- `ConnectionError`: If connection fails

**Example**:
```python
async def main():
    response = await function_name("https://api.example.com")
    print(response.status)

asyncio.run(main())
```
```

---

## Class Documentation

### Basic Class

```markdown
## ClassName

Brief description of the class purpose.

**Attributes**:
- `attribute1` (type): Description
- `attribute2` (type): Description

**Example**:
```python
obj = ClassName(param1, param2)
obj.method()
```
```

### Class with Methods

```markdown
## ClassName

Brief description.

### Constructor

```python
ClassName(param1, param2, *, option=None)
```

**Parameters**:
- `param1` (type): Description
- `param2` (type): Description
- `option` (type, optional): Description. Defaults to `None`.

### Attributes

- `attr1` (type): Description
- `attr2` (type): Description (read-only)

### Methods

#### method_name

```python
obj.method_name(arg) -> ReturnType
```

Brief description.

**Parameters**:
- `arg` (type): Description

**Returns**:
- `ReturnType`: Description

### Example

```python
# Create instance
obj = ClassName("value1", "value2")

# Use methods
result = obj.method_name(arg)
print(obj.attr1)
```
```

---

## Guide/Tutorial Templates

### Getting Started Guide

```markdown
# Getting Started with [Product]

This guide will help you get up and running with [Product] in under 5 minutes.

## Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher
- pip package manager

## Installation

Install [Product] using pip:

```bash
pip install product-name
```

## Quick Start

### 1. Import the library

```python
from product import Client
```

### 2. Create a client

```python
client = Client(api_key="your-api-key")
```

### 3. Make your first request

```python
result = client.process("Hello, World!")
print(result)
```

## Next Steps

- [Configuration Guide](./configuration.md) - Customize your setup
- [API Reference](./api.md) - Full API documentation
- [Examples](./examples.md) - More usage examples
```

### How-To Guide

```markdown
# How to [Task]

This guide explains how to [accomplish specific task].

## Overview

[Brief explanation of what this guide covers and when you'd need it]

## Prerequisites

- [Prerequisite 1]
- [Prerequisite 2]

## Steps

### Step 1: [Action]

[Explanation]

```python
# Code example
```

### Step 2: [Action]

[Explanation]

```python
# Code example
```

### Step 3: [Action]

[Explanation]

```python
# Code example
```

## Complete Example

Here's the full code:

```python
# Complete working example
```

## Troubleshooting

### Common Issue 1

**Problem**: [Description]

**Solution**: [How to fix]

### Common Issue 2

**Problem**: [Description]

**Solution**: [How to fix]

## Related

- [Related Guide 1](./related1.md)
- [Related Guide 2](./related2.md)
```

### Tutorial (Learning-Focused)

```markdown
# Tutorial: Building a [Thing]

In this tutorial, you'll learn how to build a [thing] from scratch.

**What you'll learn**:
- [Concept 1]
- [Concept 2]
- [Concept 3]

**Time required**: ~15 minutes

**Difficulty**: Beginner / Intermediate / Advanced

## Introduction

[Context and motivation - why is this useful?]

## Part 1: [Foundation]

[Explanation of first concept]

```python
# Code for part 1
```

**Key takeaway**: [What they should understand]

## Part 2: [Building]

[Explanation of second concept]

```python
# Code for part 2
```

**Key takeaway**: [What they should understand]

## Part 3: [Completing]

[Explanation of final concept]

```python
# Code for part 3
```

**Key takeaway**: [What they should understand]

## Final Result

Here's everything together:

```python
# Complete final code
```

## Summary

In this tutorial, you learned:
- [Recap point 1]
- [Recap point 2]
- [Recap point 3]

## Next Steps

Try these challenges:
1. [Challenge 1]
2. [Challenge 2]

Continue learning:
- [Next Tutorial](./next.md)
- [Advanced Topics](./advanced.md)
```

---

## API Reference Templates

### Module Reference

```markdown
# module_name

Brief description of the module.

## Overview

[What this module provides and when to use it]

## Functions

### function_one

[Function documentation]

### function_two

[Function documentation]

## Classes

### ClassName

[Class documentation]

## Constants

### CONSTANT_NAME

```python
CONSTANT_NAME: type = value
```

Description of what this constant represents.

## Examples

```python
from module_name import function_one, ClassName

# Example usage
```
```

### Configuration Reference

```markdown
# Configuration Reference

Complete reference for all configuration options.

## Configuration File

Create a `config.yaml` in your project root:

```yaml
# Example configuration
option1: value1
option2: value2
```

## Options

### option1

- **Type**: string
- **Default**: `"default_value"`
- **Required**: Yes / No

Description of what this option does.

**Example**:
```yaml
option1: "custom_value"
```

### option2

- **Type**: integer
- **Default**: `100`
- **Required**: No
- **Valid range**: 1-1000

Description.

**Example**:
```yaml
option2: 500
```

### nested_options

- **Type**: object
- **Default**: `{}`

Nested configuration options.

#### nested_options.sub_option

- **Type**: boolean
- **Default**: `true`

Description.

## Environment Variables

Configuration can also be set via environment variables:

| Option | Environment Variable | Example |
|--------|---------------------|---------|
| option1 | `PRODUCT_OPTION1` | `export PRODUCT_OPTION1=value` |
| option2 | `PRODUCT_OPTION2` | `export PRODUCT_OPTION2=500` |

## Complete Example

```yaml
# Full configuration example
option1: "production"
option2: 500
nested_options:
  sub_option: false
```
```

---

## Changelog Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description

## [2.0.0] - 2024-01-15

### Added
- New feature 1
- New feature 2

### Changed
- **BREAKING**: Changed API signature for `function_name`
- Improved performance of processing

### Deprecated
- `old_function` is deprecated, use `new_function` instead

### Removed
- Removed support for Python 3.7

### Fixed
- Fixed issue with error handling (#123)

### Security
- Updated dependencies to address CVE-XXXX-XXXX

## [1.5.0] - 2023-12-01

### Added
- Added support for new feature

[Unreleased]: https://github.com/user/repo/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/user/repo/compare/v1.5.0...v2.0.0
[1.5.0]: https://github.com/user/repo/releases/tag/v1.5.0
```
