# Documentation Manager MCP Server

An MCP (Model Context Protocol) server for comprehensive documentation lifecycle management. Automates documentation creation, maintenance, quality assessment, and synchronization for software projects.

## Features

### Currently Implemented

- **Configuration Management** (`docmgr_initialize_config`)
  - Creates `.doc-manager.yml` configuration
  - Auto-detects documentation platform (Hugo, Docusaurus, MkDocs, Sphinx, etc.)
  - Configures exclude patterns and project metadata

- **Memory System** (`docmgr_initialize_memory`)
  - Tracks repository baseline with file checksums
  - Maintains documentation conventions
  - Manages asset manifest
  - Detects code changes via checksum comparison

- **Platform Detection** (`docmgr_detect_platform`)
  - Identifies existing documentation platforms
  - Recommends best platform based on project language
  - Provides rationale for recommendations

### Planned Tools

- Quality Assessment (7 criteria: relevance, accuracy, purposefulness, uniqueness, consistency, clarity, structure)
- Documentation Validation (broken links, code snippets, asset validation)
- Change Mapping (git diff analysis for doc impacts)
- Dependency Tracking (code-to-docs mapping)
- Bootstrap Workflow (generate fresh documentation)
- Migration Workflow (restructure existing docs)
- Sync Workflow (incremental updates)

## Installation

```bash
# Clone or navigate to the doc-manager directory
cd /path/to/doc-manager

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the MCP Server

The server uses stdio transport for communication with MCP clients:

```bash
python server.py
```

### Available Tools

#### 1. Initialize Configuration

Creates `.doc-manager.yml` configuration file:

```json
{
  "project_path": "/absolute/path/to/project",
  "platform": "hugo",  // optional, auto-detected if omitted
  "exclude_patterns": ["**/node_modules", "**/dist"]  // optional
}
```

#### 2. Initialize Memory System

Sets up the documentation memory system:

```json
{
  "project_path": "/absolute/path/to/project"
}
```

Creates:
- `.doc-manager/memory/repo-baseline.json` - Project metadata and file checksums
- `.doc-manager/memory/doc-conventions.md` - Documentation style guide
- `.doc-manager/asset-manifest.json` - Asset tracking

#### 3. Detect Platform

Analyzes project and recommends documentation platform:

```json
{
  "project_path": "/absolute/path/to/project",
  "response_format": "markdown"  // or "json"
}
```

## Project Structure

```
doc-manager/
├── server.py              # Main MCP server entry point
├── src/
│   ├── constants.py       # Constants and enums
│   ├── models.py          # Pydantic input models
│   ├── utils.py           # Utility functions
│   └── tools/
│       ├── config.py      # Configuration tools
│       ├── memory.py      # Memory system tools
│       └── platform.py    # Platform detection tools
├── requirements.txt
└── README.md
```

## Configuration File Format

Example `.doc-manager.yml`:

```yaml
platform: hugo
exclude:
  - '**/node_modules'
  - '**/dist'
  - '**/vendor'
  - '**/*.log'
sources: []
docs_path: docs
metadata:
  language: Go
  created: '2025-01-13T10:30:00'
  version: '1.0.0'
```

## Memory System

The memory system tracks project state to enable intelligent documentation synchronization:

### Repo Baseline (`repo-baseline.json`)

```json
{
  "repo_name": "my-project",
  "description": "Repository for my-project",
  "language": "Go",
  "docs_exist": true,
  "docs_path": "docs",
  "git_commit": "abc123...",
  "git_branch": "main",
  "created_at": "2025-01-13T10:30:00",
  "version": "1.0.0",
  "file_count": 1234,
  "checksums": {
    "main.go": "sha256:...",
    "README.md": "sha256:..."
  }
}
```

### Doc Conventions (`doc-conventions.md`)

Customizable style guide for documentation standards. Defines:
- Voice and tone
- Formatting conventions
- Terminology standards
- Code example requirements
- Quality standards

## Development

### Adding New Tools

1. Create tool implementation in `src/tools/`
2. Define Pydantic input model in `src/models.py`
3. Register tool in `server.py` with `@mcp.tool` decorator
4. Update README with tool documentation

### Testing

```bash
# Test imports and syntax
python -m py_compile server.py

# Run server (will hang waiting for stdio input - this is expected)
timeout 5s python server.py
```

## License

[Your License Here]

## Contributing

Contributions welcome! Please follow MCP best practices and maintain modular structure.
