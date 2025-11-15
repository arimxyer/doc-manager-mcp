"""Unit tests for Pydantic field validators (T020 - US2).

Tests input validation to prevent command injection and other attacks.

@spec 001
@userStory US2
@functionalReq FR-002
"""

import pytest
from pydantic import ValidationError
from src.models import MapChangesInput
from src.constants import ResponseFormat, ChangeDetectionMode


class TestCommitHashValidator:
    """Test commit hash validation to prevent command injection."""

    def test_valid_short_commit_hash(self):
        """Test that valid short commit hashes (7 chars) are accepted."""
        valid_hashes = [
            "abc1234",
            "1234567",
            "ABCDEF0",
            "a1b2c3d",
        ]

        for commit_hash in valid_hashes:
            model = MapChangesInput(
                project_path="/test/path",
                since_commit=commit_hash,
                response_format=ResponseFormat.MARKDOWN
            )
            assert model.since_commit == commit_hash

    def test_valid_full_commit_hash(self):
        """Test that valid full commit hashes (40 chars) are accepted."""
        full_hash = "a" * 40  # 40 hex characters
        model = MapChangesInput(
            project_path="/test/path",
            since_commit=full_hash,
            response_format=ResponseFormat.MARKDOWN
        )
        assert model.since_commit == full_hash

    def test_none_commit_hash_accepted(self):
        """Test that None is accepted for optional since_commit."""
        model = MapChangesInput(
            project_path="/test/path",
            since_commit=None,
            response_format=ResponseFormat.MARKDOWN
        )
        assert model.since_commit is None

    def test_reject_shell_metacharacters(self):
        """Test that shell metacharacters are rejected (command injection prevention)."""
        malicious_inputs = [
            "HEAD; rm -rf /",  # Command separator
            "abc123 && ls",  # Command chaining
            "abc123 | cat",  # Pipe
            "$(whoami)",  # Command substitution
            "`whoami`",  # Backtick command substitution
            "abc123 > /tmp/exploit",  # Redirection
            "abc123\nrm -rf /",  # Newline injection
        ]

        for malicious in malicious_inputs:
            with pytest.raises(ValidationError) as exc_info:
                MapChangesInput(
                    project_path="/test/path",
                    since_commit=malicious,
                    response_format=ResponseFormat.MARKDOWN
                )

            error = exc_info.value
            assert "Invalid git commit hash format" in str(error)

    def test_reject_too_short_hash(self):
        """Test that commit hashes shorter than 7 characters are rejected."""
        short_hashes = ["a", "ab", "abc", "abc123"]  # <7 chars

        for short_hash in short_hashes:
            with pytest.raises(ValidationError) as exc_info:
                MapChangesInput(
                    project_path="/test/path",
                    since_commit=short_hash,
                    response_format=ResponseFormat.MARKDOWN
                )

            assert "Invalid git commit hash format" in str(exc_info.value)

    def test_reject_too_long_hash(self):
        """Test that commit hashes longer than 40 characters are rejected."""
        long_hash = "a" * 41  # 41 chars (too long for SHA-1)

        with pytest.raises(ValidationError) as exc_info:
            MapChangesInput(
                project_path="/test/path",
                since_commit=long_hash,
                response_format=ResponseFormat.MARKDOWN
            )

        assert "Invalid git commit hash format" in str(exc_info.value)

    def test_reject_non_hexadecimal(self):
        """Test that non-hexadecimal characters are rejected."""
        invalid_hashes = [
            "ghijklm",  # Contains g-m (not hex)
            "abc123z",  # Contains z (not hex)
            "abc-123",  # Contains dash
            "abc 123",  # Contains space
            "abc.123",  # Contains dot
        ]

        for invalid_hash in invalid_hashes:
            with pytest.raises(ValidationError) as exc_info:
                MapChangesInput(
                    project_path="/test/path",
                    since_commit=invalid_hash,
                    response_format=ResponseFormat.MARKDOWN
                )

            assert "Invalid git commit hash format" in str(exc_info.value)

    @pytest.mark.parametrize("length", [7, 8, 10, 20, 32, 40])
    def test_various_valid_lengths(self, length):
        """Test that various valid hash lengths (7-40) are accepted."""
        valid_hash = "a" * length
        model = MapChangesInput(
            project_path="/test/path",
            since_commit=valid_hash,
            response_format=ResponseFormat.MARKDOWN
        )
        assert model.since_commit == valid_hash

    def test_error_message_helpful(self):
        """Test that validation error messages are helpful."""
        with pytest.raises(ValidationError) as exc_info:
            MapChangesInput(
                project_path="/test/path",
                since_commit="invalid!",
                response_format=ResponseFormat.MARKDOWN
            )

        error_msg = str(exc_info.value)
        # Should mention the expected format
        assert "hexadecimal" in error_msg or "7-40" in error_msg
        # Should mention security reason
        assert "command injection" in error_msg.lower()
