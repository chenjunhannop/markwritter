"""Tests for Content API routes.

Tests the new unified content endpoints that support multiple content types.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from markwritter.storage.models import Content, ContentRef, ContentType, StorageBackend


class TestContentRoutes:
    """Tests for Content API routes."""

    @pytest.fixture
    def app(self):
        """Create test FastAPI app."""
        from markwritter.api.routes.content import router, init_content_routes
        app = FastAPI()
        app.include_router(router, prefix="/api/v1/content")
        init_content_routes()
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    # =========================================================================
    # POST /content/ingest - Content ingestion
    # =========================================================================

    def test_ingest_url_endpoint_exists(self, client):
        """Test that URL ingest endpoint exists and accepts requests."""
        # This tests the endpoint exists, not full ingestion
        response = client.post(
            "/api/v1/content/ingest",
            json={"source": "https://example.com"},
        )

        # Endpoint should exist and process (may fail on network issues)
        assert response.status_code in [200, 500]
        data = response.json()
        assert "success" in data

    def test_ingest_with_custom_tags(self, client):
        """Test ingestion with custom tags."""
        response = client.post(
            "/api/v1/content/ingest",
            json={
                "source": "https://example.com",
                "tags": ["test", "example"],
            },
        )

        # Request should be accepted
        assert response.status_code in [200, 500]
        data = response.json()
        assert "success" in data

    def test_ingest_with_metadata(self, client):
        """Test ingestion with custom metadata."""
        response = client.post(
            "/api/v1/content/ingest",
            json={
                "source": "https://example.com",
                "metadata": {"key": "value", "author": "test"},
            },
        )

        assert response.status_code in [200, 500]

    # =========================================================================
    # GET /content - List content
    # =========================================================================

    def test_list_content_default(self, client):
        """Test listing content with default parameters."""
        response = client.get("/api/v1/content")

        # Should return valid response structure
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_content_with_filters(self, client):
        """Test listing content with filters."""
        response = client.get(
            "/api/v1/content",
            params={
                "content_type": "url",
                "limit": 10,
                "offset": 0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_list_content_pagination(self, client):
        """Test content list pagination."""
        response = client.get(
            "/api/v1/content",
            params={"limit": 5, "offset": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["offset"] == 10

    # =========================================================================
    # GET /content/{content_id} - Get single content
    # =========================================================================

    def test_get_content_not_found(self, client):
        """Test getting non-existent content."""
        response = client.get("/api/v1/content/nonexistent-id")

        assert response.status_code == 404

    # =========================================================================
    # DELETE /content/{content_id} - Delete content
    # =========================================================================

    def test_delete_content_not_found(self, client):
        """Test deleting non-existent content."""
        response = client.delete("/api/v1/content/nonexistent-id")

        assert response.status_code == 404

    # =========================================================================
    # GET /content/search - Search content
    # =========================================================================

    def test_search_content_endpoint(self, client):
        """Test content search endpoint."""
        response = client.get(
            "/api/v1/content/search",
            params={"q": "test query"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "items" in data


class TestContentRequestModels:
    """Tests for content request/response models."""

    def test_ingest_request_valid(self):
        """Test valid IngestRequest from canonical models."""
        from markwritter.api.models.content import IngestRequest

        request = IngestRequest(source="https://example.com")
        assert request.source == "https://example.com"
        assert request.tags == []
        assert request.metadata == {}

    def test_ingest_request_with_tags(self):
        """Test IngestRequest with tags."""
        from markwritter.api.models.content import IngestRequest

        request = IngestRequest(
            source="https://example.com",
            tags=["tag1", "tag2"],
            metadata={"key": "value"},
        )
        assert request.tags == ["tag1", "tag2"]
        assert request.metadata == {"key": "value"}

    def test_ingest_response_success(self):
        """Test IngestResponse success case."""
        from markwritter.api.models.content import IngestResponse

        response = IngestResponse(
            success=True,
            content_id="test-id",
            processing_time_ms=100.5,
        )
        assert response.success is True
        assert response.content_id == "test-id"

    def test_ingest_response_failure(self):
        """Test IngestResponse failure case."""
        from markwritter.api.models.content import IngestResponse

        response = IngestResponse(
            success=False,
            error="Something went wrong",
        )
        assert response.success is False
        assert response.error == "Something went wrong"

    def test_content_list_response(self):
        """Test ContentListResponse model."""
        from markwritter.api.models.content import ContentListResponse

        response = ContentListResponse(
            items=[],
            total=0,
            limit=10,
            offset=0,
        )
        assert response.items == []
        assert response.total == 0
        assert response.has_more is False

    def test_content_ref_response(self):
        """Test ContentRef model (canonical replacement for ContentRefResponse)."""
        ref = ContentRef(
            id="test-id",
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            title="Test Title",
            tags=["tag1"],
        )
        assert ref.id == "test-id"
        assert ref.source_type == ContentType.URL
        assert ref.storage_backend == StorageBackend.DATABASE
        assert ref.title == "Test Title"

    def test_content_delete_response(self):
        """Test ContentDeleteResponse model."""
        from markwritter.api.models.content import ContentDeleteResponse

        response = ContentDeleteResponse(success=True, content_id="test-id")
        assert response.success is True
        assert response.content_id == "test-id"
