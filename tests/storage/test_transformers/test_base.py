"""Tests for ContentTransformer protocol and metadata models.

Tests cover:
- ContentTransformer protocol definition
- URLMetadata model
- PDFMetadata model
- ImageMetadata model
- ContentIngestResult model
"""

import pytest
from typing import Protocol, runtime_checkable
from unittest.mock import AsyncMock

from markwritter.storage.transformers.base import (
    ContentTransformer,
    URLMetadata,
    PDFMetadata,
    ImageMetadata,
)
from markwritter.storage.models import ContentType


class TestContentTransformerProtocol:
    """Tests for the ContentTransformer protocol definition."""

    def test_protocol_is_runtime_checkable(self):
        """ContentTransformer should be a runtime_checkable Protocol."""
        assert isinstance(ContentTransformer, type)
        # Check it is a Protocol (has _is_protocol attribute)
        assert hasattr(ContentTransformer, "_is_protocol")

    def test_protocol_requires_source_type_property(self):
        """Protocol should define source_type as a property."""
        # A class without source_type should not satisfy the protocol
        class IncompleteTransformer:
            async def can_handle(self, source: str) -> bool:
                return False

            async def extract(self, source: str):
                pass

            async def compute_hash(self, content) -> str:
                return ""

        assert not isinstance(IncompleteTransformer(), ContentTransformer)

    def test_protocol_requires_can_handle_method(self):
        """Protocol should define can_handle as an async method."""
        class IncompleteTransformer:
            @property
            def source_type(self) -> ContentType:
                return ContentType.URL

        assert not isinstance(IncompleteTransformer(), ContentTransformer)

    def test_protocol_requires_extract_method(self):
        """Protocol should define extract as an async method."""
        class IncompleteTransformer:
            @property
            def source_type(self) -> ContentType:
                return ContentType.URL

            async def can_handle(self, source: str) -> bool:
                return False

        assert not isinstance(IncompleteTransformer(), ContentTransformer)

    def test_protocol_requires_compute_hash_method(self):
        """Protocol should define compute_hash as an async method."""
        class IncompleteTransformer:
            @property
            def source_type(self) -> ContentType:
                return ContentType.URL

            async def can_handle(self, source: str) -> bool:
                return False

            async def extract(self, source: str):
                pass

        assert not isinstance(IncompleteTransformer(), ContentTransformer)

    def test_complete_implementation_satisfies_protocol(self):
        """A class implementing all methods should satisfy the protocol."""
        class ValidTransformer:
            @property
            def source_type(self) -> ContentType:
                return ContentType.URL

            async def can_handle(self, source: str) -> bool:
                return True

            async def extract(self, source: str):
                from markwritter.storage.models import Content
                return Content(
                    id="test",
                    source_type=ContentType.URL,
                    storage_backend="database",
                )

            async def compute_hash(self, content) -> str:
                return "abc123"

        assert isinstance(ValidTransformer(), ContentTransformer)


class TestURLMetadata:
    """Tests for URLMetadata model."""

    def test_url_metadata_creation(self):
        """URLMetadata should be creatable with required fields."""
        meta = URLMetadata(domain="example.com")
        assert meta.domain == "example.com"

    def test_url_metadata_with_all_fields(self):
        """URLMetadata should accept all optional fields."""
        from datetime import datetime

        meta = URLMetadata(
            domain="example.com",
            site_name="Example",
            author="John",
            published_date="2024-01-01",
            description="A test site",
            keywords=["test", "example"],
            og_image="https://example.com/img.png",
            canonical_url="https://example.com/original",
        )
        assert meta.domain == "example.com"
        assert meta.site_name == "Example"
        assert meta.author == "John"
        assert meta.published_date == "2024-01-01"
        assert meta.description == "A test site"
        assert meta.keywords == ["test", "example"]
        assert meta.og_image == "https://example.com/img.png"
        assert meta.canonical_url == "https://example.com/original"

    def test_url_metadata_default_values(self):
        """URLMetadata should have sensible defaults."""
        meta = URLMetadata(domain="example.com")
        assert meta.site_name is None
        assert meta.author is None
        assert meta.published_date is None
        assert meta.description is None
        assert meta.keywords == []
        assert meta.og_image is None
        assert meta.canonical_url is None

    def test_url_metadata_to_dict(self):
        """URLMetadata should be serializable to dict."""
        meta = URLMetadata(
            domain="example.com",
            author="John",
            keywords=["a", "b"],
        )
        d = meta.to_dict()
        assert isinstance(d, dict)
        assert d["domain"] == "example.com"
        assert d["author"] == "John"
        assert d["keywords"] == ["a", "b"]

    def test_url_metadata_rejects_empty_domain(self):
        """URLMetadata should not accept empty domain."""
        with pytest.raises(ValueError):
            URLMetadata(domain="")


