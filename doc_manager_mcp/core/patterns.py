"""Pattern matching utilities for file exclusion.

This module provides utilities for matching file paths against glob patterns,
supporting complex patterns like **/ prefixes and /** suffixes.
"""

import fnmatch
from pathlib import Path


def matches_exclude_pattern(path: str, exclude_patterns: list[str]) -> bool:
    """Check if a path matches any of the exclude patterns.

    Args:
        path: Relative path to check (string)
        exclude_patterns: List of glob patterns (e.g., ["**/node_modules", "**/*.log"])

    Returns:
        True if path should be excluded, False otherwise
    """
    # Normalize path separators
    normalized_path = str(Path(path)).replace('\\', '/')

    for pattern in exclude_patterns:
        # Normalize pattern separators
        normalized_pattern = pattern.replace('\\', '/')

        # Handle **/ prefix (matches any depth)
        if normalized_pattern.startswith('**/'):
            pattern_suffix = normalized_pattern[3:]  # Remove **/
            # Check if pattern matches the full path or any part
            if fnmatch.fnmatch(normalized_path, '*/' + pattern_suffix) or \
               fnmatch.fnmatch(normalized_path, pattern_suffix):
                return True
            # Check if any component matches
            parts = normalized_path.split('/')
            for i, _part in enumerate(parts):
                remaining = '/'.join(parts[i:])
                if fnmatch.fnmatch(remaining, pattern_suffix):
                    return True
        # Handle /** suffix (matches directory and contents)
        elif normalized_pattern.endswith('/**'):
            dir_pattern = normalized_pattern[:-3]  # Remove /**
            if normalized_path.startswith(dir_pattern + '/') or normalized_path == dir_pattern:
                return True
        # Regular pattern matching
        else:
            if fnmatch.fnmatch(normalized_path, normalized_pattern):
                return True

    return False
