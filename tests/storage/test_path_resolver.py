"""Tests for PathResolver.

TDD approach: These tests define the expected behavior before implementation.
PathResolver provides bidirectional mapping between file paths and content IDs.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentQuery,
    ContentRef,
    ContentType,
    StorageBackend,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_content_service() -> MagicMock:
    """Create a mock ContentService."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.list = AsyncMock()
    mock.save = AsyncMock()
    mock.delete = AsyncMock(return_value=False)
    return mock


@pytest.fixture
async def path_resolver(mock_content_service) -> "PathResolver":
    """Create a PathResolver instance."""
    from markwritter.storage.path_resolver import PathResolver

    resolver = PathResolver(content_service=mock_content_service)
    yield resolver


# ==============================================================================
# Path to ID Tests
# ==============================================================================


class TestPathToId:
    """Tests for path_to_id method."""

    @pytest.mark.asyncio
    async def test_path_to_id_existing_path(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test converting existing file path to content_id."""
        # Setup mock
        mock_content = Content(
            id="uuid-12345",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content="Test content",
            title="Test Note",
            source_path="notes/test.md",
        )
        mock_list_result = ContentListResult(
            items=[
                ContentRef(
                    id="uuid-12345",
                    source_type=ContentType.MARKDOWN,
                    storage_backend=StorageBackend.OBSIDIAN,
                    path="notes/test.md",
                )
            ],
            total=1,
            limit=1,
            offset=0,
        )
        mock_content_service.list.return_value = mock_list_result
        mock_content_service.get.return_value = mock_content

        result = await path_resolver.path_to_id("notes/test.md")

        assert result == "uuid-12345"

    @pytest.mark.asyncio
    async def test_path_to_id_nonexistent_path(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test converting non-existent path returns None."""
        mock_list_result = ContentListResult(
            items=[],
            total=0,
            limit=1,
            offset=0,
        )
        mock_content_service.list.return_value = mock_list_result

        result = await path_resolver.path_to_id("nonexistent.md")

        assert result is None

    @pytest.mark.asyncio
    async def test_path_to_id_cache_hit(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that cached paths don't query ContentService."""
        # First call - populates cache
        path_resolver._path_to_id_cache["cached.md"] = "cached-uuid"
        path_resolver._id_to_path_cache["cached-uuid"] = "cached.md"

        result = await path_resolver.path_to_id("cached.md")

        assert result == "cached-uuid"
        mock_content_service.list.assert_not_called()

    @pytest.mark.asyncio
    async def test_path_to_id_empty_path(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that empty path raises ValueError."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            await path_resolver.path_to_id("")

    @pytest.mark.asyncio
    async def test_path_to_id_whitespace_path(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that whitespace-only path raises ValueError."""
        with pytest.raises(ValueError, match="file_path cannot be empty"):
            await path_resolver.path_to_id("   ")

    @pytest.mark.asyncio
    async def test_path_to_id_normalizes_path(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that path is normalized (whitespace stripped)."""
        mock_content = Content(
            id="uuid-67890",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            source_path="notes/clean.md",
        )
        mock_list_result = ContentListResult(
            items=[
                ContentRef(
                    id="uuid-67890",
                    source_type=ContentType.MARKDOWN,
                    storage_backend=StorageBackend.OBSIDIAN,
                    path="notes/clean.md",
                )
            ],
            total=1,
            limit=1,
            offset=0,
        )
        mock_content_service.list.return_value = mock_list_result
        mock_content_service.get.return_value = mock_content

        # Path with leading/trailing whitespace
        result = await path_resolver.path_to_id("  notes/clean.md  ")

        assert result == "uuid-67890"


# ==============================================================================
# ID to Path Tests
# ==============================================================================


class TestIdToPath:
    """Tests for id_to_path method."""

    @pytest.mark.asyncio
    async def test_id_to_path_existing_id(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test converting existing content_id to path."""
        mock_content = Content(
            id="test-uuid",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            source_path="notes/from-id.md",
        )
        mock_content_service.get.return_value = mock_content

        result = await path_resolver.id_to_path("test-uuid")

        assert result == "notes/from-id.md"

    @pytest.mark.asyncio
    async def test_id_to_path_nonexistent_id(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test converting non-existent ID returns None."""
        mock_content_service.get.return_value = None

        result = await path_resolver.id_to_path("nonexistent-uuid")

        assert result is None

    @pytest.mark.asyncio
    async def test_id_to_path_cache_hit(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that cached IDs don't query ContentService."""
        path_resolver._id_to_path_cache["cached-uuid"] = "cached-path.md"
        path_resolver._path_to_id_cache["cached-path.md"] = "cached-uuid"

        result = await path_resolver.id_to_path("cached-uuid")

        assert result == "cached-path.md"
        mock_content_service.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_id_to_path_empty_id(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="content_id cannot be empty"):
            await path_resolver.id_to_path("")

    @pytest.mark.asyncio
    async def test_id_to_path_no_source_path(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test content without source_path returns None."""
        mock_content = Content(
            id="no-path-uuid",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            # No source_path
        )
        mock_content_service.get.return_value = mock_content

        result = await path_resolver.id_to_path("no-path-uuid")

        assert result is None


# ==============================================================================
# Batch Operations Tests
# ==============================================================================


class TestBatchOperations:
    """Tests for batch operations."""

    @pytest.mark.asyncio
    async def test_batch_path_to_id(self, path_resolver, mock_content_service) -> None:
        """Test batch converting multiple paths to IDs."""
        # Setup mocks
        async def mock_path_to_id(path: str):
            mapping = {
                "a.md": "uuid-a",
                "b.md": "uuid-b",
                "nonexistent.md": None,
            }
            return mapping.get(path)

        # Patch the method
        original = path_resolver.path_to_id
        path_resolver.path_to_id = mock_path_to_id

        result = await path_resolver.batch_path_to_id(["a.md", "b.md", "nonexistent.md"])

        assert result == {"a.md": "uuid-a", "b.md": "uuid-b", "nonexistent.md": None}

        # Restore
        path_resolver.path_to_id = original

    @pytest.mark.asyncio
    async def test_batch_id_to_path(self, path_resolver, mock_content_service) -> None:
        """Test batch converting multiple IDs to paths."""
        # Setup mocks
        async def mock_id_to_path(cid: str):
            mapping = {
                "uuid-a": "a.md",
                "uuid-b": "b.md",
                "uuid-c": None,
            }
            return mapping.get(cid)

        original = path_resolver.id_to_path
        path_resolver.id_to_path = mock_id_to_path

        result = await path_resolver.batch_id_to_path(["uuid-a", "uuid-b", "uuid-c"])

        assert result == {"uuid-a": "a.md", "uuid-b": "b.md", "uuid-c": None}

        path_resolver.id_to_path = original


# ==============================================================================
# Resolve Sources Tests
# ==============================================================================


class TestResolveSources:
    """Tests for resolve_sources method."""

    @pytest.mark.asyncio
    async def test_resolve_sources_filters_none(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that resolve_sources filters out unresolved paths."""
        # Setup mocks
        async def mock_path_to_id(path: str):
            mapping = {
                "found1.md": "uuid-1",
                "found2.md": "uuid-2",
                "not-found.md": None,
            }
            return mapping.get(path)

        original = path_resolver.path_to_id
        path_resolver.path_to_id = mock_path_to_id

        result = await path_resolver.resolve_sources(
            ["found1.md", "found2.md", "not-found.md"]
        )

        assert result == ["uuid-1", "uuid-2"]

        path_resolver.path_to_id = original

    @pytest.mark.asyncio
    async def test_resolve_sources_empty_input(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test resolve_sources with empty input."""
        result = await path_resolver.resolve_sources([])
        assert result == []


# ==============================================================================
# Cache Management Tests
# ==============================================================================


class TestCacheManagement:
    """Tests for cache management methods."""

    @pytest.mark.asyncio
    async def test_refresh_path_updates_cache(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test that refresh_path updates cache."""
        # Setup initial cache
        path_resolver._path_to_id_cache["old.md"] = "old-uuid"
        path_resolver._id_to_path_cache["old-uuid"] = "old.md"

        # Setup mock for re-fetch
        mock_content = Content(
            id="new-uuid",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            source_path="old.md",
        )
        mock_list_result = ContentListResult(
            items=[
                ContentRef(
                    id="new-uuid",
                    source_type=ContentType.MARKDOWN,
                    storage_backend=StorageBackend.OBSIDIAN,
                    path="old.md",
                )
            ],
            total=1,
            limit=1,
            offset=0,
        )
        mock_content_service.list.return_value = mock_list_result
        mock_content_service.get.return_value = mock_content

        result = await path_resolver.refresh_path("old.md")

        # Cache should be updated
        assert path_resolver._path_to_id_cache["old.md"] == "new-uuid"
        assert result == "new-uuid"

    @pytest.mark.asyncio
    async def test_clear_cache(self, path_resolver, mock_content_service) -> None:
        """Test clear_cache removes all entries."""
        path_resolver._path_to_id_cache["a.md"] = "uuid-a"
        path_resolver._id_to_path_cache["uuid-a"] = "a.md"

        path_resolver.clear_cache()

        assert len(path_resolver._path_to_id_cache) == 0
        assert len(path_resolver._id_to_path_cache) == 0

    @pytest.mark.asyncio
    async def test_get_cache_stats(self, path_resolver, mock_content_service) -> None:
        """Test get_cache_stats returns correct counts."""
        path_resolver._path_to_id_cache["a.md"] = "uuid-a"
        path_resolver._path_to_id_cache["b.md"] = "uuid-b"
        path_resolver._id_to_path_cache["uuid-a"] = "a.md"

        stats = path_resolver.get_cache_stats()

        assert stats["path_to_id_cache_size"] == 2
        assert stats["id_to_path_cache_size"] == 1


# ==============================================================================
# File Rename Tests
# ==============================================================================


class TestFileRename:
    """Tests for file rename handling."""

    @pytest.mark.asyncio
    async def test_handle_file_rename_success(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test handling successful file rename."""
        path_resolver._path_to_id_cache["old.md"] = "uuid-123"
        path_resolver._id_to_path_cache["uuid-123"] = "old.md"

        result = await path_resolver.handle_file_rename("old.md", "new.md")

        assert result is True
        assert "old.md" not in path_resolver._path_to_id_cache
        assert path_resolver._path_to_id_cache["new.md"] == "uuid-123"
        assert path_resolver._id_to_path_cache["uuid-123"] == "new.md"

    @pytest.mark.asyncio
    async def test_handle_file_rename_old_path_not_found(
        self, path_resolver, mock_content_service
    ) -> None:
        """Test handling rename when old path not in cache."""
        result = await path_resolver.handle_file_rename("nonexistent.md", "new.md")

        assert result is False
        assert "nonexistent.md" not in path_resolver._path_to_id_cache
        assert "new.md" not in path_resolver._path_to_id_cache
