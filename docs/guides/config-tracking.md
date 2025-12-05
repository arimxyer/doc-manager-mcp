# Config field tracking

Track changes to configuration fields and get actionable suggestions for documentation updates.

## Overview

Config field tracking automatically detects when configuration fields change in your codebase. When you add, remove, or modify config fields, doc-manager identifies these changes and suggests specific documentation updates.

**Supported config patterns:**
- Python: Pydantic models, dataclasses, attrs classes
- Go: Structs with field tags
- TypeScript: Interfaces and type aliases
- Rust: Structs with serde derive

## Enabling config field tracking

Config field tracking is enabled with the `include_semantic=true` parameter:

```json
{
  "tool": "docmgr_detect_changes",
  "arguments": {
    "project_path": "/path/to/project",
    "include_semantic": true
  }
}
```

Or via the sync tool:

```json
{
  "tool": "docmgr_sync",
  "arguments": {
    "project_path": "/path/to/project",
    "mode": "check"
  }
}
```

The sync tool runs semantic analysis by default.

## What gets detected

### Field additions

When you add a new config field:

```python
class AppConfig(BaseModel):
    timeout: int = 30  # new field
```

Doc-manager detects:
- Field name, type, and default value
- Parent class/struct
- Optional field descriptions from `Field(description="...")`

### Field removals

When a config field is removed, doc-manager flags it as a breaking change requiring documentation updates.

### Field modifications

Doc-manager detects changes to:
- Field types (`str` → `int`)
- Default values (`30` → `60`)
- Optional/required status

## Reading the output

### Config field changes

```json
{
  "config_field_changes": [
    {
      "field_name": "max_retries",
      "parent_symbol": "ClientConfig",
      "change_type": "added",
      "file": "src/config.py",
      "line": 42,
      "new_type": "int",
      "new_default": "3",
      "severity": "non-breaking",
      "documentation_action": "add_field_doc"
    }
  ]
}
```

**Change types:**
| Type | Meaning | Severity |
|------|---------|----------|
| `added` | New field | Non-breaking |
| `removed` | Field deleted | Breaking |
| `type_changed` | Type modified | Varies |
| `default_changed` | Default value changed | Non-breaking |

### Action items

```json
{
  "action_items": [
    {
      "action_type": "add_field_doc",
      "target_file": "docs/reference/configuration.md",
      "target_section": "ClientConfig",
      "description": "Document new 'max_retries' field in ClientConfig",
      "priority": "high"
    }
  ]
}
```

**Priority levels:**
| Priority | When assigned |
|----------|---------------|
| `critical` | Breaking changes (removed fields) |
| `high` | New config fields, signature changes |
| `medium` | Default value changes |
| `low` | Minor documentation updates |

## Configuration presets

Control which config classes are tracked using presets in `.doc-manager.yml`:

```yaml
api_coverage:
  preset: 'pydantic'  # Track Pydantic models
  strategy: 'all_only'
```

**Available presets:**
- `pydantic` - Python Pydantic models and dataclasses
- `go` - Go structs
- `typescript` - TypeScript interfaces
- `rust` - Rust structs with serde

## Workflow example

### After modifying config fields

1. **Detect changes:**

```json
{
  "tool": "docmgr_detect_changes",
  "arguments": {
    "project_path": "/path/to/project",
    "include_semantic": true
  }
}
```

2. **Review action items** in the output. Each item tells you:
   - Which doc file needs updating
   - What section to update
   - What change to make
   - Priority level

3. **Update documentation** based on action items.

4. **Update baselines:**

```json
{
  "tool": "docmgr_update_baseline",
  "arguments": {
    "project_path": "/path/to/project"
  }
}
```

### Using Claude Code plugin

With the plugin installed, config field tracking is built into the `/doc-sync` command:

```text
/doc-sync
```

The `@doc-expert` agent will:
1. Detect config field changes
2. Present action items
3. Coordinate documentation updates with `@doc-writer`
4. Update baselines when complete

## Performance considerations

Semantic analysis (including config field tracking) requires AST parsing with TreeSitter. For large codebases:

- Initial analysis may take a few seconds
- Subsequent runs benefit from caching
- Use `include_semantic=false` for quick validation-only checks

## See also

- [Detect changes tool](../reference/tools/docmgr_detect_changes.md) - Full parameter reference
- [Workflows](workflows.md) - Daily maintenance patterns
- [Configuration](../reference/configuration.md) - `.doc-manager.yml` options
