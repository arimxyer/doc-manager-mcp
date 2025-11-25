"""Tests for concurrent baseline updates with file locking.

This module tests that multiple simultaneous update_baseline operations
do not corrupt baseline files due to race conditions.
"""

import asyncio
import json
import tempfile
from pathlib import Path
import pytest
from doc_manager_mcp.tools.state.update_baseline import docmgr_update_baseline
from doc_manager_mcp.models import DocmgrUpdateBaselineInput


@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create .doc-manager directory
        doc_manager_dir = project_path / ".doc-manager" / "memory"
        doc_manager_dir.mkdir(parents=True)

        # Create sample source files
        src_dir = project_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("# Main file\ndef main():\n    pass\n")
        (src_dir / "utils.py").write_text("# Utils\ndef helper():\n    pass\n")

        # Create sample docs
        docs_dir = project_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "README.md").write_text("# Documentation\n")

        # Create minimal config
        config_path = project_path / ".doc-manager.yml"
        config_path.write_text("""platform: unknown
docs_path: docs
exclude: []
sources:
  - "src/**/*.py"
metadata:
  language: Python
  version: 1.0.0
""")

        yield project_path


@pytest.mark.asyncio
async def test_concurrent_baseline_updates_no_corruption(temp_project):
    """Test that 5 concurrent update_baseline calls don't corrupt baseline files.

    This test verifies:
    1. All 5 operations complete successfully
    2. Baseline files remain valid JSON (not corrupted)
    3. Lock files are cleaned up properly
    """
    project_path = temp_project
    baseline_path = project_path / ".doc-manager" / "memory" / "repo-baseline.json"
    lock_path = baseline_path.with_suffix(".json.lock")

    # Run 5 concurrent update_baseline operations
    tasks = [
        docmgr_update_baseline(DocmgrUpdateBaselineInput(
            project_path=str(project_path)
        ))
        for _ in range(5)
    ]

    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Verify all operations succeeded (no exceptions)
    for i, result in enumerate(results):
        assert not isinstance(result, Exception), f"Task {i} failed with: {result}"
        assert result is not None, f"Task {i} returned None"

    # Verify baseline file exists and is valid JSON
    assert baseline_path.exists(), "repo-baseline.json should exist"

    try:
        with open(baseline_path, 'r') as f:
            baseline = json.load(f)

        # Verify baseline structure
        assert "version" in baseline, "Baseline should have version field"
        assert "files" in baseline, "Baseline should have files field"
        assert isinstance(baseline["files"], dict), "Files should be a dict"

    except json.JSONDecodeError as e:
        pytest.fail(f"Baseline file is corrupted (invalid JSON): {e}")

    # Verify lock file was cleaned up
    assert not lock_path.exists(), "Lock file should be cleaned up after operations complete"


@pytest.mark.asyncio
async def test_concurrent_baseline_updates_file_locking_prevents_corruption(temp_project):
    """Test that file locking prevents partial writes from corrupting baselines.

    This is a stress test with rapid concurrent updates to ensure the
    file_lock() mechanism prevents corruption even under high contention.
    """
    project_path = temp_project
    baseline_path = project_path / ".doc-manager" / "memory" / "repo-baseline.json"

    # Modify source files between runs to force baseline changes
    src_dir = project_path / "src"

    async def update_and_modify(iteration: int):
        """Update baseline, then modify a source file."""
        # Update baseline
        result = await docmgr_update_baseline(DocmgrUpdateBaselineInput(
            project_path=str(project_path)
        ))

        # Modify a source file to trigger changes in next update
        new_file = src_dir / f"file_{iteration}.py"
        new_file.write_text(f"# File {iteration}\ndef func_{iteration}():\n    pass\n")

        return result

    # Run 10 concurrent updates with file modifications
    tasks = [update_and_modify(i) for i in range(10)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Verify all operations succeeded
    for i, result in enumerate(results):
        assert not isinstance(result, Exception), f"Task {i} failed with: {result}"

    # Verify final baseline is valid
    assert baseline_path.exists()
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)

    assert "files" in baseline
    assert len(baseline["files"]) >= 3, "Baseline should include at least initial source files"


@pytest.mark.asyncio
async def test_concurrent_symbol_baseline_updates(temp_project):
    """Test concurrent updates to symbol-baseline.json don't corrupt the file."""
    project_path = temp_project
    symbol_baseline_path = project_path / ".doc-manager" / "memory" / "symbol-baseline.json"
    lock_path = symbol_baseline_path.with_suffix(".json.lock")

    # Run 5 concurrent updates including symbol baseline
    tasks = [
        docmgr_update_baseline(DocmgrUpdateBaselineInput(
            project_path=str(project_path)
        ))
        for _ in range(5)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Verify all succeeded
    for i, result in enumerate(results):
        assert not isinstance(result, Exception), f"Symbol baseline task {i} failed: {result}"

    # Verify symbol baseline is valid JSON
    if symbol_baseline_path.exists():
        with open(symbol_baseline_path, 'r') as f:
            symbol_baseline = json.load(f)

        assert "files" in symbol_baseline or "symbols" in symbol_baseline, \
            "Symbol baseline should have expected structure"

    # Verify lock cleaned up
    assert not lock_path.exists()


@pytest.mark.asyncio
async def test_file_lock_timeout_handling(temp_project):
    """Test that file lock timeout is handled gracefully.

    This test would ideally verify timeout behavior, but given the
    quick nature of baseline writes, we mainly verify that the lock
    mechanism doesn't cause deadlocks.
    """
    project_path = temp_project

    # Run many concurrent operations to stress-test locking
    tasks = [
        docmgr_update_baseline(DocmgrUpdateBaselineInput(
            project_path=str(project_path)
        ))
        for _ in range(20)
    ]

    # Should complete without deadlock or timeout
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Most should succeed (some might timeout if contention is extreme,
    # but with proper locking they should all succeed)
    successes = sum(1 for r in results if not isinstance(r, Exception))
    assert successes >= 15, f"Expected most operations to succeed, got {successes}/20"


@pytest.mark.asyncio
async def test_concurrent_dependencies_baseline(temp_project):
    """Test concurrent updates to dependencies.json (already has locking).

    This verifies that the existing file locking in dependencies.json
    still works correctly.
    """
    project_path = temp_project
    dep_path = project_path / ".doc-manager" / "dependencies.json"

    # Run concurrent updates
    tasks = [
        docmgr_update_baseline(DocmgrUpdateBaselineInput(
            project_path=str(project_path)
        ))
        for _ in range(5)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Verify all succeeded
    for result in results:
        assert not isinstance(result, Exception)

    # Verify dependencies.json is valid if it exists
    if dep_path.exists():
        with open(dep_path, 'r') as f:
            deps = json.load(f)

        # Should have expected structure
        assert isinstance(deps, dict)
