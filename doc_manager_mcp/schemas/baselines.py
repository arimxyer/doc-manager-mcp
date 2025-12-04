"""Pydantic schemas for doc-manager baseline files.

These schemas provide validation for auto-generated files in .doc-manager/:
- repo-baseline.json: File checksums and project metadata
- symbol-baseline.json: Code symbol index for semantic tracking
- dependencies.json: Code-to-doc dependency mappings
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Shared metadata for all auto-generated files
# =============================================================================

class BaselineMeta(BaseModel):
    """Metadata block for auto-generated baseline files.

    This appears as `_meta` at the top of each JSON baseline file to indicate
    the file is auto-generated and should not be manually edited.
    """

    model_config = ConfigDict(extra="forbid")

    generated_by: str = Field(
        default="doc-manager-mcp",
        description="Tool that generated this file"
    )
    tool_version: str = Field(
        description="Version of doc-manager-mcp that generated this file"
    )
    warning: str = Field(
        default="AUTO-GENERATED FILE - Do not edit manually. "
                "Changes will be overwritten by doc-manager.",
        description="Warning message for users/AI agents"
    )


# =============================================================================
# repo-baseline.json schema
# =============================================================================

class GitMetadata(BaseModel):
    """Git commit and branch information."""

    model_config = ConfigDict(extra="allow")

    git_commit: str | None = Field(
        default=None,
        description="Git commit hash at baseline creation"
    )
    git_branch: str | None = Field(
        default=None,
        description="Git branch at baseline creation"
    )


class RepoBaseline(BaseModel):
    """Schema for repo-baseline.json.

    Tracks file checksums for change detection via checksum comparison.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # Auto-generated metadata (serializes as "_meta" in JSON)
    meta: BaselineMeta | None = Field(
        default=None,
        alias="_meta",
        description="Auto-generation metadata"
    )

    # Required fields
    repo_name: str = Field(description="Repository/project name")
    version: str = Field(description="Baseline schema version")
    timestamp: str = Field(description="ISO timestamp of baseline creation")
    file_count: int = Field(ge=0, description="Number of tracked files")
    files: dict[str, str] = Field(
        description="Map of relative file paths to SHA-256 checksums"
    )

    # Optional fields
    description: str | None = Field(
        default=None,
        description="Project description"
    )
    language: str | None = Field(
        default=None,
        description="Primary programming language"
    )
    docs_exist: bool = Field(
        default=False,
        description="Whether documentation directory exists"
    )
    # DEPRECATED in v1.2.0: Use config.docs_path as authoritative source
    # Kept for backward compatibility with older baselines
    docs_path: str | None = Field(
        default=None,
        description="DEPRECATED: Use config.docs_path instead"
    )
    metadata: GitMetadata | None = Field(
        default=None,
        description="Git metadata"
    )


# =============================================================================
# symbol-baseline.json schema
# =============================================================================

class ConfigFieldEntry(BaseModel):
    """Schema for a config field within a symbol."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(description="Field name")
    parent_symbol: str = Field(description="Parent class/struct name")
    field_type: str | None = Field(default=None, description="Type annotation")
    default_value: str | None = Field(default=None, description="Default value")
    file: str = Field(description="File path")
    line: int = Field(ge=1, description="Line number")
    column: int = Field(ge=0, default=0, description="Column number")
    tags: list[str] | None = Field(default=None, description="Field tags")
    is_optional: bool = Field(default=False, description="Whether field is optional")
    doc: str | None = Field(default=None, description="Documentation string")


class SymbolEntry(BaseModel):
    """Schema for a code symbol entry."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(description="Symbol name")
    type: str = Field(description="Symbol type (function, class, method, etc.)")
    file: str = Field(description="File path relative to project root")
    line: int = Field(ge=1, description="Line number (1-indexed)")
    column: int = Field(ge=0, default=0, description="Column number (0-indexed)")
    signature: str | None = Field(default=None, description="Function/method signature")
    parent: str | None = Field(default=None, description="Parent symbol name")
    doc: str | None = Field(default=None, description="Documentation string")
    config_fields: list[ConfigFieldEntry] | None = Field(
        default=None,
        description="Config fields for Pydantic models, dataclasses, etc."
    )


class SymbolBaseline(BaseModel):
    """Schema for symbol-baseline.json.

    Tracks code symbols for semantic change detection.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # Auto-generated metadata (serializes as "_meta" in JSON)
    meta: BaselineMeta | None = Field(
        default=None,
        alias="_meta",
        description="Auto-generation metadata"
    )

    # Required fields
    version: str = Field(description="Baseline schema version")
    created_at: str = Field(description="ISO timestamp of initial creation")
    updated_at: str = Field(description="ISO timestamp of last update")
    project_root: str = Field(description="Absolute path to project root")
    symbols: dict[str, list[SymbolEntry]] = Field(
        description="Map of symbol names to list of symbol entries"
    )


# =============================================================================
# dependencies.json schema
# =============================================================================

class ReferenceEntry(BaseModel):
    """Schema for a reference entry in all_references."""

    model_config = ConfigDict(extra="allow")

    reference: str = Field(description="Reference text (function name, file path, etc.)")
    doc_file: str = Field(description="Documentation file containing this reference")


class DependenciesBaseline(BaseModel):
    """Schema for dependencies.json.

    Tracks code-to-documentation dependency mappings for affected doc detection.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    # Auto-generated metadata (serializes as "_meta" in JSON)
    meta: BaselineMeta | None = Field(
        default=None,
        alias="_meta",
        description="Auto-generation metadata"
    )

    # Required fields
    generated_at: str = Field(description="ISO timestamp of generation")

    # File-level dependency mappings
    doc_to_code: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map of doc paths to code files they reference"
    )
    code_to_doc: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map of code paths to docs that reference them"
    )
    asset_to_docs: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Map of asset paths to docs that use them"
    )

    # Reference-level mappings
    unmatched_references: dict[str, list[str]] = Field(
        default_factory=dict,
        description="References mentioned in docs that couldn't be matched to source files"
    )
    all_references: dict[str, list[ReferenceEntry]] = Field(
        default_factory=dict,
        description="All references grouped by type (function, class, file_path, command, etc.)"
    )

    # DEPRECATED: reference_to_doc is redundant with all_references
    # Kept for backward compatibility, will be removed in future version
    reference_to_doc: dict[str, list[str]] | None = Field(
        default=None,
        description="DEPRECATED: Use get_reference_to_doc() helper instead"
    )


# =============================================================================
# Validation helpers
# =============================================================================

def validate_repo_baseline(data: dict[str, Any]) -> RepoBaseline:
    """Validate repo-baseline.json data.

    Args:
        data: Raw JSON data from file

    Returns:
        Validated RepoBaseline model

    Raises:
        pydantic.ValidationError: If validation fails
    """
    return RepoBaseline.model_validate(data)


def validate_symbol_baseline(data: dict[str, Any]) -> SymbolBaseline:
    """Validate symbol-baseline.json data.

    Args:
        data: Raw JSON data from file

    Returns:
        Validated SymbolBaseline model

    Raises:
        pydantic.ValidationError: If validation fails
    """
    return SymbolBaseline.model_validate(data)


def validate_dependencies_baseline(data: dict[str, Any]) -> DependenciesBaseline:
    """Validate dependencies.json data.

    Args:
        data: Raw JSON data from file

    Returns:
        Validated DependenciesBaseline model

    Raises:
        pydantic.ValidationError: If validation fails
    """
    return DependenciesBaseline.model_validate(data)
