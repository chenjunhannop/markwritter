"""Tests for content API models (Phase 4 - TDD RED phase).

Tests for request/response models used by the content endpoints.
These models must be validated before the route tests can work.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from markwritter.api.models.content import (
    ContentListResponse,
    ContentResponse,
    IngestRequest,
    IngestResponse,
)
from markwritter.storage.models import Content, ContentRef, ContentType, StorageBackend


# ==============================================================================
# IngestRequest Tests
# ==============================================================================


class TestIngestRequest:
    """Tests for IngestRequest model."""

    def test_valid_request_with_source_only(self) -> None:
        """A request with only a source field should be valid."""
        req = IngestRequest(source="https://example.com")
        assert req.source == "https://example.com"
        assert req.tags == []
        assert req.metadata == {}

    def test_valid_request_with_all_fields(self) -> None:
        """A request with all fields populated should be valid."""
        req = IngestRequest(
            source="https://example.com/article",
            tags=["tech", "python"],
            metadata={"custom": "value", "priority": 1},
        )
        assert req.source == "https://example.com/article"
        assert req.tags == ["tech", "python"]
        assert req.metadata == {"custom": "value", "priority": 1}

    def test_missing_source_raises_error(self) -> None:
        """A request without a source field should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest()  # type: ignore[call-arg]
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("source",) and e["type"] == "missing" for e in errors)

    def test_empty_source_raises_error(self) -> None:
        """An empty string source should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest(source="")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("source",) for e in errors)

    def test_whitespace_only_source_raises_error(self) -> None:
        """A whitespace-only source should fail validation."""
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest(source="   ")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("source",) for e in errors)

    def test_null_source_raises_error(self) -> None:
        """A null source should fail validation."""
        with pytest.raises(ValidationError):
            IngestRequest(source=None)  # type: ignore[arg-type]

    def test_tags_default_to_empty_list(self) -> None:
        """Tags should default to an empty list."""
        req = IngestRequest(source="https://example.com")
        assert req.tags == []

    def test_metadata_default_to_empty_dict(self) -> None:
        """Metadata should default to an empty dict."""
        req = IngestRequest(source="https://example.com")
        assert req.metadata == {}

    def test_special_characters_in_source(self) -> None:
        """Sources with special characters (Unicode) should be accepted."""
        req = IngestRequest(source="https://example.com/path?q=val&other=1")
        assert "other=1" in req.source

    def test_file_path_source(self) -> None:
        """A local file path should be accepted as a source."""
        req = IngestRequest(source="/tmp/document.pdf")
        assert req.source == "/tmp/document.pdf"

    def test_tags_with_special_characters(self) -> None:
        """Tags containing special characters should be accepted."""
        req = IngestRequest(source="https://example.com", tags=["c++", "node.js", "AI/ML"])
        assert req.tags == ["c++", "node.js", "AI/ML"]

    def test_metadata_with_nested_values(self) -> None:
        """Metadata with nested structures should be accepted."""
        nested = {"level1": {"level2": [1, 2, 3]}}
        req = IngestRequest(source="https://example.com", metadata=nested)
        assert req.metadata["level1"]["level2"] == [1, 2, 3]


# ==============================================================================
# IngestResponse Tests
# ==============================================================================


class TestIngestResponse:
    """Tests for IngestResponse model."""

    def test_successful_response(self) -> None:
        """A successful response with all fields populated."""
        content_ref = ContentRef(
            id="abc-123",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            title="Test Article",
        )
        resp = IngestResponse(
            success=True,
            content_id="abc-123",
            content=content_ref,
            error=None,
            warnings=[],
            processing_time_ms=150.5,
        )
        assert resp.success is True
        assert resp.content_id == "abc-123"
        assert resp.content is not None
        assert resp.content.title == "Test Article"
        assert resp.processing_time_ms == 150.5

    def test_failed_response(self) -> None:
        """A failed response should have error and no content."""
        resp = IngestResponse(
            success=False,
            content_id=None,
            content=None,
            error="Unsupported content type",
            warnings=["Source could not be parsed"],
            processing_time_ms=5.0,
        )
        assert resp.success is False
        assert resp.content_id is None
        assert resp.content is None
        assert resp.error == "Unsupported content type"
        assert resp.warnings == ["Source could not be parsed"]

    def test_warnings_default_to_empty_list(self) -> None:
        """Warnings should default to empty list."""
        resp = IngestResponse(success=True, processing_time_ms=0.0)
        assert resp.warnings == []

    def test_processing_time_is_float(self) -> None:
        """Processing time should accept float values."""
        resp = IngestResponse(success=True, processing_time_ms=0.001)
        assert isinstance(resp.processing_time_ms, float)

    def test_response_serialization(self) -> None:
        """Response should serialize to dict correctly."""
        resp = IngestResponse(
            success=True,
            content_id="id-1",
            processing_time_ms=100.0,
        )
        data = resp.model_dump()
        assert data["success"] is True
        assert data["content_id"] == "id-1"
        assert data["content"] is None
        assert data["error"] is None


# ==============================================================================
# ContentListResponse Tests
# ==============================================================================


class TestContentListResponse:
    """Tests for ContentListResponse model."""

    def test_empty_list(self) -> None:
        """An empty content list should be valid."""
        resp = ContentListResponse(items=[], total=0, limit=100, offset=0)
        assert resp.items == []
        assert resp.total == 0

    def test_list_with_items(self) -> None:
        """A list with items should be valid."""
        items = [
            ContentRef(
                id="1",
                source_type=ContentType.MARKDOWN,
                storage_backend=StorageBackend.OBSIDIAN,
                title="Note 1",
            ),
            ContentRef(
                id="2",
                source_type=ContentType.URL,
                storage_backend=StorageBackend.DATABASE,
                title="Article 2",
            ),
        ]
        resp = ContentListResponse(items=items, total=2, limit=100, offset=0)
        assert len(resp.items) == 2
        assert resp.total == 2

    def test_pagination_fields(self) -> None:
        """Pagination fields should be correctly stored."""
        resp = ContentListResponse(items=[], total=50, limit=10, offset=20)
        assert resp.total == 50
        assert resp.limit == 10
        assert resp.offset == 20

    def test_total_greater_than_items_length(self) -> None:
        """Total can be greater than items length (indicating more pages)."""
        resp = ContentListResponse(items=[], total=100, limit=10, offset=0)
        assert resp.total == 100
        assert len(resp.items) == 0

    def test_negative_limit_raises_error(self) -> None:
        """Negative limit should raise validation error."""
        with pytest.raises(ValidationError):
            ContentListResponse(items=[], total=0, limit=-1, offset=0)

    def test_negative_offset_raises_error(self) -> None:
        """Negative offset should raise validation error."""
        with pytest.raises(ValidationError):
            ContentListResponse(items=[], total=0, limit=10, offset=-5)


# ==============================================================================
# ContentResponse Tests
# ==============================================================================


class TestContentResponse:
    """Tests for ContentResponse model."""

    def test_response_with_full_content(self) -> None:
        """A response wrapping a full Content object."""
        content = Content(
            id="full-1",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content="Hello world",
            title="Test Page",
            source_url="https://example.com",
            tags=["test"],
        )
        resp = ContentResponse(content=content)
        assert resp.content.id == "full-1"
        assert resp.content.text_content == "Hello world"
        assert resp.content.title == "Test Page"

    def test_response_serialization(self) -> None:
        """Response should serialize to dict correctly."""
        content = Content(
            id="s1",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content="# Title\nContent here",
        )
        resp = ContentResponse(content=content)
        data = resp.model_dump()
        assert data["content"]["id"] == "s1"
        assert data["content"]["text_content"] == "# Title\nContent here"
