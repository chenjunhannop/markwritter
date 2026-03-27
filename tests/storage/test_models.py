"""Tests for storage models.

TDD approach: These tests define the expected behavior before implementation.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentType,
    ContentQuery,
    ContentRef,
    StorageBackend,
)


class TestContentTypeEnum:
    """Tests for ContentType enum."""

    def test_content_type_values(self) -> None:
        """Test ContentType enum has expected values."""
        assert ContentType.MARKDOWN == "markdown"
        assert ContentType.PDF == "pdf"
        assert ContentType.URL == "url"
        assert ContentType.IMAGE == "image"

    def test_content_type_from_string(self) -> None:
        """Test ContentType can be created from string."""
        assert ContentType("markdown") == ContentType.MARKDOWN
        assert ContentType("pdf") == ContentType.PDF

    def test_content_type_invalid_value_raises_error(self) -> None:
        """Test invalid ContentType value raises error."""
        with pytest.raises(ValueError):
            ContentType("invalid")


class TestStorageBackendEnum:
    """Tests for StorageBackend enum."""

    def test_storage_backend_values(self) -> None:
        """Test StorageBackend enum has expected values."""
        assert StorageBackend.OBSIDIAN == "obsidian"
        assert StorageBackend.DATABASE == "database"
        assert StorageBackend.OBJECT_STORE == "object_store"

    def test_storage_backend_from_string(self) -> None:
        """Test StorageBackend can be created from string."""
        assert StorageBackend("obsidian") == StorageBackend.OBSIDIAN

    def test_storage_backend_invalid_value_raises_error(self) -> None:
        """Test invalid StorageBackend value raises error."""
        with pytest.raises(ValueError):
            StorageBackend("invalid")


class TestContentRef:
    """Tests for ContentRef model - lightweight reference."""

    def test_content_ref_minimal(self) -> None:
        """Test ContentRef with minimal required fields."""
        ref = ContentRef(
            id="test-id-123",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
        )

        assert ref.id == "test-id-123"
        assert ref.source_type == ContentType.MARKDOWN
        assert ref.storage_backend == StorageBackend.OBSIDIAN
        assert ref.title is None
        assert ref.created is None
        assert ref.modified is None
        assert ref.tags == []
        assert ref.path is None

    def test_content_ref_full(self) -> None:
        """Test ContentRef with all fields."""
        now = datetime.now()
        ref = ContentRef(
            id="test-id-456",
            source_type=ContentType.PDF,
            storage_backend=StorageBackend.DATABASE,
            title="Test Document",
            created=now,
            modified=now,
            tags=["important", "research"],
            path="/documents/test.pdf",
        )

        assert ref.id == "test-id-456"
        assert ref.source_type == ContentType.PDF
        assert ref.storage_backend == StorageBackend.DATABASE
        assert ref.title == "Test Document"
        assert ref.created == now
        assert ref.modified == now
        assert ref.tags == ["important", "research"]
        assert ref.path == "/documents/test.pdf"

    def test_content_ref_missing_required_raises_error(self) -> None:
        """Test ContentRef without required fields raises error."""
        with pytest.raises(ValidationError):
            ContentRef()  # Missing id, source_type, storage_backend

    def test_content_ref_invalid_source_type_raises_error(self) -> None:
        """Test ContentRef with invalid source_type raises error."""
        with pytest.raises(ValidationError):
            ContentRef(
                id="test-id",
                source_type="invalid",  # type: ignore
                storage_backend=StorageBackend.OBSIDIAN,
            )


class TestContent:
    """Tests for Content model - full content representation."""

    def test_content_minimal(self) -> None:
        """Test Content with minimal required fields."""
        content = Content(
            id="content-id-123",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
        )

        assert content.id == "content-id-123"
        assert content.source_type == ContentType.MARKDOWN
        assert content.storage_backend == StorageBackend.OBSIDIAN
        assert content.text_content is None
        assert content.title is None
        assert content.source_path is None
        assert content.metadata == {}
        assert content.links == []
        assert content.backlinks == []
        assert content.tags == []
        assert content.created is None
        assert content.modified is None

    def test_content_full(self) -> None:
        """Test Content with all fields."""
        now = datetime.now()
        content = Content(
            id="content-id-456",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content="# Test Note\n\nContent here.",
            title="Test Note",
            source_path="notes/test.md",
            metadata={"author": "test", "version": 1},
            links=["note1", "note2"],
            backlinks=["note3"],
            tags=["test", "example"],
            created=now,
            modified=now,
        )

        assert content.id == "content-id-456"
        assert content.text_content == "# Test Note\n\nContent here."
        assert content.title == "Test Note"
        assert content.source_path == "notes/test.md"
        assert content.metadata == {"author": "test", "version": 1}
        assert content.links == ["note1", "note2"]
        assert content.backlinks == ["note3"]
        assert content.tags == ["test", "example"]

    def test_content_to_ref(self) -> None:
        """Test converting Content to ContentRef."""
        now = datetime.now()
        content = Content(
            id="content-id-789",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            title="Sample",
            created=now,
            modified=now,
            tags=["a", "b"],
            source_path="sample.md",
        )

        ref = content.to_ref()

        assert isinstance(ref, ContentRef)
        assert ref.id == "content-id-789"
        assert ref.source_type == ContentType.MARKDOWN
        assert ref.storage_backend == StorageBackend.OBSIDIAN
        assert ref.title == "Sample"
        assert ref.created == now
        assert ref.modified == now
        assert ref.tags == ["a", "b"]
        assert ref.path == "sample.md"

    def test_content_from_obsidian_note(self) -> None:
        """Test creating Content from Obsidian Note model."""
        from markwritter.obsidian.models import Note

        note = Note(
            path="test/note.md",
            content="# Test\n\nContent",
            metadata={"title": "Test Note", "tags": ["tag1"]},
            links=["link1"],
            backlinks=["backlink1"],
            modified=datetime(2024, 1, 15, 10, 30),
        )

        content = Content.from_obsidian_note(note)

        assert content.id == "test/note.md"
        assert content.source_type == ContentType.MARKDOWN
        assert content.storage_backend == StorageBackend.OBSIDIAN
        assert content.text_content == "# Test\n\nContent"
        assert content.title == "Test Note"
        assert content.source_path == "test/note.md"
        assert content.tags == ["tag1"]
        assert content.links == ["link1"]
        assert content.backlinks == ["backlink1"]

    def test_content_from_obsidian_note_with_string_tags(self) -> None:
        """Test creating Content from Obsidian Note with string tags."""
        from markwritter.obsidian.models import Note

        note = Note(
            path="test/note.md",
            content="# Test",
            metadata={"title": "Test Note", "tags": "single-tag"},
        )

        content = Content.from_obsidian_note(note)

        assert content.tags == ["single-tag"]

    def test_content_from_obsidian_note_invalid_type_raises_error(self) -> None:
        """Test that from_obsidian_note raises TypeError for invalid input."""
        with pytest.raises(TypeError, match="Expected Note"):
            Content.from_obsidian_note("not a note")  # type: ignore


class TestContentQuery:
    """Tests for ContentQuery model."""

    def test_content_query_defaults(self) -> None:
        """Test ContentQuery default values."""
        query = ContentQuery()

        assert query.query is None
        assert query.tags == []
        assert query.source_types == []
        assert query.storage_backends == []
        assert query.path_prefix is None
        assert query.limit == 100
        assert query.offset == 0

    def test_content_query_full(self) -> None:
        """Test ContentQuery with all fields."""
        query = ContentQuery(
            query="python testing",
            tags=["python", "testing"],
            source_types=[ContentType.MARKDOWN],
            storage_backends=[StorageBackend.OBSIDIAN],
            path_prefix="notes/",
            limit=50,
            offset=10,
        )

        assert query.query == "python testing"
        assert query.tags == ["python", "testing"]
        assert query.source_types == [ContentType.MARKDOWN]
        assert query.storage_backends == [StorageBackend.OBSIDIAN]
        assert query.path_prefix == "notes/"
        assert query.limit == 50
        assert query.offset == 10

    def test_content_query_negative_limit_raises_error(self) -> None:
        """Test ContentQuery with negative limit raises error."""
        with pytest.raises(ValidationError):
            ContentQuery(limit=-1)

    def test_content_query_negative_offset_raises_error(self) -> None:
        """Test ContentQuery with negative offset raises error."""
        with pytest.raises(ValidationError):
            ContentQuery(offset=-1)


class TestContentListResult:
    """Tests for ContentListResult model."""

    def test_content_list_result(self) -> None:
        """Test ContentListResult with items."""
        ref1 = ContentRef(
            id="id1",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
        )
        ref2 = ContentRef(
            id="id2",
            source_type=ContentType.PDF,
            storage_backend=StorageBackend.DATABASE,
        )

        result = ContentListResult(
            items=[ref1, ref2],
            total=2,
            limit=100,
            offset=0,
        )

        assert len(result.items) == 2
        assert result.total == 2
        assert result.limit == 100
        assert result.offset == 0
        assert result.has_more is False

    def test_content_list_result_with_pagination(self) -> None:
        """Test ContentListResult with pagination info."""
        refs = [
            ContentRef(
                id=f"id{i}",
                source_type=ContentType.MARKDOWN,
                storage_backend=StorageBackend.OBSIDIAN,
            )
            for i in range(10)
        ]

        result = ContentListResult(
            items=refs,
            total=25,
            limit=10,
            offset=0,
        )

        assert len(result.items) == 10
        assert result.total == 25
        assert result.has_more is True

    def test_content_list_result_empty(self) -> None:
        """Test ContentListResult with no items."""
        result = ContentListResult(items=[], total=0, limit=100, offset=0)

        assert result.items == []
        assert result.total == 0
        assert result.has_more is False