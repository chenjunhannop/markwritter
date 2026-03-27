"""Content ingestion pipeline.

Orchestrates content ingestion from multiple sources (URL, PDF, Image, etc.)
through registered transformers.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from pydantic import BaseModel, Field

from markwritter.storage.models import Content, ContentType
from markwritter.storage.transformers.base import ContentTransformer
from markwritter.storage.transformers.url import URLTransformer
from markwritter.storage.transformers.pdf import PDFTransformer
from markwritter.storage.transformers.image import ImageTransformer

logger = logging.getLogger(__name__)


class ContentIngestResult(BaseModel):
    """Result of content ingestion.
    
    Attributes:
        success: Whether ingestion succeeded.
        content: Extracted content (if successful).
        content_id: ID of saved content (if saved).
        error: Error message (if failed).
        warnings: List of warning messages.
        bytes_processed: Number of bytes processed.
        processing_time_ms: Processing time in milliseconds.
    """

    success: bool
    content: Optional[Content] = None
    content_id: Optional[str] = None
    error: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    bytes_processed: int = 0
    processing_time_ms: float = 0.0


class IngestionPipeline:
    """Orchestrates content ingestion from multiple sources.
    
    Registers transformers for different content types and routes
    sources to the appropriate transformer.
    
    Example:
        >>> pipeline = IngestionPipeline()
        >>> result = await pipeline.ingest("https://example.com")
        >>> if result.success:
        ...     print(f"Ingested: {result.content.title}")
    """

    def __init__(self) -> None:
        """Initialize ingestion pipeline with default transformers."""
        self._transformers: dict[ContentType, ContentTransformer] = {}
        self._register_default_transformers()

    def _register_default_transformers(self) -> None:
        """Register built-in transformers."""
        self.register(URLTransformer())
        self.register(PDFTransformer())
        self.register(ImageTransformer())

    def register(self, transformer: ContentTransformer) -> None:
        """Register a content transformer.
        
        Args:
            transformer: Transformer instance to register.
        """
        self._transformers[transformer.source_type] = transformer
        logger.debug(f"Registered transformer for {transformer.source_type}")

    def get_transformer(self, content_type: ContentType) -> Optional[ContentTransformer]:
        """Get transformer for a content type.
        
        Args:
            content_type: Content type to get transformer for.
            
        Returns:
            Transformer instance or None if not registered.
        """
        return self._transformers.get(content_type)

    async def detect_type(self, source: str) -> Optional[ContentType]:
        """Detect content type from source.
        
        Tries each registered transformer to find one that can handle
        the source.
        
        Args:
            source: Source string to detect type for.
            
        Returns:
            Detected ContentType or None if no transformer can handle it.
        """
        for content_type, transformer in self._transformers.items():
            try:
                if await transformer.can_handle(source):
                    return content_type
            except Exception as e:
                logger.debug(f"Transformer {content_type} error checking source: {e}")
                continue
        return None

    async def ingest(self, source: str) -> ContentIngestResult:
        """Ingest content from a source.
        
        Detects the content type and uses the appropriate transformer
        to extract content.
        
        Args:
            source: URL, file path, or other source identifier.
            
        Returns:
            ContentIngestResult with extraction results.
        """
        start_time = time.time()

        try:
            # Detect content type
            content_type = await self.detect_type(source)
            if not content_type:
                return ContentIngestResult(
                    success=False,
                    error=f"Unsupported content type for source: {source}",
                )

            # Get appropriate transformer
            transformer = self._transformers.get(content_type)
            if not transformer:
                return ContentIngestResult(
                    success=False,
                    error=f"No transformer registered for type: {content_type}",
                )

            # Extract content
            content = await transformer.extract(source)

            # Calculate processing stats
            processing_time = (time.time() - start_time) * 1000
            bytes_processed = (
                len(content.raw_content)
                if content.raw_content
                else len(content.text_content or "")
            )

            return ContentIngestResult(
                success=True,
                content=content,
                bytes_processed=bytes_processed,
                processing_time_ms=processing_time,
            )

        except FileNotFoundError as e:
            return ContentIngestResult(
                success=False,
                error=f"File not found: {e}",
            )
        except Exception as e:
            logger.exception(f"Ingestion failed for {source}")
            return ContentIngestResult(
                success=False,
                error=str(e),
            )


__all__ = ["ContentIngestResult", "IngestionPipeline"]
