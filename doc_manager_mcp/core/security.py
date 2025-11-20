"""Security utilities for file locking and safe operations.

This module provides cross-platform file locking utilities to prevent
concurrent access issues and ensure data integrity.
"""

import platform
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def file_lock(file_path: Path, timeout: int = 5, retries: int = 3):
    """Acquire exclusive file lock with timeout and retry (cross-platform).

    Args:
        file_path: Path to file to lock
        timeout: Lock acquisition timeout in seconds (default: 5 per clarification)
        retries: Number of retry attempts (default: 3 per clarification)

    Yields:
        None when lock is acquired

    Raises:
        TimeoutError: If lock cannot be acquired after all retries

    Example:
        with file_lock(baseline_path):
            # Read/write state file safely
            data = json.load(f)
    """

    lock_file_path = file_path.with_suffix(file_path.suffix + '.lock')
    lock_handle = None
    acquired = False

    try:
        for attempt in range(retries):
            try:
                # Create lock file
                lock_handle = open(lock_file_path, 'w')

                # Platform-specific locking
                if platform.system() == 'Windows':
                    import msvcrt
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl  # type: ignore[attr-defined]
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]

                acquired = True
                break  # Lock acquired successfully
            except OSError as e:
                if attempt < retries - 1:
                    # Wait before retry
                    time.sleep(1)
                    continue
                else:
                    # Final attempt failed
                    raise TimeoutError(f"Failed to acquire lock on {file_path.name} after {retries} attempts ({timeout}s timeout)") from e

        yield  # Lock held, execute critical section

    finally:
        # Always release lock
        if acquired and lock_handle:
            try:
                if platform.system() == 'Windows':
                    import msvcrt
                    msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl  # type: ignore[attr-defined]
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)  # type: ignore[attr-defined]
            except Exception:  # noqa: S110
                # Best effort release - failures during cleanup are non-critical
                pass

        if lock_handle:
            lock_handle.close()

        # Remove lock file
        try:
            if lock_file_path.exists():
                lock_file_path.unlink()
        except Exception:  # noqa: S110
            # Best effort cleanup - lock file removal failures are non-critical
            pass
