"""RAG (Retrieval-Augmented Generation) search tool.

This module provides RAGSearchTool, which implements source-scoped vector search
for the Chat with Sources feature.

Features:
- Source-filtered retrieval (search only within selected files)
- Chunk-based retrieval with context window
- Citation generation for retrieved chunks
- Integration with PathResolver for path→content_id mapping
"""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Optional

from markwritter.storage.cache import VectorSearchCache, get_global_cache
from markwritter.storage.models import ContentRef
from markwritter.storage.path_resolver import PathResolver
from markwritter.storage.service import ContentService

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """A retrieved chunk of text with metadata."""

    text: str  # The actual text content
    file_path: str  # Source file path
    page_num: int = 0  # PDF page number, 0 for MD
    paragraph_idx: int = 0  # Paragraph index
    score: float = 0.0  # Relevance score
    content_id: str = ""  # Content ID for reference


@dataclass
class RAGSearchResult:
    """Result of a RAG search."""

    query: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    total_chunks: int = 0
    sources_searched: list[str] = field(default_factory=list)

    def get_context_text(self, max_chunks: int = 5) -> str:
        """Get concatenated context text for LLM prompt.

        Args:
            max_chunks: Maximum number of chunks to include

        Returns:
            Concatenated context text with source markers
        """
        if not self.chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(self.chunks[:max_chunks]):
            source_marker = f"[Source {i+1}: {chunk.file_path}"
            if chunk.page_num > 0:
                source_marker += f", page {chunk.page_num}"
            source_marker += "]"

            context_parts.append(f"{source_marker}\n{chunk.text}")

        return "\n\n---\n\n".join(context_parts)


class RAGSearchTool:
    """RAG search tool for source-scoped retrieval.

    Example:
        >>> tool = RAGSearchTool(content_service, path_resolver)
        >>> result = await tool.search(
        ...     query="What is transformer architecture?",
        ...     source_paths=["notes/ML/transformer.md"],
        ...     limit=5
        ... )
        >>> context = result.get_context_text()
    """

    def __init__(
        self,
        content_service: ContentService,
        path_resolver: Optional[PathResolver] = None,
        cache: Optional[VectorSearchCache] = None,
    ):
        """Initialize RAG search tool.

        Args:
            content_service: ContentService for content lookup
            path_resolver: PathResolver for path→content_id mapping
            cache: VectorSearchCache for caching results
        """
        self._content_service = content_service
        self._path_resolver = path_resolver
        self._cache = cache or get_global_cache()

    async def search(
        self,
        query: str,
        source_paths: Optional[list[str]] = None,
        limit: int = 5,
        use_cache: bool = True,
    ) -> RAGSearchResult:
        """Search for relevant chunks.

        Args:
            query: Search query string
            source_paths: Optional list of source file paths to scope search
            limit: Maximum number of chunks to retrieve
            use_cache: Whether to use caching

        Returns:
            RAGSearchResult with retrieved chunks
        """
        # Resolve source paths to content IDs
        content_ids: Optional[list[str]] = None
        if source_paths and self._path_resolver:
            content_ids = await self._path_resolver.resolve_sources(source_paths)
            logger.info(f"Resolved {len(source_paths)} paths to {len(content_ids)} content IDs")

        # Generate cache key
        cache_key = self._generate_cache_key(query, content_ids, limit)

        # Try cache first
        if use_cache:
            cached = await self._cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return self._deserialize_result(cached, query)

        # Perform search
        result = await self._do_search(query, content_ids, limit)
        result.sources_searched = source_paths or []

        # Cache result
        if use_cache:
            await self._cache.set(cache_key, self._serialize_result(result))

        return result

    async def _do_search(
        self,
        query: str,
        content_ids: Optional[list[str]],
        limit: int,
    ) -> RAGSearchResult:
        """Perform actual search.

        Currently implements keyword-based retrieval.
        TODO: Integrate with LlamaIndex for vector search.

        Args:
            query: Search query
            content_ids: Optional content ID filter
            limit: Result limit

        Returns:
            RAGSearchResult
        """
        # For now, implement keyword search via ContentService
        # This will be replaced with LlamaIndex vector search

        # Search for content matching query
        matches = await self._content_service.search(query, limit=limit * 2)

        # Filter by content_ids if provided
        if content_ids:
            matches = [m for m in matches if m.id in content_ids]

        # Convert to RetrievedChunk
        chunks: list[RetrievedChunk] = []
        for match in matches[:limit]:
            # Fetch full content
            content = await self._content_service.get(match.id)
            if content and content.text_content:
                # Extract snippet (first 500 chars for now)
                snippet = content.text_content[:500]
                chunk = RetrievedChunk(
                    text=snippet,
                    file_path=content.source_path or match.path or match.id,
                    page_num=0,  # Would come from LlamaIndex
                    paragraph_idx=0,
                    score=1.0,  # Would come from vector search
                    content_id=content.id,
                )
                chunks.append(chunk)

        return RAGSearchResult(
            query=query,
            chunks=chunks,
            total_chunks=len(chunks),
        )

    def _generate_cache_key(
        self,
        query: str,
        content_ids: Optional[list[str]],
        limit: int,
    ) -> str:
        """Generate cache key for search results."""
        key_data = f"{query}:{sorted(content_ids or [])}:{limit}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _serialize_result(self, result: RAGSearchResult) -> list[dict]:
        """Serialize result for caching."""
        return [
            {
                "text": chunk.text,
                "file_path": chunk.file_path,
                "page_num": chunk.page_num,
                "paragraph_idx": chunk.paragraph_idx,
                "score": chunk.score,
                "content_id": chunk.content_id,
            }
            for chunk in result.chunks
        ]

    def _deserialize_result(
        self,
        data: list[dict],
        query: str,
    ) -> RAGSearchResult:
        """Deserialize result from cache."""
        chunks = [
            RetrievedChunk(
                text=item["text"],
                file_path=item["file_path"],
                page_num=item["page_num"],
                paragraph_idx=item["paragraph_idx"],
                score=item["score"],
                content_id=item["content_id"],
            )
            for item in data
        ]
        return RAGSearchResult(
            query=query,
            chunks=chunks,
            total_chunks=len(chunks),
        )


__all__ = ["RAGSearchTool", "RetrievedChunk", "RAGSearchResult"]
