#!/usr/bin/env python3
"""
check-doc-health.py
Silent documentation health check for session start.
Only outputs if significant drift detected (10+ files changed or 7+ days).
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def get_baseline_mtime(baseline_file: Path) -> float | None:
    """Get the modification time of the baseline file."""
    try:
        return baseline_file.stat().st_mtime
    except OSError:
        return None


def get_changed_files_count(project_dir: Path, baseline_mtime: float) -> int:
    """Count unique files changed since baseline using git."""
    git_dir = project_dir / ".git"
    if not git_dir.is_dir():
        return 0

    # Format baseline date for git
    baseline_date = datetime.fromtimestamp(baseline_mtime).strftime("%Y-%m-%d %H:%M:%S")

    changed_files: set[str] = set()

    try:
        # Files changed in commits since baseline
        result = subprocess.run(
            ["git", "log", f"--since={baseline_date}", "--name-only", "--pretty=format:"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.strip():
                    changed_files.add(line.strip())

        # Uncommitted staged changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.strip():
                    changed_files.add(line.strip())

        # Uncommitted unstaged changes
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.strip():
                    changed_files.add(line.strip())

    except (subprocess.SubprocessError, OSError):
        return 0

    return len(changed_files)


def main() -> None:
    """Main entry point for documentation health check."""
    # Get project directory
    project_dir = Path(os.environ.get("PWD", os.getcwd()))
    doc_manager_dir = project_dir / ".doc-manager"
    baseline_file = doc_manager_dir / "memory" / "repo-baseline.json"

    # Check if doc-manager is initialized
    if not doc_manager_dir.is_dir():
        sys.exit(0)

    # Check if baseline exists
    if not baseline_file.is_file():
        sys.exit(0)

    # Get baseline timestamp
    baseline_mtime = get_baseline_mtime(baseline_file)
    if baseline_mtime is None:
        sys.exit(0)

    # Calculate days since last sync
    current_time = time.time()
    days_since_sync = int((current_time - baseline_mtime) / 86400)

    # Count changed files since baseline
    changed_count = get_changed_files_count(project_dir, baseline_mtime)

    # Silent check - only output if significant drift (10+ files OR 7+ days)
    if changed_count >= 10 or days_since_sync >= 7:
        context_msg = (
            f"Documentation drift detected: {changed_count} files changed "
            f"since last sync ({days_since_sync} days ago). "
            f"Run /doc-status to check sync status."
        )

        # Output compact JSON to stdout (Claude Code SessionStart hook format)
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context_msg,
            }
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
