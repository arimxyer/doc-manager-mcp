"""Staleness detection for doc-manager baselines.

Provides utilities for detecting when baseline files are outdated
and may need to be refreshed to ensure accurate change detection.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import NamedTuple


class StalenessLevel(Enum):
    """Staleness severity levels for baseline files."""

    FRESH = "fresh"
    STALE = "stale"
    VERY_STALE = "very_stale"
    CRITICAL = "critical"


class StalenessResult(NamedTuple):
    """Result of a staleness check.

    Attributes:
        level: Staleness severity level
        days_old: Number of days since baseline was updated (-1 if unknown)
        message: Optional warning message for user display
    """

    level: StalenessLevel
    days_old: int
    message: str | None


# Threshold days for each staleness level
THRESHOLDS = {
    StalenessLevel.FRESH: 7,
    StalenessLevel.STALE: 30,
    StalenessLevel.VERY_STALE: 90,
}


def check_staleness(timestamp_str: str | None) -> StalenessResult:
    """Check staleness of a baseline timestamp.

    Args:
        timestamp_str: ISO 8601 timestamp string (e.g., "2024-01-15T10:30:00")

    Returns:
        StalenessResult with level, days_old, and optional warning message

    Examples:
        >>> result = check_staleness("2024-01-01T00:00:00")
        >>> result.level
        <StalenessLevel.FRESH: 'fresh'>  # if within 7 days

        >>> result = check_staleness(None)
        >>> result.level
        <StalenessLevel.CRITICAL: 'critical'>
    """
    if not timestamp_str:
        return StalenessResult(
            StalenessLevel.CRITICAL,
            -1,
            "No timestamp found - baseline may be corrupted or missing",
        )

    try:
        # Handle various ISO 8601 formats
        timestamp_str_normalized = timestamp_str.replace("Z", "+00:00")

        # Try parsing with timezone
        try:
            timestamp = datetime.fromisoformat(timestamp_str_normalized)
        except ValueError:
            # Try without timezone (assume UTC)
            timestamp = datetime.fromisoformat(timestamp_str).replace(
                tzinfo=timezone.utc
            )

        # Ensure timestamp has timezone for comparison
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        delta = now - timestamp
        days_old = delta.days

        if days_old < THRESHOLDS[StalenessLevel.FRESH]:
            return StalenessResult(StalenessLevel.FRESH, days_old, None)
        elif days_old < THRESHOLDS[StalenessLevel.STALE]:
            return StalenessResult(
                StalenessLevel.STALE,
                days_old,
                f"Baseline is {days_old} days old. Consider running docmgr_update_baseline.",
            )
        elif days_old < THRESHOLDS[StalenessLevel.VERY_STALE]:
            return StalenessResult(
                StalenessLevel.VERY_STALE,
                days_old,
                f"Baseline is {days_old} days old and may be significantly outdated.",
            )
        else:
            return StalenessResult(
                StalenessLevel.CRITICAL,
                days_old,
                f"Baseline is {days_old} days old. Results may be unreliable.",
            )
    except (ValueError, TypeError) as e:
        return StalenessResult(
            StalenessLevel.CRITICAL,
            -1,
            f"Invalid timestamp format - baseline may be corrupted: {e}",
        )


def check_branch_mismatch(
    baseline_branch: str | None, current_branch: str | None
) -> str | None:
    """Check if current git branch differs from baseline branch.

    Args:
        baseline_branch: Branch name stored in baseline
        current_branch: Current git branch name

    Returns:
        Warning message if branches differ, None otherwise

    Examples:
        >>> check_branch_mismatch("main", "feature/new")
        "Current branch 'feature/new' differs from baseline branch 'main'. ..."

        >>> check_branch_mismatch("main", "main")
        None
    """
    if not baseline_branch or not current_branch:
        return None

    if baseline_branch != current_branch:
        return (
            f"Current branch '{current_branch}' differs from baseline branch "
            f"'{baseline_branch}'. Change detection may be inaccurate."
        )
    return None


def format_staleness_warnings(
    repo_staleness: StalenessResult | None = None,
    symbol_staleness: StalenessResult | None = None,
    deps_staleness: StalenessResult | None = None,
    branch_warning: str | None = None,
) -> list[dict[str, str | int]]:
    """Format staleness results into structured warnings for tool output.

    Args:
        repo_staleness: Staleness result for repo-baseline.json
        symbol_staleness: Staleness result for symbol-baseline.json
        deps_staleness: Staleness result for dependencies.json
        branch_warning: Optional branch mismatch warning message

    Returns:
        List of warning dictionaries suitable for JSON output
    """
    warnings = []

    if repo_staleness and repo_staleness.message:
        warnings.append({
            "type": "staleness",
            "baseline": "repo-baseline.json",
            "level": repo_staleness.level.value,
            "days_old": repo_staleness.days_old,
            "message": repo_staleness.message,
        })

    if symbol_staleness and symbol_staleness.message:
        warnings.append({
            "type": "staleness",
            "baseline": "symbol-baseline.json",
            "level": symbol_staleness.level.value,
            "days_old": symbol_staleness.days_old,
            "message": symbol_staleness.message,
        })

    if deps_staleness and deps_staleness.message:
        warnings.append({
            "type": "staleness",
            "baseline": "dependencies.json",
            "level": deps_staleness.level.value,
            "days_old": deps_staleness.days_old,
            "message": deps_staleness.message,
        })

    if branch_warning:
        warnings.append({
            "type": "branch_mismatch",
            "message": branch_warning,
        })

    return warnings
