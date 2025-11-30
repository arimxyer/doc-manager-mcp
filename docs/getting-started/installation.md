# Installation

Documentation Manager is an MCP (Model Context Protocol) server that integrates with Claude Desktop and other MCP clients to automate documentation lifecycle management.

## Prerequisites

- Python 3.10 or higher
- An MCP client (Claude Desktop, Claude Code, or other MCP-compatible client)
- Git (optional, for version control features)

## Choose your installation

### Option 1: Claude Code with Plugin (Recommended)

**Best for:** Interactive documentation workflows with specialized agents and quick commands.

**Installation:**

```bash
# Add the marketplace
/plugin marketplace add ari1110/doc-manager-mcp

# Install the plugin (automatically configures MCP server)
/plugin install doc-manager@doc-manager-suite
```

**What you get:**
- `@doc-expert` and `@doc-writer` agents
- `/doc-status`, `/doc-sync`, `/doc-quality` commands
- Automatic MCP server configuration

See the [Claude Code Plugin guide](../guides/claude-code-plugin.md) for usage examples.

---

### Option 2: Standalone MCP Server

**Best for:** Using the MCP server without the plugin (Claude Desktop, Claude Code, or other MCP clients).

**Claude Code:**

```bash
claude mcp add doc-manager --scope project -- uvx doc-manager-mcp
```

Your AI assistant can then use the 8 doc-manager tools directly.

**Claude Desktop:**

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "doc-manager": {
      "command": "uvx",
      "args": ["doc-manager-mcp"]
    }
  }
}
```

Restart Claude Desktop to load the server.

---

## Alternative installation methods

### Local development

For contributing or testing local changes:

```json
{
  "mcpServers": {
    "doc-manager": {
      "command": "uvx",
      "args": ["--from", "/path/to/doc-manager-mcp", "doc-manager-mcp"]
    }
  }
}
```

### Standalone installation (advanced)

If you need to install the package directly (not common for MCP usage):

```bash
# With pip
pip install doc-manager-mcp

# From source
git clone https://github.com/ari1110/doc-manager-mcp
cd doc-manager-mcp
pip install -e .
```

## Verification

Verify the installation by checking the tools are available in your MCP client. You should see 8 tools:

- `docmgr_init`
- `docmgr_detect_changes`
- `docmgr_detect_platform`
- `docmgr_validate_docs`
- `docmgr_assess_quality`
- `docmgr_update_baseline`
- `docmgr_sync`
- `docmgr_migrate`

## Troubleshooting

Having installation issues? See the [Troubleshooting guide](../guides/troubleshooting.md#installation-issues) for solutions to TreeSitter availability, permission errors, import errors, and Python version compatibility.
