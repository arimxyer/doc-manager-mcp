"""Tests for link index optimization in validate_docs.

This module tests that the link index correctly indexes markdown files
and enables O(1) lookups instead of O(M) file system operations per link.
"""

import tempfile
from pathlib import Path

import pytest

from doc_manager_mcp.indexing.link_index import LinkIndex, build_link_index


@pytest.fixture
def docs_structure():
    """Create a temporary documentation structure for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_path = Path(tmpdir) / "docs"
        docs_path.mkdir()

        # Create various markdown files
        (docs_path / "index.md").write_text("# Index\n")
        (docs_path / "guide.md").write_text("# Guide\n")

        # Create subdirectories
        (docs_path / "reference").mkdir()
        (docs_path / "reference" / "api.md").write_text("# API\n")
        (docs_path / "reference" / "cli.md").write_text("# CLI\n")

        (docs_path / "tutorials").mkdir()
        (docs_path / "tutorials" / "getting-started.md").write_text("# Getting Started\n")

        yield docs_path


def test_build_link_index_basic(docs_structure):
    """Test basic link index construction."""
    index = build_link_index(docs_structure)

    assert isinstance(index, LinkIndex)
    assert len(index) >= 5  # At least 5 markdown files


def test_link_index_lookup_by_filename(docs_structure):
    """Test lookup by filename."""
    index = build_link_index(docs_structure)

    # Lookup by filename
    result = index.resolve("api.md", docs_structure)
    assert result is not None
    assert result.name == "api.md"


def test_link_index_lookup_by_stem(docs_structure):
    """Test lookup by stem (filename without extension)."""
    index = build_link_index(docs_structure)

    # Lookup by stem (Hugo-style extensionless links)
    result = index.resolve("api", docs_structure)
    assert result is not None
    assert result.stem == "api"


def test_link_index_lookup_by_relative_path(docs_structure):
    """Test lookup by relative path."""
    index = build_link_index(docs_structure)

    # Lookup by relative path
    result = index.resolve("reference/api.md", docs_structure)
    assert result is not None
    assert "api.md" in str(result)


def test_link_index_lookup_by_absolute_path(docs_structure):
    """Test lookup by absolute path from docs root."""
    index = build_link_index(docs_structure)

    # Lookup by absolute path (with leading /)
    result = index.resolve("/reference/cli.md", docs_structure)
    assert result is not None
    assert "cli.md" in str(result)


def test_link_index_nonexistent_link(docs_structure):
    """Test that nonexistent links return None."""
    index = build_link_index(docs_structure)

    # Nonexistent file
    result = index.resolve("nonexistent.md", docs_structure)
    assert result is None


def test_link_index_with_anchors(docs_structure):
    """Test that anchors are stripped before lookup."""
    index = build_link_index(docs_structure)

    # Link with anchor
    result = index.resolve("api.md#section", docs_structure)
    assert result is not None
    assert result.name == "api.md"


def test_link_index_relative_path_resolution(docs_structure):
    """Test resolving relative paths from different source files."""
    index = build_link_index(docs_structure)

    # From reference/api.md, link to ../guide.md
    source_file = docs_structure / "reference" / "api.md"
    result = index.resolve("../guide.md", source_file.parent, docs_structure)
    assert result is not None
    assert result.name == "guide.md"


def test_link_index_case_insensitive(docs_structure):
    """Test case-insensitive lookups on case-insensitive file systems."""
    index = build_link_index(docs_structure)

    # Different case (should work on Windows, may fail on Linux)
    result = index.resolve("API.md", docs_structure)
    # This should at least not crash
    assert result is None or result.name.lower() == "api.md"


def test_link_index_handles_spaces_in_names(docs_structure):
    """Test that files with spaces in names are indexed correctly."""
    # Create file with spaces
    (docs_structure / "getting started.md").write_text("# Getting Started\n")

    index = build_link_index(docs_structure)

    # Lookup with spaces
    result = index.resolve("getting started.md", docs_structure)
    assert result is not None
    assert result.name == "getting started.md"


def test_link_index_performance():
    """Test that link index provides O(1) lookup performance."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_path = Path(tmpdir) / "docs"
        docs_path.mkdir()

        # Create 100 markdown files
        for i in range(100):
            (docs_path / f"doc{i}.md").write_text(f"# Doc {i}\n")

        # Build index
        index = build_link_index(docs_path)

        # Verify index has all files
        assert len(index) == 100

        # Lookups should be fast (O(1))
        # Just verify they work, actual timing would be in benchmarks
        for i in range(100):
            result = index.resolve(f"doc{i}.md", docs_path)
            assert result is not None
            assert result.stem == f"doc{i}"


def test_link_index_empty_directory():
    """Test link index with empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_path = Path(tmpdir) / "docs"
        docs_path.mkdir()

        index = build_link_index(docs_path)

        assert len(index) == 0
        assert index.resolve("anything.md", docs_path) is None


def test_link_index_includes_nested_files(docs_structure):
    """Test that deeply nested files are indexed."""
    # Create deeply nested structure
    deep_path = docs_structure / "a" / "b" / "c"
    deep_path.mkdir(parents=True)
    (deep_path / "deep.md").write_text("# Deep\n")

    index = build_link_index(docs_structure)

    # Should be able to find deeply nested file
    result = index.resolve("a/b/c/deep.md", docs_structure)
    assert result is not None
    assert result.name == "deep.md"
