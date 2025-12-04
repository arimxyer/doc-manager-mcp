"""Pydantic schema for .doc-manager.yml configuration file.

This schema validates the user-editable configuration file at project root.
Unlike baseline files, this is NOT auto-generated - users create and edit it.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ApiCoverageConfig(BaseModel):
    """Configuration for API coverage metrics."""

    model_config = ConfigDict(extra="allow")

    strategy: Literal["all_then_underscore", "all_only", "underscore_only"] = Field(
        default="all_then_underscore",
        description="Strategy for detecting public symbols"
    )
    preset: str | None = Field(
        default=None,
        description="Language/framework preset (e.g., 'pydantic', 'django', 'go-test')"
    )
    exclude_symbols: list[str] = Field(
        default_factory=list,
        description="Additional symbol patterns to exclude (fnmatch syntax)"
    )
    include_symbols: list[str] = Field(
        default_factory=list,
        description="Symbol patterns to force-include (overrides exclusions)"
    )


class DocManagerConfig(BaseModel):
    """Schema for .doc-manager.yml configuration file.

    This file is user-created and user-edited. It configures doc-manager
    behavior for the project.
    """

    model_config = ConfigDict(extra="allow")

    # Documentation settings
    docs_path: str = Field(
        default="docs",
        description="Relative path to documentation directory"
    )
    platform: str | None = Field(
        default=None,
        description="Documentation platform (mkdocs, sphinx, hugo, docusaurus, unknown)"
    )

    # File filtering
    sources: list[str] = Field(
        default_factory=list,
        description="Glob patterns for source files to track"
    )
    exclude: list[str] = Field(
        default_factory=list,
        description="Glob patterns for files to exclude"
    )
    use_gitignore: bool = Field(
        default=False,
        description="Whether to respect .gitignore patterns"
    )
    include_root_readme: bool = Field(
        default=False,
        description="Whether to include root README.md in doc operations"
    )

    # Documentation mappings
    doc_mappings: dict[str, str] | None = Field(
        default=None,
        description="Map of change categories to documentation file paths"
    )

    # API coverage settings
    api_coverage: ApiCoverageConfig | None = Field(
        default=None,
        description="Configuration for API coverage metrics"
    )

    @field_validator("sources", "exclude", mode="before")
    @classmethod
    def normalize_list_fields(cls, v: Any) -> list[str]:
        """Normalize None to empty list for list fields."""
        if v is None:
            return []
        return v

    @field_validator("doc_mappings", mode="before")
    @classmethod
    def normalize_doc_mappings(cls, v: Any) -> dict[str, str] | None:
        """Normalize empty dict to None for doc_mappings."""
        if v is None or v == {}:
            return None
        return v


def validate_config(data: dict[str, Any]) -> DocManagerConfig:
    """Validate .doc-manager.yml configuration data.

    Args:
        data: Raw YAML data from file

    Returns:
        Validated DocManagerConfig model

    Raises:
        pydantic.ValidationError: If validation fails
    """
    return DocManagerConfig.model_validate(data)
