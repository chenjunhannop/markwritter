"""Base transformer protocol and metadata models.

Defines the ContentTransformer protocol that all transformers must implement,
plus metadata models for URL, PDF, and Image content.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from pydantic import BaseModel, Field, field_validator

from markwritter.storage.models import ContentType

if TYPE_CHECKING:
    from markwritter.storage.models import Content


class URLMetadata(BaseModel):
    """Metadata extracted from a web URL.

    Attributes:
        domain: The domain name of the URL (required).
        site_name: The name of the site.
        author: Content author.
        published_date: Publication date string.
        description: Meta description.
        keywords: List of meta keywords.
        og_image: OpenGraph image URL.
        canonical_url: Canonical URL of the page.
    """

    domain: str
    site_name: str | None = None
    author: str | None = None
    published_date: str | None = None
    description: str | None = None
    keywords: list[str] = Field(default_factory=list)
    og_image: str | None = None
    canonical_url: str | None = None

    @field_validator("domain")
    @classmethod
    def domain_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("domain must not be empty")
        return v.strip()

    def to_dict(self) -> dict:
        """Serialize metadata to a dictionary.

        Returns:
            Dictionary representation of all fields.
        """
        return self.model_dump()


class PDFMetadata(BaseModel):
    """Metadata extracted from a PDF document.

    Attributes:
        page_count: Number of pages (required, must be > 0).
        author: Document author.
        title: Document title.
        producer: PDF producer software.
        creator: PDF creator software.
        creation_date: Creation date string.
        modification_date: Last modification date string.
        file_size: File size in bytes.
    """

    page_count: int
    author: str | None = None
    title: str | None = None
    producer: str | None = None
    creator: str | None = None
    creation_date: str | None = None
    modification_date: str | None = None
    file_size: int | None = None

    @field_validator("page_count")
    @classmethod
    def page_count_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("page_count must be positive")
        return v

    def to_dict(self) -> dict:
        """Serialize metadata to a dictionary.

        Returns:
            Dictionary representation of all fields.
        """
        return self.model_dump()


class ImageMetadata(BaseModel):
    """Metadata extracted from an image file.

    Attributes:
        width: Image width in pixels (required, must be > 0).
        height: Image height in pixels (required, must be > 0).
        format: Image format string, e.g. "JPEG", "PNG" (required).
        mode: Color mode, e.g. "RGB", "RGBA".
        file_size: File size in bytes.
        ocr_text: Text extracted via OCR.
        dpi: Image DPI resolution.
        color_space: Color space description.
    """

    width: int
    height: int
    format: str
    mode: str | None = None
    file_size: int | None = None
    ocr_text: str | None = None
    dpi: int | None = None
    color_space: str | None = None

    @field_validator("width", "height")
    @classmethod
    def dimensions_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("dimensions must be positive")
        return v

    @field_validator("format")
    @classmethod
    def format_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("format must not be empty")
        return v.strip()

    def to_dict(self) -> dict:
        """Serialize metadata to a dictionary.

        Returns:
            Dictionary representation of all fields.
        """
        return self.model_dump()


@runtime_checkable
class ContentTransformer(Protocol):
    """Protocol for content transformers.

    A ContentTransformer converts a source (URL, file path, etc.)
    into a unified Content object. Each transformer handles a specific
    content type and provides methods for detection and extraction.
    """

    @property
    def source_type(self) -> ContentType:
        """Return the content type this transformer handles.

        Returns:
            ContentType enum value.
        """
        ...

    async def can_handle(self, source: str) -> bool:
        """Check if this transformer can handle the given source.

        Args:
            source: URL, file path, or other source identifier.

        Returns:
            True if this transformer can process the source.
        """
        ...

    async def extract(self, source: str) -> Content:
        """Extract content from the source.

        Args:
            source: URL, file path, or other source identifier.

        Returns:
            Content object with extracted text and metadata.
        """
        ...

    async def compute_hash(self, content: bytes | str) -> str:
        """Compute a deterministic hash for content deduplication.

        Args:
            content: Raw bytes or text content to hash.

        Returns:
            Hexadecimal hash string.
        """
        ...


__all__ = [
    "URLMetadata",
    "PDFMetadata",
    "ImageMetadata",
    "ContentTransformer",
]