class TestPDFMetadata:
    """Tests for PDFMetadata model."""

    def test_pdf_metadata_creation(self):
        """PDFMetadata should be creatable with required fields."""
        meta = PDFMetadata(page_count=10)
        assert meta.page_count == 10

    def test_pdf_metadata_with_all_fields(self):
        """PDFMetadata should accept all optional fields."""
        meta = PDFMetadata(
            page_count=42,
            author="PDF Author",
            title="Document Title",
            producer="PDF Producer",
            creator="PDF Creator",
            creation_date="2024-06-01",
            modification_date="2024-06-15",
            file_size=1024000,
        )
        assert meta.page_count == 42
        assert meta.author == "PDF Author"
        assert meta.title == "Document Title"
        assert meta.producer == "PDF Producer"
        assert meta.creator == "PDF Creator"
        assert meta.creation_date == "2024-06-01"
        assert meta.modification_date == "2024-06-15"
        assert meta.file_size == 1024000

    def test_pdf_metadata_default_values(self):
        """PDFMetadata should have sensible defaults."""
        meta = PDFMetadata(page_count=1)
        assert meta.author is None
        assert meta.title is None
        assert meta.producer is None
        assert meta.creator is None
        assert meta.creation_date is None
        assert meta.modification_date is None
        assert meta.file_size is None

    def test_pdf_metadata_to_dict(self):
        """PDFMetadata should be serializable to dict."""
        meta = PDFMetadata(page_count=5, author="Test")
        d = meta.to_dict()
        assert isinstance(d, dict)
        assert d["page_count"] == 5
        assert d["author"] == "Test"

    def test_pdf_metadata_rejects_negative_page_count(self):
        """PDFMetadata should not accept negative page count."""
        with pytest.raises(ValueError):
            PDFMetadata(page_count=-1)

    def test_pdf_metadata_rejects_zero_page_count(self):
        """PDFMetadata should not accept zero page count."""
        with pytest.raises(ValueError):
            PDFMetadata(page_count=0)


class TestImageMetadata:
    """Tests for ImageMetadata model."""

    def test_image_metadata_creation(self):
        """ImageMetadata should be creatable with required fields."""
        meta = ImageMetadata(width=800, height=600, format="JPEG")
        assert meta.width == 800
        assert meta.height == 600
        assert meta.format == "JPEG"

    def test_image_metadata_with_all_fields(self):
        """ImageMetadata should accept all optional fields."""
        meta = ImageMetadata(
            width=1920,
            height=1080,
            format="PNG",
            mode="RGB",
            file_size=2048000,
            ocr_text="Extracted text from image",
            dpi=300,
            color_space="sRGB",
        )
        assert meta.width == 1920
        assert meta.height == 1080
        assert meta.format == "PNG"
        assert meta.mode == "RGB"
        assert meta.file_size == 2048000
        assert meta.ocr_text == "Extracted text from image"
        assert meta.dpi == 300
        assert meta.color_space == "sRGB"

    def test_image_metadata_default_values(self):
        """ImageMetadata should have sensible defaults."""
        meta = ImageMetadata(width=100, height=100, format="PNG")
        assert meta.mode is None
        assert meta.file_size is None
        assert meta.ocr_text is None
        assert meta.dpi is None
        assert meta.color_space is None

    def test_image_metadata_to_dict(self):
        """ImageMetadata should be serializable to dict."""
        meta = ImageMetadata(width=800, height=600, format="JPEG", ocr_text="hello")
        d = meta.to_dict()
        assert isinstance(d, dict)
        assert d["width"] == 800
        assert d["height"] == 600
        assert d["format"] == "JPEG"
        assert d["ocr_text"] == "hello"

    def test_image_metadata_rejects_zero_dimensions(self):
        """ImageMetadata should not accept zero dimensions."""
        with pytest.raises(ValueError):
            ImageMetadata(width=0, height=600, format="JPEG")
        with pytest.raises(ValueError):
            ImageMetadata(width=800, height=0, format="JPEG")

    def test_image_metadata_rejects_negative_dimensions(self):
        """ImageMetadata should not accept negative dimensions."""
        with pytest.raises(ValueError):
            ImageMetadata(width=-1, height=600, format="JPEG")

    def test_image_metadata_rejects_empty_format(self):
        """ImageMetadata should not accept empty format."""
        with pytest.raises(ValueError):
            ImageMetadata(width=800, height=600, format="")
