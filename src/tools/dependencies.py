"""Dependency tracking tools for doc-manager."""

from pathlib import Path
import json
import re
from typing import List, Dict, Any, Set
from datetime import datetime

from ..models import TrackDependenciesInput
from ..constants import ResponseFormat
from ..utils import find_docs_directory, handle_error


def _find_markdown_files(docs_path: Path) -> List[Path]:
    """Find all markdown files in documentation directory."""
    markdown_files = []
    for pattern in ["**/*.md", "**/*.markdown"]:
        markdown_files.extend(docs_path.glob(pattern))
    return sorted(markdown_files)


def _extract_code_references(content: str, doc_file: Path) -> List[Dict[str, Any]]:
    """Extract code references from documentation content."""
    references = []

    # Extract file path references (common patterns)
    # Pattern: `path/to/file.ext`
    file_path_pattern = r'`([a-zA-Z0-9_\-/.]+\.(go|py|js|ts|java|rs|rb|php|c|cpp|h|hpp|cs|swift|kt))`'
    for match in re.finditer(file_path_pattern, content):
        file_path = match.group(1)
        references.append({
            "type": "file_path",
            "reference": file_path,
            "doc_file": str(doc_file)
        })

    # Extract function/method references
    # Pattern: `functionName()` or `ClassName.methodName()`
    function_pattern = r'`([A-Z][a-zA-Z0-9]*\.)?([a-z][a-zA-Z0-9]*)\(\)`'
    for match in re.finditer(function_pattern, content):
        func_name = match.group(0).strip('`')
        references.append({
            "type": "function",
            "reference": func_name,
            "doc_file": str(doc_file)
        })

    # Extract class/type references
    # Pattern: `ClassName` (capitalized words in backticks)
    class_pattern = r'`([A-Z][a-zA-Z0-9]+)`'
    for match in re.finditer(class_pattern, content):
        class_name = match.group(1)
        # Exclude common words and single letters
        if len(class_name) > 2 and class_name not in ['API', 'CLI', 'HTTP', 'HTTPS', 'URL', 'JSON', 'XML']:
            references.append({
                "type": "class",
                "reference": class_name,
                "doc_file": str(doc_file)
            })

    # Extract command references
    # Pattern: command in code blocks or $ command
    command_patterns = [
        r'`([a-z][a-z0-9\-]+(?:\s+[a-z][a-z0-9\-]+)*)`',  # `command subcommand`
        r'\$\s+([a-z][a-z0-9\-]+(?:\s+[a-z][a-z0-9\-]+)*)'  # $ command subcommand
    ]

    for pattern in command_patterns:
        for match in re.finditer(pattern, content):
            command = match.group(1)
            # Filter out common words
            if command.split()[0] not in ['the', 'and', 'for', 'with', 'from', 'this', 'that', 'your', 'you']:
                references.append({
                    "type": "command",
                    "reference": command,
                    "doc_file": str(doc_file)
                })

    # Extract configuration keys
    # Pattern: config keys in YAML/JSON format or in backticks
    config_pattern = r'`([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)`'
    for match in re.finditer(config_pattern, content):
        config_key = match.group(1)
        references.append({
            "type": "config_key",
            "reference": config_key,
            "doc_file": str(doc_file)
        })

    return references


def _find_source_files(project_path: Path, docs_path: Path) -> List[Path]:
    """Find all source code files in the project."""
    source_files = []

    # Common source file extensions
    extensions = [
        '.go', '.py', '.js', '.ts', '.jsx', '.tsx',
        '.java', '.rs', '.rb', '.php', '.c', '.cpp',
        '.h', '.hpp', '.cs', '.swift', '.kt'
    ]

    for ext in extensions:
        pattern = f"**/*{ext}"
        for file_path in project_path.glob(pattern):
            # Exclude docs, tests, vendor, node_modules, etc.
            path_str = str(file_path)
            if any(x in path_str for x in ['node_modules', 'vendor', 'venv', '.git', 'dist', 'build']):
                continue
            if file_path.is_relative_to(docs_path):
                continue
            source_files.append(file_path)

    return source_files


