"""Tests for public symbol detection following industry standards.

Tests that is_public_symbol() correctly implements conventions from
Sphinx autodoc, mkdocstrings/Griffe, and pdoc:
1. __all__ takes precedence when defined
2. Underscore convention as fallback
3. Known internal patterns (Pydantic validators, etc.) excluded
"""

import pytest
from dataclasses import dataclass
from pathlib import Path

from doc_manager_mcp.core.project import (
    is_public_symbol,
    extract_module_all,
    PYTHON_INTERNAL_PATTERNS,
    PYTHON_INTERNAL_PREFIXES,
)


@dataclass
class MockSymbol:
    """Mock symbol for testing."""
    name: str
    file: str
    parent: str | None = None


class TestUnderscoreConvention:
    """Test basic underscore convention (no __all__ defined)."""

    def test_public_function_is_public(self):
        """Functions without underscore prefix are public."""
        symbol = MockSymbol(name="process_data", file="module.py")
        assert is_public_symbol(symbol) is True

    def test_private_function_is_private(self):
        """Functions with single underscore prefix are private."""
        symbol = MockSymbol(name="_internal_helper", file="module.py")
        assert is_public_symbol(symbol) is False

    def test_dunder_is_private(self):
        """Dunder methods are private (not part of API coverage)."""
        symbol = MockSymbol(name="__init__", file="module.py", parent="MyClass")
        assert is_public_symbol(symbol) is False

    def test_public_class_is_public(self):
        """Classes without underscore prefix are public."""
        symbol = MockSymbol(name="DataProcessor", file="module.py")
        assert is_public_symbol(symbol) is True

    def test_private_class_is_private(self):
        """Classes with underscore prefix are private."""
        symbol = MockSymbol(name="_InternalHelper", file="module.py")
        assert is_public_symbol(symbol) is False


class TestAllTakesPrecedence:
    """Test that __all__ takes absolute precedence."""

    def test_symbol_in_all_is_public(self):
        """Symbols listed in __all__ are public."""
        symbol = MockSymbol(name="process_data", file="module.py")
        module_all = {"process_data", "DataClass"}
        assert is_public_symbol(symbol, module_all) is True

    def test_symbol_not_in_all_is_private(self):
        """Symbols not in __all__ are private, even without underscore."""
        symbol = MockSymbol(name="helper_function", file="module.py")
        module_all = {"main_function"}
        assert is_public_symbol(symbol, module_all) is False

    def test_underscore_in_all_is_public(self):
        """Underscore-prefixed symbols are public if in __all__."""
        symbol = MockSymbol(name="_special_export", file="module.py")
        module_all = {"_special_export"}
        assert is_public_symbol(symbol, module_all) is True

    def test_empty_all_means_no_public_api(self):
        """Empty __all__ means module has no public API."""
        symbol = MockSymbol(name="some_function", file="module.py")
        module_all: set[str] = set()
        assert is_public_symbol(symbol, module_all) is False


class TestPythonInternalPatterns:
    """Test exclusion of known internal patterns."""

    def test_pydantic_validators_are_internal(self):
        """Pydantic validators are internal implementation details."""
        for validator_name in ["model_validator", "field_validator", "root_validator", "validator"]:
            symbol = MockSymbol(name=validator_name, file="models.py")
            assert is_public_symbol(symbol) is False, f"{validator_name} should be internal"

    def test_config_class_is_internal(self):
        """Config classes (Pydantic, Django) are internal."""
        symbol = MockSymbol(name="Config", file="models.py")
        assert is_public_symbol(symbol) is False

    def test_meta_class_is_internal(self):
        """Meta classes are internal."""
        symbol = MockSymbol(name="Meta", file="models.py")
        assert is_public_symbol(symbol) is False

    def test_test_functions_are_internal(self):
        """Test functions should not be in API coverage."""
        symbol = MockSymbol(name="test_something", file="test_module.py")
        assert is_public_symbol(symbol) is False

    def test_test_classes_are_internal(self):
        """Test classes should not be in API coverage."""
        symbol = MockSymbol(name="TestSomething", file="test_module.py")
        assert is_public_symbol(symbol) is False


