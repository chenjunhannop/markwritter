"""PDF content transformer.

Extracts text and metadata from PDF files.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from pypdf import PdfReader

from markwritter.storage.models import Content, ContentType, StorageBackend
from markwritter.storage.transformers.base import PDFMetadata

logger = logging.getLogger(__name__)


class PDFTransformer:
    """Transformer for PDF content.
    
    Extracts text content and metadata from PDF files using pypdf.
    
    Attributes:
        max_file_size_mb: Maximum PDF file size in megabytes.
    """

    # Supported PDF extensions
    PDF_EXTENSIONS = {".pdf"}

    def __init__(self, max_file_size_mb: int = 100) -> None:
        """Initialize PDF transformer.
        
        Args:
            max_file_size_mb: Maximum PDF file size in megabytes.
        """
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    @property
    def source_type(self) -> ContentType:
        """Return PDF content type."""
        return ContentType.PDF

    async def can_handle(self, source: str) -> bool:
        """Check if source is a PDF file path.
        
        Args:
            source: Source string to check.
            
        Returns:
            True if source is a path ending with .pdf.
        """
        path = Path(source)
        return path.suffix.lower() in self.PDF_EXTENSIONS

    async def extract(self, source: str) -> Content:
        """Extract text and metadata from PDF.
        
        Args:
            source: Path to PDF file.
            
        Returns:
            Content object with extracted text and metadata.
            
        Raises:
            FileNotFoundError: If PDF file does not exist.
        """
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {source}")

        # Read PDF
        reader = PdfReader(str(path))

        # Extract text from all pages
        text_pages = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
        text_content = "\n\n".join(text_pages)

        # Extract metadata
        pdf_meta = self._extract_metadata(reader, path)

        # Determine title
        title = pdf_meta.title or path.stem

        # Compute hash
        raw_content = path.read_bytes()
        content_hash = await self.compute_hash(raw_content)

        return Content(
            id="",  # Will be assigned by repository
            source_type=ContentType.PDF,
            storage_backend=StorageBackend.DATABASE,
            text_content=text_content,
            raw_content=raw_content,
            title=title,
            source_path=str(path),
            storage_path=f"pdfs/{path.name}",
            metadata={"pdf_meta": pdf_meta.model_dump()},
            tags=[],
            links=[],
            backlinks=[],
            content_hash=content_hash,
            mime_type="application/pdf",
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

    def _extract_metadata(self, reader: PdfReader, path: Path) -> PDFMetadata:
        """Extract metadata from PDF.
        
        Args:
            reader: PdfReader instance.
            path: Path to PDF file.
            
        Returns:
            PDFMetadata object.
        """
        file_size = path.stat().st_size if path.exists() else None

        meta = PDFMetadata(
            page_count=len(reader.pages),
            file_size=file_size,
        )

        # Extract PDF metadata if available
        if reader.metadata:
            if reader.metadata.title:
                meta.title = reader.metadata.title
            if reader.metadata.author:
                meta.author = reader.metadata.author
            if reader.metadata.producer:
                meta.producer = reader.metadata.producer
            if reader.metadata.creator:
                meta.creator = reader.metadata.creator
            if reader.metadata.creation_date:
                meta.creation_date = str(reader.metadata.creation_date)
            if reader.metadata.modification_date:
                meta.modification_date = str(reader.metadata.modification_date)

        return meta


__all__ = ["PDFTransformer"]
