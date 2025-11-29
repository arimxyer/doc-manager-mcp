# Pydantic Models Reference

**Module:** `doc_manager_mcp.models`

Complete reference for all Pydantic models in the doc-manager MCP server.

## Overview

The models are organized into three categories:

1. **Input Models** - Validated request parameters for tools
2. **Convention Models** - Documentation standards and conventions
3. **Output Models** - Structured response data

All models use Pydantic v2 with strict validation, string whitespace trimming, and forbidden extra fields.

---

## Input Models

### DocmgrInitInput

Initialize doc-manager for a project (existing docs or create new).

**Purpose**: Sets up doc-manager infrastructure by creating configuration files and baseline tracking.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory (e.g., `/home/user/project` or `C:\Users\user\project`) |
| `mode` | `str` | No | `"existing"` | Init mode: `"existing"` (config+baselines+deps) or `"bootstrap"` (+ doc templates) |
| `platform` | `DocumentationPlatform \| None` | No | `None` | Documentation platform (mkdocs, docusaurus, sphinx, etc.) - auto-detected if not specified |
| `exclude_patterns` | `list[str] \| None` | No | `None` | Glob patterns for files to exclude from documentation tracking (max 50 patterns) |
| `docs_path` | `str \| None` | No | `None` | Path to documentation directory relative to project root (e.g., `docs/`, `documentation/`) |
| `sources` | `list[str] \| None` | No | `None` | Source file patterns to track for documentation (e.g., `['src/**/*.py']`, max 50 patterns) |
| `include_root_readme` | `bool` | No | `False` | Include root README.md in documentation operations (validation, quality assessment, change detection) |
| `use_gitignore` | `bool` | No | `False` | Automatically exclude files based on .gitignore patterns (opt-in). Priority: user excludes > gitignore > defaults |

**Validation**:

- `project_path`: Must be absolute path, must exist, must be directory, no path traversal sequences
- `docs_path`: Must be relative path, no path traversal sequences
- `exclude_patterns` and `sources`: Each pattern max 512 chars, no ReDoS-vulnerable patterns, max 50 patterns total

**Example**:

```python
from doc_manager_mcp.models import DocmgrInitInput
from doc_manager_mcp.constants import DocumentationPlatform

# Initialize for existing documentation
init = DocmgrInitInput(
    project_path="/home/user/my-project",
    mode="existing",
    platform=DocumentationPlatform.MKDOCS,
    sources=["src/**/*.py"],
    exclude_patterns=["tests/**", "**/__pycache__/**"]
)

# Bootstrap new documentation
init = DocmgrInitInput(
    project_path="/home/user/my-project",
    mode="bootstrap",
    platform=DocumentationPlatform.SPHINX,
    sources=["lib/**/*.js", "packages/**/*.ts"]
)
```

---

### DocmgrDetectChangesInput

Detect code changes without modifying baselines (pure read-only).

**Purpose**: Identifies changed files by comparing current state against baselines.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory |
| `since_commit` | `str \| None` | No | `None` | Git commit SHA to compare from (only for `git_diff` mode). Must be 7-40 hexadecimal characters |
| `mode` | `ChangeDetectionMode` | No | `ChangeDetectionMode.CHECKSUM` | Detection mode: `"checksum"` (file checksums) or `"git_diff"` (git changes) |
| `include_semantic` | `bool` | No | `False` | Include semantic diff analysis (TreeSitter AST comparison) for function/class changes |

**Validation**:

- `project_path`: Must be absolute path, must exist, must be directory
- `since_commit`: Must be 7-40 hexadecimal characters if provided (git SHA format)
- `mode`: If `"git_diff"`, `since_commit` is required

**Example**:

