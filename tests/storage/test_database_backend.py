"""Tests for DatabaseRepository backend.

TDD approach: These tests define the expected behavior before implementation.
This backend provides SQLite-based storage for non-Markdown content types.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Generator
import hashlib

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
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield db_path


@pytest.fixture
async def db_repo(temp_db_path: Path) -> AsyncGenerator:
    """Create a DatabaseRepository instance."""
    # Import here to allow tests to run before implementation
    from markwritter.storage.backends.database import DatabaseRepository

    repo = DatabaseRepository(db_path=temp_db_path)
    await repo.initialize()
    yield repo
    await repo.close()


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content."""
    return hashlib.sha256(content.encode()).hexdigest()


# ==============================================================================
# Initialization Tests
# ==============================================================================


class TestDatabaseRepositoryInit:
    """Tests for DatabaseRepository initialization."""

    def test_init_with_path(self, temp_db_path: Path) -> None:
        """Test initialization with database path."""
        from markwritter.storage.backends.database import DatabaseRepository

        repo = DatabaseRepository(db_path=temp_db_path)

        assert repo.backend_type == StorageBackend.DATABASE
        assert ContentType.URL in repo.supported_content_types
        assert ContentType.PDF in repo.supported_content_types
        assert ContentType.HTML in repo.supported_content_types
        assert ContentType.PLAINTEXT in repo.supported_content_types

    def test_init_with_string_path(self, temp_db_path: Path) -> None:
        """Test initialization with string path."""
        from markwritter.storage.backends.database import DatabaseRepository

        repo = DatabaseRepository(db_path=str(temp_db_path))

        assert repo.backend_type == StorageBackend.DATABASE

    @pytest.mark.asyncio
    async def test_initialize_creates_tables(self, temp_db_path: Path) -> None:
        """Test that initialize creates required tables."""
        import aiosqlite

        from markwritter.storage.backends.database import DatabaseRepository

        repo = DatabaseRepository(db_path=temp_db_path)
        await repo.initialize()

        # Check tables exist
        async with aiosqlite.connect(temp_db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='contents'"
            )
            result = await cursor.fetchone()
            assert result is not None

            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='contents_fts'"
            )
            result = await cursor.fetchone()
            assert result is not None

            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='content_vectors'"
            )
            result = await cursor.fetchone()
            assert result is not None

        await repo.close()


# ==============================================================================
# Get Tests
# ==============================================================================


class TestDatabaseRepositoryGet:
    """Tests for DatabaseRepository.get method."""

    @pytest.mark.asyncio
    async def test_get_existing_content(self, db_repo) -> None:
        """Test getting existing content by ID."""
        content = Content(
            id="test-001",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Test content for URL",
            title="Test URL",
            source_url="https://example.com/test",
            tags=["test", "example"],
        )

        await db_repo.save(content)
        retrieved = await db_repo.get("test-001")

        assert retrieved is not None
        assert retrieved.id == "test-001"
        assert retrieved.title == "Test URL"
        assert retrieved.source_type == ContentType.URL
        assert retrieved.storage_backend == StorageBackend.DATABASE
        assert "test" in retrieved.tags

    @pytest.mark.asyncio
    async def test_get_nonexistent_content(self, db_repo) -> None:
        """Test getting non-existent content returns None."""
        retrieved = await db_repo.get("nonexistent-id")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_get_content_with_raw_bytes(self, db_repo) -> None:
        """Test getting content with raw binary data."""
        raw_data = b"Binary PDF content here"
        content = Content(
            id="pdf-001",
            source_type=ContentType.PDF,
            storage_backend=StorageBackend.DATABASE,
            text_content="Extracted text from PDF",
            raw_content=raw_data,
            title="Test PDF",
            mime_type="application/pdf",
        )

        await db_repo.save(content)
        retrieved = await db_repo.get("pdf-001")

        assert retrieved is not None
        assert retrieved.raw_content == raw_data
        assert retrieved.mime_type == "application/pdf"

    @pytest.mark.asyncio
    async def test_get_by_path(self, db_repo) -> None:
        """Test getting content by path."""
        content = Content(
            id="path-test",
            source_type=ContentType.HTML,
            storage_backend=StorageBackend.DATABASE,
            text_content="HTML content",
            title="HTML Page",
            storage_path="saved/pages/test.html",
        )

        await db_repo.save(content)
        retrieved = await db_repo.get_by_path("saved/pages/test.html")

        assert retrieved is not None
        assert retrieved.id == "path-test"


