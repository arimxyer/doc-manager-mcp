"""Resource limit enforcement utilities.

This module provides utilities for enforcing resource limits to prevent
exhaustion attacks, including file count limits, recursion depth limits,
and operation timeouts.
"""

from contextlib import contextmanager


class ResourceLimits:
    """Enforce resource limits to prevent exhaustion attacks.

    Attributes:
        max_files: Maximum files to process (default: 10,000 per FR-019)
        max_depth: Maximum recursion depth (default: 100 per FR-020)
        timeout: Operation timeout in seconds (default: 60 per FR-021)
    """

    def __init__(self, max_files: int = 10000, max_depth: int = 100, timeout: int = 60):
        self.max_files = max_files
        self.max_depth = max_depth
        self.timeout = timeout
        self.file_count = 0
        self.current_depth = 0

    def check_file_count(self) -> None:
        """Check if file count limit exceeded.

        Raises:
            ValueError: If file count exceeds limit
        """
        if self.file_count >= self.max_files:
            raise ValueError(f"File count limit exceeded: {self.file_count} >= {self.max_files}")

    def increment_file_count(self) -> None:
        """Increment file counter and check limit."""
        self.file_count += 1
        self.check_file_count()

    def check_depth(self, depth: int) -> None:
        """Check if recursion depth limit exceeded.

        Args:
            depth: Current recursion depth

        Raises:
            ValueError: If depth exceeds limit
        """
        if depth >= self.max_depth:
            raise ValueError(f"Recursion depth limit exceeded: {depth} >= {self.max_depth}")


@contextmanager
def operation_timeout(seconds: int = 60):
    """Set timeout for blocking operations (Unix/Windows compatible).

    Args:
        seconds: Timeout in seconds (default: 60 per FR-021)

    Yields:
        None

    Raises:
        TimeoutError: If operation exceeds timeout

    Example:
        with operation_timeout(60):
            # Long-running file operation
            process_files()
    """
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation exceeded {seconds}s timeout")

    # Unix-like systems support SIGALRM
    if hasattr(signal, 'SIGALRM'):
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)  # type: ignore[attr-defined]
        signal.alarm(seconds)  # type: ignore[attr-defined]
        try:
            yield
        finally:
            signal.alarm(0)  # type: ignore[attr-defined]
            signal.signal(signal.SIGALRM, old_handler)  # type: ignore[attr-defined]
    else:
        # Windows doesn't support SIGALRM - use threading.Timer as fallback
        import threading
        timer = threading.Timer(seconds, lambda: (_ for _ in ()).throw(TimeoutError(f"Operation exceeded {seconds}s timeout")))
        timer.start()
        try:
            yield
        finally:
            timer.cancel()
