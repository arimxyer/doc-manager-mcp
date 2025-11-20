"""Response formatting and size enforcement utilities.

This module provides utilities for enforcing response size limits and
safe JSON serialization to comply with MCP protocol constraints.
"""

from typing import Any, overload


@overload
def enforce_response_limit(response: dict[str, Any], limit: int = 25000) -> dict[str, Any]: ...

@overload
def enforce_response_limit(response: str, limit: int = 25000) -> str: ...

def enforce_response_limit(response: str | dict, limit: int = 25000) -> str | dict[str, Any]:
    """Truncate response if exceeds CHARACTER_LIMIT.

    Args:
        response: Response string or dict to check
        limit: Character limit (default: 25,000 per constants.py)

    Returns:
        Response truncated if necessary (str) or dict as-is

    Note:
        MCP protocol has response size limits. Large dependency graphs
        or validation reports can exceed limits.

        Dicts are passed through unchanged - FastMCP handles JSON serialization
        and size limits. Only strings (markdown) need truncation.
    """
    # If dict, return as-is (FastMCP will serialize it)
    if isinstance(response, dict):
        return response

    # String handling (existing logic)
    if len(response) <= limit:
        return response

    # Leave room for truncation marker (126 characters total)
    truncation_message = (
        "\n\n[Response truncated - exceeded 25,000 character limit]"
        "\n[Tip: Request specific sections or use filters to reduce output size]"
    )
    truncated = response[:limit - len(truncation_message)]
    truncated += truncation_message

    return truncated


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Safely serialize object to JSON with error handling (T050 - FR-012).

    Args:
        obj: Object to serialize
        **kwargs: Additional arguments to pass to json.dumps (e.g., indent=2)

    Returns:
        JSON string or error message if serialization fails

    Note:
        Prevents crashes from unserializable objects (e.g., datetime, Path, custom classes).
        Returns a structured error message that's still valid for MCP responses.
    """
    import json

    try:
        return json.dumps(obj, **kwargs)
    except (TypeError, ValueError) as e:
        # JSON serialization failed - return error as JSON
        error_response = {
            "status": "error",
            "message": "JSON serialization error",
            "error": str(e),
            "type": type(e).__name__
        }
        try:
            return json.dumps(error_response, indent=2)
        except Exception:
            # Fallback if even error serialization fails
            return '{"status": "error", "message": "Critical JSON serialization failure"}'