# ==============================================================================
# List Tests
# ==============================================================================


class TestDatabaseRepositoryList:
    """Tests for DatabaseRepository.list method."""

    @pytest.mark.asyncio
    async def test_list_all_content(self, db_repo) -> None:
        """Test listing all content."""
        # Save multiple content items
        for i in range(5):
            content = Content(
                id=f"list-test-{i}",
                source_type=ContentType.URL,
                storage_backend=StorageBackend.DATABASE,
                text_content=f"Content {i}",
                title=f"Item {i}",
            )
            await db_repo.save(content)

        result = await db_repo.list(ContentQuery())

        assert result.total == 5
        assert len(result.items) == 5

    @pytest.mark.asyncio
    async def test_list_with_tag_filter(self, db_repo) -> None:
        """Test listing content with tag filter."""
        # Save content with different tags
        content1 = Content(
            id="tag-test-1",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Python content",
            title="Python Article",
            tags=["python", "programming"],
        )
        content2 = Content(
            id="tag-test-2",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="JavaScript content",
            title="JS Article",
            tags=["javascript", "programming"],
        )

        await db_repo.save(content1)
        await db_repo.save(content2)

        result = await db_repo.list(ContentQuery(tags=["python"]))

        assert result.total == 1
        assert result.items[0].id == "tag-test-1"

    @pytest.mark.asyncio
    async def test_list_with_source_type_filter(self, db_repo) -> None:
        """Test listing content with source type filter."""
        content1 = Content(
            id="type-url",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="URL content",
            title="URL Item",
        )
        content2 = Content(
            id="type-pdf",
            source_type=ContentType.PDF,
            storage_backend=StorageBackend.DATABASE,
            text_content="PDF content",
            title="PDF Item",
        )

        await db_repo.save(content1)
        await db_repo.save(content2)

        result = await db_repo.list(ContentQuery(source_types=[ContentType.PDF]))

        assert result.total == 1
        assert result.items[0].source_type == ContentType.PDF

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, db_repo) -> None:
        """Test listing content with pagination."""
        # Save 10 items
        for i in range(10):
            content = Content(
                id=f"page-{i}",
                source_type=ContentType.URL,
                storage_backend=StorageBackend.DATABASE,
                text_content=f"Content {i}",
                title=f"Item {i}",
            )
            await db_repo.save(content)

        # First page
        result1 = await db_repo.list(ContentQuery(limit=3, offset=0))
        assert len(result1.items) == 3
        assert result1.has_more is True

        # Last page
        result2 = await db_repo.list(ContentQuery(limit=3, offset=9))
        assert len(result2.items) == 1
        assert result2.has_more is False

    @pytest.mark.asyncio
    async def test_list_with_keyword_query(self, db_repo) -> None:
        """Test listing content with keyword search (FTS5)."""
        content1 = Content(
            id="search-1",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Python is a programming language",
            title="Python Guide",
        )
        content2 = Content(
            id="search-2",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="JavaScript for web development",
            title="JS Tutorial",
        )

        await db_repo.save(content1)
        await db_repo.save(content2)

        result = await db_repo.list(ContentQuery(query="Python"))

        assert result.total >= 1
        assert any("Python" in (item.title or "") for item in result.items)


# ==============================================================================
# Save Tests
# ==============================================================================


