"""Tests for storage base module - ContentRepository protocol.

TDD approach: These tests define the expected behavior before implementation.
"""

import tempfile
from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest

from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentType,
    ContentQuery,
    ContentRef,
    StorageBackend,
)


class TestContentRepositoryProtocol:
    """Tests for ContentRepository protocol definition."""

    def test_protocol_has_backend_type_property(self) -> None:
        """Test that protocol defines backend_type property."""
        from markwritter.storage.base import ContentRepository

        # Check that backend_type is defined
        assert hasattr(ContentRepository, "backend_type")

    def test_protocol_has_supported_content_types_property(self) -> None:
        """Test that protocol defines supported_content_types property."""
        from markwritter.storage.base import ContentRepository

        assert hasattr(ContentRepository, "supported_content_types")

    def test_protocol_has_get_method(self) -> None:
        """Test that protocol defines async get method."""
        from markwritter.storage.base import ContentRepository

        assert hasattr(ContentRepository, "get")

    def test_protocol_has_get_by_path_method(self) -> None:
        """Test that protocol defines async get_by_path method."""
        from markwritter.storage.base import ContentRepository

        assert hasattr(ContentRepository, "get_by_path")

    def test_protocol_has_list_method(self) -> None:
        """Test that protocol defines async list method."""
        from markwritter.storage.base import ContentRepository

        assert hasattr(ContentRepository, "list")

    def test_protocol_has_save_method(self) -> None:
        """Test that protocol defines async save method."""
        from markwritter.storage.base import ContentRepository

        assert hasattr(ContentRepository, "save")

    def test_protocol_has_delete_method(self) -> None:
        """Test that protocol defines async delete method."""
        from markwritter.storage.base import ContentRepository

        assert hasattr(ContentRepository, "delete")

    def test_protocol_has_exists_method(self) -> None:
        """Test that protocol defines async exists method."""
        from markwritter.storage.base import ContentRepository

        assert hasattr(ContentRepository, "exists")


class TestMockRepositoryImplementation:
    """Test that a mock implementation satisfies the protocol."""

    def test_mock_implementation_satisfies_protocol(self) -> None:
        """Test that MockRepository correctly implements the protocol."""

        class MockRepository:
            """Mock implementation for testing."""

            @property
            def backend_type(self) -> StorageBackend:
                return StorageBackend.DATABASE

            @property
            def supported_content_types(self) -> list[ContentType]:
                return [ContentType.MARKDOWN, ContentType.PDF]

            async def get(self, content_id: str) -> Content | None:
                return None

            async def get_by_path(self, path: str) -> Content | None:
                return None

            async def list(self, query: ContentQuery) -> ContentListResult:
                return ContentListResult(items=[], total=0, limit=100, offset=0)

            async def save(self, content: Content) -> Content:
                return content

            async def delete(self, content_id: str) -> bool:
                return False

            async def exists(self, content_id: str) -> bool:
                return False

        # Should be able to create instance
        repo = MockRepository()
        assert repo.backend_type == StorageBackend.DATABASE
        assert ContentType.MARKDOWN in repo.supported_content_types


class TestRepositoryExceptions:
    """Tests for repository-specific exceptions."""

    def test_storage_error_exists(self) -> None:
        """Test StorageError exception exists."""
        from markwritter.storage.base import StorageError

        with pytest.raises(StorageError):
            raise StorageError("Test error")

    def test_content_not_found_error_exists(self) -> None:
        """Test ContentNotFoundError exception exists."""
        from markwritter.storage.base import ContentNotFoundError

        with pytest.raises(ContentNotFoundError):
            raise ContentNotFoundError("Not found")

    def test_content_not_found_inherits_from_storage_error(self) -> None:
        """Test ContentNotFoundError inherits from StorageError."""
        from markwritter.storage.base import ContentNotFoundError, StorageError

        assert issubclass(ContentNotFoundError, StorageError)

    def test_storage_error_inherits_from_markwritter_error(self) -> None:
        """Test StorageError inherits from MarkwritterError."""
        from markwritter.exceptions import MarkwritterError
        from markwritter.storage.base import StorageError

        assert issubclass(StorageError, MarkwritterError)