```python
from doc_manager_mcp.models import DocmgrDetectChangesInput
from doc_manager_mcp.constants import ChangeDetectionMode

# Basic change detection (checksum mode)
detect = DocmgrDetectChangesInput(
    project_path="/home/user/my-project",
    mode=ChangeDetectionMode.CHECKSUM
)

# Semantic change detection
detect = DocmgrDetectChangesInput(
    project_path="/home/user/my-project",
    mode=ChangeDetectionMode.CHECKSUM,
    include_semantic=True
)

# Compare against specific commit
detect = DocmgrDetectChangesInput(
    project_path="/home/user/my-project",
    mode=ChangeDetectionMode.GIT_DIFF,
    since_commit="abc123def456"
)
```

---

### DocmgrUpdateBaselineInput

Update all baseline files atomically after documentation changes.

**Purpose**: Updates baselines (file checksums, code symbols, code-to-doc mappings) to reflect current state.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory |
| `docs_path` | `str \| None` | No | `None` | Path to documentation directory relative to project root (auto-detected if not specified) |

**Updates**:

- `repo-baseline.json` - File checksums
- `symbol-baseline.json` - TreeSitter code symbols
- `dependencies.json` - Code-to-doc mappings

**Example**:

```python
from doc_manager_mcp.models import DocmgrUpdateBaselineInput

# Update all baselines
baseline = DocmgrUpdateBaselineInput(
    project_path="/home/user/my-project"
)

# Update with custom docs path
baseline = DocmgrUpdateBaselineInput(
    project_path="/home/user/my-project",
    docs_path="documentation"
)
```

---

### ValidateDocsInput

Validate documentation for broken links, missing assets, and code syntax.

**Purpose**: Checks documentation quality and integrity across multiple dimensions.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory |
| `docs_path` | `str \| None` | No | `None` | Path to documentation directory relative to project root (auto-detected if not specified) |
| `check_links` | `bool` | No | `True` | Check for broken internal and external links |
| `check_assets` | `bool` | No | `True` | Validate asset links and alt text |
| `check_snippets` | `bool` | No | `True` | Extract and validate code snippets |
| `validate_code_syntax` | `bool` | No | `False` | Validate code example syntax using TreeSitter (semantic validation) |
| `validate_symbols` | `bool` | No | `False` | Validate that documented symbols (functions/classes) exist in codebase |
| `include_root_readme` | `bool` | No | `False` | Include root README.md in validation |
| `incremental` | `bool` | No | `False` | Only validate files that changed since last baseline (5-10x faster) |

**Example**:

```python
from doc_manager_mcp.models import ValidateDocsInput

# Basic validation
validate = ValidateDocsInput(
    project_path="/home/user/my-project"
)

# Full validation with syntax checking
validate = ValidateDocsInput(
    project_path="/home/user/my-project",
    check_links=True,
    check_assets=True,
    check_snippets=True,
    validate_code_syntax=True,
    validate_symbols=True
)

# Incremental validation (faster)
validate = ValidateDocsInput(
    project_path="/home/user/my-project",
    incremental=True
)
```

---

### AssessQualityInput

Assess documentation quality against defined criteria.

**Purpose**: Evaluates documentation quality across 7 criteria: relevance, accuracy, purposefulness, uniqueness, consistency, clarity, and structure.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory |
| `docs_path` | `str \| None` | No | `None` | Path to documentation directory relative to project root (auto-detected if not specified) |
| `criteria` | `list[QualityCriterion] \| None` | No | `None` | Specific criteria to assess. If not specified, all 7 criteria will be assessed |
| `include_root_readme` | `bool` | No | `False` | Include root README.md in quality assessment |

**Criteria Options**:

- `QualityCriterion.RELEVANCE` - Documentation addresses actual user needs
- `QualityCriterion.ACCURACY` - Information is factually correct and up-to-date
- `QualityCriterion.PURPOSEFULNESS` - Content has clear purpose and value
- `QualityCriterion.UNIQUENESS` - Information is not redundant
- `QualityCriterion.CONSISTENCY` - Style and terminology are consistent
- `QualityCriterion.CLARITY` - Content is clear and accessible
- `QualityCriterion.STRUCTURE` - Organization is logical and navigable

**Example**:

