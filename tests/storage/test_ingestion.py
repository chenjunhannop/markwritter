"""Tests for IngestionPipeline.

Tests the content ingestion pipeline that orchestrates transformers.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from markwritter.storage.models import ContentType
from markwritter.storage.ingestion import ContentIngestResult, IngestionPipeline


class TestContentIngestResult:
    """Tests for ContentIngestResult model."""

    def test_create_success_result(self):
        """Test creation of successful result."""
        result = ContentIngestResult(success=True)
        assert result.success is True
        assert result.content is None
        assert result.error is None
        assert result.warnings == []

    def test_create_failure_result(self):
        """Test creation of failure result."""
        result = ContentIngestResult(
            success=False,
            error="Something went wrong",
        )
        assert result.success is False
        assert result.error == "Something went wrong"

    def test_create_with_all_fields(self):
        """Test creation with all fields."""
        from markwritter.storage.models import Content
        
        content = Content(
            id="test-id",
            source_type=ContentType.URL,
            storage_backend="database",
        )
        
        result = ContentIngestResult(
            success=True,
            content=content,
            content_id="test-id",
            warnings=["Minor issue"],
            bytes_processed=1024,
            processing_time_ms=100.5,
        )
        assert result.success is True
        assert result.content == content
        assert result.bytes_processed == 1024


class TestIngestionPipeline:
    """Tests for IngestionPipeline class."""

    @pytest.fixture
    def pipeline(self):
        """Create IngestionPipeline instance."""
        return IngestionPipeline()

    # =========================================================================
    # Initialization
    # =========================================================================

    def test_initializes_with_default_transformers(self, pipeline):
        """Test that pipeline initializes with default transformers."""
        assert pipeline.get_transformer(ContentType.URL) is not None
        assert pipeline.get_transformer(ContentType.PDF) is not None
        assert pipeline.get_transformer(ContentType.IMAGE) is not None

    # =========================================================================
    # Transformer registration
    # =========================================================================

    def test_register_transformer(self, pipeline):
        """Test registering a custom transformer."""
        from markwritter.storage.transformers.base import ContentTransformer
        
        class CustomTransformer:
            @property
            def source_type(self):
                return ContentType.MARKDOWN
            
            async def can_handle(self, source):
                return source.endswith(".md")
            
            async def extract(self, source):
                from markwritter.storage.models import Content
                return Content(
                    id="",
                    source_type=ContentType.MARKDOWN,
                    storage_backend="database",
                )
            
            async def compute_hash(self, content):
                return "hash"
        
        pipeline.register(CustomTransformer())
        assert pipeline.get_transformer(ContentType.MARKDOWN) is not None

    # =========================================================================
    # detect_type
    # =========================================================================

    @pytest.mark.asyncio
    async def test_detect_type_url(self, pipeline):
        """Test detection of URL content type."""
        content_type = await pipeline.detect_type("https://example.com")
        assert content_type == ContentType.URL

    @pytest.mark.asyncio
    async def test_detect_type_pdf(self, pipeline):
        """Test detection of PDF content type."""
        content_type = await pipeline.detect_type("/path/to/document.pdf")
        assert content_type == ContentType.PDF

    @pytest.mark.asyncio
    async def test_detect_type_image(self, pipeline):
        """Test detection of image content type."""
        content_type = await pipeline.detect_type("/path/to/image.png")
        assert content_type == ContentType.IMAGE

    @pytest.mark.asyncio
    async def test_detect_type_unknown(self, pipeline):
        """Test detection returns None for unknown types."""
        content_type = await pipeline.detect_type("/path/to/document.xyz")
        assert content_type is None

    # =========================================================================
    # ingest
    # =========================================================================

    @pytest.mark.asyncio
    async def test_ingest_unsupported_type(self, pipeline):
        """Test ingestion fails for unsupported types."""
        result = await pipeline.ingest("/path/to/file.xyz")
        assert result.success is False
        assert "Unsupported content type" in result.error

    @pytest.mark.asyncio
    async def test_ingest_missing_file(self, pipeline):
        """Test ingestion fails for missing files."""
        result = await pipeline.ingest("/nonexistent/file.pdf")
        assert result.success is False
        assert "File not found" in result.error

    @pytest.mark.asyncio
    async def test_ingest_url_success(self, pipeline):
        """Test successful URL ingestion."""
        html = "<html><head><title>Test</title></head><body><p>Content</p></body></html>"
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.text = AsyncMock(return_value=html)
            mock_response.status = 200
            mock_response.raise_for_status = MagicMock()
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_response
            
            result = await pipeline.ingest("https://example.com")
            
            assert result.success is True
            assert result.content is not None
            assert result.content.source_type == ContentType.URL
            assert result.bytes_processed > 0
            assert result.processing_time_ms > 0
