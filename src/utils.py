"""Utility functions for doc-manager MCP server."""

from typing import Optional, Dict, Any
from pathlib import Path
import hashlib
import subprocess
import yaml

def calculate_checksum(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return ""

def run_git_command(cwd: Path, *args) -> Optional[str]:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None

def detect_project_language(project_path: Path) -> str:
    """Detect primary programming language of project."""
    language_indicators = {
        "go.mod": "Go",
        "package.json": "JavaScript/TypeScript",
        "Cargo.toml": "Rust",
        "requirements.txt": "Python",
        "setup.py": "Python",
        "pom.xml": "Java",
        "build.gradle": "Java",
        "Gemfile": "Ruby",
        "composer.json": "PHP"
    }

    for file, language in language_indicators.items():
        if (project_path / file).exists():
            return language

    return "Unknown"

def find_docs_directory(project_path: Path) -> Optional[Path]:
    """Find documentation directory in project."""
    common_doc_dirs = ["docs", "doc", "documentation", "docsite", "website/docs"]

    for dir_name in common_doc_dirs:
        doc_path = project_path / dir_name
        if doc_path.exists() and doc_path.is_dir():
            return doc_path

    return None

def load_config(project_path: Path) -> Optional[Dict[str, Any]]:
    """Load .doc-manager.yml configuration."""
    config_path = project_path / ".doc-manager.yml"
    if not config_path.exists():
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return None

def save_config(project_path: Path, config: Dict[str, Any]) -> bool:
    """Save .doc-manager.yml configuration."""
    config_path = project_path / ".doc-manager.yml"
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception:
        return False

def handle_error(e: Exception, context: str = "") -> str:
    """Consistent error formatting across all tools."""
    error_msg = f"Error: {type(e).__name__}"
    if context:
        error_msg += f" in {context}"
    error_msg += f": {str(e)}"
    return error_msg