class TestDatabaseRepositorySave:
    """Tests for DatabaseRepository.save method."""

    @pytest.mark.asyncio
    async def test_save_new_content(self, db_repo) -> None:
        """Test saving new content."""
        content = Content(
            id="save-test-1",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="New content to save",
            title="New Item",
            source_url="https://example.com/new",
        )

        saved = await db_repo.save(content)

        assert saved.id == "save-test-1"
        assert saved.title == "New Item"
        assert saved.created is not None
        assert saved.modified is not None

    @pytest.mark.asyncio
    async def test_save_update_existing_content(self, db_repo) -> None:
        """Test updating existing content."""
        content = Content(
            id="update-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Original content",
            title="Original Title",
        )

        await db_repo.save(content)

        # Update
        content.text_content = "Updated content"
        content.title = "Updated Title"
        saved = await db_repo.save(content)

        assert saved.text_content == "Updated content"
        assert saved.title == "Updated Title"

    @pytest.mark.asyncio
    async def test_save_with_content_hash(self, db_repo) -> None:
        """Test saving with content hash for deduplication."""
        text = "Content for hashing"
        content_hash = compute_content_hash(text)

        content = Content(
            id="hash-test",
            source_type=ContentType.PLAINTEXT,
            storage_backend=StorageBackend.DATABASE,
            text_content=text,
            content_hash=content_hash,
        )

        saved = await db_repo.save(content)

        assert saved.content_hash == content_hash

    @pytest.mark.asyncio
    async def test_save_prevents_duplicate_by_hash(self, db_repo) -> None:
        """Test that saving with duplicate hash raises error."""
        text = "Duplicate content"
        content_hash = compute_content_hash(text)

        content1 = Content(
            id="dup-1",
            source_type=ContentType.PLAINTEXT,
            storage_backend=StorageBackend.DATABASE,
            text_content=text,
            content_hash=content_hash,
        )

        content2 = Content(
            id="dup-2",
            source_type=ContentType.PLAINTEXT,
            storage_backend=StorageBackend.DATABASE,
            text_content=text,
            content_hash=content_hash,
        )

        await db_repo.save(content1)

        with pytest.raises(Exception):  # Should raise integrity error
            await db_repo.save(content2)


# ==============================================================================
# Delete Tests
# ==============================================================================


