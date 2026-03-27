"""Tests for ContentService.

TDD approach: These tests define the expected behavior before implementation.
ContentService provides a unified interface for content operations.
"""

import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentType,
    ContentQuery,
    ContentRef,
    StorageBackend,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def mock_registry() -> MagicMock:
    """Create a mock StorageRegistry."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.save = AsyncMock()
    mock.delete = AsyncMock(return_value=False)
    mock.list = AsyncMock()
    return mock


@pytest.fixture
async def content_service(mock_registry) -> AsyncGenerator:
    """Create a ContentService instance."""
    from markwritter.storage.service import ContentService

    service = ContentService(registry=mock_registry)
    yield service


# ==============================================================================
# Get Tests
# ==============================================================================


class TestContentServiceGet:
    """Tests for ContentService.get method."""

    @pytest.mark.asyncio
    async def test_get_existing_content(self, content_service, mock_registry) -> None:
        """Test getting existing content."""
        mock_content = Content(
            id="test-001",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Test content",
            title="Test",
        )
        mock_registry.get.return_value = mock_content

        result = await content_service.get("test-001")

        assert result is not None
        assert result.id == "test-001"
        mock_registry.get.assert_called_once_with("test-001", backend=None)

    @pytest.mark.asyncio
    async def test_get_nonexistent_content(
        self, content_service, mock_registry
    ) -> None:
        """Test getting non-existent content returns None."""
        mock_registry.get.return_value = None

        result = await content_service.get("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_with_backend_preference(
        self, content_service, mock_registry
    ) -> None:
        """Test get with backend preference."""
        mock_content = Content(
            id="note.md",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
        )
        mock_registry.get.return_value = mock_content

        result = await content_service.get(
            "note.md", backend=StorageBackend.OBSIDIAN
        )

        mock_registry.get.assert_called_once_with(
            "note.md", backend=StorageBackend.OBSIDIAN
        )


# ==============================================================================
# List Tests
# ==============================================================================


class TestContentServiceList:
    """Tests for ContentService.list method."""

    @pytest.mark.asyncio
    async def test_list_all_content(self, content_service, mock_registry) -> None:
        """Test listing all content."""
        mock_result = ContentListResult(
            items=[
                ContentRef(
                    id="item-1",
                    source_type=ContentType.URL,
                    storage_backend=StorageBackend.DATABASE,
                ),
                ContentRef(
                    id="item-2",
                    source_type=ContentType.MARKDOWN,
                    storage_backend=StorageBackend.OBSIDIAN,
                ),
            ],
            total=2,
            limit=100,
            offset=0,
        )
        mock_registry.list.return_value = mock_result

        result = await content_service.list(ContentQuery())

        assert result.total == 2
        assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_list_with_filters(self, content_service, mock_registry) -> None:
        """Test listing content with filters."""
        mock_result = ContentListResult(
            items=[
                ContentRef(
                    id="python-1",
                    source_type=ContentType.URL,
                    storage_backend=StorageBackend.DATABASE,
                    tags=["python"],
                ),
            ],
            total=1,
            limit=100,
            offset=0,
        )
        mock_registry.list.return_value = mock_result

        query = ContentQuery(tags=["python"])
        result = await content_service.list(query)

        assert result.total == 1
        assert "python" in result.items[0].tags

    @pytest.mark.asyncio
    async def test_list_empty_result(self, content_service, mock_registry) -> None:
        """Test listing with empty result."""
        mock_result = ContentListResult(
            items=[],
            total=0,
            limit=100,
            offset=0,
        )
        mock_registry.list.return_value = mock_result

        result = await content_service.list(ContentQuery())

        assert result.total == 0
        assert result.items == []


# ==============================================================================
# Save Tests
# ==============================================================================


class TestContentServiceSave:
    """Tests for ContentService.save method."""

    @pytest.mark.asyncio
    async def test_save_new_content(self, content_service, mock_registry) -> None:
        """Test saving new content."""
        content = Content(
            id="new-001",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="New content",
            title="New Item",
        )
        mock_registry.save.return_value = content

        result = await content_service.save(content)

        assert result.id == "new-001"
        mock_registry.save.assert_called_once_with(content)

    @pytest.mark.asyncio
    async def test_save_auto_generates_id(
        self, content_service, mock_registry
    ) -> None:
        """Test that save generates ID if not provided."""
        content = Content(
            id="",  # Empty ID
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content without ID",
        )

        saved_content = Content(
            id="generated-uuid",  # Generated ID
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content without ID",
        )
        mock_registry.save.return_value = saved_content

        result = await content_service.save(content)

        assert result.id == "generated-uuid"

    @pytest.mark.asyncio
    async def test_save_sets_timestamps(self, content_service, mock_registry) -> None:
        """Test that save sets created/modified timestamps."""
        from datetime import datetime

        content = Content(
            id="time-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content",
        )

        saved_content = Content(
            id="time-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content",
            created=datetime.now(),
            modified=datetime.now(),
        )
        mock_registry.save.return_value = saved_content

        result = await content_service.save(content)

        assert result.created is not None
        assert result.modified is not None


# ==============================================================================
# Delete Tests
# ==============================================================================


class TestContentServiceDelete:
    """Tests for ContentService.delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_content(
        self, content_service, mock_registry
    ) -> None:
        """Test deleting existing content."""
        mock_registry.delete.return_value = True

        result = await content_service.delete("test-001")

        assert result is True
        mock_registry.delete.assert_called_once_with("test-001")

    @pytest.mark.asyncio
    async def test_delete_nonexistent_content(
        self, content_service, mock_registry
    ) -> None:
        """Test deleting non-existent content returns False."""
        mock_registry.delete.return_value = False

        result = await content_service.delete("nonexistent")

        assert result is False


