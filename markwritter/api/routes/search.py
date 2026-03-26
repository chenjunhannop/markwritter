"""Search API routes.

Provides endpoints for semantic search and Q&A over notes.

This module integrates with:
- SemanticSearch for vector-based search
- QASystem for question answering
- KeywordSearch for FTS5 full-text search
"""

from typing import Any, Optional

from fastapi import APIRouter, Query

from markwritter.query.models import (
    AskRequest,
    AskResponse,
    IndexRequest,
    IndexResponse,
    SearchResponse,
)

router = APIRouter()

# Global instances (set by dependency injection or initialization)
_semantic_search: Optional[Any] = None  # SemanticSearch
_qa_system: Optional[Any] = None  # QASystem
_keyword_search: Optional[Any] = None  # KeywordSearch


def init_search_routes(
    semantic_search: Optional[Any] = None,
    qa_system: Optional[Any] = None,
    keyword_search: Optional[Any] = None,
) -> None:
    """Initialize search routes with dependencies.

    Args:
        semantic_search: SemanticSearch instance for vector search
        qa_system: QASystem instance for Q&A
        keyword_search: KeywordSearch instance for FTS5 search
    """
    global _semantic_search, _qa_system, _keyword_search
    _semantic_search = semantic_search
    _qa_system = qa_system
    _keyword_search = keyword_search


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Semantic search",
    description="Search notes using semantic similarity",
)
async def semantic_search(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=20, description="Maximum results"),
) -> SearchResponse:
    """Search notes using semantic search.

    Falls back to keyword search if semantic search is not available.

    Args:
        query: Search query
        top_k: Maximum number of results

    Returns:
        Search results ranked by relevance
    """
    # Try semantic search first
    if _semantic_search is not None:
        try:
            results = await _semantic_search.search(query, top_k=top_k)
            return SearchResponse(
                query=query,
                results=[r.model_dump() for r in results],
                total=len(results),
            )
        except Exception:
            pass  # Fall through to keyword search

    # Fallback to keyword search
    if _keyword_search is not None:
        results = _keyword_search.search(query, limit=top_k)
        return SearchResponse(
            query=query,
            results=[r.model_dump() for r in results],
            total=len(results),
        )

    # No search available
    return SearchResponse(
        query=query,
        results=[],
        total=0,
    )


@router.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask a question",
    description="Ask a question and get an answer based on notes",
)
async def ask_question(request: AskRequest) -> AskResponse:
    """Ask a question about notes.

    Uses RAG to answer questions based on indexed content.

    Args:
        request: Ask request with question

    Returns:
        Answer with sources
    """
    if _qa_system is None:
        return AskResponse(
            question=request.question,
            answer="Q&A system not initialized. Please configure the memory service.",
            sources=[],
        )

    try:
        result = await _qa_system.ask(request.question, top_k=request.top_k)
        return AskResponse(
            question=result.question,
            answer=result.answer,
            sources=[s.model_dump() for s in result.sources],
        )
    except Exception as e:
        return AskResponse(
            question=request.question,
            answer=f"Error processing question: {str(e)}",
            sources=[],
        )


@router.post(
    "/index",
    response_model=IndexResponse,
    summary="Index vault",
    description="Index all notes in the vault for semantic search",
)
async def index_vault(request: IndexRequest) -> IndexResponse:
    """Index all notes in the vault.

    Note: This endpoint requires memory service integration.
    Currently returns a placeholder response.

    Args:
        request: Indexing parameters

    Returns:
        Indexing results
    """
    # TODO: Integrate with memory service for vector indexing
    # For now, use keyword search indexing if available
    if _keyword_search is not None:
        # Keyword search handles its own indexing via index_note method
        return IndexResponse(
            indexed=0,
            skipped=0,
            errors=["Keyword search indexing requires vault integration"],
        )

    return IndexResponse(
        indexed=0,
        skipped=0,
        errors=["Memory service not configured"],
    )


@router.post(
    "/index/{note_path:path}",
    response_model=dict[str, Any],
    summary="Index single note",
    description="Index a single note for semantic search",
)
async def index_note(note_path: str) -> dict[str, Any]:
    """Index a single note.

    Args:
        note_path: Path to the note

    Returns:
        Indexing result
    """
    # TODO: Integrate with memory service for vector indexing
    return {
        "indexed": 0,
        "note_path": note_path,
        "error": "Memory service not configured",
    }


@router.delete(
    "/index",
    summary="Clear index",
    description="Clear all indexed content",
)
async def clear_index() -> dict[str, Any]:
    """Clear the memory index.

    Returns:
        Clear result
    """
    if _keyword_search is not None:
        try:
            cleared = _keyword_search.clear_index()
            return {
                "cleared": cleared,
                "message": "Keyword search index cleared" if cleared else "Failed to clear index",
            }
        except Exception as e:
            return {
                "cleared": False,
                "error": str(e),
            }

    return {
        "cleared": False,
        "error": "Memory service not configured",
    }
