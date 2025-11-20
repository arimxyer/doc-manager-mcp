"""Workflow orchestration modules for doc-manager.

This package contains high-level workflow orchestration functions that
coordinate multiple tools to accomplish complex documentation tasks.

Available workflows:
- migrate: Restructure existing documentation to a new organization
- sync: Keep documentation aligned with code changes
"""

from .migrate import migrate
from .sync import sync

__all__ = ["migrate", "sync"]
