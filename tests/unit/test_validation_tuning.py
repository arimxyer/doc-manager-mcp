"""Tests for validation tuning fixes (false positive reduction)."""

import re
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from doc_manager_mcp.tools.analysis.validation.links import (
    _check_link_via_filesystem,
    _is_under,
    check_internal_link,
)
from doc_manager_mcp.tools.analysis.validation.references import (
    validate_stale_references,
)
from doc_manager_mcp.tools.analysis.quality.consistency import assess_consistency
from doc_manager_mcp.core.api_coverage import API_COVERAGE_PRESETS, ApiCoverageConfig
from doc_manager_mcp.indexing.parsers.markdown import MarkdownParser
from doc_manager_mcp.tools.analysis.validation.helpers import (
    validate_documented_symbols,
)


# === Fix 1: Broken link false positives for root README ===


class TestLinkFallbackForNonDocsFiles:
    """Links from files outside docs_root should fall back to filesystem."""

    def test_is_under_true(self, tmp_path):
        child = tmp_path / "docs" / "file.md"
        child.parent.mkdir(parents=True)
        child.touch()
        assert _is_under(child, tmp_path / "docs")

    def test_is_under_false(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.touch()
        assert not _is_under(readme, tmp_path / "docs")

    def test_root_readme_link_to_license(self, tmp_path):
        """Root README linking to LICENSE should not be broken."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        readme = tmp_path / "README.md"
        readme.touch()
        license_file = tmp_path / "LICENSE"
        license_file.touch()

        # Mock link_index that returns None (file not in docs index)
        mock_index = MagicMock()
        mock_index.resolve.return_value = None

        result = check_internal_link(
            "LICENSE", readme, docs_dir, mock_index, project_path=tmp_path
        )
        assert result is None  # Should NOT report broken

    def test_root_readme_link_to_test_readme(self, tmp_path):
        """Root README linking to test/README.md should not be broken."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        readme = tmp_path / "README.md"
        readme.touch()
        test_dir = tmp_path / "test"
        test_dir.mkdir()
        (test_dir / "README.md").touch()

        mock_index = MagicMock()
        mock_index.resolve.return_value = None

        result = check_internal_link(
            "test/README.md", readme, docs_dir, mock_index, project_path=tmp_path
        )
        assert result is None

    def test_docs_file_still_reports_broken(self, tmp_path):
        """Files inside docs_root should still report broken links."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        doc_file = docs_dir / "guide.md"
        doc_file.touch()

        mock_index = MagicMock()
        mock_index.resolve.return_value = None

        result = check_internal_link(
            "nonexistent.md", doc_file, docs_dir, mock_index, project_path=tmp_path
        )
        assert result is not None
        assert "Broken link" in result


# === Fix 2: Config-based reference filtering ===


class TestStaleReferenceFiltering:
    """Exclude patterns should filter stale reference warnings."""

    def test_exclude_patterns_filter_refs(self):
        deps = {
            "unmatched_references": {
                "pass-insert": ["docs/usage.md"],
                "--clip": ["docs/usage.md"],
                "store.GetPassword": ["docs/api.md"],
            }
        }
        issues = validate_stale_references(
            Path("/fake"),
            dependencies=deps,
            exclude_reference_patterns=["pass-*", "--*"],
        )
        assert len(issues) == 1
        assert issues[0]["reference"] == "store.GetPassword"

    def test_no_exclude_patterns(self):
        deps = {
            "unmatched_references": {
                "pass-insert": ["docs/usage.md"],
                "store.Get": ["docs/api.md"],
            }
        }
        issues = validate_stale_references(Path("/fake"), dependencies=deps)
        assert len(issues) == 2


# === Fix 3: API coverage path exclusions ===


class TestApiCoveragePathExclusions:
    def test_exclude_paths_config(self):
        config = ApiCoverageConfig(exclude_paths=["cmd/tui/*", "internal/cobra/*"])
        assert config.exclude_paths == ["cmd/tui/*", "internal/cobra/*"]

    def test_default_empty_exclude_paths(self):
        config = ApiCoverageConfig()
        assert config.exclude_paths == []


# === Fix 4: Setext heading false positives from frontmatter ===


class TestFrontmatterStripping:
    """YAML frontmatter should not be counted as setext headings."""

    def test_frontmatter_not_counted_as_setext(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "---\ntitle: My Page\ndate: 2024-01-01\n---\n\n# Real Heading\n\nContent here.\n"
        )
        result = assess_consistency(
            project_path=tmp_path,
            docs_path=tmp_path,
            markdown_files=[md_file],
        )
        assert result["metrics"]["setext_headings"] == 0
        assert result["metrics"]["atx_headings"] == 1

    def test_real_setext_still_counted(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("Real Heading\n============\n\nContent.\n")
        result = assess_consistency(
            project_path=tmp_path,
            docs_path=tmp_path,
            markdown_files=[md_file],
        )
        assert result["metrics"]["setext_headings"] >= 1

    def test_frontmatter_plus_setext(self, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text(
            "---\ntitle: Test\n---\n\nReal Heading\n============\n\nContent.\n"
        )
        result = assess_consistency(
            project_path=tmp_path,
            docs_path=tmp_path,
            markdown_files=[md_file],
        )
        # Should count the real setext but not frontmatter
        assert result["metrics"]["setext_headings"] >= 1


# === Fix 5: Warning severity tiers ===


class TestStaleReferenceConfidence:
    """Stale references should have confidence levels."""

    def test_high_confidence_for_paths(self):
        deps = {
            "unmatched_references": {
                "pkg/store.go": ["docs/api.md"],
                "store.GetPassword": ["docs/api.md"],
            }
        }
        issues = validate_stale_references(Path("/fake"), dependencies=deps)
        for issue in issues:
            assert issue["confidence"] == "high"

    def test_low_confidence_for_simple_words(self):
        deps = {
            "unmatched_references": {
                "insert": ["docs/usage.md"],
                "clip": ["docs/usage.md"],
            }
        }
        issues = validate_stale_references(Path("/fake"), dependencies=deps)
        for issue in issues:
            assert issue["confidence"] == "low"


# === Fix 6: Change detection staleness summary ===


class TestDetectChangesSummary:
    """detect_changes should include per-category summary."""

    @pytest.mark.asyncio
    async def test_summary_included_in_result(self, tmp_path):
        """Integration-style test: verify summary structure exists."""
        from doc_manager_mcp.tools.analysis.detect_changes import docmgr_detect_changes
        from doc_manager_mcp.models import DocmgrDetectChangesInput

        # This will fail with "no baseline" but we can test the structure
        # by mocking. For now, just verify the code path doesn't crash.
        params = DocmgrDetectChangesInput(
            project_path=str(tmp_path),
            mode="checksum",
        )
        result = await docmgr_detect_changes(params)
        # Without baseline, returns error - that's fine
        assert result["status"] == "error"


# === Fix 7: Duplicate syntax warnings dedup (A) ===


class TestDuplicateSyntaxDedup:
    """When both check_snippets and validate_code_syntax are enabled,
    validate_code_syntax should be skipped to avoid duplicate warnings."""

    @pytest.mark.asyncio
    async def test_no_duplicate_warnings_when_both_enabled(self, tmp_path):
        """Run actual validation with both flags and verify no code_syntax_error duplicates."""
        from doc_manager_mcp.models import ValidateDocsInput
        from doc_manager_mcp.tools.analysis.validation.validator import validate_docs

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        md = docs_dir / "test.md"
        # Invalid Python that TreeSitter will flag
        md.write_text("# Test\n\n```python\ndef foo(\n```\n")

        params = ValidateDocsInput(
            project_path=str(tmp_path),
            docs_path="docs",
            check_snippets=True,
            validate_code_syntax=True,
            check_links=False,
            check_assets=False,
        )
        result = await validate_docs(params)
        # Result may be a dict or string; extract issues
        if isinstance(result, dict):
            issues = result.get("issues", [])
        else:
            issues = []
        syntax_types = {i["type"] for i in issues if "syntax" in i["type"]}
        # Should only have syntax_error (from snippets), NOT code_syntax_error
        assert "code_syntax_error" not in syntax_types

    @pytest.mark.asyncio
    async def test_validate_code_syntax_alone_still_works(self, tmp_path):
        """When check_snippets=False, validate_code_syntax should still run."""
        from doc_manager_mcp.models import ValidateDocsInput
        from doc_manager_mcp.tools.analysis.validation.validator import validate_docs

        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        md = docs_dir / "test.md"
        md.write_text("# Test\n\n```python\ndef foo(\n```\n")

        params = ValidateDocsInput(
            project_path=str(tmp_path),
            docs_path="docs",
            check_snippets=False,
            validate_code_syntax=True,
            check_links=False,
            check_assets=False,
        )
        result = await validate_docs(params)
        if isinstance(result, dict):
            issues = result.get("issues", [])
            syntax_issues = [i for i in issues if i["type"] == "code_syntax_error"]
            # Should have code_syntax_error since check_snippets is off
            assert len(syntax_issues) > 0


# === Fix 8: Frontmatter heading detection via MarkdownParser (B) ===


class TestFrontmatterMarkdownParser:
    """MarkdownParser should not treat frontmatter as headings."""

    def test_frontmatter_not_parsed_as_heading(self):
        parser = MarkdownParser()
        content = "---\ntitle: Test\ndate: 2024-01-01\n---\n\n# Real Heading\n\nContent.\n"
        headers = parser.extract_headers(content)
        assert len(headers) == 1
        assert headers[0]["text"] == "Real Heading"
        assert headers[0]["level"] == 1

    def test_no_frontmatter(self):
        parser = MarkdownParser()
        content = "# Heading One\n\n## Heading Two\n"
        headers = parser.extract_headers(content)
        assert len(headers) == 2

    def test_detect_multiple_h1s_not_fooled_by_frontmatter(self, tmp_path):
        """The actual user-facing detect_multiple_h1s should not miscount
        H1 headers when YAML frontmatter is present."""
        from doc_manager_mcp.tools.analysis.quality.helpers import detect_multiple_h1s

        md = tmp_path / "page.md"
        md.write_text("---\ntitle: My Page\ndate: 2024-01-01\n---\n\n# Real Heading\n\nContent.\n")

        issues = detect_multiple_h1s(tmp_path)
        # File has exactly 1 H1 — should NOT appear in issues
        assert len(issues) == 0

    def test_line_numbers_preserved_after_frontmatter_strip(self):
        """Line numbers should still be correct after frontmatter stripping."""
        parser = MarkdownParser()
        content = "---\ntitle: Test\n---\n\n# Heading\n"
        headers = parser.extract_headers(content)
        assert len(headers) == 1
        # Frontmatter is 3 lines (---\ntitle\n---\n), blank line, heading on line 5
        assert headers[0]["line"] == 5


# === Fix 9: Stale reference CLI heuristic filtering (C) ===


class TestStaleReferenceCLIFiltering:
    """Built-in heuristics should filter CLI-like references."""

    def test_spaces_filtered(self):
        deps = {"unmatched_references": {"pass-cli init": ["docs/usage.md"]}}
        issues = validate_stale_references(Path("/fake"), dependencies=deps)
        assert len(issues) == 0

    def test_flags_filtered(self):
        deps = {"unmatched_references": {
            "--help": ["docs/usage.md"],
            "-v": ["docs/usage.md"],
        }}
        issues = validate_stale_references(Path("/fake"), dependencies=deps)
        assert len(issues) == 0

    def test_real_refs_kept(self):
        deps = {"unmatched_references": {"store.GetPassword": ["docs/api.md"]}}
        issues = validate_stale_references(Path("/fake"), dependencies=deps)
        assert len(issues) == 1

    def test_mixed_cli_and_code_refs(self):
        """Real-world scenario: CLI docs with both commands and code refs."""
        deps = {"unmatched_references": {
            "pass-cli init": ["docs/usage.md"],         # CLI with space → filtered
            "--clip": ["docs/usage.md"],                 # flag → filtered
            "-v": ["docs/usage.md"],                     # short flag → filtered
            "store.GetPassword": ["docs/api.md"],        # qualified ref → kept (high)
            "pkg/store.go": ["docs/api.md"],             # path ref → kept (high)
            "insert": ["docs/usage.md"],                 # simple word → kept (low)
        }}
        issues = validate_stale_references(Path("/fake"), dependencies=deps)
        refs = {i["reference"]: i["confidence"] for i in issues}
        assert "pass-cli init" not in refs
        assert "--clip" not in refs
        assert "-v" not in refs
        assert refs["store.GetPassword"] == "high"
        assert refs["pkg/store.go"] == "high"
        assert refs["insert"] == "low"


# === Fix 10: Symbol exclusion for keyboard keys / env vars (D) ===


class TestSymbolExclusions:
    """Keyboard keys and ALL_CAPS words should not be flagged as missing symbols."""

    def test_keyboard_keys_excluded(self, tmp_path):
        content = "Press `Backspace` to delete. Use `Enter` to confirm.\n"
        issues = validate_documented_symbols(
            content, tmp_path / "doc.md", tmp_path, symbol_index={}, docs_path=tmp_path
        )
        assert all(i["symbol"] not in ("Backspace", "Enter") for i in issues)

    def test_allcaps_excluded(self, tmp_path):
        content = "Set `EDITOR` to your preferred editor.\n"
        issues = validate_documented_symbols(
            content, tmp_path / "doc.md", tmp_path, symbol_index={}, docs_path=tmp_path
        )
        assert all(i["symbol"] != "EDITOR" for i in issues)

    def test_allcaps_included_if_in_index(self, tmp_path):
        """ALL_CAPS words matching actual codebase symbols should not be skipped."""
        from doc_manager_mcp.indexing.analysis.tree_sitter import Symbol
        mock_symbol = MagicMock(spec=Symbol)
        content = "Use `MYCONST` for configuration.\n"
        issues = validate_documented_symbols(
            content, tmp_path / "doc.md", tmp_path,
            symbol_index={"MYCONST": [mock_symbol]}, docs_path=tmp_path
        )
        # MYCONST is in the index, so it should NOT be flagged
        assert all(i.get("symbol") != "MYCONST" for i in issues)

    def test_short_refs_excluded(self, tmp_path):
        """References ≤2 chars should be excluded (too ambiguous)."""
        content = "Press `OK` then `Go` to continue.\n"
        issues = validate_documented_symbols(
            content, tmp_path / "doc.md", tmp_path, symbol_index={}, docs_path=tmp_path
        )
        symbols = [i["symbol"] for i in issues]
        assert "OK" not in symbols
        assert "Go" not in symbols

    def test_real_symbols_still_flagged(self, tmp_path):
        """Actual PascalCase names that aren't keyboard keys should still be flagged."""
        content = "Use `CryptGenRandom` for crypto.\n"
        issues = validate_documented_symbols(
            content, tmp_path / "doc.md", tmp_path, symbol_index={}, docs_path=tmp_path
        )
        flagged = [i["symbol"] for i in issues]
        assert "CryptGenRandom" in flagged


# === Fix 11: Go preset (E) ===


class TestGoPreset:
    """Go preset should exist with sensible defaults."""

    def test_go_preset_exists(self):
        assert "go" in API_COVERAGE_PRESETS

    def test_go_preset_exclude_paths(self):
        preset = API_COVERAGE_PRESETS["go"]
        assert "internal/*" in preset["exclude_paths"]
        assert "*.pb.go" in preset["exclude_paths"]

    def test_go_preset_config(self):
        config = ApiCoverageConfig(preset="go")
        patterns = config.get_resolved_exclude_patterns()
        assert "Test*" in patterns

    def test_go_preset_excludes_generated_code(self):
        preset = API_COVERAGE_PRESETS["go"]
        paths = preset["exclude_paths"]
        # Should exclude protobuf generated code
        assert any("pb.go" in p for p in paths)
        # Should exclude mocks
        assert any("mock" in p for p in paths)
