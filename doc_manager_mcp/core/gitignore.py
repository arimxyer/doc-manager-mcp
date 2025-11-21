"""Gitignore parsing utilities for doc-manager.

Provides integration with .gitignore files to automatically exclude files
based on project's git ignore patterns.
"""

from pathlib import Path

import pathspec


def parse_gitignore(project_path: Path) -> pathspec.PathSpec:
    """Parse .gitignore file from project root.

    Args:
        project_path: Root directory of the project

    Returns:
        PathSpec object for matching files against gitignore patterns.
        Returns empty PathSpec if .gitignore doesn't exist.

    Example:
        >>> spec = parse_gitignore(Path('/my/project'))
        >>> spec.match_file('node_modules/package.json')
        True
        >>> spec.match_file('src/main.py')
        False
    """
    gitignore_path = project_path / ".gitignore"

    if not gitignore_path.exists():
        # Return empty pathspec if no .gitignore file
        return pathspec.PathSpec.from_lines("gitwildmatch", [])

    try:
        with open(gitignore_path, encoding="utf-8") as f:
            patterns = f.read().splitlines()

        # Use gitwildmatch pattern style (git's native pattern matching)
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    except Exception as e:
        # If we can't read the file, return empty pathspec
        import sys
        print(f"Warning: Failed to parse .gitignore: {e}", file=sys.stderr)
        return pathspec.PathSpec.from_lines("gitwildmatch", [])


def get_gitignore_patterns(project_path: Path) -> list[str]:
    """Get list of patterns from .gitignore file.

    This is primarily for debugging/documentation purposes.
    For actual matching, use parse_gitignore() directly.

    Args:
        project_path: Root directory of the project

    Returns:
        List of non-empty, non-comment lines from .gitignore

    Example:
        >>> patterns = get_gitignore_patterns(Path('/my/project'))
        >>> patterns
        ['node_modules/', '*.log', 'dist/']
    """
    gitignore_path = project_path / ".gitignore"

    if not gitignore_path.exists():
        return []

    try:
        with open(gitignore_path, encoding="utf-8") as f:
            lines = f.read().splitlines()

        # Filter out comments and empty lines
        patterns = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                patterns.append(line)

        return patterns

    except Exception:
        return []
