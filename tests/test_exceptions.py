"""Tests for centralized exception module.

Test coverage for markwritter/exceptions.py
"""

import pytest

# These imports should fail initially (RED phase)
from markwritter.exceptions import (
    InvalidVaultError,
    LLMError,
    MarkwritterError,
    NodeNotFoundError,
    NoteNotFoundError,
    VaultError,
)


class TestMarkwritterError:
    """Test the base exception class."""

    def test_is_exception_subclass(self) -> None:
        """MarkwritterError should be a subclass of Exception."""
        assert issubclass(MarkwritterError, Exception)

    def test_can_be_raised(self) -> None:
        """MarkwritterError should be raisable with a message."""
        with pytest.raises(MarkwritterError) as exc_info:
            raise MarkwritterError("Test error")
        assert str(exc_info.value) == "Test error"

    def test_can_be_caught_as_base_exception(self) -> None:
        """MarkwritterError should be catchable as Exception."""
        with pytest.raises(Exception):
            raise MarkwritterError("Base error")


class TestVaultError:
    """Test VaultError exception class."""

    def test_inherits_from_markwritter_error(self) -> None:
        """VaultError should inherit from MarkwritterError."""
        assert issubclass(VaultError, MarkwritterError)

    def test_inherits_from_exception(self) -> None:
        """VaultError should be a subclass of Exception."""
        assert issubclass(VaultError, Exception)

    def test_can_be_raised_with_message(self) -> None:
        """VaultError should be raisable with a message."""
        with pytest.raises(VaultError) as exc_info:
            raise VaultError("Vault operation failed")
        assert str(exc_info.value) == "Vault operation failed"

    def test_can_be_caught_as_markwritter_error(self) -> None:
        """VaultError should be catchable as MarkwritterError."""
        with pytest.raises(MarkwritterError):
            raise VaultError("Caught as MarkwritterError")


class TestInvalidVaultError:
    """Test InvalidVaultError exception class."""

    def test_inherits_from_vault_error(self) -> None:
        """InvalidVaultError should inherit from VaultError."""
        assert issubclass(InvalidVaultError, VaultError)

    def test_inherits_from_markwritter_error(self) -> None:
        """InvalidVaultError should inherit from MarkwritterError."""
        assert issubclass(InvalidVaultError, MarkwritterError)

    def test_can_be_raised_with_path(self) -> None:
        """InvalidVaultError should be raisable with vault path."""
        with pytest.raises(InvalidVaultError) as exc_info:
            raise InvalidVaultError("Vault path does not exist: /invalid/path")
        assert "does not exist" in str(exc_info.value)

    def test_can_be_caught_as_vault_error(self) -> None:
        """InvalidVaultError should be catchable as VaultError."""
        with pytest.raises(VaultError):
            raise InvalidVaultError("Caught as VaultError")


class TestNoteNotFoundError:
    """Test NoteNotFoundError exception class."""

    def test_inherits_from_vault_error(self) -> None:
        """NoteNotFoundError should inherit from VaultError."""
        assert issubclass(NoteNotFoundError, VaultError)

    def test_inherits_from_markwritter_error(self) -> None:
        """NoteNotFoundError should inherit from MarkwritterError."""
        assert issubclass(NoteNotFoundError, MarkwritterError)

    def test_can_be_raised_with_note_path(self) -> None:
        """NoteNotFoundError should be raisable with note path."""
        with pytest.raises(NoteNotFoundError) as exc_info:
            raise NoteNotFoundError("Note not found: missing.md")
        assert "not found" in str(exc_info.value)

    def test_can_be_caught_as_vault_error(self) -> None:
        """NoteNotFoundError should be catchable as VaultError."""
        with pytest.raises(VaultError):
            raise NoteNotFoundError("Caught as VaultError")


class TestNodeNotFoundError:
    """Test NodeNotFoundError exception class."""

    def test_inherits_from_markwritter_error(self) -> None:
        """NodeNotFoundError should inherit from MarkwritterError."""
        assert issubclass(NodeNotFoundError, MarkwritterError)

    def test_does_not_inherit_from_vault_error(self) -> None:
        """NodeNotFoundError should NOT inherit from VaultError."""
        assert not issubclass(NodeNotFoundError, VaultError)

    def test_can_be_raised_with_node_id(self) -> None:
        """NodeNotFoundError should be raisable with node id."""
        with pytest.raises(NodeNotFoundError) as exc_info:
            raise NodeNotFoundError("Node not found: graph-node-123")
        assert "Node not found" in str(exc_info.value)


class TestLLMError:
    """Test LLMError exception class."""

    def test_inherits_from_markwritter_error(self) -> None:
        """LLMError should inherit from MarkwritterError."""
        assert issubclass(LLMError, MarkwritterError)

    def test_does_not_inherit_from_vault_error(self) -> None:
        """LLMError should NOT inherit from VaultError."""
        assert not issubclass(LLMError, VaultError)

    def test_can_be_raised_with_api_error(self) -> None:
        """LLMError should be raisable with API error message."""
        with pytest.raises(LLMError) as exc_info:
            raise LLMError("LLM API rate limit exceeded")
        assert "rate limit" in str(exc_info.value)


class TestExceptionHierarchy:
    """Test the overall exception hierarchy."""

    def test_vault_errors_can_be_caught_together(self) -> None:
        """All vault-related errors should be catchable as VaultError."""
        errors = [
            InvalidVaultError("Invalid vault"),
            NoteNotFoundError("Note missing"),
        ]

        for error in errors:
            with pytest.raises(VaultError):
                raise error

    def test_all_errors_can_be_caught_as_markwritter_error(self) -> None:
        """All custom errors should be catchable as MarkwritterError."""
        errors = [
            VaultError("Vault error"),
            InvalidVaultError("Invalid vault"),
            NoteNotFoundError("Note missing"),
            NodeNotFoundError("Node missing"),
            LLMError("LLM error"),
        ]

        for error in errors:
            with pytest.raises(MarkwritterError):
                raise error

    def test_exception_isolation(self) -> None:
        """VaultError should not catch non-vault errors."""
        # NodeNotFoundError should NOT be caught as VaultError
        try:
            raise NodeNotFoundError("Node missing")
        except VaultError:
            pytest.fail("NodeNotFoundError should not be caught as VaultError")
        except MarkwritterError:
            pass  # Expected

        # LLMError should NOT be caught as VaultError
        try:
            raise LLMError("LLM error")
        except VaultError:
            pytest.fail("LLMError should not be caught as VaultError")
        except MarkwritterError:
            pass  # Expected