def _match_references_to_sources(references: List[Dict[str, Any]], source_files: List[Path],
                                 project_path: Path) -> Dict[str, List[str]]:
    """Match documentation references to actual source files."""
    dependencies = {}  # doc_file -> [source_files]

    for ref in references:
        doc_file = ref["doc_file"]
        reference = ref["reference"]
        ref_type = ref["type"]

        if doc_file not in dependencies:
            dependencies[doc_file] = set()

        # Match file path references
        if ref_type == "file_path":
            for source_file in source_files:
                relative_path = str(source_file.relative_to(project_path))
                if reference in relative_path or relative_path.endswith(reference):
                    dependencies[doc_file].add(relative_path)

        # Match function/class references by searching in source files
        elif ref_type in ["function", "class"]:
            # Extract the identifier (without parentheses or namespace)
            identifier = reference.replace('()', '').split('.')[-1]

            for source_file in source_files:
                try:
                    with open(source_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Look for function/class definitions
                    patterns = [
                        rf'\bfunc\s+{identifier}\b',  # Go
                        rf'\bdef\s+{identifier}\b',   # Python
                        rf'\bfunction\s+{identifier}\b',  # JavaScript
                        rf'\bclass\s+{identifier}\b',  # Most languages
                        rf'\b{identifier}\s*\(',      # Function call/definition
                    ]

                    for pattern in patterns:
                        if re.search(pattern, content):
                            relative_path = str(source_file.relative_to(project_path))
                            dependencies[doc_file].add(relative_path)
                            break

                except Exception:
                    continue

        # Match command references to CLI source files
        elif ref_type == "command":
            command_name = reference.split()[0]
            for source_file in source_files:
                relative_path = str(source_file.relative_to(project_path))
                # Look for command files (e.g., cmd/add.go for "add" command)
                if f"cmd/{command_name}" in relative_path or f"cli/{command_name}" in relative_path:
                    dependencies[doc_file].add(relative_path)

    # Convert sets to sorted lists
    return {k: sorted(list(v)) for k, v in dependencies.items()}


def _build_reverse_index(dependencies: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Build reverse index: source_file -> [doc_files]."""
    reverse_index = {}

    for doc_file, source_files in dependencies.items():
        for source_file in source_files:
            if source_file not in reverse_index:
                reverse_index[source_file] = []
            reverse_index[source_file].append(doc_file)

    return reverse_index


def _save_dependencies_to_memory(project_path: Path, dependencies: Dict[str, List[str]],
                                 reverse_index: Dict[str, List[str]]):
    """Save dependency graph to memory directory."""
    memory_dir = project_path / ".doc-manager"
    if not memory_dir.exists():
        return

    dependency_file = memory_dir / "dependencies.json"

    data = {
        "generated_at": datetime.now().isoformat(),
        "doc_to_code": dependencies,
        "code_to_doc": reverse_index
    }

    try:
        with open(dependency_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def _format_dependency_report(dependencies: Dict[str, List[str]], reverse_index: Dict[str, List[str]],
                              total_references: int, response_format: ResponseFormat) -> str:
    """Format dependency tracking report."""
    if response_format == ResponseFormat.JSON:
        return json.dumps({
            "generated_at": datetime.now().isoformat(),
            "total_references": total_references,
            "total_doc_files": len(dependencies),
            "total_source_files": len(reverse_index),
            "doc_to_code": dependencies,
            "code_to_doc": reverse_index
        }, indent=2)
    else:
        lines = ["# Code-to-Documentation Dependency Graph", ""]
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total References:** {total_references}")
        lines.append(f"**Documentation Files:** {len(dependencies)}")
        lines.append(f"**Source Files Referenced:** {len(reverse_index)}")
        lines.append("")

        # Documentation → Code Dependencies
        lines.append("## Documentation → Code Dependencies")
        lines.append("")
        lines.append("Shows which source files each documentation file depends on.")
        lines.append("")

        if not dependencies:
            lines.append("No dependencies detected.")
        else:
            for doc_file in sorted(dependencies.keys()):
                source_files = dependencies[doc_file]
                if source_files:
                    lines.append(f"### {doc_file}")
                    lines.append(f"**Depends on {len(source_files)} source file(s):**")
                    for source_file in source_files:
                        lines.append(f"- `{source_file}`")
                    lines.append("")

        # Code → Documentation Reverse Index
        lines.append("## Code → Documentation Reverse Index")
        lines.append("")
        lines.append("Shows which documentation files reference each source file.")
        lines.append("")

        if not reverse_index:
            lines.append("No reverse dependencies detected.")
        else:
            # Show most-referenced files first
            sorted_sources = sorted(reverse_index.items(), key=lambda x: len(x[1]), reverse=True)

            for source_file, doc_files in sorted_sources[:20]:  # Top 20
                lines.append(f"### {source_file}")
                lines.append(f"**Referenced by {len(doc_files)} doc file(s):**")
                for doc_file in doc_files:
                    lines.append(f"- `{doc_file}`")
                lines.append("")

            if len(sorted_sources) > 20:
                lines.append(f"*... and {len(sorted_sources) - 20} more source files*")
                lines.append("")

        lines.append("## Impact Analysis")
        lines.append("")
        lines.append("Use this dependency graph to:")
        lines.append("- Identify which docs need updates when code changes")
        lines.append("- Find orphaned documentation (no code references)")
        lines.append("- Detect missing documentation for important source files")
        lines.append("")

        # Find docs with no dependencies
        orphaned_docs = [doc for doc, sources in dependencies.items() if not sources]
        if orphaned_docs:
            lines.append(f"**Orphaned Documentation ({len(orphaned_docs)} files):**")
            lines.append("These docs have no detected code references:")
            for doc in orphaned_docs[:10]:
                lines.append(f"- {doc}")
            if len(orphaned_docs) > 10:
                lines.append(f"  ... and {len(orphaned_docs) - 10} more")

        return "\n".join(lines)


async def track_dependencies(params: TrackDependenciesInput) -> str:
    """Track code-to-docs dependencies by analyzing references in documentation.

    Builds a bidirectional dependency graph:
    - Doc → Code: Which source files each doc depends on
    - Code → Doc: Which docs reference each source file

    Extracts references for:
    - File paths (e.g., `src/main.go`)
    - Functions/methods (e.g., `initialize()`, `User.save()`)
    - Classes/types (e.g., `Customer`, `HttpClient`)
    - Commands (e.g., `pass add`, `git commit`)
    - Configuration keys (e.g., `server.port`)

    Args:
        params (TrackDependenciesInput): Validated input parameters containing:
            - project_path (str): Absolute path to project root
            - response_format (ResponseFormat): Output format (markdown or json)

    Returns:
        str: Dependency graph report

    Examples:
        - Use when: Analyzing documentation coverage
        - Use when: Planning code refactoring (see impact on docs)
        - Use when: Finding orphaned documentation

    Error Handling:
        - Returns error if project_path doesn't exist
        - Returns error if docs_path not found
    """
    try:
        project_path = Path(params.project_path).resolve()

        if not project_path.exists():
            return f"Error: Project path does not exist: {project_path}"

        # Find docs directory
        docs_path = find_docs_directory(project_path)
        if not docs_path:
            return "Error: Could not find documentation directory."

        # Find all markdown files
        markdown_files = _find_markdown_files(docs_path)
        if not markdown_files:
            return f"Error: No markdown files found in {docs_path}"

        # Extract references from all docs
        all_references = []
        for md_file in markdown_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                references = _extract_code_references(content, md_file.relative_to(docs_path))
                all_references.extend(references)
            except Exception:
                continue

        # Find source files
        source_files = _find_source_files(project_path, docs_path)

        # Match references to actual source files
        dependencies = _match_references_to_sources(all_references, source_files, project_path)

        # Build reverse index
        reverse_index = _build_reverse_index(dependencies)

        # Save to memory
        _save_dependencies_to_memory(project_path, dependencies, reverse_index)

        return _format_dependency_report(dependencies, reverse_index, len(all_references), params.response_format)

    except Exception as e:
        return handle_error(e, "track_dependencies")
