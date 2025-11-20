"""Integration tests for error handling and propagation."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from doc_manager_mcp.models import DocmgrInitInput
from doc_manager_mcp.tools.state.init import docmgr_init


@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create minimal project structure
        (project_path / "src").mkdir()
        (project_path / "src" / "main.py").write_text("def hello(): pass\n")

        # Initialize git repo (required for some operations)
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


@pytest.mark.asyncio
async def test_init_fails_when_memory_init_fails(temp_project):
    """Test that docmgr_init propagates memory initialization errors."""

    # Create docs first
    docs_path = temp_project / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test Docs\n")

    # Mock initialize_memory to fail
    mock_memory_fail = AsyncMock(return_value={
        "status": "error",
        "message": "Baseline creation failed: Permission denied"
    })

    with patch("doc_manager_mcp.tools.state.init.initialize_memory", mock_memory_fail):
        result = await docmgr_init(DocmgrInitInput(
            project_path=str(temp_project),
            mode="existing",
            docs_path="docs"
        ))

    assert result["status"] == "error"
    assert "Baseline creation failed" in result["message"]
    assert "Permission denied" in result["message"]


@pytest.mark.asyncio
async def test_init_fails_when_deps_tracking_fails(temp_project):
    """Test that docmgr_init propagates dependency tracking errors."""

    # Create docs first
    docs_path = temp_project / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test Docs\n")

    # Mock track_dependencies to fail
    mock_deps_fail = AsyncMock(return_value={
        "status": "error",
        "message": "Dependency tracking failed: Invalid docs path"
    })

    with patch("doc_manager_mcp.tools.state.init.track_dependencies", mock_deps_fail):
        result = await docmgr_init(DocmgrInitInput(
            project_path=str(temp_project),
            mode="existing",
            docs_path="docs"
        ))

    assert result["status"] == "error"
    assert "Dependency tracking failed" in result["message"]
    assert "Invalid docs path" in result["message"]


@pytest.mark.asyncio
async def test_bootstrap_fails_when_deps_tracking_fails(temp_project):
    """Test that docmgr_init bootstrap mode propagates dependency tracking errors."""

    # Mock track_dependencies to fail in bootstrap mode
    mock_deps_fail = AsyncMock(return_value={
        "status": "error",
        "message": "Dependency tracking failed: No markdown files found"
    })

    with patch("doc_manager_mcp.tools.state.init.track_dependencies", mock_deps_fail):
        result = await docmgr_init(DocmgrInitInput(
            project_path=str(temp_project),
            mode="bootstrap",
            docs_path="docs"
        ))

    assert result["status"] == "error"
    assert "Dependency tracking failed" in result["message"]
    assert "No markdown files found" in result["message"]


@pytest.mark.asyncio
async def test_init_succeeds_when_all_sub_tools_succeed(temp_project):
    """Test that docmgr_init succeeds when all sub-tools succeed."""

    # Create docs first
    docs_path = temp_project / "docs"
    docs_path.mkdir()
    (docs_path / "README.md").write_text("# Test Docs\n")

    # Run with real implementations (should succeed)
    result = await docmgr_init(DocmgrInitInput(
        project_path=str(temp_project),
        mode="existing",
        docs_path="docs"
    ))

    assert result["status"] == "success"
    assert result["mode"] == "existing"
    assert "steps_completed" in result
    # All steps should be marked as created or completed
    assert result["steps_completed"]["config"] in ["created", "completed"]
    assert result["steps_completed"]["memory"] in ["created", "completed"]
    assert result["steps_completed"]["dependencies"] in ["created", "completed"]
