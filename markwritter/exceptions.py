"""Centralized exception definitions for Markwritter.

This module provides a unified exception hierarchy for the entire application:
- MarkwritterError: Base exception for all custom errors
- VaultError: Base exception for vault operations
- InvalidVaultError: Raised when vault path is invalid
- NoteNotFoundError: Raised when a note cannot be found
- NodeNotFoundError: Raised when a graph node cannot be found
- LLMError: LLM API errors
"""


class MarkwritterError(Exception):
    """Base exception for all Markwritter errors.

    All custom exceptions in Markwritter should inherit from this class.
    This allows catching all application-specific errors with a single except clause.

    Example:
        try:
            # Some operation
            pass
        except MarkwritterError as e:
            # Handle any Markwritter-specific error
            print(f"Application error: {e}")
    """

    pass


class VaultError(MarkwritterError):
    """Base exception for vault operations.

    All vault-related errors inherit from this class.

    Example:
        try:
            vault.read_note("missing.md")
        except VaultError as e:
            # Handle any vault-related error
            print(f"Vault error: {e}")
    """

    pass


class InvalidVaultError(VaultError):
    """Raised when vault path is invalid.

    This error is raised when:
    - Vault path does not exist
    - Vault path is not a directory
    - Vault path lacks required permissions

    Example:
        if not vault_path.exists():
            raise InvalidVaultError(f"Vault path does not exist: {vault_path}")
    """

    pass


class NoteNotFoundError(VaultError):
    """Raised when a note cannot be found.

    This error is raised when attempting to access a note that does not exist
    in the vault.

    Example:
        if not note_exists:
            raise NoteNotFoundError(f"Note not found: {note_path}")
    """

    pass


class NodeNotFoundError(MarkwritterError):
    """Raised when a graph node cannot be found.

    This error is raised when attempting to access a node in the knowledge graph
    that does not exist.

    Note: This does not inherit from VaultError as it relates to the graph
    structure, not vault file operations.

    Example:
        if node_id not in graph_nodes:
            raise NodeNotFoundError(f"Node not found: {node_id}")
    """

    pass


class LLMError(MarkwritterError):
    """LLM API error.

    This error is raised when:
    - LLM API call fails
    - Rate limit is exceeded
    - Invalid API response is received
    - Model is unavailable

    Example:
        try:
            response = await llm_client.generate(prompt)
        except Exception as e:
            raise LLMError(f"LLM API error: {e}")
    """

    pass


__all__ = [
    "MarkwritterError",
    "VaultError",
    "InvalidVaultError",
    "NoteNotFoundError",
    "NodeNotFoundError",
    "LLMError",
]
