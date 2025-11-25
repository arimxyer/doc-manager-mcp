"""Tests for shared file scanning logic."""

import tempfile
from pathlib import Path

import pytest

from doc_manager_mcp.core.file_scanner import (
    build_exclude_patterns,
    categorize_file,
    scan_and_categorize,
    scan_project_files,
)


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        # Create various file types
        (project_path / "main.py").write_text("print('hello')")
        (project_path / "app.js").write_text("console.log('test');")
        (project_path / "README.md").write_text("# Test Project")
        (project_path / "config.yml").write_text("key: value")
        (project_path / "logo.png").write_text("fake image")

        # Create hidden files (should be excluded)
        (project_path / ".git").mkdir()
        (project_path / ".git" / "config").write_text("git config")

        # Create subdirectory
        (project_path / "src").mkdir()
        (project_path / "src" / "utils.py").write_text("def helper(): pass")

        # Create docs directory
        (project_path / "docs").mkdir()
        (project_path / "docs" / "guide.md").write_text("# Guide")

        yield project_path


def test_build_exclude_patterns_no_config(temp_project):
    """Test building exclude patterns when no config exists."""
    exclude_patterns, gitignore_spec = build_exclude_patterns(temp_project)

    assert isinstance(exclude_patterns, list)
    assert len(exclude_patterns) > 0  # Should have default patterns
    assert gitignore_spec is None  # No gitignore by default


def test_scan_project_files_basic(temp_project):
    """Test basic file scanning."""
    files = list(scan_project_files(temp_project))

    # Should find files (excluding hidden .git/)
    assert len(files) >= 5  # At least the non-hidden files

    # Files should be Path objects
    assert all(isinstance(f, Path) for f in files)

    # Should not include .git directory files
    git_files = [f for f in files if '.git' in str(f)]
    assert len(git_files) == 0


def test_scan_project_files_with_walk(temp_project):
    """Test file scanning using walk method."""
    files_rglob = list(scan_project_files(temp_project, use_walk=False))
    files_walk = list(scan_project_files(temp_project, use_walk=True))

    # Both methods should find similar files
    assert len(files_walk) >= len(files_rglob) - 2  # Allow small difference


def test_scan_project_files_max_limit(temp_project):
    """Test file count limit enforcement."""
    with pytest.raises(ValueError, match="File count limit exceeded"):
        list(scan_project_files(temp_project, max_files=2))


def test_scan_project_files_respects_exclusions(temp_project):
    """Test that exclusion patterns are respected."""
    exclude_patterns = ["**/*.py"]  # Recursive pattern
    files = list(scan_project_files(
        temp_project,
        exclude_patterns=exclude_patterns,
        gitignore_spec=None
    ))

    # Should not include any .py files
    py_files = [f for f in files if f.suffix == '.py']
    assert len(py_files) == 0


def test_categorize_file_code(temp_project):
    """Test file categorization for code files."""
    assert categorize_file(temp_project / "main.py") == "code"
    assert categorize_file(temp_project / "app.js") == "code"
    assert categorize_file(temp_project / "src" / "utils.py") == "code"


def test_categorize_file_docs(temp_project):
    """Test file categorization for documentation files."""
    assert categorize_file(temp_project / "README.md") == "docs"
    assert categorize_file(temp_project / "docs" / "guide.md") == "docs"


def test_categorize_file_config(temp_project):
    """Test file categorization for config files."""
    assert categorize_file(temp_project / "config.yml") == "config"


def test_categorize_file_assets(temp_project):
    """Test file categorization for asset files."""
    assert categorize_file(temp_project / "logo.png") == "assets"


def test_categorize_file_other(temp_project):
    """Test file categorization for unknown file types."""
    other_file = temp_project / "data.bin"
    other_file.write_text("binary data")
    assert categorize_file(other_file) == "other"


def test_scan_and_categorize(temp_project):
    """Test scanning and categorizing in one operation."""
    categorized = scan_and_categorize(temp_project)

    # Should return dict with all categories
    assert set(categorized.keys()) == {"code", "docs", "config", "assets", "other"}

    # Should have code files
    assert len(categorized["code"]) >= 2  # main.py, app.js, utils.py

    # Should have docs
    assert len(categorized["docs"]) >= 2  # README.md, guide.md

    # Should have config
    assert len(categorized["config"]) >= 1  # config.yml

    # Should have assets
    assert len(categorized["assets"]) >= 1  # logo.png


def test_scan_excludes_hidden_directories(temp_project):
    """Test that hidden directories are excluded."""
    files = list(scan_project_files(temp_project))

    # Should not include any files from .git/
    hidden_files = [f for f in files if any(part.startswith('.') for part in f.parts)]
    assert len(hidden_files) == 0


def test_scan_returns_relative_paths_correctly(temp_project):
    """Test that files can be converted to relative paths."""
    files = list(scan_project_files(temp_project))

    for file_path in files:
        # Should be able to compute relative path
        rel_path = file_path.relative_to(temp_project)
        assert not rel_path.is_absolute()
