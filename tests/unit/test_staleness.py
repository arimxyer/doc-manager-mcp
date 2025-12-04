"""Tests for staleness detection functionality."""

from datetime import datetime, timedelta, timezone

import pytest

from doc_manager_mcp.core.staleness import (
    StalenessLevel,
    check_branch_mismatch,
    check_staleness,
    format_staleness_warnings,
)


class TestCheckStaleness:
    """Tests for check_staleness function."""

    def test_fresh_baseline(self):
        """Baseline < 7 days old is fresh."""
        # 3 days ago
        timestamp = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        result = check_staleness(timestamp)

        assert result.level == StalenessLevel.FRESH
        assert result.days_old == 3
        assert result.message is None

    def test_stale_baseline(self):
        """Baseline 7-30 days old is stale."""
        # 15 days ago
        timestamp = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        result = check_staleness(timestamp)

        assert result.level == StalenessLevel.STALE
        assert result.days_old == 15
        assert "15 days old" in result.message
        assert "docmgr_update_baseline" in result.message

    def test_very_stale_baseline(self):
        """Baseline 30-90 days old is very stale."""
        # 45 days ago
        timestamp = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
        result = check_staleness(timestamp)

        assert result.level == StalenessLevel.VERY_STALE
        assert result.days_old == 45
        assert "45 days old" in result.message
        assert "significantly outdated" in result.message

    def test_critical_baseline(self):
        """Baseline > 90 days old is critical."""
        # 120 days ago
        timestamp = (datetime.now(timezone.utc) - timedelta(days=120)).isoformat()
        result = check_staleness(timestamp)

        assert result.level == StalenessLevel.CRITICAL
        assert result.days_old == 120
        assert "120 days old" in result.message
        assert "unreliable" in result.message

    def test_none_timestamp(self):
        """None timestamp returns critical with error message."""
        result = check_staleness(None)

        assert result.level == StalenessLevel.CRITICAL
        assert result.days_old == -1
        assert "No timestamp found" in result.message

    def test_invalid_timestamp_format(self):
        """Invalid timestamp returns critical with error message."""
        result = check_staleness("not-a-timestamp")

        assert result.level == StalenessLevel.CRITICAL
        assert result.days_old == -1
        assert "Invalid timestamp format" in result.message

    def test_empty_string_timestamp(self):
        """Empty string timestamp returns critical."""
        result = check_staleness("")

        assert result.level == StalenessLevel.CRITICAL
        assert result.days_old == -1

    def test_z_suffix_timezone(self):
        """Handles Z suffix for UTC timezone."""
        timestamp = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat().replace("+00:00", "Z")
        result = check_staleness(timestamp)

        assert result.level == StalenessLevel.FRESH
        assert result.days_old == 2

    def test_no_timezone_assumes_utc(self):
        """Timestamp without timezone is treated as UTC."""
        # Create a naive timestamp (no timezone info)
        timestamp = (datetime.now() - timedelta(days=5)).isoformat()
        result = check_staleness(timestamp)

        assert result.level == StalenessLevel.FRESH
        # Allow some tolerance for timezone differences
        assert 4 <= result.days_old <= 6


class TestCheckBranchMismatch:
    """Tests for check_branch_mismatch function."""

    def test_matching_branches(self):
        """Same branch returns None (no warning)."""
        result = check_branch_mismatch("main", "main")
        assert result is None

    def test_different_branches(self):
        """Different branches return warning message."""
        result = check_branch_mismatch("main", "feature/new")

        assert result is not None
        assert "feature/new" in result
        assert "main" in result
        assert "differs" in result

    def test_none_baseline_branch(self):
        """None baseline branch returns None."""
        result = check_branch_mismatch(None, "main")
        assert result is None

    def test_none_current_branch(self):
        """None current branch returns None."""
        result = check_branch_mismatch("main", None)
        assert result is None

    def test_both_none(self):
        """Both None returns None."""
        result = check_branch_mismatch(None, None)
        assert result is None


class TestFormatStalenessWarnings:
    """Tests for format_staleness_warnings function."""

    def test_no_warnings(self):
        """No staleness issues returns empty list."""
        result = format_staleness_warnings()
        assert result == []

    def test_fresh_no_warnings(self):
        """Fresh baseline doesn't generate warnings."""
        fresh_result = check_staleness(
            (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        )
        result = format_staleness_warnings(repo_staleness=fresh_result)
        assert result == []

    def test_stale_repo_warning(self):
        """Stale repo baseline generates warning."""
        stale_result = check_staleness(
            (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
        )
        result = format_staleness_warnings(repo_staleness=stale_result)

        assert len(result) == 1
        assert result[0]["type"] == "staleness"
        assert result[0]["baseline"] == "repo-baseline.json"
        assert result[0]["level"] == "stale"
        assert result[0]["days_old"] == 15

    def test_multiple_warnings(self):
        """Multiple stale baselines generate multiple warnings."""
        repo_stale = check_staleness(
            (datetime.now(timezone.utc) - timedelta(days=20)).isoformat()
        )
        symbol_stale = check_staleness(
            (datetime.now(timezone.utc) - timedelta(days=50)).isoformat()
        )

        result = format_staleness_warnings(
            repo_staleness=repo_stale,
            symbol_staleness=symbol_stale
        )

        assert len(result) == 2
        baselines = [w["baseline"] for w in result]
        assert "repo-baseline.json" in baselines
        assert "symbol-baseline.json" in baselines

    def test_branch_mismatch_warning(self):
        """Branch mismatch generates warning."""
        branch_warning = check_branch_mismatch("main", "develop")
        result = format_staleness_warnings(branch_warning=branch_warning)

        assert len(result) == 1
        assert result[0]["type"] == "branch_mismatch"
        assert "develop" in result[0]["message"]

    def test_combined_staleness_and_branch_warnings(self):
        """Both staleness and branch mismatch warnings."""
        stale_result = check_staleness(
            (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        )
        branch_warning = check_branch_mismatch("main", "feature")

        result = format_staleness_warnings(
            repo_staleness=stale_result,
            branch_warning=branch_warning
        )

        assert len(result) == 2
        types = [w["type"] for w in result]
        assert "staleness" in types
        assert "branch_mismatch" in types
