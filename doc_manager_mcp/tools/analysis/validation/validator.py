"""Documentation validation tools for doc-manager."""

import asyncio
from pathlib import Path
from typing import Any

from doc_manager_mcp.core import (
    enforce_response_limit,
    find_docs_directory,
    handle_error,
    load_config,
    load_conventions,
    safe_resolve,
)
from doc_manager_mcp.core.markdown_cache import MarkdownCache
from doc_manager_mcp.models import ValidateDocsInput

from .assets import validate_assets
from .conventions import validate_conventions
from .links import check_broken_links
from .snippets import validate_code_snippets
from .symbols import validate_symbols
from .syntax import validate_code_syntax


def _format_validation_report(issues: list[dict[str, Any]]) -> dict[str, Any]:
    """Format validation report as structured data."""
    return {
        "total_issues": len(issues),
        "errors": len([i for i in issues if i['severity'] == 'error']),
        "warnings": len([i for i in issues if i['severity'] == 'warning']),
        "issues": issues
    }


async def validate_docs(params: ValidateDocsInput) -> str | dict[str, Any]:
    """Validate documentation for broken links, missing assets, and code snippet issues.

    This tool performs comprehensive validation:
    1. Broken Links - Checks internal markdown and HTML links
    2. Asset Validation - Verifies images exist and have alt text
    3. Code Snippet Validation - Basic syntax checking for code blocks
    4. Code Syntax Validation - TreeSitter-based semantic validation (optional)
    5. Symbol Validation - Verify documented symbols exist in codebase (optional)

    Args:
        params (ValidateDocsInput): Validated input parameters containing:
            - project_path (str): Absolute path to project root
            - docs_path (Optional[str]): Relative path to docs directory
            - check_links (bool): Enable link validation (default: True)
            - check_assets (bool): Enable asset validation (default: True)
            - check_snippets (bool): Enable code snippet validation (default: True)
            - validate_code_syntax (bool): Enable TreeSitter syntax validation (default: False)
            - validate_symbols (bool): Validate documented symbols exist (default: False)
            - response_format (ResponseFormat): Output format (markdown or json)

    Returns:
        str: Validation report with all issues found

    Examples:
        - Use when: Preparing documentation for release
        - Use when: After making significant doc changes
        - Use when: Running CI/CD validation checks

    Error Handling:
        - Returns error if project_path doesn't exist
        - Returns error if docs_path specified but not found
        - Skips individual files that can't be read
    """
    try:
        project_path = safe_resolve(Path(params.project_path))

        if not project_path.exists():
            return enforce_response_limit(f"Error: Project path does not exist: {project_path}")

        # Determine docs directory
        if params.docs_path:
            docs_path = project_path / params.docs_path
            if not docs_path.exists():
                return enforce_response_limit(f"Error: Documentation path does not exist: {docs_path}")
        else:
            docs_path = find_docs_directory(project_path)
            if not docs_path:
                return enforce_response_limit("Error: Could not find documentation directory. Please specify docs_path parameter.")

        if not docs_path.is_dir():
            return enforce_response_limit(f"Error: Documentation path is not a directory: {docs_path}")

        # Load config and conventions
        config = load_config(project_path)
        include_root_readme = config.get('include_root_readme', False) if config else False
        conventions = load_conventions(project_path)

        # Create markdown cache for performance (eliminates redundant parsing)
        markdown_cache = MarkdownCache()

        # Run validation checks in parallel (2-3x faster)
        validators = []

        # Check convention compliance if conventions exist
        if conventions:
            validators.append(
                asyncio.to_thread(validate_conventions, docs_path, project_path, conventions, include_root_readme)
            )

        if params.check_links:
            validators.append(
                asyncio.to_thread(check_broken_links, docs_path, project_path, include_root_readme, markdown_cache)
            )

        if params.check_assets:
            validators.append(
                asyncio.to_thread(validate_assets, docs_path, project_path, include_root_readme, markdown_cache)
            )

        if params.check_snippets:
            validators.append(
                asyncio.to_thread(validate_code_snippets, docs_path, project_path, include_root_readme, markdown_cache)
            )

        if params.validate_code_syntax:
            validators.append(
                asyncio.to_thread(validate_code_syntax, docs_path, project_path, include_root_readme)
            )

        if params.validate_symbols:
            validators.append(
                asyncio.to_thread(validate_symbols, docs_path, project_path, include_root_readme)
            )

        # Run all validators concurrently
        results = await asyncio.gather(*validators) if validators else []

        # Aggregate all issues
        all_issues = []
        for issues in results:
            all_issues.extend(issues)

        return enforce_response_limit(_format_validation_report(all_issues))

    except Exception as e:
        return enforce_response_limit(handle_error(e, "validate_docs"))
