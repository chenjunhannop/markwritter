"""Base module for storage abstraction.

This module defines:
- ContentRepository: Protocol for content storage backends
- StorageError: Base exception for storage operations
- ContentNotFoundError: Exception for content not found
"""

from typing import Protocol, runtime_checkable

from markwritter.exceptions import MarkwritterError
from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentQuery,
    ContentType,
    StorageBackend,
)


class StorageError(MarkwritterError):
    """Base exception for storage operations.

    All storage-related errors inherit from this class.
    """

    pass


class ContentNotFoundError(StorageError):
    """Raised when content cannot be found.

    This error is raised when attempting to access content that does not exist
    in the storage backend.
    """

    pass


@runtime_checkable
class ContentRepository(Protocol):
    """Protocol for content storage backends.

    Defines the interface that all storage backends must implement.
    This enables polymorphic storage - the same code can work with
    Obsidian, databases, object stores, etc.
    """

    @property
    def backend_type(self) -> StorageBackend:
        """Return the storage backend type.

        Returns:
            StorageBackend enum value
        """
        ...

    @property
    def supported_content_types(self) -> list[ContentType]:
        """Return list of supported content types.

        Returns:
            List of ContentType enum values this backend supports
        """
        ...

    async def get(self, content_id: str) -> Content | None:
        """Get content by ID.

        Args:
            content_id: Unique identifier for the content

        Returns:
            Content object if found, None otherwise
        """
        ...

    async def get_by_path(self, path: str) -> Content | None:
        """Get content by path.

        Args:
            path: Path to the content

        Returns:
            Content object if found, None otherwise
        """
        ...

    async def list(self, query: ContentQuery) -> ContentListResult:
        """List content matching query parameters.

        Args:
            query: Query parameters for filtering and pagination

        Returns:
            Paginated result with ContentRef items
        """
        ...

    async def save(self, content: Content) -> Content:
        """Save content to storage.

        Args:
            content: Content to save

        Returns:
            Saved content object
        """
        ...

    async def delete(self, content_id: str) -> bool:
        """Delete content by ID.

        Args:
            content_id: ID of content to delete

        Returns:
            True if deleted, False if not found
        """
        ...

    async def exists(self, content_id: str) -> bool:
        """Check if content exists.

        Args:
            content_id: ID of content to check

        Returns:
            True if content exists, False otherwise
        """
        ...


__all__ = [
    "StorageError",
    "ContentNotFoundError",
    "ContentRepository",
]
