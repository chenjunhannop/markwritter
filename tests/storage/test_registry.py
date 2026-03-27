"""Tests for StorageRegistry.

TDD approach: These tests define the expected behavior before implementation.
The registry routes content operations to appropriate backends.
"""

import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest

from markwritter.storage.models import (
    Content,
    ContentType,
    ContentQuery,
    StorageBackend,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_obsidian_repo() -> MagicMock:
    """Create a mock ObsidianRepository."""
    mock = MagicMock()
    mock.backend_type = StorageBackend.OBSIDIAN
    mock.supported_content_types = [ContentType.MARKDOWN]
    mock.get = AsyncMock(return_value=None)
    mock.save = AsyncMock()
    mock.delete = AsyncMock(return_value=True)
    mock.list = AsyncMock()
    mock.exists = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def mock_database_repo() -> MagicMock:
    """Create a mock DatabaseRepository."""
    mock = MagicMock()
    mock.backend_type = StorageBackend.DATABASE
    mock.supported_content_types = [
        ContentType.URL,
        ContentType.PDF,
        ContentType.HTML,
        ContentType.PLAINTEXT,
    ]
    mock.get = AsyncMock(return_value=None)
    mock.save = AsyncMock()
    mock.delete = AsyncMock(return_value=True)
    mock.list = AsyncMock()
    mock.exists = AsyncMock(return_value=False)
    return mock


@pytest.fixture
def registry() -> Generator:
    """Create a StorageRegistry instance."""
    from markwritter.storage.registry import StorageRegistry

    reg = StorageRegistry()
    yield reg


# ==============================================================================
# Registration Tests
# ==============================================================================


class TestStorageRegistryRegistration:
    """Tests for StorageRegistry registration."""

    def test_register_backend(self, registry, mock_obsidian_repo) -> None:
        """Test registering a backend."""
        registry.register(mock_obsidian_repo)

        assert registry.get_backend(StorageBackend.OBSIDIAN) is mock_obsidian_repo

    def test_register_multiple_backends(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test registering multiple backends."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        assert registry.get_backend(StorageBackend.OBSIDIAN) is mock_obsidian_repo
        assert registry.get_backend(StorageBackend.DATABASE) is mock_database_repo

    def test_get_backend_not_found(self, registry) -> None:
        """Test getting non-registered backend returns None."""
        result = registry.get_backend(StorageBackend.OBSIDIAN)

        assert result is None

    def test_get_backend_by_type(self, registry, mock_database_repo) -> None:
        """Test getting backend by type."""
        registry.register(mock_database_repo)

        result = registry.get_backend(StorageBackend.DATABASE)

        assert result is mock_database_repo


# ==============================================================================
# Content Type Routing Tests
# ==============================================================================


class TestStorageRegistryContentTypeRouting:
    """Tests for content type based routing."""

    def test_get_preferred_backend_for_markdown(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test getting preferred backend for MARKDOWN content."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        result = registry.get_preferred_backend(ContentType.MARKDOWN)

        assert result is mock_obsidian_repo

    def test_get_preferred_backend_for_url(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test getting preferred backend for URL content."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        result = registry.get_preferred_backend(ContentType.URL)

        assert result is mock_database_repo

    def test_get_preferred_backend_for_pdf(
        self,
        registry,
        mock_database_repo,
    ) -> None:
        """Test getting preferred backend for PDF content."""
        registry.register(mock_database_repo)

        result = registry.get_preferred_backend(ContentType.PDF)

        assert result is mock_database_repo

    def test_get_preferred_backend_not_found(self, registry) -> None:
        """Test getting preferred backend when none registered."""
        result = registry.get_preferred_backend(ContentType.MARKDOWN)

        assert result is None


# ==============================================================================
# Operation Routing Tests
# ==============================================================================


class TestStorageRegistryOperations:
    """Tests for operation routing."""

    @pytest.mark.asyncio
    async def test_save_routes_to_correct_backend(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test that save routes to correct backend based on content type."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        content = Content(
            id="test.md",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content="Test content",
        )

        await registry.save(content)

        mock_obsidian_repo.save.assert_called_once_with(content)
        mock_database_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_save_routes_url_to_database(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test that save routes URL content to database backend."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        content = Content(
            id="url-001",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="URL content",
        )

        await registry.save(content)

        mock_database_repo.save.assert_called_once_with(content)
        mock_obsidian_repo.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_by_backend_type(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test get by content ID and backend type."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        # Setup mock to return content
        mock_content = Content(
            id="test.md",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
        )
        mock_obsidian_repo.get.return_value = mock_content

        result = await registry.get("test.md", backend=StorageBackend.OBSIDIAN)

        assert result is mock_content
        mock_obsidian_repo.get.assert_called_once_with("test.md")

    @pytest.mark.asyncio
    async def test_get_searches_all_backends(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test get searches all registered backends."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        # Only database has the content
        mock_content = Content(
            id="url-001",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
        )
        mock_obsidian_repo.get.return_value = None
        mock_database_repo.get.return_value = mock_content

        result = await registry.get("url-001")

        assert result is mock_content

    @pytest.mark.asyncio
    async def test_list_aggregates_from_all_backends(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test list aggregates results from all backends."""
        from markwritter.storage.models import ContentListResult, ContentRef

        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        # Setup mocks
        obsidian_result = ContentListResult(
            items=[
                ContentRef(
                    id="note.md",
                    source_type=ContentType.MARKDOWN,
                    storage_backend=StorageBackend.OBSIDIAN,
                )
            ],
            total=1,
            limit=100,
            offset=0,
        )
        database_result = ContentListResult(
            items=[
                ContentRef(
                    id="url-001",
                    source_type=ContentType.URL,
                    storage_backend=StorageBackend.DATABASE,
                )
            ],
            total=1,
            limit=100,
            offset=0,
        )

        mock_obsidian_repo.list.return_value = obsidian_result
        mock_database_repo.list.return_value = database_result

        result = await registry.list(ContentQuery())

        assert result.total == 2
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_list_filters_by_backend(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test list can filter by specific backend."""
        from markwritter.storage.models import ContentListResult, ContentRef

        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        obsidian_result = ContentListResult(
            items=[
                ContentRef(
                    id="note.md",
                    source_type=ContentType.MARKDOWN,
                    storage_backend=StorageBackend.OBSIDIAN,
                )
            ],
            total=1,
            limit=100,
            offset=0,
        )
        mock_obsidian_repo.list.return_value = obsidian_result

        result = await registry.list(
            ContentQuery(storage_backends=[StorageBackend.OBSIDIAN])
        )

        mock_obsidian_repo.list.assert_called_once()
        mock_database_repo.list.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_from_correct_backend(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test delete from correct backend."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        # Setup mock to indicate content exists
        mock_obsidian_repo.exists.return_value = True

        result = await registry.delete("test.md")

        mock_obsidian_repo.delete.assert_called_once_with("test.md")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, registry) -> None:
        """Test delete when content not found."""
        result = await registry.delete("nonexistent")

        assert result is False


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestStorageRegistryErrors:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_save_no_backend_registered(self, registry) -> None:
        """Test save when no backend is registered raises error."""
        from markwritter.storage.base import StorageError

        content = Content(
            id="test.md",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
        )

        with pytest.raises(StorageError):
            await registry.save(content)

    @pytest.mark.asyncio
    async def test_save_unsupported_content_type(
        self,
        registry,
        mock_obsidian_repo,
    ) -> None:
        """Test save with content type not supported by any backend."""
        from markwritter.storage.base import StorageError

        registry.register(mock_obsidian_repo)

        # URL is not supported by Obsidian
        content = Content(
            id="url-001",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
        )

        with pytest.raises(StorageError):
            await registry.save(content)


# ==============================================================================
# Backend Priority Tests
# ==============================================================================


class TestStorageRegistryPriority:
    """Tests for backend priority."""

    def test_first_registered_is_preferred(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test that first registered backend is preferred for overlapping content types."""
        # Both support MARKDOWN if we modify mock_database_repo
        mock_database_repo.supported_content_types = [
            ContentType.URL,
            ContentType.PDF,
            ContentType.MARKDOWN,  # Also supports markdown
        ]

        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        # Obsidian was registered first, should be preferred
        result = registry.get_preferred_backend(ContentType.MARKDOWN)

        assert result is mock_obsidian_repo


# ==============================================================================
# Registry State Tests
# ==============================================================================


class TestStorageRegistryState:
    """Tests for registry state."""

    def test_registered_backends_property(
        self,
        registry,
        mock_obsidian_repo,
        mock_database_repo,
    ) -> None:
        """Test listing registered backends."""
        registry.register(mock_obsidian_repo)
        registry.register(mock_database_repo)

        backends = registry.registered_backends

        assert StorageBackend.OBSIDIAN in backends
        assert StorageBackend.DATABASE in backends
        assert len(backends) == 2

    def test_clear_registry(self, registry, mock_obsidian_repo) -> None:
        """Test clearing all registered backends."""
        registry.register(mock_obsidian_repo)
        registry.clear()

        assert registry.get_backend(StorageBackend.OBSIDIAN) is None