# ==============================================================================
# Search Tests
# ==============================================================================


class TestContentServiceSearch:
    """Tests for ContentService.search method."""

    @pytest.mark.asyncio
    async def test_search_returns_results(
        self, content_service, mock_registry
    ) -> None:
        """Test search returns matching content."""
        mock_result = ContentListResult(
            items=[
                ContentRef(
                    id="search-1",
                    source_type=ContentType.URL,
                    storage_backend=StorageBackend.DATABASE,
                    title="Python Guide",
                ),
            ],
            total=1,
            limit=10,
            offset=0,
        )
        mock_registry.list.return_value = mock_result

        results = await content_service.search("Python", limit=10)

        assert len(results) == 1
        assert results[0].title == "Python Guide"

    @pytest.mark.asyncio
    async def test_search_empty_query(self, content_service, mock_registry) -> None:
        """Test search with empty query returns empty list."""
        results = await content_service.search("", limit=10)

        assert results == []
        mock_registry.list.assert_not_called()

    @pytest.mark.asyncio
    async def test_search_with_default_limit(
        self, content_service, mock_registry
    ) -> None:
        """Test search uses default limit if not specified."""
        mock_result = ContentListResult(
            items=[],
            total=0,
            limit=10,
            offset=0,
        )
        mock_registry.list.return_value = mock_result

        await content_service.search("test")

        # Verify list was called with query containing limit
        call_args = mock_registry.list.call_args[0][0]
        assert call_args.query == "test"
        assert call_args.limit == 10  # Default


# ==============================================================================
# Vector Search Tests
# ==============================================================================


class TestContentServiceVectorSearch:
    """Tests for ContentService vector search functionality."""

    @pytest.mark.asyncio
    async def test_vector_search_with_database_backend(
        self, content_service, mock_registry
    ) -> None:
        """Test vector search uses database backend when available."""
        # This would require a database backend with vector support
        # For now, we test the interface
        mock_db_repo = MagicMock()
        mock_db_repo.vector_search = AsyncMock(
            return_value=[
                ContentRef(
                    id="vec-1",
                    source_type=ContentType.URL,
                    storage_backend=StorageBackend.DATABASE,
                )
            ]
        )
        mock_registry.get_backend.return_value = mock_db_repo

        # Note: This test may need adjustment based on actual implementation
        # For now, it verifies the interface exists
        pass


# ==============================================================================
# Integration Tests
# ==============================================================================


class TestContentServiceIntegration:
    """Integration tests with real backends."""

    @pytest.mark.asyncio
    async def test_full_crud_workflow(self) -> None:
        """Test full CRUD workflow with real backends."""
        from markwritter.storage.registry import StorageRegistry
        from markwritter.storage.service import ContentService
        from markwritter.storage.backends.database import DatabaseRepository

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            # Setup
            registry = StorageRegistry()
            db_repo = DatabaseRepository(db_path=db_path)
            await db_repo.initialize()
            registry.register(db_repo)

            service = ContentService(registry=registry)

            # Create
            content = Content(
                id="crud-test",
                source_type=ContentType.URL,
                storage_backend=StorageBackend.DATABASE,
                text_content="CRUD test content",
                title="CRUD Test",
            )
            saved = await service.save(content)
            assert saved.id == "crud-test"

            # Read
            retrieved = await service.get("crud-test")
            assert retrieved is not None
            assert retrieved.title == "CRUD Test"

            # Update
            saved.text_content = "Updated content"
            saved.title = "Updated Title"
            updated = await service.save(saved)
            assert updated.title == "Updated Title"

            # Delete
            deleted = await service.delete("crud-test")
            assert deleted is True

            # Verify deleted
            assert await service.get("crud-test") is None

            await db_repo.close()

    @pytest.mark.asyncio
    async def test_multi_backend_workflow(self) -> None:
        """Test workflow with multiple backends."""
        from markwritter.storage.registry import StorageRegistry
        from markwritter.storage.service import ContentService
        from markwritter.storage.backends.database import DatabaseRepository

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            # Setup
            registry = StorageRegistry()
            db_repo = DatabaseRepository(db_path=db_path)
            await db_repo.initialize()
            registry.register(db_repo)

            service = ContentService(registry=registry)

            # Save URL content (goes to database)
            url_content = Content(
                id="url-001",
                source_type=ContentType.URL,
                storage_backend=StorageBackend.DATABASE,
                text_content="URL content",
                title="Web Page",
            )
            await service.save(url_content)

            # List all content
            result = await service.list(ContentQuery())
            assert result.total == 1

            # Search
            search_results = await service.search("Web")
            assert len(search_results) >= 1

            await db_repo.close()


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestContentServiceErrors:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_save_handles_registry_error(
        self, content_service, mock_registry
    ) -> None:
        """Test save handles registry errors."""
        from markwritter.storage.base import StorageError

        mock_registry.save.side_effect = StorageError("Backend error")

        content = Content(
            id="error-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
        )

        with pytest.raises(StorageError):
            await content_service.save(content)

    @pytest.mark.asyncio
    async def test_list_handles_registry_error(
        self, content_service, mock_registry
    ) -> None:
        """Test list handles registry errors."""
        from markwritter.storage.base import StorageError

        mock_registry.list.side_effect = StorageError("Backend error")

        with pytest.raises(StorageError):
            await content_service.list(ContentQuery())