```python
from doc_manager_mcp.models import AssessQualityInput
from doc_manager_mcp.constants import QualityCriterion

# Assess all quality criteria
assess = AssessQualityInput(
    project_path="/home/user/my-project"
)

# Assess specific criteria
assess = AssessQualityInput(
    project_path="/home/user/my-project",
    criteria=[
        QualityCriterion.CLARITY,
        QualityCriterion.CONSISTENCY,
        QualityCriterion.ACCURACY
    ]
)
```

---

### MigrateInput

Migrate existing documentation between platforms or locations.

**Purpose**: Migrate documentation from one platform to another while preserving structure and history.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory |
| `source_path` | `str` | Yes | - | Path to existing documentation directory (relative to project root) |
| `target_path` | `str` | No | `"docs"` | Path where migrated documentation should be created (relative to project root) |
| `target_platform` | `DocumentationPlatform \| None` | No | `None` | Target platform for migration. If not specified, will preserve existing platform |
| `preserve_history` | `bool` | No | `True` | Use git mv to preserve file history during migration |
| `rewrite_links` | `bool` | No | `False` | Automatically rewrite internal links when migrating documentation to new structure |
| `regenerate_toc` | `bool` | No | `False` | Regenerate table of contents for each migrated file using <!-- TOC --> markers |
| `dry_run` | `bool` | No | `False` | Preview migration changes without modifying files |

**Example**:

```python
from doc_manager_mcp.models import MigrateInput
from doc_manager_mcp.constants import DocumentationPlatform

# Migrate from docusaurus to mkdocs
migrate = MigrateInput(
    project_path="/home/user/my-project",
    source_path="docsite",
    target_path="docs",
    target_platform=DocumentationPlatform.MKDOCS,
    rewrite_links=True
)

# Preview migration (dry run)
migrate = MigrateInput(
    project_path="/home/user/my-project",
    source_path="documentation",
    target_path="docs",
    dry_run=True
)
```

---

### SyncInput

Synchronize documentation with code changes.

**Purpose**: Detects documentation drift and optionally updates baselines.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory |
| `mode` | `str` | No | `"check"` | Sync mode: `"check"` (read-only analysis) or `"resync"` (update baselines + analysis) |
| `docs_path` | `str \| None` | No | `None` | Path to documentation directory relative to project root (auto-detected if not specified) |

**Modes**:

- `"check"` - Analyze documentation drift without modifying baselines (read-only)
- `"resync"` - Update baselines and analyze drift

**Example**:

```python
from doc_manager_mcp.models import SyncInput

# Check drift without updating baselines
sync = SyncInput(
    project_path="/home/user/my-project",
    mode="check"
)

# Resync: update baselines after docs updated
sync = SyncInput(
    project_path="/home/user/my-project",
    mode="resync"
)
```

---

### DetectPlatformInput

Detect documentation platform.

**Purpose**: Auto-detect which documentation platform is used in the project.

**Fields**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `project_path` | `str` | Yes | - | Absolute path to project root directory |

**Example**:

```python
from doc_manager_mcp.models import DetectPlatformInput

detect = DetectPlatformInput(
    project_path="/home/user/my-project"
)
```

---

## Convention Models

### StyleConventions

Style-related documentation conventions.

**Fields**:

```python
class HeadingConfig(BaseModel):
    case: Literal["sentence_case", "title_case", "lower", "upper"] | None
    consistency_required: bool = True

class CodeConfig(BaseModel):
    inline_format: Literal["backticks", "html"] = "backticks"
    block_language_required: bool = True

class VoiceConfig(BaseModel):
    person: Literal["first", "second", "third"] = "second"
    active_voice_preferred: bool = True

headings: HeadingConfig
code: CodeConfig
voice: VoiceConfig
```

**Example**:

```python
from doc_manager_mcp.models import StyleConventions

style = StyleConventions(
    headings=StyleConventions.HeadingConfig(
        case="title_case",
        consistency_required=True
    ),
    code=StyleConventions.CodeConfig(
        inline_format="backticks",
        block_language_required=True
    ),
    voice=StyleConventions.VoiceConfig(
        person="second",
        active_voice_preferred=True
    )
)
```

