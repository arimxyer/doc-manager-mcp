"""Test dependency tracking correctly classifies tool names as functions."""

import tempfile
from pathlib import Path

import pytest

from doc_manager_mcp.indexing import SymbolIndexer
from doc_manager_mcp.indexing.analysis.tree_sitter import Symbol, SymbolType
from doc_manager_mcp.tools._internal.dependencies import _extract_code_references


@pytest.fixture
def sample_doc_content():
    """Sample documentation with tool references."""
    return """
# Quick Start

Initialize doc-manager with `docmgr_init`:

```bash
docmgr_init --mode=existing
```

Configure with `platform: mkdocs` in your config.

Use `docmgr_sync()` to sync documentation.
"""


@pytest.fixture
def symbol_index():
    """Create symbol index with sample functions."""
    indexer = SymbolIndexer()

    # Add tool functions to index
    indexer.index = {
        "docmgr_init": [
            Symbol(
                name="docmgr_init",
                type=SymbolType.FUNCTION,
                file="doc_manager_mcp/tools/state/init.py",
                line=22,
                column=0,
                signature="async def docmgr_init(params)"
            )
        ],
        "docmgr_sync": [
            Symbol(
                name="docmgr_sync",
                type=SymbolType.FUNCTION,
                file="doc_manager_mcp/tools/state/sync.py",
                line=15,
                column=0,
                signature="async def docmgr_sync(params)"
            )
        ]
    }

    return indexer


def test_tool_name_classified_as_function_not_config_key(sample_doc_content, symbol_index):
    """Tool names should be classified as functions when they exist in symbol index."""
    doc_file = Path("test.md")

    references = _extract_code_references(sample_doc_content, doc_file, indexer=symbol_index)

    # Find docmgr_init reference
    init_refs = [r for r in references if "docmgr_init" in r["reference"]]

    assert len(init_refs) > 0, "Should find docmgr_init reference"

    # Should be classified as function, not config_key
    for ref in init_refs:
        assert ref["type"] == "function", f"Expected 'function', got '{ref['type']}'"
        assert ref["reference"] == "docmgr_init()", f"Reference should be normalized: {ref['reference']}"


def test_genuine_config_key_still_classified_correctly(sample_doc_content, symbol_index):
    """Config keys that aren't functions should stay as config_key."""
    doc_file = Path("test.md")

    references = _extract_code_references(sample_doc_content, doc_file, indexer=symbol_index)

    # Find platform reference
    platform_refs = [r for r in references if r["reference"] == "platform"]

    assert len(platform_refs) > 0, "Should find platform config key"
    assert platform_refs[0]["type"] == "config_key", "platform should be config_key"


def test_function_with_parentheses_still_works(symbol_index):
    """Functions with () should still be matched by existing logic."""
    content = "Call `docmgr_sync()` to synchronize."
    doc_file = Path("test.md")

    references = _extract_code_references(content, doc_file, indexer=symbol_index)

    sync_refs = [r for r in references if "docmgr_sync" in r["reference"]]

    assert len(sync_refs) > 0, "Should find docmgr_sync reference"
    # Should be classified as function (either by FUNCTION_PATTERN or symbol lookup)
    assert sync_refs[0]["type"] == "function", "Should be classified as function"


def test_without_symbol_index_fallback_behavior(sample_doc_content):
    """Without symbol index, should fallback to original behavior."""
    doc_file = Path("test.md")

    # Call without symbol index
    references = _extract_code_references(sample_doc_content, doc_file, indexer=None)

    # Without symbol index, docmgr_init (no parens) will be config_key
    init_refs = [r for r in references if "docmgr_init" in r["reference"]]

    # Should still extract reference (as config_key since no index available)
    assert len(init_refs) > 0, "Should still find reference"
    # Without symbol index, it falls back to config_key
    assert init_refs[0]["type"] == "config_key", "Should fallback to config_key without index"


def test_function_not_in_index_classified_as_config_key():
    """Identifiers not in symbol index should fallback to config_key."""
    content = "Use `some_random_key` for configuration."
    doc_file = Path("test.md")

    indexer = SymbolIndexer()
    indexer.index = {}  # Empty index

    references = _extract_code_references(content, doc_file, indexer=indexer)

    key_refs = [r for r in references if r["reference"] == "some_random_key"]

    assert len(key_refs) > 0, "Should find reference"
    assert key_refs[0]["type"] == "config_key", "Should be config_key when not in index"


def test_class_in_index_not_matched_as_function():
    """Classes in symbol index should not be matched by function logic."""
    content = "Use `MyClass` for this."
    doc_file = Path("test.md")

    indexer = SymbolIndexer()
    indexer.index = {
        "MyClass": [
            Symbol(
                name="MyClass",
                type=SymbolType.CLASS,
                file="src/module.py",
                line=10,
                column=0,
                signature="class MyClass"
            )
        ]
    }

    references = _extract_code_references(content, doc_file, indexer=indexer)

    # MyClass should be matched by CLASS_PATTERN before symbol lookup
    class_refs = [r for r in references if "MyClass" in r["reference"]]

    assert len(class_refs) > 0, "Should find reference"
    assert class_refs[0]["type"] == "class", "Should be classified as class"
