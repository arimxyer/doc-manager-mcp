"""Pydantic schemas for doc-manager baseline and config files."""

from .baselines import (
    BaselineMeta,
    DependenciesBaseline,
    RepoBaseline,
    SymbolBaseline,
    SymbolEntry,
    validate_dependencies_baseline,
    validate_repo_baseline,
    validate_symbol_baseline,
)
from .config import DocManagerConfig, validate_config
from .metadata import (
    AUTO_GENERATED_WARNING,
    TOOL_VERSION,
    get_json_meta,
    get_yaml_header,
    insert_meta_first,
)

__all__ = [
    # Schema models
    "BaselineMeta",
    "DependenciesBaseline",
    "DocManagerConfig",
    "RepoBaseline",
    "SymbolBaseline",
    "SymbolEntry",
    # Validation functions
    "validate_config",
    "validate_dependencies_baseline",
    "validate_repo_baseline",
    "validate_symbol_baseline",
    # Metadata helpers
    "AUTO_GENERATED_WARNING",
    "TOOL_VERSION",
    "get_json_meta",
    "get_yaml_header",
    "insert_meta_first",
]
