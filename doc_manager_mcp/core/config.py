"""Configuration file management utilities.

This module provides utilities for loading and saving .doc-manager.yml
configuration files with helpful examples and documentation.
"""

from pathlib import Path
from typing import Any

import yaml


def load_config(project_path: Path) -> dict[str, Any] | None:
    """Load .doc-manager.yml configuration."""
    config_path = project_path / ".doc-manager.yml"
    if not config_path.exists():
        return None

    try:
        with open(config_path, encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def save_config(project_path: Path, config: dict[str, Any]) -> bool:
    """Save .doc-manager.yml configuration with helpful examples."""
    config_path = project_path / ".doc-manager.yml"
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            # Write main configuration
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            # Add helpful examples and documentation
            f.write("\n")
            f.write("# " + "=" * 76 + "\n")
            f.write("# Configuration Guide & Examples\n")
            f.write("# " + "=" * 76 + "\n")
            f.write("\n")
            f.write("# Exclude Patterns\n")
            f.write("# ----------------\n")
            f.write("# Use glob patterns to exclude files from documentation tracking.\n")
            f.write("# Examples:\n")
            f.write("#   exclude:\n")
            f.write("#     - \"**/node_modules/**\"     # Exclude all node_modules directories\n")
            f.write("#     - \"**/*.pyc\"               # Exclude Python bytecode files\n")
            f.write("#     - \"**/dist/**\"             # Exclude build artifacts\n")
            f.write("#     - \"**/.git/**\"             # Exclude git directory\n")
            f.write("#     - \"**/venv/**\"             # Exclude Python virtual environments\n")
            f.write("#     - \"**/__pycache__/**\"      # Exclude Python cache\n")
            f.write("\n")
            f.write("# Source Directories\n")
            f.write("# ------------------\n")
            f.write("# Additional source directories to track (relative to project root).\n")
            f.write("# Examples:\n")
            f.write("#   sources:\n")
            f.write("#     - \"src\"                    # Track src directory\n")
            f.write("#     - \"lib\"                    # Track lib directory\n")
            f.write("#     - \"packages/core\"          # Track monorepo package\n")
            f.write("\n")
            f.write("# Documentation Path\n")
            f.write("# -------------------\n")
            f.write("# Path to documentation directory (relative to project root).\n")
            f.write("# Common values: docs, doc, documentation, website/docs\n")
            f.write("\n")
            f.write("# Platform\n")
            f.write("# --------\n")
            f.write("# Documentation platform: mkdocs, sphinx, hugo, docusaurus, etc.\n")
            f.write("# Set to 'unknown' if not using a specific platform.\n")

        return True
    except Exception:
        return False
