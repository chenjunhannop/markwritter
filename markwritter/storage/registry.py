"""Storage registry for routing content operations.

This module provides StorageRegistry, which routes content operations
to the appropriate backend based on content type and storage preferences.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from markwritter.storage.base import ContentRepository, StorageError
from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentQuery,
    ContentRef,
    ContentType,
    StorageBackend,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class StorageRegistry:
    """Registry for content storage backends.

    Routes content operations to appropriate backends based on:
    - Content type (MARKDOWN -> Obsidian, URL/PDF -> Database)
    - Explicit backend preference
    - Registration order (first registered is preferred)

    Example:
        >>> registry = StorageRegistry()
        >>> registry.register(obsidian_repo)
        >>> registry.register(database_repo)
        >>>
        >>> # Routes to Obsidian
        >>> content = await registry.get("note.md")
        >>>
        >>> # Routes to Database
        >>> content = await registry.get("url-001", backend=StorageBackend.DATABASE)
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._backends: dict[StorageBackend, ContentRepository] = {}
        self._type_preferences: dict[ContentType, StorageBackend] = {}

    @property
    def registered_backends(self) -> list[StorageBackend]:
        """Return list of registered backend types."""
        return list(self._backends.keys())

    def register(self, backend: ContentRepository) -> None:
        """Register a storage backend.

        Args:
            backend: Backend implementing ContentRepository protocol
        """
        self._backends[backend.backend_type] = backend

        # Update content type preferences
        for content_type in backend.supported_content_types:
            if content_type not in self._type_preferences:
                self._type_preferences[content_type] = backend.backend_type

        logger.info(
            f"Registered backend {backend.backend_type.value} "
            f"supporting {[t.value for t in backend.supported_content_types]}"
        )

    def get_backend(
        self, backend_type: StorageBackend
    ) -> Optional[ContentRepository]:
        """Get backend by type.

        Args:
            backend_type: Type of backend to retrieve

        Returns:
            Backend instance if registered, None otherwise
        """
        return self._backends.get(backend_type)

    def get_preferred_backend(
        self, content_type: ContentType
    ) -> Optional[ContentRepository]:
        """Get preferred backend for content type.

        Args:
            content_type: Type of content

        Returns:
            Preferred backend if available, None otherwise
        """
        backend_type = self._type_preferences.get(content_type)
        if backend_type:
            return self._backends.get(backend_type)
        return None

    def clear(self) -> None:
        """Clear all registered backends."""
        self._backends.clear()
        self._type_preferences.clear()

    # ==============================================================================
    # Content Operations
    # ==============================================================================

    async def save(self, content: Content) -> Content:
        """Save content to appropriate backend.

        Routes based on storage_backend field in content.

        Args:
            content: Content to save

        Returns:
            Saved content

        Raises:
            StorageError: If no backend is registered for the content type
        """
        # Use explicit backend from content
        backend = self._backends.get(content.storage_backend)

        if backend is None:
            raise StorageError(
                f"No backend registered for {content.storage_backend.value}"
            )

        # Check if backend supports this content type
        if content.source_type not in backend.supported_content_types:
            raise StorageError(
                f"Backend {backend.backend_type.value} does not support "
                f"content type {content.source_type.value}"
            )

        return await backend.save(content)

    async def get(
        self,
        content_id: str,
        backend: Optional[StorageBackend] = None,
    ) -> Optional[Content]:
        """Get content by ID.

        Searches all backends if no specific backend is provided.

        Args:
            content_id: Content ID to retrieve
            backend: Optional specific backend to search

        Returns:
            Content if found, None otherwise
        """
        if backend:
            # Search specific backend
            repo = self._backends.get(backend)
            if repo:
                return await repo.get(content_id)
            return None

        # Search all backends
        for repo in self._backends.values():
            content = await repo.get(content_id)
            if content is not None:
                return content

        return None

    async def list(self, query: ContentQuery) -> ContentListResult:
        """List content matching query.

        Aggregates results from all backends unless filtered.

        Args:
            query: Query parameters

        Returns:
            Aggregated and paginated results
        """
        if query.storage_backends:
            # Query specific backends
            all_refs: list[ContentRef] = []
            total = 0

            for backend_type in query.storage_backends:
                repo = self._backends.get(backend_type)
                if repo:
                    result = await repo.list(query)
                    all_refs.extend(result.items)
                    total += result.total

            # Sort by creation date (handle None values)
            all_refs.sort(
                key=lambda x: x.created or datetime.min,
                reverse=True,
            )

            # Apply pagination to combined results
            paginated = all_refs[query.offset : query.offset + query.limit]

            return ContentListResult(
                items=paginated,
                total=total,
                limit=query.limit,
                offset=query.offset,
            )

        # Query all backends
        all_refs = []
        total = 0

        for repo in self._backends.values():
            try:
                result = await repo.list(query)
                all_refs.extend(result.items)
                total += result.total
            except Exception as e:
                logger.warning(f"Error listing from backend: {e}")
                continue

        # Sort by creation date (handle None values)
        all_refs.sort(
            key=lambda x: x.created or datetime.min,
            reverse=True,
        )

        # Apply pagination
        paginated = all_refs[query.offset : query.offset + query.limit]

        return ContentListResult(
            items=paginated,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )

    async def delete(
        self,
        content_id: str,
        backend: Optional[StorageBackend] = None,
    ) -> bool:
        """Delete content.

        Args:
            content_id: ID of content to delete
            backend: Optional specific backend to delete from

        Returns:
            True if deleted, False if not found
        """
        if backend:
            # Delete from specific backend
            repo = self._backends.get(backend)
            if repo:
                return await repo.delete(content_id)
            return False

        # Try all backends
        for repo in self._backends.values():
            if await repo.exists(content_id):
                return await repo.delete(content_id)

        return False


__all__ = ["StorageRegistry"]