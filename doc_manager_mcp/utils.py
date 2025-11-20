"""Utility functions for doc-manager MCP server.

DEPRECATED: This module is kept for backward compatibility.
New code should import from doc_manager_mcp.core submodules directly:

- from doc_manager_mcp.core.checksums import calculate_checksum
- from doc_manager_mcp.core.git import run_git_command
- from doc_manager_mcp.core.paths import safe_resolve, validate_path_boundary
- from doc_manager_mcp.core.patterns import matches_exclude_pattern
- from doc_manager_mcp.core.project import detect_project_language, find_docs_directory, etc.
- from doc_manager_mcp.core.config import load_config, save_config
- from doc_manager_mcp.core.errors import handle_error
- from doc_manager_mcp.core.resources import ResourceLimits, operation_timeout
- from doc_manager_mcp.core.responses import enforce_response_limit, safe_json_dumps
- from doc_manager_mcp.core.security import file_lock

Or import from doc_manager_mcp.core:
- from doc_manager_mcp.core import calculate_checksum, run_git_command, etc.
"""

# Re-export all functions from core for backward compatibility
from .core import (
    ResourceLimits,
    calculate_checksum,
    detect_platform_quick,
    detect_project_language,
    enforce_response_limit,
    file_lock,
    find_docs_directory,
    find_markdown_files,
    handle_error,
    is_public_symbol,
    load_config,
    matches_exclude_pattern,
    operation_timeout,
    run_git_command,
    safe_json_dumps,
    safe_resolve,
    save_config,
    validate_path_boundary,
)

__all__ = [
    "ResourceLimits",
    "calculate_checksum",
    "detect_platform_quick",
    "detect_project_language",
    "enforce_response_limit",
    "file_lock",
    "find_docs_directory",
    "find_markdown_files",
    "handle_error",
    "is_public_symbol",
    "load_config",
    "matches_exclude_pattern",
    "operation_timeout",
    "run_git_command",
    "safe_json_dumps",
    "safe_resolve",
    "save_config",
    "validate_path_boundary",
]
