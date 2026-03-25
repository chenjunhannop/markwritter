"""Query API routes.

Provides endpoints for keyword search, semantic search, and Q&A.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from markwritter.query.search import (
    KeywordSearch,
    QASystem,
    SemanticSearch,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (set by dependency injection or initialization)
_keyword_search: Optional[KeywordSearch] = None
_semantic_search: Optional[SemanticSearch] = None
_qa_system: Optional[QASystem] = None


def init_query_routes(
    keyword_search: Optional[KeywordSearch] = None,
    semantic_search: Optional[SemanticSearch] = None,
    qa_system: Optional[QASystem] = None,
) -> None:
    """Initialize query routes with dependencies.

    Args:
        keyword_search: Keyword search instance
        semantic_search: Semantic search instance
        qa_system: Q&A system instance
    """
    global _keyword_search, _semantic_search, _qa_system
    _keyword_search = keyword_search
    _semantic_search = semantic_search
    _qa_system = qa_system


# ==============================================================================
# Request/Response Models
# ==============================================================================


class SearchRequest(BaseModel):
    """Request model for keyword search."""

    query: str
    limit: int = Field(default=10, ge=1, le=100)


class SearchHighlightRequest(BaseModel):
    """Request model for search with highlight."""

    query: str
    limit: int = Field(default=10, ge=1, le=100)


class SearchResponse(BaseModel):
    """Response model for search."""

    query: str
    results: list[dict[str, Any]]
    total: int


class SemanticSearchRequest(BaseModel):
    """Request model for semantic search."""

    query: str
    top_k: int = Field(default=5, ge=1, le=20)


class HybridSearchRequest(BaseModel):
    """Request model for hybrid search."""

    query: str
    mode: str = Field(default="balanced", pattern="^(keyword|semantic|balanced)$")
    top_k: int = Field(default=5, ge=1, le=20)


class AskRequest(BaseModel):
    """Request model for Q&A."""

    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    context: Optional[list[dict[str, str]]] = None


class AskResponse(BaseModel):
    """Response model for Q&A."""

    question: str
    answer: str
    sources: list[dict[str, Any]]


class AskStreamRequest(BaseModel):
    """Request model for streaming Q&A."""

    question: str
    top_k: int = Field(default=5, ge=1, le=20)
    context: Optional[list[dict[str, str]]] = None


class SuggestResponse(BaseModel):
    """Response model for suggestions."""

    query: str
    suggestions: list[str]


# ==============================================================================
# Keyword Search Endpoints
# ==============================================================================


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Keyword search",
    description="Search notes using SQLite FTS5 full-text search",
)
async def keyword_search(request: SearchRequest) -> SearchResponse:
    """Search notes using keyword matching.

    Args:
        request: Search request with query and limit

    Returns:
        Search results with matched notes
    """
    if not _keyword_search:
        return SearchResponse(
            query=request.query,
            results=[],
            total=0,
        )

    results = _keyword_search.search(request.query, limit=request.limit)

    return SearchResponse(
        query=request.query,
        results=[r.model_dump() for r in results],
        total=len(results),
    )


@router.post(
    "/search/highlight",
    response_model=SearchResponse,
    summary="Search with highlighting",
    description="Search notes with highlighted snippets",
)
async def search_with_highlight(request: SearchHighlightRequest) -> SearchResponse:
    """Search notes with highlighted results.

    Args:
        request: Search request

    Returns:
        Search results with highlighted snippets
    """
    if not _keyword_search:
        return SearchResponse(
            query=request.query,
            results=[],
            total=0,
        )

    results = _keyword_search.search_with_highlight(request.query, limit=request.limit)

    return SearchResponse(
        query=request.query,
        results=[r.model_dump() for r in results],
        total=len(results),
    )


# ==============================================================================
# Semantic Search Endpoints
# ==============================================================================


@router.post(
    "/semantic",
    response_model=SearchResponse,
    summary="Semantic search",
    description="Search notes using semantic similarity",
)
async def semantic_search(request: SemanticSearchRequest) -> SearchResponse:
    """Search notes using semantic similarity.

    Args:
        request: Semantic search request

    Returns:
        Semantically similar notes
    """
    if not _semantic_search:
        return SearchResponse(
            query=request.query,
            results=[],
            total=0,
        )

    results = await _semantic_search.search(request.query, top_k=request.top_k)

    return SearchResponse(
        query=request.query,
        results=[r.model_dump() for r in results],
        total=len(results),
    )


@router.post(
    "/hybrid",
    response_model=SearchResponse,
    summary="Hybrid search",
    description="Combine keyword and semantic search for best results",
)
async def hybrid_search(request: HybridSearchRequest) -> SearchResponse:
    """Hybrid search combining keyword and semantic approaches.

    Args:
        request: Hybrid search request with mode

    Returns:
        Combined and ranked search results
    """
    if not _semantic_search:
        # Fallback to keyword-only if no semantic search
        if _keyword_search:
            results = _keyword_search.search(request.query, limit=request.top_k)
            return SearchResponse(
                query=request.query,
                results=[r.model_dump() for r in results],
                total=len(results),
            )

        return SearchResponse(
            query=request.query,
            results=[],
            total=0,
        )

    results = await _semantic_search.hybrid_search(
        request.query,
        mode=request.mode,
        top_k=request.top_k,
    )

    return SearchResponse(
        query=request.query,
        results=[r.model_dump() for r in results],
        total=len(results),
    )


# ==============================================================================
# Q&A Endpoints
# ==============================================================================


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question",
    description="Ask a question and get an answer based on indexed notes",
)
async def ask_question(request: AskRequest) -> AskResponse:
    """Ask a question about your notes.

    Uses RAG to answer questions based on indexed content.

    Args:
        request: Question request

    Returns:
        Answer with source references
    """
    if not _qa_system:
        return AskResponse(
            question=request.question,
            answer="Q&A system not initialized. Please configure the memory service.",
            sources=[],
        )

    result = await _qa_system.ask(
        request.question,
        top_k=request.top_k,
        context=request.context,
    )

    return AskResponse(
        question=result.question,
        answer=result.answer,
        sources=[s.model_dump() for s in result.sources],
    )


@router.post(
    "/ask/stream",
    summary="Ask with streaming",
    description="Ask a question and receive a streaming response",
)
async def ask_question_stream(request: AskStreamRequest) -> StreamingResponse:
    """Ask a question with streaming response.

    Uses Server-Sent Events (SSE) for streaming.

    Args:
        request: Question request

    Returns:
        Streaming response with tokens and sources
    """
    if not _qa_system:
        async def error_stream():
            error_msg = json.dumps(
                {"type": "error", "content": "Q&A system not initialized"}
            )
            yield f"data: {error_msg}\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
        )

    import json

    async def generate_stream():
        try:
            async for chunk in _qa_system.ask_stream(
                request.question,
                top_k=request.top_k,
                context=request.context,
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
    )


# ==============================================================================
# Suggestion Endpoints
# ==============================================================================


@router.get(
    "/suggest",
    response_model=SuggestResponse,
    summary="Search suggestions",
    description="Get search suggestions based on query prefix",
)
async def get_suggestions(
    query: str = Query(default="", description="Query prefix for suggestions"),
    limit: int = Query(default=5, ge=1, le=10, description="Maximum suggestions"),
) -> SuggestResponse:
    """Get search suggestions.

    Args:
        query: Query prefix
        limit: Maximum suggestions

    Returns:
        List of suggested queries
    """
    if not query or len(query) < 2:
        return SuggestResponse(query=query, suggestions=[])

    suggestions: list[str] = []

    # Get suggestions from keyword search index if available
    if _keyword_search:
        # Search for notes with similar terms
        results = _keyword_search.search(query, limit=limit)

        # Extract unique terms from results
        for result in results:
            title = result.title
            if title and title.lower().startswith(query.lower()):
                if title not in suggestions:
                    suggestions.append(title)

            if len(suggestions) >= limit:
                break

    return SuggestResponse(
        query=query,
        suggestions=suggestions[:limit],
    )
