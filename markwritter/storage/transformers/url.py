"""URL content transformer.

Fetches and extracts content from web URLs, including metadata
from Open Graph tags and other sources.
"""

from __future__ import annotations

import hashlib
import logging
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from markwritter.storage.models import Content, ContentType, StorageBackend
from markwritter.storage.transformers.base import URLMetadata

logger = logging.getLogger(__name__)


class URLTransformer:
    """Transformer for URL content.
    
    Fetches web pages and extracts:
    - Title (from <title>, og:title, or h1)
    - Main text content (from <main>, <article>, or body)
    - Metadata (domain, author, published date, etc.)
    
    Attributes:
        timeout: Request timeout in seconds.
        max_size_bytes: Maximum response size in bytes.
    """

    # URL pattern for detection
    URL_PATTERN = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+"  # domain parts
        r"[A-Z]{2,6}\b"  # TLD
        r"(?:/[^\s]*)?$",  # optional path
        re.IGNORECASE,
    )

    def __init__(
        self,
        timeout: int = 30,
        max_size_mb: int = 10,
    ) -> None:
        """Initialize URL transformer.
        
        Args:
            timeout: Request timeout in seconds.
            max_size_mb: Maximum response size in megabytes.
        """
        self.timeout = timeout
        self.max_size_bytes = max_size_mb * 1024 * 1024

    @property
    def source_type(self) -> ContentType:
        """Return URL content type."""
        return ContentType.URL

    async def can_handle(self, source: str) -> bool:
        """Check if source is a valid HTTP/HTTPS URL.
        
        Args:
            source: Source string to check.
            
        Returns:
            True if source is an HTTP/HTTPS URL.
        """
        return bool(self.URL_PATTERN.match(source))

    async def extract(self, source: str) -> Content:
        """Fetch and extract content from URL.
        
        Args:
            source: URL to fetch.
            
        Returns:
            Content object with extracted text and metadata.
            
        Raises:
            aiohttp.ClientError: If fetching fails.
        """
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.get(source) as response:
                response.raise_for_status()
                html = await response.text()

        soup = BeautifulSoup(html, "html.parser")

        # Extract components
        title = self._extract_title(soup)
        text_content = self._extract_text(soup)
        metadata = self._extract_metadata(soup, source)

        # Compute content hash
        content_hash = await self.compute_hash(text_content)

        return Content(
            id="",  # Will be assigned by repository
            source_type=ContentType.URL,
            storage_backend=StorageBackend.DATABASE,
            text_content=text_content,
            title=title,
            source_url=source,
            source_path=source,
            metadata={"url_meta": metadata.model_dump()},
            tags=[],
            links=[],
            backlinks=[],
            content_hash=content_hash,
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

    # =========================================================================
    # Private extraction methods
    # =========================================================================

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from various sources.
        
        Priority: <title> -> og:title -> <h1>
        
        Args:
            soup: BeautifulSoup parsed HTML.
            
        Returns:
            Extracted title or "Untitled".
        """
        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        # Try og:title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        # Try first <h1>
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)

        return "Untitled"

    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main text content from HTML.
        
        Removes script, style, nav, and other non-content elements,
        then extracts text from main content area.
        
        Args:
            soup: BeautifulSoup parsed HTML.
            
        Returns:
            Extracted text content.
        """
        # Remove non-content elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Try to find main content area
        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", class_="content")
            or soup.find("div", class_="main")
        )

        if main:
            return main.get_text(separator="\n", strip=True)

        # Fall back to body
        if soup.body:
            return soup.body.get_text(separator="\n", strip=True)

        return ""

    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> URLMetadata:
        """Extract URL metadata from HTML.
        
        Extracts Open Graph tags, meta tags, and URL components.
        
        Args:
            soup: BeautifulSoup parsed HTML.
            url: Original URL.
            
        Returns:
            URLMetadata object.
        """
        parsed = urlparse(url)

        meta = URLMetadata(domain=parsed.netloc)

        # Open Graph tags
        og_site = soup.find("meta", property="og:site_name")
        if og_site and og_site.get("content"):
            meta.site_name = og_site["content"].strip()

        og_author = soup.find("meta", property="article:author")
        if og_author and og_author.get("content"):
            meta.author = og_author["content"].strip()

        # Meta description
        description = soup.find("meta", attrs={"name": "description"})
        if description and description.get("content"):
            meta.description = description["content"].strip()

        # Meta keywords
        keywords = soup.find("meta", attrs={"name": "keywords"})
        if keywords and keywords.get("content"):
            meta.keywords = [k.strip() for k in keywords["content"].split(",")]

        # Canonical URL
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            meta.canonical_url = canonical["href"]

        # OG image
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            meta.og_image = og_image["content"]

        # Published date
        published = soup.find("meta", property="article:published_time")
        if published and published.get("content"):
            meta.published_date = published["content"]

        return meta


__all__ = ["URLTransformer"]
