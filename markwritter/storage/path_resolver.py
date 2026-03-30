"""Path to ContentID mapping layer.

This module provides PathResolver, which maintains a bidirectional mapping
between file paths (from Obsidian vault) and content IDs (UUIDs used in vector index).

Features:
- Bidirectional mapping: path → content_id and content_id → path
- In-memory caching for performance
- Support for file rename handling
- Integration with ContentService for metadata lookup
"""

import logging
from typing import Optional

from markwritter.storage.models import Content, ContentRef
from markwritter.storage.service import ContentService

logger = logging.getLogger(__name__)


class PathResolver:
    """Path to ContentID mapping resolver.

    Maintains bidirectional mapping between file paths and content IDs.
    Used for translating selected_sources (file paths) to content_ids
    for vector index retrieval.

    Example:
        >>> resolver = PathResolver(content_service)
        >>>
        >>> # Get content_id for a file path
        >>> content_id = await resolver.path_to_id("notes/ML/transformer.md")
        >>>
        >>> # Get file path for a content_id
        >>> path = await resolver.id_to_path(content_id)
        >>>
        >>> # Batch resolve multiple paths
        >>> ids = await resolver.batch_path_to_id(["a.md", "b.md"])
    """

    def __init__(self, content_service: ContentService) -> None:
        """Initialize path resolver.

        Args:
            content_service: ContentService instance for metadata lookup
        """
        self._content_service = content_service
        # In-memory caches for fast lookup
        self._path_to_id_cache: dict[str, str] = {}
        self._id_to_path_cache: dict[str, str] = {}

    async def path_to_id(self, file_path: str) -> Optional[str]:
        """Convert file path to content_id.

        Args:
            file_path: File path in Obsidian vault (relative or absolute)

        Returns:
            Content ID if found, None if not indexed

        Raises:
            ValueError: If file_path is empty or invalid
        """
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")

        # Normalize path
        normalized_path = file_path.strip()

        # Check cache first
        if normalized_path in self._path_to_id_cache:
            logger.debug(f"Cache hit for path: {normalized_path}")
            return self._path_to_id_cache[normalized_path]

        # Lookup in ContentService
        content = await self._lookup_by_path(normalized_path)
        if content is None:
            logger.debug(f"No content found for path: {normalized_path}")
            return None

        # Update caches
        content_id = content.id
        self._path_to_id_cache[normalized_path] = content_id
        self._id_to_path_cache[content_id] = normalized_path

        logger.debug(f"Mapped path '{normalized_path}' → content_id '{content_id}'")
        return content_id

    async def id_to_path(self, content_id: str) -> Optional[str]:
        """Convert content_id to file path.

        Args:
            content_id: Content ID from vector index

        Returns:
            File path if found, None if not indexed

        Raises:
            ValueError: If content_id is empty or invalid
        """
        if not content_id or not content_id.strip():
            raise ValueError("content_id cannot be empty")

        # Check cache first
        if content_id in self._id_to_path_cache:
            logger.debug(f"Cache hit for id: {content_id}")
            return self._id_to_path_cache[content_id]

        # Lookup in ContentService
        content = await self._content_service.get(content_id)
        if content is None:
            logger.debug(f"No content found for id: {content_id}")
            return None

        # Extract path from content
        path = content.source_path
        if path is None:
            logger.debug(f"Content {content_id} has no source_path")
            return None

        # Update caches
        self._id_to_path_cache[content_id] = path
        self._path_to_id_cache[path] = content_id

        logger.debug(f"Mapped content_id '{content_id}' → path '{path}'")
        return path

    async def batch_path_to_id(
        self,
        file_paths: list[str],
    ) -> dict[str, Optional[str]]:
        """Batch convert multiple file paths to content_ids.

        Args:
            file_paths: List of file paths to resolve

        Returns:
            Dictionary mapping paths to content_ids (None if not found)
        """
        result: dict[str, Optional[str]] = {}
        for path in file_paths:
            result[path] = await self.path_to_id(path)
        return result

    async def batch_id_to_path(
        self,
        content_ids: list[str],
    ) -> dict[str, Optional[str]]:
        """Batch convert multiple content_ids to file paths.

        Args:
            content_ids: List of content IDs to resolve

        Returns:
            Dictionary mapping content_ids to paths (None if not found)
        """
        result: dict[str, Optional[str]] = {}
        for content_id in content_ids:
            result[content_id] = await self.id_to_path(content_id)
        return result

    async def resolve_sources(
        self,
        source_paths: list[str],
    ) -> list[str]:
        """Resolve a list of source paths to content_ids.

        Filters out paths that cannot be resolved (not indexed).

        Args:
            source_paths: List of file paths from selected_sources

        Returns:
            List of resolved content_ids (only found items)
        """
        resolved = await self.batch_path_to_id(source_paths)
        # Filter out None values
        content_ids = [cid for cid in resolved.values() if cid is not None]
        logger.info(
            f"Resolved {len(content_ids)}/{len(source_paths)} sources to content_ids"
        )
        return content_ids

    async def refresh_path(self, file_path: str) -> Optional[str]:
        """Refresh cache for a specific path.

        Use this when you know a file has been modified and want to
        ensure the latest mapping.

        Args:
            file_path: File path to refresh

        Returns:
            Updated content_id if found, None if not indexed
        """
        # Remove from cache if exists
        normalized_path = file_path.strip()
        old_id = self._path_to_id_cache.pop(normalized_path, None)
        if old_id:
            self._id_to_path_cache.pop(old_id, None)

        # Re-resolve
        return await self.path_to_id(normalized_path)

    async def handle_file_rename(
        self,
        old_path: str,
        new_path: str,
    ) -> bool:
        """Handle file rename by updating cache.

        When a file is renamed in the vault, this method updates the
        internal mapping to reflect the change.

        Args:
            old_path: Original file path
            new_path: New file path after rename

        Returns:
            True if successfully updated, False if old_path not found
        """
        old_id = self._path_to_id_cache.pop(old_path, None)
        if old_id is None:
            logger.debug(f"Cannot handle rename: old_path '{old_path}' not in cache")
            return False

        # Update caches
        self._path_to_id_cache[new_path] = old_id
        self._id_to_path_cache[old_id] = new_path

        logger.info(f"Handled file rename: '{old_path}' → '{new_path}'")
        return True

    def clear_cache(self) -> None:
        """Clear all cached mappings.

        Use this when you want to force a full refresh from ContentService.
        """
        self._path_to_id_cache.clear()
        self._id_to_path_cache.clear()
        logger.info("PathResolver cache cleared")

    def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "path_to_id_cache_size": len(self._path_to_id_cache),
            "id_to_path_cache_size": len(self._id_to_path_cache),
        }

    # ==============================================================================
    # Private Helpers
    # ==============================================================================

    async def _lookup_by_path(self, file_path: str) -> Optional[Content]:
        """Lookup content by file path.

        Uses ContentService to find content with matching source_path.

        Args:
            file_path: File path to lookup

        Returns:
            Content if found, None otherwise
        """
        # List content with path_prefix filter
        from markwritter.storage.models import ContentQuery

        query = ContentQuery(path_prefix=file_path, limit=1)
        result = await self._content_service.list(query)

        # Find exact match
        for item in result.items:
            if item.path == file_path:
                # Fetch full content
                return await self._content_service.get(item.id)

        return None


__all__ = ["PathResolver"]
