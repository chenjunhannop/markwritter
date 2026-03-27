"""Tests for ImageTransformer.

Tests the image content extraction functionality with mocked file operations.
"""

import hashlib
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from markwritter.storage.models import ContentType, StorageBackend
from markwritter.storage.transformers.base import ImageMetadata


class TestImageTransformer:
    """Tests for ImageTransformer class."""

    @pytest.fixture
    def transformer(self):
        """Create ImageTransformer instance."""
        from markwritter.storage.transformers.image import ImageTransformer
        return ImageTransformer(enable_ocr=False)

    @pytest.fixture
    def transformer_with_ocr(self):
        """Create ImageTransformer instance with OCR enabled."""
        from markwritter.storage.transformers.image import ImageTransformer
        return ImageTransformer(enable_ocr=True)

    # =========================================================================
    # source_type property
    # =========================================================================

    def test_source_type_returns_image(self, transformer):
        """Test that source_type returns IMAGE."""
        assert transformer.source_type == ContentType.IMAGE

    # =========================================================================
    # can_handle
    # =========================================================================

    @pytest.mark.asyncio
    async def test_can_handle_png(self, transformer):
        """Test detection of PNG files."""
        assert await transformer.can_handle("image.png") is True
        assert await transformer.can_handle("/path/to/image.PNG") is True

    @pytest.mark.asyncio
    async def test_can_handle_jpeg(self, transformer):
        """Test detection of JPEG files."""
        assert await transformer.can_handle("image.jpg") is True
        assert await transformer.can_handle("image.jpeg") is True
        assert await transformer.can_handle("image.JPG") is True

    @pytest.mark.asyncio
    async def test_can_handle_other_formats(self, transformer):
        """Test detection of other image formats."""
        assert await transformer.can_handle("image.gif") is True
        assert await transformer.can_handle("image.webp") is True
        assert await transformer.can_handle("image.bmp") is True
        assert await transformer.can_handle("image.svg") is True

    @pytest.mark.asyncio
    async def test_can_handle_rejects_non_image(self, transformer):
        """Test rejection of non-image files."""
        assert await transformer.can_handle("document.pdf") is False
        assert await transformer.can_handle("document.txt") is False
        assert await transformer.can_handle("https://example.com") is False

    # =========================================================================
    # extract (with mocked file system)
    # =========================================================================

    @pytest.mark.asyncio
    async def test_extract_raises_on_missing_file(self, transformer):
        """Test that extract raises on missing file."""
        with pytest.raises(FileNotFoundError):
            await transformer.extract("/nonexistent/image.png")

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
    # OCR functionality
    # =========================================================================

    def test_ocr_disabled_by_default(self):
        """Test that OCR is disabled by default."""
        from markwritter.storage.transformers.image import ImageTransformer
        t = ImageTransformer()
        assert t.enable_ocr is False


class TestImageMetadata:
    """Tests for ImageMetadata model."""

    def test_create_with_required_fields(self):
        """Test creation with only required fields."""
        meta = ImageMetadata(width=100, height=200, format="PNG")
        assert meta.width == 100
        assert meta.height == 200
        assert meta.format == "PNG"
        assert meta.mode is None
        assert meta.ocr_text is None

    def test_create_with_all_fields(self):
        """Test creation with all fields."""
        meta = ImageMetadata(
            width=100,
            height=200,
            format="JPEG",
            mode="RGB",
            file_size=1024,
            ocr_text="extracted text",
            dpi=72,
            color_space="sRGB",
        )
        assert meta.width == 100
        assert meta.height == 200
        assert meta.format == "JPEG"
        assert meta.mode == "RGB"
        assert meta.ocr_text == "extracted text"

    def test_dimension_validation_zero(self):
        """Test that zero dimensions are rejected."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ImageMetadata(width=0, height=100, format="PNG")
        
        with pytest.raises(ValidationError):
            ImageMetadata(width=100, height=0, format="PNG")

    def test_dimension_validation_negative(self):
        """Test that negative dimensions are rejected."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ImageMetadata(width=-1, height=100, format="PNG")

    def test_format_validation_empty(self):
        """Test that empty format is rejected."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ImageMetadata(width=100, height=100, format="")

    def test_to_dict(self):
        """Test serialization to dictionary."""
        meta = ImageMetadata(width=100, height=200, format="PNG", mode="RGBA")
        result = meta.to_dict()
        assert isinstance(result, dict)
        assert result["width"] == 100
        assert result["height"] == 200
        assert result["format"] == "PNG"
        assert result["mode"] == "RGBA"
