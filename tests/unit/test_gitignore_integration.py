"""Unit tests for .gitignore integration feature."""

import tempfile
from pathlib import Path

import pytest

from doc_manager_mcp.core import parse_gitignore, get_gitignore_patterns
from doc_manager_mcp.models import DocmgrInitInput, DocmgrDetectChangesInput
from doc_manager_mcp.tools.state.init import docmgr_init
from doc_manager_mcp.tools.analysis.detect_changes import docmgr_detect_changes


@pytest.fixture
def temp_project_with_gitignore():
    """Create a temporary project with .gitignore file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create .gitignore file
        gitignore_content = """
# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# Node.js
node_modules/
dist/
build/

# IDEs
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
"""
        (project_path / ".gitignore").write_text(gitignore_content)

        # Create project structure
        (project_path / "src").mkdir()
        (project_path / "src" / "main.py").write_text("def hello(): pass\n")

        # Create files that should be excluded by .gitignore
        (project_path / "__pycache__").mkdir()
        (project_path / "__pycache__" / "main.cpython-310.pyc").write_text("bytecode")
        (project_path / "node_modules").mkdir()
        (project_path / "node_modules" / "package.json").write_text("{}")
        (project_path / ".venv").mkdir()
        (project_path / ".venv" / "lib").mkdir()

        # Initialize git repo
        import subprocess
        subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=project_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=project_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "add", "."],
            cwd=project_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=project_path,
            check=True,
            capture_output=True
        )

        yield project_path


def test_parse_gitignore():
    """Test that parse_gitignore correctly parses .gitignore file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create .gitignore
        gitignore_content = """
# Comment
*.pyc
__pycache__/
node_modules/
"""
        (project_path / ".gitignore").write_text(gitignore_content)

        # Parse
        spec = parse_gitignore(project_path)

        # Test matching
        assert spec.match_file("test.pyc")
        assert spec.match_file("__pycache__/main.pyc")
        assert spec.match_file("node_modules/package.json")
        assert not spec.match_file("test.py")


def test_parse_gitignore_missing_file():
    """Test that parse_gitignore handles missing .gitignore gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Parse without .gitignore
        spec = parse_gitignore(project_path)

        # Should return empty spec that matches nothing
        assert not spec.match_file("test.pyc")
        assert not spec.match_file("anything")


def test_get_gitignore_patterns():
    """Test that get_gitignore_patterns returns list of patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create .gitignore
        gitignore_content = """
# Comment line
*.pyc

__pycache__/
node_modules/
"""
        (project_path / ".gitignore").write_text(gitignore_content)

        # Get patterns
        patterns = get_gitignore_patterns(project_path)

        # Should filter out comments and empty lines
        assert "*.pyc" in patterns
        assert "__pycache__/" in patterns
        assert "node_modules/" in patterns
        assert len(patterns) == 3  # Only non-comment, non-empty lines


@pytest.mark.asyncio
async def test_init_with_gitignore_disabled(temp_project_with_gitignore):
    """Test that use_gitignore=false doesn't apply .gitignore patterns."""
    project_path = temp_project_with_gitignore

    # Create docs
    docs_path = project_path / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test\n")

    # Initialize with use_gitignore=false (default)
    params = DocmgrInitInput(
        project_path=str(project_path),
        mode="existing",
        docs_path="docs",
        use_gitignore=False
    )

    result = await docmgr_init(params)

    assert result["status"] == "success"

    # Check repo-baseline.json to see what files were tracked
    import json
    baseline_path = project_path / ".doc-manager" / "memory" / "repo-baseline.json"
    with open(baseline_path) as f:
        baseline = json.load(f)

    # Files in .gitignore should still be tracked when use_gitignore=false
    # (unless they match built-in defaults)
    tracked_files = list(baseline["files"].keys())

    # At minimum, should have tracked src/main.py
    assert any("src/main.py" in f for f in tracked_files)


