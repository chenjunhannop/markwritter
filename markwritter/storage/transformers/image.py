"""Image content transformer.

Extracts metadata and optionally OCR text from image files.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image

from markwritter.storage.models import Content, ContentType, StorageBackend
from markwritter.storage.transformers.base import ImageMetadata

logger = logging.getLogger(__name__)


class ImageTransformer:
    """Transformer for image content.
    
    Extracts image metadata (dimensions, format, etc.) and optionally
    performs OCR to extract text content.
    
    Attributes:
        enable_ocr: Whether to enable OCR text extraction.
    """

    # Supported image extensions
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}

    def __init__(self, enable_ocr: bool = False) -> None:
        """Initialize image transformer.
        
        Args:
            enable_ocr: Whether to enable OCR text extraction.
        """
        self.enable_ocr = enable_ocr

    @property
    def source_type(self) -> ContentType:
        """Return IMAGE content type."""
        return ContentType.IMAGE

    async def can_handle(self, source: str) -> bool:
        """Check if source is an image file path.
        
        Args:
            source: Source string to check.
            
        Returns:
            True if source is a path to an image file.
        """
        path = Path(source)
        return path.suffix.lower() in self.IMAGE_EXTENSIONS

    async def extract(self, source: str) -> Content:
        """Extract metadata and optionally OCR text from image.
        
        Args:
            source: Path to image file.
            
        Returns:
            Content object with extracted metadata.
            
        Raises:
            FileNotFoundError: If image file does not exist.
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {source}")

        # Read image data
        image_data = path.read_bytes()

        # Extract image metadata using Pillow
        with Image.open(path) as img:
            width, height = img.size
            format_name = img.format or "UNKNOWN"
            mode = img.mode
            dpi = img.info.get("dpi")
            if dpi and isinstance(dpi, tuple):
                dpi = dpi[0]

        # Optional OCR
        ocr_text = None
        if self.enable_ocr:
            ocr_text = self._perform_ocr(path)

        # Create metadata
        image_meta = ImageMetadata(
            width=width,
            height=height,
            format=format_name,
            mode=mode,
            file_size=len(image_data),
            ocr_text=ocr_text,
            dpi=dpi,
        )

        # Compute hash
        content_hash = await self.compute_hash(image_data)

        # Determine MIME type
        mime_type = f"image/{format_name.lower()}"
        if format_name.lower() == "jpeg":
            mime_type = "image/jpeg"
        elif format_name.lower() == "svg":
            mime_type = "image/svg+xml"

        return Content(
            id="",  # Will be assigned by repository
            source_type=ContentType.IMAGE,
            storage_backend=StorageBackend.DATABASE,
            text_content=ocr_text,  # For searchability
            raw_content=image_data,
            title=path.stem,
            source_path=str(path),
            storage_path=f"images/{path.name}",
            metadata={"image_meta": image_meta.model_dump()},
            tags=[],
            links=[],
            backlinks=[],
            content_hash=content_hash,
            mime_type=mime_type,
            created=datetime.now(),
            modified=datetime.now(),
        )

    async def compute_hash(self, content: bytes | str) -> str:
        """Compute SHA-256 hash for content.
        
        Args:
            content: Content to hash.
            
        Returns:
            Hexadecimal hash string.
        """
        if isinstance(content, str):
            content = content.encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def _perform_ocr(self, path: Path) -> Optional[str]:
        """Perform OCR on image to extract text.
        
        Args:
            path: Path to image file.
            
        Returns:
            Extracted text or None if OCR fails.
        """
        if not self.enable_ocr:
            return None

        try:
            import pytesseract
            with Image.open(path) as img:
                text = pytesseract.image_to_string(img)
                return text.strip() if text else None
        except ImportError:
            logger.warning("pytesseract not installed, OCR disabled")
            return None
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return None


__all__ = ["ImageTransformer"]
