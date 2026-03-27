"""Content service for unified content operations.

This module provides ContentService, which offers a high-level API
for content management with automatic routing and validation.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from markwritter.storage.base import StorageError
from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentQuery,
    ContentRef,
    ContentType,
    StorageBackend,
)

if TYPE_CHECKING:
    from markwritter.storage.registry import StorageRegistry

logger = logging.getLogger(__name__)


class ContentService:
    """High-level content management service.

    Provides a unified interface for content operations with:
    - Automatic ID generation
    - Timestamp management
    - Simplified search interface

    Example:
        >>> service = ContentService(registry=registry)
        >>>
        >>> # Save content
        >>> content = Content(...)
        >>> saved = await service.save(content)
        >>>
        >>> # Search
        >>> results = await service.search("python tutorial")
    """

    def __init__(self, registry: StorageRegistry) -> None:
        """Initialize content service.

        Args:
            registry: Storage registry for backend routing
        """
        self._registry = registry

    @property
    def registry(self) -> StorageRegistry:
        """Return storage registry."""
        return self._registry

    async def get(
        self,
        content_id: str,
        backend: Optional[StorageBackend] = None,
    ) -> Optional[Content]:
        """Get content by ID.

        Args:
            content_id: Content ID to retrieve
            backend: Optional specific backend to search

        Returns:
            Content if found, None otherwise
        """
        return await self._registry.get(content_id, backend=backend)

    async def list(self, query: ContentQuery) -> ContentListResult:
        """List content matching query.

        Args:
            query: Query parameters

        Returns:
            Paginated results
        """
        return await self._registry.list(query)

    async def save(self, content: Content) -> Content:
        """Save content.

        Automatically generates ID and sets timestamps if not provided.

        Args:
            content: Content to save

        Returns:
            Saved content with ID and timestamps set

        Raises:
            StorageError: If save fails
        """
        # Generate ID if not provided
        if not content.id:
            content.id = self._generate_id()

        # Set timestamps
        now = datetime.now()
        if content.created is None:
            content.created = now
        content.modified = now

        return await self._registry.save(content)

    async def delete(self, content_id: str) -> bool:
        """Delete content by ID.

        Args:
            content_id: ID of content to delete

        Returns:
            True if deleted, False if not found
        """
        return await self._registry.delete(content_id)

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[ContentRef]:
        """Search for content by keyword.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching content references
        """
        if not query or not query.strip():
            return []

        result = await self._registry.list(
            ContentQuery(query=query.strip(), limit=limit)
        )

        return result.items

    async def vector_search(
        self,
        embedding: list[float],
        limit: int = 10,
    ) -> list[ContentRef]:
        """Search for similar content using vector embedding.

        Args:
            embedding: Query embedding vector
            limit: Maximum results

        Returns:
            List of similar content references
        """
        # Get database backend for vector search
        db_backend = self._registry.get_backend(StorageBackend.DATABASE)

        if db_backend is None:
            logger.warning("No database backend registered for vector search")
            return []

        # Check if backend supports vector search
        if hasattr(db_backend, "vector_search"):
            return await db_backend.vector_search(embedding, limit=limit)

        logger.warning("Database backend does not support vector search")
        return []

    # ==============================================================================
    # Private Helpers
    # ==============================================================================

    def _generate_id(self) -> str:
        """Generate unique content ID.

        Returns:
            UUID-based unique ID
        """
        return str(uuid.uuid4())


__all__ = ["ContentService"]