---

### StructureConventions

Structure-related documentation conventions.

**Fields**:

```python
class TocConfig(BaseModel):
    enabled: bool = True
    min_length: int = 500  # Minimum words for requiring TOC

require_intro: bool = True
require_toc: TocConfig
max_heading_depth: int | None = 3
heading_hierarchy: Literal["strict", "relaxed"] = "strict"
```

**Example**:

```python
from doc_manager_mcp.models import StructureConventions

structure = StructureConventions(
    require_intro=True,
    require_toc=StructureConventions.TocConfig(
        enabled=True,
        min_length=500
    ),
    max_heading_depth=3,
    heading_hierarchy="strict"
)
```

---

### QualityConventions

Quality-related documentation conventions.

**Fields**:

```python
class SentenceConfig(BaseModel):
    max_length: int | None = 25  # Words
    min_length: int | None = 3   # Words

class ParagraphConfig(BaseModel):
    max_length: int | None = 150  # Words

class LinkConfig(BaseModel):
    validate_links: bool = True

class ImageConfig(BaseModel):
    require_alt_text: bool = True

class CodeQualityConfig(BaseModel):
    validate_syntax: bool = False

sentences: SentenceConfig
paragraphs: ParagraphConfig
links: LinkConfig
images: ImageConfig
code: CodeQualityConfig
```

**Example**:

```python
from doc_manager_mcp.models import QualityConventions

quality = QualityConventions(
    sentences=QualityConventions.SentenceConfig(
        max_length=25,
        min_length=3
    ),
    paragraphs=QualityConventions.ParagraphConfig(
        max_length=150
    ),
    links=QualityConventions.LinkConfig(
        validate_links=True
    ),
    images=QualityConventions.ImageConfig(
        require_alt_text=True
    ),
    code=QualityConventions.CodeQualityConfig(
        validate_syntax=False
    )
)
```

---

### TerminologyConventions

Terminology-related documentation conventions.

**Fields**:

```python
preferred: dict[str, PreferredTerminology]  # Preferred terms (detection only)
avoid: list[TerminologyRule]                # Words/phrases to avoid (flagged as warnings)
```

**Nested Models**:

```python
class PreferredTerminology(BaseModel):
    full_form: str  # e.g., "Model Context Protocol"
    abbreviation: str | None  # e.g., "MCP"
    guidance: str | None  # e.g., "Spell out on first use, abbreviate after"

class TerminologyRule(BaseModel):
    word: str  # Word or phrase to avoid
    reason: str | None  # Why this term should be avoided
    exceptions: list[str]  # Phrases that should not be flagged
```

**Example**:

```python
from doc_manager_mcp.models import TerminologyConventions, PreferredTerminology, TerminologyRule

terminology = TerminologyConventions(
    preferred={
        "mcp": PreferredTerminology(
            full_form="Model Context Protocol",
            abbreviation="MCP",
            guidance="Spell out on first use, abbreviate after"
        )
    },
    avoid=[
        TerminologyRule(
            word="just",
            reason="Avoid for clarity",
            exceptions=["just-in-time"]
        )
    ]
)
```

---

### DocumentationConventions

Complete documentation conventions configuration.

**Purpose**: Represents the schema for `doc-conventions.yml` files.

**Fields**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `style` | `StyleConventions` | `{}` | Style conventions (headings, code, voice) |
| `structure` | `StructureConventions` | `{}` | Structure conventions (intro, TOC, hierarchy) |
| `quality` | `QualityConventions` | `{}` | Quality conventions (sentences, links, images) |
| `terminology` | `TerminologyConventions` | `{}` | Terminology conventions (preferred terms, words to avoid) |

**Example**:

```python
from doc_manager_mcp.models import DocumentationConventions

conventions = DocumentationConventions()

# Or with custom settings
conventions = DocumentationConventions(
    style=StyleConventions(...),
    structure=StructureConventions(...),
    quality=QualityConventions(...),
    terminology=TerminologyConventions(...)
)
```

