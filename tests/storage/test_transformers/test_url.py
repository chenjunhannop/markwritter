"""Tests for URLTransformer.

Tests the URL content extraction functionality with mocked HTTP responses.
"""

import hashlib
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from markwritter.storage.models import ContentType, StorageBackend
from markwritter.storage.transformers.base import URLMetadata


class TestURLTransformer:
    """Tests for URLTransformer class."""

    @pytest.fixture
    def transformer(self):
        """Create URLTransformer instance."""
        from markwritter.storage.transformers.url import URLTransformer
        return URLTransformer()

    # =========================================================================
    # source_type property
    # =========================================================================

    def test_source_type_returns_url(self, transformer):
        """Test that source_type returns URL."""
        assert transformer.source_type == ContentType.URL

    # =========================================================================
    # can_handle
    # =========================================================================

    @pytest.mark.asyncio
    async def test_can_handle_http_url(self, transformer):
        """Test detection of HTTP URLs."""
        assert await transformer.can_handle("http://example.com") is True
        assert await transformer.can_handle("http://example.com/page") is True
        assert await transformer.can_handle("http://example.com/page?query=value") is True

    @pytest.mark.asyncio
    async def test_can_handle_https_url(self, transformer):
        """Test detection of HTTPS URLs."""
        assert await transformer.can_handle("https://example.com") is True
        assert await transformer.can_handle("https://example.com/page") is True
        assert await transformer.can_handle("https://sub.example.com/path") is True

    @pytest.mark.asyncio
    async def test_can_handle_rejects_non_url(self, transformer):
        """Test rejection of non-URL sources."""
        assert await transformer.can_handle("/path/to/file.pdf") is False
        assert await transformer.can_handle("file.pdf") is False
        assert await transformer.can_handle("not a url") is False
        assert await transformer.can_handle("ftp://example.com") is False

    # =========================================================================
    # compute_hash
    # =========================================================================

    @pytest.mark.asyncio
    async def test_compute_hash_string(self, transformer):
        """Test hash computation for string content."""
        content = "test content"
        hash_result = await transformer.compute_hash(content)
        expected = hashlib.sha256(content.encode()).hexdigest()
        assert hash_result == expected

    @pytest.mark.asyncio
    async def compute_hash_bytes(self, transformer):
        """Test hash computation for bytes content."""
        content = b"test content"
        hash_result = await transformer.compute_hash(content)
        expected = hashlib.sha256(content).hexdigest()
        assert hash_result == expected

    # =========================================================================
    # extract
    # =========================================================================

    @pytest.mark.asyncio
    async def test_extract_basic_content(self, transformer):
        """Test extraction of basic HTML content."""
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Test Heading</h1>
                <p>Test paragraph content.</p>
            </body>
        </html>
        """
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.text = AsyncMock(return_value=html)
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_response
            
            content = await transformer.extract("https://example.com")
            
            assert content.title == "Test Page"
            assert content.source_type == ContentType.URL
            assert content.storage_backend == StorageBackend.DATABASE
            assert "Test Heading" in content.text_content or "Test paragraph" in content.text_content

    @pytest.mark.asyncio
    async def test_extract_with_opengraph(self, transformer):
        """Test extraction of Open Graph metadata."""
        html = """
        <html>
            <head>
                <title>OG Test</title>
                <meta property="og:site_name" content="Test Site">
                <meta property="article:author" content="John Doe">
            </head>
            <body><p>Content</p></body>
        </html>
        """
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.text = AsyncMock(return_value=html)
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)
            mock_get.return_value = mock_response
            
            content = await transformer.extract("https://example.com/article")
            
            assert content.metadata.get("url_meta") is not None
            url_meta = content.metadata["url_meta"]
            assert url_meta.get("site_name") == "Test Site" or url_meta.get("author") == "John Doe"

    @pytest.mark.asyncio
    async def test_extract_raises_on_http_error(self, transformer):
        """Test that extract raises on HTTP error."""
        import aiohttp
        
        with patch("aiohttp.ClientSession.get") as mock_get:
            mock_get.side_effect = aiohttp.ClientError("Connection failed")
            
            with pytest.raises(Exception):
                await transformer.extract("https://example.com/error")


class TestURLMetadata:
    """Tests for URLMetadata model."""

    def test_create_with_required_fields(self):
        """Test creation with only required fields."""
        meta = URLMetadata(domain="example.com")
        assert meta.domain == "example.com"
        assert meta.site_name is None
        assert meta.author is None

    def test_create_with_all_fields(self):
        """Test creation with all fields."""
        meta = URLMetadata(
            domain="example.com",
            site_name="Example Site",
            author="John Doe",
            published_date="2024-01-01",
            description="Test description",
            keywords=["test", "example"],
            og_image="https://example.com/image.png",
            canonical_url="https://example.com/canonical",
        )
        assert meta.domain == "example.com"
        assert meta.site_name == "Example Site"
        assert meta.author == "John Doe"

    def test_domain_validation_empty(self):
        """Test that empty domain is rejected."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            URLMetadata(domain="")

    def test_to_dict(self):
        """Test serialization to dictionary."""
        meta = URLMetadata(domain="example.com", author="John Doe")
        result = meta.to_dict()
        assert isinstance(result, dict)
        assert result["domain"] == "example.com"
        assert result["author"] == "John Doe"
