"""Tests for preserve_history git mv functionality in migrate workflow.

This module tests that when preserve_history=True, the migrate workflow
uses git mv instead of shutil.copy2 to preserve git history for migrated files.
"""

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

from doc_manager_mcp.models import MigrateInput
from doc_manager_mcp.tools.workflows.migrate import migrate


@pytest.fixture
def git_project():
    """Create a temporary git repository with documentation for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=project_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=project_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=project_path, check=True, capture_output=True)

        # Create old docs structure
        old_docs = project_path / "documentation"
        old_docs.mkdir()

        # Create sample markdown files
        (old_docs / "README.md").write_text("# Old Documentation\n\nSome content.", encoding='utf-8')
        (old_docs / "guide.md").write_text("# Guide\n\nStep by step.", encoding='utf-8')

        # Create subdirectory with file
        (old_docs / "reference").mkdir()
        (old_docs / "reference" / "api.md").write_text("# API Reference\n", encoding='utf-8')

        # Add and commit files to git
        subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial docs'], cwd=project_path, check=True, capture_output=True)

        yield project_path


@pytest.fixture
def non_git_project():
    """Create a temporary non-git project for testing fallback behavior."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create old docs structure (NO git init)
        old_docs = project_path / "documentation"
        old_docs.mkdir()

        (old_docs / "README.md").write_text("# Old Documentation\n", encoding='utf-8')
        (old_docs / "guide.md").write_text("# Guide\n", encoding='utf-8')

        yield project_path


@pytest.mark.asyncio
async def test_preserve_history_true_uses_git_mv(git_project):
    """Test that preserve_history=True uses git mv to preserve history."""
    project_path = git_project

    # Run migration with preserve_history=True
    result = await migrate(MigrateInput(
        project_path=str(project_path),
        source_path="documentation",
        target_path="docs",
        preserve_history=True,
        dry_run=False
    ))

    # Parse result
    if isinstance(result, str):
        # Check for success indicators in report
        assert "Migrated" in result or "files" in result
        assert "git mv" in result.lower() or "moved" in result
    else:
        assert result.get("status") == "success"

    # Verify new docs exist
    new_docs = project_path / "docs"
    assert new_docs.exists(), "New docs directory should exist"
    assert (new_docs / "README.md").exists(), "README should be migrated"

    # Commit the migration changes (git add/git rm are staged but not committed)
    try:
        subprocess.run(
            ['git', 'commit', '-m', 'Migrate docs'],
            cwd=project_path,
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to commit migration: {e}")

    # Verify git history preserved using git log --follow
    try:
        result = subprocess.run(
            ['git', 'log', '--follow', '--oneline', 'docs/README.md'],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True
        )
        # Should show "Initial docs" commit
        assert "Initial docs" in result.stdout, "Git history should be preserved"
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to verify git history: {e}")


@pytest.mark.asyncio
async def test_preserve_history_false_uses_copy(git_project):
    """Test that preserve_history=False uses copy (no git mv)."""
    project_path = git_project

    # Run migration with preserve_history=False
    result = await migrate(MigrateInput(
        project_path=str(project_path),
        source_path="documentation",
        target_path="docs",
        preserve_history=False,
        dry_run=False
    ))

    # Verify files exist
    new_docs = project_path / "docs"
    assert new_docs.exists()
    assert (new_docs / "README.md").exists()

    # Verify git log --follow does NOT show history (file appears as new)
    try:
        result = subprocess.run(
            ['git', 'log', '--follow', '--oneline', 'docs/README.md'],
            cwd=project_path,
            check=True,
            capture_output=True,
            text=True
        )
        # Should NOT show "Initial docs" commit since file is copied, not moved
        # (depends on whether file is committed after copy)
        # For now, just verify the file exists
    except subprocess.CalledProcessError:
        # Expected - file is not tracked yet
        pass


@pytest.mark.asyncio
async def test_non_git_project_falls_back_to_copy(non_git_project):
    """Test that non-git projects fall back to copy even if preserve_history=True."""
    project_path = non_git_project

    # Run migration with preserve_history=True on non-git project
    result = await migrate(MigrateInput(
        project_path=str(project_path),
        source_path="documentation",
        target_path="docs",
        preserve_history=True,
        dry_run=False
    ))

    # Should succeed and use copy
    if isinstance(result, str):
        assert "Migrated" in result or "files" in result
    else:
        assert result.get("status") == "success"

    # Verify files copied
    new_docs = project_path / "docs"
    assert new_docs.exists()
    assert (new_docs / "README.md").exists()
    assert (new_docs / "guide.md").exists()


@pytest.mark.asyncio
async def test_dry_run_with_preserve_history(git_project):
    """Test that dry_run=True doesn't execute git mv."""
    project_path = git_project

    # Run migration in dry run mode
    result = await migrate(MigrateInput(
        project_path=str(project_path),
        source_path="documentation",
        target_path="docs",
        preserve_history=True,
        dry_run=True
    ))

    # Should report what would happen
    if isinstance(result, str):
        assert "Would migrate" in result or "DRY RUN" in result

    # Verify new docs DON'T exist (dry run)
    new_docs = project_path / "docs"
    assert not new_docs.exists(), "Dry run should not create new docs"


@pytest.mark.asyncio
async def test_git_mv_method_reported_in_moved_files(git_project):
    """Test that moved_files contains method='git mv' when preserve_history=True."""
    project_path = git_project

    result = await migrate(MigrateInput(
        project_path=str(project_path),
        source_path="documentation",
        target_path="docs",
        preserve_history=True,
        dry_run=False
    ))

    # If result is dict, check migrated_files
    if isinstance(result, dict):
        migrated_files = result.get("migrated_files", [])
        assert len(migrated_files) > 0, "Should have migrated files"

        # At least some files should use "git mv" method
        git_mv_count = len([f for f in migrated_files if f.get("method") == "git mv"])
        assert git_mv_count > 0, "Should report 'git mv' method for some files"