class TestGoConventions:
    """Test Go language conventions."""

    def test_exported_function_is_public(self):
        """Go functions starting with uppercase are exported."""
        symbol = MockSymbol(name="ProcessData", file="handler.go")
        assert is_public_symbol(symbol) is True

    def test_unexported_function_is_private(self):
        """Go functions starting with lowercase are unexported."""
        symbol = MockSymbol(name="processData", file="handler.go")
        assert is_public_symbol(symbol) is False

    def test_exported_type_is_public(self):
        """Go types starting with uppercase are exported."""
        symbol = MockSymbol(name="DataHandler", file="types.go")
        assert is_public_symbol(symbol) is True


class TestJavaScriptConventions:
    """Test JavaScript/TypeScript conventions."""

    def test_public_function_js(self):
        """JS functions without underscore are public."""
        symbol = MockSymbol(name="handleClick", file="component.js")
        assert is_public_symbol(symbol) is True

    def test_private_function_js(self):
        """JS functions with underscore are private."""
        symbol = MockSymbol(name="_handleClick", file="component.js")
        assert is_public_symbol(symbol) is False

    def test_public_function_ts(self):
        """TS functions without underscore are public."""
        symbol = MockSymbol(name="processData", file="service.ts")
        assert is_public_symbol(symbol) is True

    def test_public_function_tsx(self):
        """TSX functions without underscore are public."""
        symbol = MockSymbol(name="MyComponent", file="Component.tsx")
        assert is_public_symbol(symbol) is True


class TestExtractModuleAll:
    """Test __all__ extraction from Python modules."""

    def test_extract_all_list(self, tmp_path):
        """Extract __all__ from a simple list definition."""
        test_file = tmp_path / "module_with_all.py"
        test_file.write_text(
            '__all__ = ["func1", "func2", "MyClass"]\n'
            'def func1(): pass\n'
            'def func2(): pass\n'
            'def _private(): pass\n'
            'class MyClass: pass\n'
        )
        result = extract_module_all(test_file)
        assert result == {"func1", "func2", "MyClass"}

    def test_no_all_returns_none(self, tmp_path):
        """Module without __all__ returns None."""
        test_file = tmp_path / "module_no_all.py"
        test_file.write_text(
            'def func1(): pass\n'
            'def func2(): pass\n'
        )
        result = extract_module_all(test_file)
        assert result is None

    def test_empty_all_returns_empty_set(self, tmp_path):
        """Empty __all__ returns empty set (no public API)."""
        test_file = tmp_path / "module_empty_all.py"
        test_file.write_text(
            '__all__ = []\n'
            'def _internal(): pass\n'
        )
        result = extract_module_all(test_file)
        assert result == set()

    def test_syntax_error_returns_none(self, tmp_path):
        """Files with syntax errors return None gracefully."""
        test_file = tmp_path / "broken_module.py"
        test_file.write_text('def broken(\n')  # Syntax error
        result = extract_module_all(test_file)
        assert result is None


class TestInternalPatternsCompleteness:
    """Verify internal patterns cover common cases."""

    def test_internal_patterns_exist(self):
        """Verify PYTHON_INTERNAL_PATTERNS is populated."""
        assert len(PYTHON_INTERNAL_PATTERNS) > 0
        assert "Config" in PYTHON_INTERNAL_PATTERNS
        assert "model_validator" in PYTHON_INTERNAL_PATTERNS

    def test_internal_prefixes_exist(self):
        """Verify PYTHON_INTERNAL_PREFIXES is populated."""
        assert len(PYTHON_INTERNAL_PREFIXES) > 0
        assert "test_" in PYTHON_INTERNAL_PREFIXES
        assert "Test" in PYTHON_INTERNAL_PREFIXES
