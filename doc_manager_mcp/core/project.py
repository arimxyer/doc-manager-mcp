"""Project detection and analysis utilities.

This module provides utilities for detecting project languages, documentation
directories, markdown files, and documentation platforms.
"""

from pathlib import Path
from typing import Any

from ..constants import MAX_FILES, DocumentationPlatform


def detect_project_language(project_path: Path) -> str:
    """Detect primary programming language of project.

    Returns the detected language based on project files.
    """
    language_indicators = {
        # Go
        "go.mod": "Go",
        # JavaScript/TypeScript
        "package.json": "JavaScript/TypeScript",
        # Rust
        "Cargo.toml": "Rust",
        # Python (check pyproject.toml first as it's the modern standard)
        "pyproject.toml": "Python",
        "Pipfile": "Python",
        "requirements.txt": "Python",
        "setup.py": "Python",
        # Java/Kotlin
        "pom.xml": "Java",
        "build.gradle": "Java",
        "build.gradle.kts": "Kotlin",
        # Ruby
        "Gemfile": "Ruby",
        # PHP
        "composer.json": "PHP",
        # C/C++
        "CMakeLists.txt": "C/C++",
        # Scala
        "build.sbt": "Scala",
        # Elixir
        "mix.exs": "Elixir",
        # Swift
        "Package.swift": "Swift",
    }

    for file, language in language_indicators.items():
        if (project_path / file).exists():
            return language

    return "Unknown"


def find_docs_directory(project_path: Path) -> Path | None:
    """Find documentation directory in project."""
    common_doc_dirs = ["docs", "doc", "documentation", "docsite", "website/docs"]

    for dir_name in common_doc_dirs:
        doc_path = project_path / dir_name
        if doc_path.exists() and doc_path.is_dir():
            return doc_path

    return None


def find_markdown_files(
    docs_path: Path,
    project_path: Path | None = None,
    validate_boundaries: bool = True,
    max_files: int | None = None
) -> list[Path]:
    """Find all markdown files in documentation directory.

    Args:
        docs_path: Documentation directory path
        project_path: Project root path (for boundary validation). Required if validate_boundaries=True.
        validate_boundaries: Whether to validate paths don't escape project boundary (default: True)
        max_files: Maximum number of files to process. Defaults to MAX_FILES constant if None.

    Returns:
        List of validated markdown file paths, sorted alphabetically

    Raises:
        ValueError: If file count exceeds max_files limit
        ValueError: If validate_boundaries=True but project_path is None
    """
    from .paths import validate_path_boundary

    if validate_boundaries and project_path is None:
        raise ValueError("project_path is required when validate_boundaries=True")

    markdown_files = []
    file_count = 0
    limit = max_files if max_files is not None else MAX_FILES

    for pattern in ["**/*.md", "**/*.markdown"]:
        for file_path in docs_path.glob(pattern):
            if file_count >= limit:
                raise ValueError(
                    f"File count limit exceeded (maximum: {limit:,} files)\n"
                    f"→ Consider processing a smaller directory or increasing the limit."
                )

            # Optionally validate path boundary and check for malicious symlinks
            if validate_boundaries:
                try:
                    _ = validate_path_boundary(file_path, project_path)  # type: ignore
                    markdown_files.append(file_path)
                    file_count += 1
                except ValueError:
                    # Skip files that escape project boundary or malicious symlinks
                    continue
            else:
                markdown_files.append(file_path)
                file_count += 1

    return sorted(markdown_files)


def is_public_symbol(symbol: Any) -> bool:
    """Determine if a symbol is public based on language-specific conventions.

    Args:
        symbol: Symbol object with 'name' and 'file' attributes

    Returns:
        True if symbol is public, False otherwise

    Language-specific rules:
        - Go: exported names start with uppercase
        - Python: public if no leading underscore
        - JavaScript/TypeScript: public if no leading underscore
    """
    if not symbol.name:
        return False

    # Language-specific public conventions
    if symbol.file.endswith('.go'):
        # Go: exported names start with uppercase
        return symbol.name[0].isupper()
    elif symbol.file.endswith('.py'):
        # Python: public if no leading underscore
        return not symbol.name.startswith('_')
    elif symbol.file.endswith(('.js', '.ts', '.jsx', '.tsx')):
        # JavaScript/TypeScript: public if no leading underscore
        return not symbol.name.startswith('_')

    # Default: consider public for unknown languages
    return True


def detect_platform_quick(project_path: Path) -> DocumentationPlatform:
    """Quick platform detection by checking for common config files.

    This is a fast, simple check for initialization purposes. For comprehensive
    detection with confidence scores, use the docmgr_detect_platform MCP tool.

    Args:
        project_path: Project root directory

    Returns:
        DocumentationPlatform enum value
    """
    if (project_path / "docsite" / "hugo.yaml").exists() or (project_path / "hugo.toml").exists():
        return DocumentationPlatform.HUGO
    elif (project_path / "docusaurus.config.js").exists():
        return DocumentationPlatform.DOCUSAURUS
    elif (project_path / "mkdocs.yml").exists():
        return DocumentationPlatform.MKDOCS
    elif (project_path / "conf.py").exists():
        return DocumentationPlatform.SPHINX
    else:
        return DocumentationPlatform.UNKNOWN
