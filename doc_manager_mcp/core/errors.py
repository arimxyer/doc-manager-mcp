"""Error handling utilities.

This module provides consistent error formatting and logging utilities
with path sanitization for security.
"""


def handle_error(e: Exception, context: str = "", log_to_stderr: bool = True) -> str:
    """Consistent error formatting across all tools.

    Args:
        e: Exception that occurred
        context: Context where error occurred (e.g., tool name, operation)
        log_to_stderr: Whether to log error to stderr (default: True per FR-015)

    Returns:
        Formatted error message string (sanitized per FR-017)
    """
    import re
    import sys
    from datetime import datetime

    # Format error message without sensitive paths (FR-017)
    error_msg = f"Error: {type(e).__name__}"
    if context:
        error_msg += f" in {context}"

    # Sanitize error message - remove full paths
    error_str = str(e)
    # Remove Windows paths (C:\..., R:\...)
    error_str = re.sub(r'[A-Z]:\\[^\s]+', '[path]', error_str)
    # Remove Unix paths (/home/..., /usr/...)
    error_str = re.sub(r'/[\w/]+/[\w/]+', '[path]', error_str)

    error_msg += f": {error_str}"

    # Log to stderr (FR-015: errors must be logged, not silent)
    if log_to_stderr:
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] {error_msg}", file=sys.stderr)

    return error_msg