@pytest.mark.asyncio
async def test_init_with_gitignore_enabled(temp_project_with_gitignore):
    """Test that use_gitignore=true excludes files from .gitignore."""
    project_path = temp_project_with_gitignore

    # Create docs
    docs_path = project_path / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test\n")

    # Initialize with use_gitignore=true
    params = DocmgrInitInput(
        project_path=str(project_path),
        mode="existing",
        docs_path="docs",
        use_gitignore=True
    )

    result = await docmgr_init(params)

    assert result["status"] == "success"

    # Check repo-baseline.json
    import json
    baseline_path = project_path / ".doc-manager" / "memory" / "repo-baseline.json"
    with open(baseline_path) as f:
        baseline = json.load(f)

    tracked_files = list(baseline["files"].keys())

    # Files in .gitignore should NOT be tracked
    assert not any("__pycache__" in f for f in tracked_files)
    assert not any("node_modules" in f for f in tracked_files)
    assert not any(".venv" in f for f in tracked_files)

    # Source files should still be tracked
    assert any("src/main.py" in f for f in tracked_files)


@pytest.mark.asyncio
async def test_user_excludes_override_gitignore(temp_project_with_gitignore):
    """Test that user exclude patterns have highest priority."""
    project_path = temp_project_with_gitignore

    # Create a file that's NOT in .gitignore but we want to exclude
    (project_path / "specs").mkdir()
    (project_path / "specs" / "spec.md").write_text("# Spec\n")

    # Create docs
    docs_path = project_path / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test\n")

    # Initialize with use_gitignore=true AND user excludes
    params = DocmgrInitInput(
        project_path=str(project_path),
        mode="existing",
        docs_path="docs",
        use_gitignore=True,
        exclude_patterns=["specs/**"]
    )

    result = await docmgr_init(params)

    assert result["status"] == "success"

    # Check repo-baseline.json
    import json
    baseline_path = project_path / ".doc-manager" / "memory" / "repo-baseline.json"
    with open(baseline_path) as f:
        baseline = json.load(f)

    tracked_files = list(baseline["files"].keys())

    # specs/ should be excluded (user pattern)
    assert not any("specs/" in f for f in tracked_files)

    # .gitignore patterns should also be applied
    assert not any("__pycache__" in f for f in tracked_files)
    assert not any("node_modules" in f for f in tracked_files)


@pytest.mark.asyncio
async def test_detect_changes_with_gitignore(temp_project_with_gitignore):
    """Test that detect_changes respects use_gitignore setting."""
    project_path = temp_project_with_gitignore

    # Create docs
    docs_path = project_path / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test\n")

    # Initialize with use_gitignore=true
    init_params = DocmgrInitInput(
        project_path=str(project_path),
        mode="existing",
        docs_path="docs",
        use_gitignore=True
    )
    await docmgr_init(init_params)

    # Add a new file in node_modules (should be ignored)
    (project_path / "node_modules" / "new-package.json").write_text("{}")

    # Add a new source file (should be detected)
    (project_path / "src" / "new_module.py").write_text("def new(): pass\n")

    # Detect changes
    detect_params = DocmgrDetectChangesInput(
        project_path=str(project_path),
        mode="checksum",
        include_semantic=False
    )

    result = await docmgr_detect_changes(detect_params)

    assert result["status"] == "success"

    # Check changed files
    changed_files = result["changed_files"]
    changed_paths = [cf["file"] for cf in changed_files]

    # new_module.py should be detected
    assert any("src/new_module.py" in p for p in changed_paths)

    # node_modules file should NOT be detected (excluded by .gitignore)
    assert not any("node_modules/new-package.json" in p for p in changed_paths)


@pytest.mark.asyncio
async def test_config_persists_use_gitignore(temp_project_with_gitignore):
    """Test that use_gitignore setting is persisted in config."""
    project_path = temp_project_with_gitignore

    # Create docs
    docs_path = project_path / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test\n")

    # Initialize with use_gitignore=true
    params = DocmgrInitInput(
        project_path=str(project_path),
        mode="existing",
        docs_path="docs",
        use_gitignore=True
    )

    result = await docmgr_init(params)

    assert result["status"] == "success"

    # Load config and verify use_gitignore is set
    import yaml
    config_path = project_path / ".doc-manager.yml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    assert config["use_gitignore"] is True
