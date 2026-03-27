"""Content transformers for the ingestion pipeline.

Provides transformers that convert various source formats (URL, PDF, Image)
into unified Content objects.
"""

from markwritter.storage.transformers.base import (
    ContentTransformer,
    URLMetadata,
    PDFMetadata,
    ImageMetadata,
)
from markwritter.storage.transformers.url import URLTransformer
from markwritter.storage.transformers.pdf import PDFTransformer
from markwritter.storage.transformers.image import ImageTransformer

__all__ = [
    # Protocol
    "ContentTransformer",
    # Metadata models
    "URLMetadata",
    "PDFMetadata",
    "ImageMetadata",
    # Transformers
    "URLTransformer",
    "PDFTransformer",
    "ImageTransformer",
]
