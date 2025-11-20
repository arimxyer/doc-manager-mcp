"""Path validation and resolution utilities.

This module provides secure path handling utilities including symlink resolution,
boundary validation, and path traversal attack prevention.
"""

import os
from pathlib import Path


def safe_resolve(path: Path, max_depth: int | None = None) -> Path:
    """Safely resolve path with recursion depth limit (FR-020).

    Args:
        path: Path to resolve
        max_depth: Maximum symlink resolution depth (default: MAX_RECURSION_DEPTH from constants)

    Returns:
        Resolved path

    Raises:
        RecursionError: If symlink resolution exceeds max_depth

    Note:
        Prevents infinite loops from circular symlinks by limiting resolution depth.
    """
    from ..constants import MAX_RECURSION_DEPTH

    if max_depth is None:
        max_depth = MAX_RECURSION_DEPTH

    # Track symlink resolution depth
    current_path = path
    depth = 0

    while current_path.is_symlink() and depth < max_depth:
        current_path = Path(os.readlink(current_path))
        if not current_path.is_absolute():
            current_path = path.parent / current_path
        depth += 1

    if depth >= max_depth and current_path.is_symlink():
        raise RecursionError(
            f"Symlink resolution exceeded maximum depth ({max_depth})\n"
            f"→ Check for circular symlinks or reduce symlink chain length."
        )

    return current_path.resolve()


def validate_path_boundary(path: Path, project_root: Path) -> Path:
    """Validate path stays within project boundary (prevents path traversal).

    Args:
        path: Path to validate
        project_root: Project root directory (security boundary)

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path escapes project boundary or is a malicious symlink

    Security:
        - Detects and rejects symlinks that escape boundary (FR-003)
        - Prevents path traversal attacks (FR-001)
        - Verifies resolved path stays within boundary (FR-025)
    """
    # Check if it's a symlink before resolution (FR-028)
    if path.is_symlink():
        # Resolve and verify target stays within boundary
        resolved = path.resolve()
        try:
            # Check if resolved path is relative to project root
            resolved.relative_to(project_root.resolve())
        except ValueError as err:
            raise ValueError(f"Symlink escapes project boundary: {path.name} points outside project root") from err
    else:
        # Regular path resolution
        resolved = path.resolve()

    # Verify resolved path is within project boundary (FR-025)
    try:
        resolved.relative_to(project_root.resolve())
    except ValueError as err:
        raise ValueError(f"Path escapes project boundary: {path.name} is outside project root") from err

    return resolved
