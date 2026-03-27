"""Tests for PDFTransformer.

Tests the PDF content extraction functionality with mocked file operations.
"""

import hashlib
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from markwritter.storage.models import ContentType, StorageBackend
from markwritter.storage.transformers.base import PDFMetadata


class TestPDFTransformer:
    """Tests for PDFTransformer class."""

    @pytest.fixture
    def transformer(self):
        """Create PDFTransformer instance."""
        from markwritter.storage.transformers.pdf import PDFTransformer
        return PDFTransformer()

    # =========================================================================
    # source_type property
    # =========================================================================

    def test_source_type_returns_pdf(self, transformer):
        """Test that source_type returns PDF."""
        assert transformer.source_type == ContentType.PDF

    # =========================================================================
    # can_handle
    # =========================================================================

    @pytest.mark.asyncio
    async def test_can_handle_pdf_extension(self, transformer):
        """Test detection of PDF files by extension."""
        assert await transformer.can_handle("document.pdf") is True
        assert await transformer.can_handle("/path/to/document.pdf") is True
        assert await transformer.can_handle("DOCUMENT.PDF") is True

    @pytest.mark.asyncio
    async def test_can_handle_rejects_non_pdf(self, transformer):
        """Test rejection of non-PDF files."""
        assert await transformer.can_handle("document.txt") is False
        assert await transformer.can_handle("image.png") is False
        assert await transformer.can_handle("https://example.com") is False

    # =========================================================================
    # compute_hash
    # =========================================================================

    @pytest.mark.asyncio
    async def test_compute_hash_bytes(self, transformer):
        """Test hash computation for bytes content."""
        content = b"test content"
        hash_result = await transformer.compute_hash(content)
        expected = hashlib.sha256(content).hexdigest()
        assert hash_result == expected

    # =========================================================================
    # extract (with mocked file system)
    # =========================================================================

    @pytest.mark.asyncio
    async def test_extract_raises_on_missing_file(self, transformer):
        """Test that extract raises on missing file."""
        with pytest.raises(FileNotFoundError):
            await transformer.extract("/nonexistent/file.pdf")


class TestPDFMetadata:
    """Tests for PDFMetadata model."""

    def test_create_with_required_fields(self):
        """Test creation with only required fields."""
        meta = PDFMetadata(page_count=10)
        assert meta.page_count == 10
        assert meta.author is None
        assert meta.title is None

    def test_create_with_all_fields(self):
        """Test creation with all fields."""
        meta = PDFMetadata(
            page_count=10,
            author="John Doe",
            title="Test Document",
            producer="Adobe",
            creator="Word",
            creation_date="2024-01-01",
            modification_date="2024-01-02",
            file_size=1024,
        )
        assert meta.page_count == 10
        assert meta.author == "John Doe"
        assert meta.title == "Test Document"

    def test_page_count_validation_zero(self):
        """Test that zero page count is rejected."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            PDFMetadata(page_count=0)

    def test_page_count_validation_negative(self):
        """Test that negative page count is rejected."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            PDFMetadata(page_count=-1)

    def test_to_dict(self):
        """Test serialization to dictionary."""
        meta = PDFMetadata(page_count=10, author="John Doe")
        result = meta.to_dict()
        assert isinstance(result, dict)
        assert result["page_count"] == 10
        assert result["author"] == "John Doe"
