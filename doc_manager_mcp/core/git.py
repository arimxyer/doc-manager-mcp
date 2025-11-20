"""Git command execution utilities.

This module provides secure git command execution with proper error handling,
timeouts, and validation.
"""

from pathlib import Path


async def run_git_command(cwd: Path, *args, check_git_available: bool = True) -> str | None:
    """Run a git command and return output.

    Args:
        cwd: Working directory for git command
        *args: Git command arguments (e.g., "status", "--short")
        check_git_available: Whether to check git binary availability first

    Returns:
        Command output if successful, None otherwise

    Raises:
        RuntimeError: If git binary is not found (T018 - FR-002)

    Security:
        - Uses array form to prevent command injection
        - 30-second timeout to prevent hangs
        - Git availability check with clear error message
    """
    import asyncio
    import shutil

    # Check if git is available in PATH (T018)
    if check_git_available:
        if shutil.which('git') is None:
            raise RuntimeError(
                "Git is required but not found. Please install git and ensure it's in your PATH. "
                "Visit https://git-scm.com/downloads for installation instructions."
            )

    try:
        # Security: Using array form with hardcoded "git" binary and validated args
        # to prevent command injection. All args are from trusted internal sources.
        proc = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.DEVNULL,  # Prevent hanging on Windows
        )

        # 30-second timeout (T019)
        stdout, _stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

        if proc.returncode == 0:
            return stdout.decode().strip()
        else:
            return None
    except FileNotFoundError as err:
        # Git binary not found even after check
        raise RuntimeError("Git is required but not found. Please install git.") from err
    except asyncio.TimeoutError:
        return None
    except Exception:
        return None