---

## Output Models

### MapChangesOutput

Structured response for change detection operations.

**Purpose**: Returns analyzed changes with semantic information when requested.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `analyzed_at` | `str` | ISO 8601 timestamp when analysis was performed |
| `baseline_commit` | `str \| None` | Git commit SHA used as baseline (null if using checksum mode) |
| `baseline_created` | `str \| None` | ISO 8601 timestamp when baseline was created (null if git mode) |
| `changes_detected` | `bool` | Whether any changes were detected |
| `total_changes` | `int` | Total number of changed files detected |
| `changed_files` | `list[dict[str, str]]` | List of files that changed with their paths and change types |
| `affected_documentation` | `list[dict[str, Any]]` | List of documentation files affected by code changes |
| `semantic_changes` | `list[SemanticChange]` | Code-level semantic changes (function signatures, classes, methods). Only populated when `include_semantic=True` |

**Example**:

```python
{
    "analyzed_at": "2025-01-15T10:30:45Z",
    "baseline_commit": None,
    "baseline_created": "2025-01-15T10:00:00Z",
    "changes_detected": True,
    "total_changes": 3,
    "changed_files": [
        {"path": "src/api.py", "type": "code"},
        {"path": "src/models.py", "type": "code"},
        {"path": "docs/api.md", "type": "documentation"}
    ],
    "affected_documentation": [
        {"file": "docs/api.md", "reason": "src/api.py changed"},
        {"file": "docs/reference.md", "reason": "src/models.py changed"}
    ],
    "semantic_changes": [
        {"type": "added", "symbol": "new_function"},
        {"type": "modified", "symbol": "existing_class"}
    ]
}
```

---

## Validation Behavior

All input models include validators for security and correctness:

### Path Validation

- **Absolute paths**: Must be absolute, not relative
- **Path existence**: Must exist on filesystem
- **Directory validation**: Must be directories (where applicable)
- **Path traversal prevention**: No `..` sequences allowed

### Glob Pattern Validation

- **Length limit**: Max 512 characters per pattern
- **ReDoS prevention**: Detects nested quantifiers like `(a+)+` or `(a*)*`
- **List limit**: Max 50 patterns in list
- **Empty check**: Patterns must be non-empty strings

### Security

- **Command injection prevention**: Git commit hashes validated as hex format only
- **No special sequences**: Rejects shell metacharacters in sensitive fields
- **Extra fields forbidden**: Unknown fields are rejected (prevents API abuse)

---

## Common Usage Patterns

### Creating Input Models

```python
from doc_manager_mcp.models import DocmgrInitInput
from doc_manager_mcp.constants import DocumentationPlatform

# Valid instantiation
init = DocmgrInitInput(
    project_path="/home/user/project",
    platform=DocumentationPlatform.MKDOCS
)

# Invalid - relative path raises ValueError
try:
    init = DocmgrInitInput(project_path="./project")
except ValueError as e:
    print(f"Validation error: {e}")
```

### Handling Validation Errors

```python
from pydantic import ValidationError
from doc_manager_mcp.models import ValidateDocsInput

try:
    validate = ValidateDocsInput(
        project_path="/nonexistent/path"
    )
except ValidationError as e:
    for error in e.errors():
        print(f"Field: {error['loc'][0]}")
        print(f"Error: {error['msg']}")
```

### Working with Enums

```python
from doc_manager_mcp.constants import DocumentationPlatform, ChangeDetectionMode

# Using enum values
platform = DocumentationPlatform.MKDOCS  # Preferred
platform = DocumentationPlatform("mkdocs")  # Also valid

# Checking enum membership
if platform in [DocumentationPlatform.SPHINX, DocumentationPlatform.MKDOCS]:
    print("Python-friendly platform")
```

---

## See also

- [Enums reference](./enums.md) - DocumentationPlatform, QualityCriterion, ChangeDetectionMode
- [Configuration reference](../configuration.md) - .doc-manager.yml schema
- [Tools reference](../tools.md) - Tool descriptions and usage
