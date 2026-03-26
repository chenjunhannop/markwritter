"""Query models for Markwritter.

This module defines the data models used in search and Q&A operations:
- SearchResult: Basic search result with note path, title, score, snippet
- HighlightResult: Search result with highlighted snippet
- HybridSearchResult: Result with combined semantic and keyword scores
- SourceReference: Reference to a source note in Q&A
- AnswerResult: Q&A answer with sources
- SearchResponse: Response wrapper for search results

These models are used by:
- markwritter.query.search: Search implementations
- markwritter.api.routes.search: API endpoints
"""

from typing import Any

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Model for a single search result.

    Attributes:
        note_path: Path to the note relative to vault root
        title: Title of the note
        score: Relevance score (higher is better)
        snippet: Text snippet from the note
    """

    note_path: str
    title: str
    score: float
    snippet: str


class HighlightResult(BaseModel):
    """Model for a search result with highlighted snippet.

    Attributes:
        note_path: Path to the note relative to vault root
        title: Title of the note
        score: Relevance score (higher is better)
        highlighted_snippet: Snippet with <mark> tags around matching terms
    """

    note_path: str
    title: str
    score: float
    highlighted_snippet: str


class HybridSearchResult(BaseModel):
    """Model for hybrid search result with combined scores.

    Combines semantic (vector) and keyword (FTS) search scores.

    Attributes:
        note_path: Path to the note relative to vault root
        title: Title of the note
        semantic_score: Score from semantic/vector search
        keyword_score: Score from keyword/FTS search
        combined_score: Weighted combination of both scores
        snippet: Text snippet from the note
    """

    note_path: str
    title: str
    semantic_score: float
    keyword_score: float
    combined_score: float
    snippet: str


class SourceReference(BaseModel):
    """Model for a source reference in Q&A.

    Represents a note that was used as context for answering a question.

    Attributes:
        note_path: Path to the source note
        title: Title of the source note
        relevance_score: How relevant this source was to the question
        snippet: Relevant excerpt from the source
    """

    note_path: str
    title: str
    relevance_score: float = 0.0
    snippet: str = ""


class AnswerResult(BaseModel):
    """Model for Q&A answer.

    Attributes:
        question: The original question
        answer: The generated answer
        sources: List of source references used to generate the answer
    """

    question: str
    answer: str
    sources: list[SourceReference] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Response model for search endpoint.

    Attributes:
        query: The original search query
        results: List of search results
        total: Total number of matching results (may differ from len(results) for pagination)
    """

    query: str
    results: list[SearchResult]
    total: int


class AskRequest(BaseModel):
    """Request model for ask endpoint.

    Attributes:
        question: The question to ask
        top_k: Number of top results to consider
    """

    question: str
    top_k: int = Field(default=5, ge=1, le=20)


class AskResponse(BaseModel):
    """Response model for ask endpoint.

    Attributes:
        question: The original question
        answer: The generated answer
        sources: List of source references
    """

    question: str
    answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)


class IndexRequest(BaseModel):
    """Request model for indexing.

    Attributes:
        overwrite: Whether to overwrite existing index
        batch_size: Number of notes to process per batch
    """

    overwrite: bool = False
    batch_size: int = Field(default=10, ge=1, le=100)


class IndexResponse(BaseModel):
    """Response model for indexing.

    Attributes:
        indexed: Number of notes successfully indexed
        skipped: Number of notes skipped
        errors: List of error messages
    """

    indexed: int
    skipped: int
    errors: list[str] = Field(default_factory=list)


__all__ = [
    "SearchResult",
    "HighlightResult",
    "HybridSearchResult",
    "SourceReference",
    "AnswerResult",
    "SearchResponse",
    "AskRequest",
    "AskResponse",
    "IndexRequest",
    "IndexResponse",
]