class TestDatabaseRepositoryDelete:
    """Tests for DatabaseRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_content(self, db_repo) -> None:
        """Test deleting existing content."""
        content = Content(
            id="delete-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content to delete",
        )

        await db_repo.save(content)
        result = await db_repo.delete("delete-test")

        assert result is True
        assert await db_repo.exists("delete-test") is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_content(self, db_repo) -> None:
        """Test deleting non-existent content returns False."""
        result = await db_repo.delete("nonexistent-id")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_cleans_fts_index(self, db_repo) -> None:
        """Test that delete also removes from FTS index."""
        content = Content(
            id="fts-delete-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Unique searchable content",
            title="FTS Delete Test",
        )

        await db_repo.save(content)

        # Verify it's searchable
        result = await db_repo.list(ContentQuery(query="searchable"))
        assert result.total >= 1

        # Delete
        await db_repo.delete("fts-delete-test")

        # Verify it's no longer searchable
        result = await db_repo.list(ContentQuery(query="searchable"))
        # Should not find it anymore (may still have other results)
        for item in result.items:
            assert item.id != "fts-delete-test"


# ==============================================================================
# Exists Tests
# ==============================================================================


class TestDatabaseRepositoryExists:
    """Tests for DatabaseRepository.exists method."""

    @pytest.mark.asyncio
    async def test_exists_true(self, db_repo) -> None:
        """Test exists returns True for existing content."""
        content = Content(
            id="exists-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content",
        )

        await db_repo.save(content)

        assert await db_repo.exists("exists-test") is True

    @pytest.mark.asyncio
    async def test_exists_false(self, db_repo) -> None:
        """Test exists returns False for non-existing content."""
        assert await db_repo.exists("nonexistent-id") is False


# ==============================================================================
# Vector Index Tests
# ==============================================================================


class TestDatabaseRepositoryVectors:
    """Tests for vector indexing functionality."""

    @pytest.mark.asyncio
    async def test_store_vector(self, db_repo) -> None:
        """Test storing embedding vector."""
        content = Content(
            id="vector-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content for vectorization",
        )

        await db_repo.save(content)

        # Store vector (mock embedding)
        embedding = [0.1] * 1536  # OpenAI embedding size
        await db_repo.store_vector("vector-test", embedding, "text-embedding-ada-002")

        # Verify stored
        stored = await db_repo.get_vector("vector-test")
        assert stored is not None
        assert len(stored) == 1536

    @pytest.mark.asyncio
    async def test_vector_search(self, db_repo) -> None:
        """Test semantic search using vectors."""
        # Save content
        content1 = Content(
            id="vec-search-1",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Python programming tutorial",
            title="Python Tutorial",
        )
        content2 = Content(
            id="vec-search-2",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Cooking recipes for dinner",
            title="Cooking Guide",
        )

        await db_repo.save(content1)
        await db_repo.save(content2)

        # Store vectors (mock embeddings - in real use, these would be from an embedding model)
        python_embedding = [0.8] * 1536  # Similar to programming query
        cooking_embedding = [0.2] * 1536  # Different from programming query

        await db_repo.store_vector("vec-search-1", python_embedding, "test-model")
        await db_repo.store_vector("vec-search-2", cooking_embedding, "test-model")

        # Search with similar vector
        query_embedding = [0.9] * 1536  # Similar to python_embedding
        results = await db_repo.vector_search(query_embedding, limit=2)

        assert len(results) >= 1
        # Python content should rank higher (more similar vector)
        assert results[0].id == "vec-search-1"

    @pytest.mark.asyncio
    async def test_delete_removes_vector(self, db_repo) -> None:
        """Test that deleting content also removes its vector."""
        content = Content(
            id="vec-delete-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content",
        )

        await db_repo.save(content)
        embedding = [0.5] * 1536
        await db_repo.store_vector("vec-delete-test", embedding, "test-model")

        # Delete content
        await db_repo.delete("vec-delete-test")

        # Vector should be gone
        stored = await db_repo.get_vector("vec-delete-test")
        assert stored is None


# ==============================================================================
# Protocol Compliance Tests
# ==============================================================================


class TestDatabaseRepositoryProtocolCompliance:
    """Tests that DatabaseRepository satisfies ContentRepository protocol."""

    @pytest.mark.asyncio
    async def test_satisfies_protocol(self, db_repo) -> None:
        """Test that DatabaseRepository satisfies ContentRepository protocol."""
        from markwritter.storage.base import ContentRepository

        # Should be able to use as ContentRepository
        assert isinstance(db_repo, ContentRepository)

        # Check properties
        assert db_repo.backend_type == StorageBackend.DATABASE
        assert ContentType.URL in db_repo.supported_content_types


# ==============================================================================
# Edge Cases
# ==============================================================================


class TestDatabaseRepositoryEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_database(self, temp_db_path: Path) -> None:
        """Test operations on empty database."""
        from markwritter.storage.backends.database import DatabaseRepository

        repo = DatabaseRepository(db_path=temp_db_path)
        await repo.initialize()

        result = await repo.list(ContentQuery())
        assert result.total == 0
        assert result.items == []

        await repo.close()

    @pytest.mark.asyncio
    async def test_special_characters_in_content(self, db_repo) -> None:
        """Test handling special characters in content."""
        content = Content(
            id="special-chars",
            source_type=ContentType.HTML,
            storage_backend=StorageBackend.DATABASE,
            text_content="<html><body>Unicode: cafe, resume, emoji: </body></html>",
            title="Special Characters",
        )

        await db_repo.save(content)
        retrieved = await db_repo.get("special-chars")

        assert retrieved is not None
        assert "cafe" in retrieved.text_content
        assert "" in retrieved.text_content

    @pytest.mark.asyncio
    async def test_large_content(self, db_repo) -> None:
        """Test handling large content."""
        large_text = "x" * 100000  # 100KB of text

        content = Content(
            id="large-content",
            source_type=ContentType.PLAINTEXT,
            storage_backend=StorageBackend.DATABASE,
            text_content=large_text,
        )

        await db_repo.save(content)
        retrieved = await db_repo.get("large-content")

        assert retrieved is not None
        assert len(retrieved.text_content) == 100000

    @pytest.mark.asyncio
    async def test_metadata_serialization(self, db_repo) -> None:
        """Test JSON serialization of metadata."""
        metadata = {
            "author": "Test Author",
            "version": 1,
            "nested": {"key": "value"},
            "list": ["a", "b", "c"],
        }

        content = Content(
            id="metadata-test",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Content with metadata",
            metadata=metadata,
        )

        await db_repo.save(content)
        retrieved = await db_repo.get("metadata-test")

        assert retrieved is not None
        assert retrieved.metadata["author"] == "Test Author"
        assert retrieved.metadata["nested"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, db_repo) -> None:
        """Test sequential operations work correctly."""
        # Write multiple
        for i in range(10):
            content = Content(
                id=f"concurrent-{i}",
                source_type=ContentType.URL,
                storage_backend=StorageBackend.DATABASE,
                text_content=f"Content {i}",
            )
            await db_repo.save(content)

        # Read all
        for i in range(10):
            retrieved = await db_repo.get(f"concurrent-{i}")
            assert retrieved is not None

        # Delete some
        for i in range(5):
            await db_repo.delete(f"concurrent-{i}")

        # Verify
        result = await db_repo.list(ContentQuery())
        assert result.total == 5