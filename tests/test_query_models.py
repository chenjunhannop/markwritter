"""Tests for query models module.

Test coverage for markwritter/query/models.py
"""

import pytest

# These imports should fail initially (RED phase)
from markwritter.query.models import (
    AnswerResult,
    HighlightResult,
    HybridSearchResult,
    SearchResponse,
    SearchResult,
    SourceReference,
)


class TestSearchResult:
    """Test SearchResult model."""

    def test_create_search_result(self) -> None:
        """Should create SearchResult with all fields."""
        result = SearchResult(
            note_path="notes/test.md",
            title="Test Note",
            score=0.95,
            snippet="This is a test snippet...",
        )
        assert result.note_path == "notes/test.md"
        assert result.title == "Test Note"
        assert result.score == 0.95
        assert result.snippet == "This is a test snippet..."

    def test_search_result_is_pydantic_model(self) -> None:
        """SearchResult should be a Pydantic model."""
        assert hasattr(SearchResult, "model_dump")
        assert hasattr(SearchResult, "model_json_schema")

    def test_search_result_json_serialization(self) -> None:
        """SearchResult should be JSON serializable."""
        result = SearchResult(
            note_path="test.md",
            title="Title",
            score=1.0,
            snippet="Content",
        )
        json_data = result.model_dump()
        assert json_data["note_path"] == "test.md"
        assert json_data["score"] == 1.0


class TestHighlightResult:
    """Test HighlightResult model."""

    def test_create_highlight_result(self) -> None:
        """Should create HighlightResult with highlighted snippet."""
        result = HighlightResult(
            note_path="notes/test.md",
            title="Test Note",
            score=0.85,
            highlighted_snippet="This is <mark>highlighted</mark> text",
        )
        assert result.note_path == "notes/test.md"
        assert "<mark>" in result.highlighted_snippet

    def test_highlight_result_has_required_fields(self) -> None:
        """HighlightResult should have all required fields."""
        result = HighlightResult(
            note_path="test.md",
            title="Title",
            score=0.5,
            highlighted_snippet="Highlighted",
        )
        assert hasattr(result, "note_path")
        assert hasattr(result, "title")
        assert hasattr(result, "score")
        assert hasattr(result, "highlighted_snippet")


class TestHybridSearchResult:
    """Test HybridSearchResult model."""

    def test_create_hybrid_search_result(self) -> None:
        """Should create HybridSearchResult with combined scores."""
        result = HybridSearchResult(
            note_path="notes/test.md",
            title="Test Note",
            semantic_score=0.8,
            keyword_score=0.6,
            combined_score=0.72,
            snippet="Combined result snippet",
        )
        assert result.semantic_score == 0.8
        assert result.keyword_score == 0.6
        assert result.combined_score == 0.72

    def test_hybrid_search_result_score_fields(self) -> None:
        """HybridSearchResult should have separate score fields."""
        result = HybridSearchResult(
            note_path="test.md",
            title="Title",
            semantic_score=0.9,
            keyword_score=0.3,
            combined_score=0.6,
            snippet="Snippet",
        )
        assert result.semantic_score != result.keyword_score
        assert result.combined_score > 0


class TestSourceReference:
    """Test SourceReference model."""

    def test_create_source_reference(self) -> None:
        """Should create SourceReference with all fields."""
        ref = SourceReference(
            note_path="notes/source.md",
            title="Source Note",
            relevance_score=0.92,
            snippet="Relevant content...",
        )
        assert ref.note_path == "notes/source.md"
        assert ref.relevance_score == 0.92

    def test_source_reference_defaults(self) -> None:
        """SourceReference should have default values."""
        ref = SourceReference(
            note_path="test.md",
            title="Title",
        )
        assert ref.relevance_score == 0.0
        assert ref.snippet == ""

    def test_source_reference_optional_fields(self) -> None:
        """SourceReference optional fields should work correctly."""
        ref = SourceReference(
            note_path="test.md",
            title="Title",
            relevance_score=0.5,
        )
        assert ref.snippet == ""


class TestAnswerResult:
    """Test AnswerResult model."""

    def test_create_answer_result(self) -> None:
        """Should create AnswerResult with question, answer, and sources."""
        sources = [
            SourceReference(
                note_path="note1.md",
                title="Note 1",
                relevance_score=0.9,
            )
        ]
        result = AnswerResult(
            question="What is TDD?",
            answer="Test-Driven Development is a software development process.",
            sources=sources,
        )
        assert result.question == "What is TDD?"
        assert "Test-Driven" in result.answer
        assert len(result.sources) == 1

    def test_answer_result_default_sources(self) -> None:
        """AnswerResult should default to empty sources list."""
        result = AnswerResult(
            question="Question?",
            answer="Answer",
        )
        assert result.sources == []

    def test_answer_result_multiple_sources(self) -> None:
        """AnswerResult should support multiple sources."""
        sources = [
            SourceReference(note_path=f"note{i}.md", title=f"Note {i}")
            for i in range(3)
        ]
        result = AnswerResult(
            question="Question?",
            answer="Answer",
            sources=sources,
        )
        assert len(result.sources) == 3


class TestSearchResponse:
    """Test SearchResponse model."""

    def test_create_search_response(self) -> None:
        """Should create SearchResponse with results."""
        results = [
            SearchResult(
                note_path="note1.md",
                title="Note 1",
                score=0.9,
                snippet="Snippet 1",
            )
        ]
        response = SearchResponse(
            query="test query",
            results=results,
            total=1,
        )
        assert response.query == "test query"
        assert len(response.results) == 1
        assert response.total == 1

    def test_search_response_empty_results(self) -> None:
        """SearchResponse should handle empty results."""
        response = SearchResponse(
            query="no results query",
            results=[],
            total=0,
        )
        assert response.results == []
        assert response.total == 0

    def test_search_response_total_can_differ_from_results_length(
        self,
    ) -> None:
        """SearchResponse total can differ from results length for pagination."""
        results = [
            SearchResult(
                note_path=f"note{i}.md",
                title=f"Note {i}",
                score=0.9,
                snippet=f"Snippet {i}",
            )
            for i in range(5)
        ]
        response = SearchResponse(
            query="paginated query",
            results=results,
            total=100,  # Total matches, not just returned results
        )
        assert len(response.results) == 5
        assert response.total == 100


class TestModelIntegration:
    """Test model integration and compatibility."""

    def test_search_result_to_dict(self) -> None:
        """All models should support dict conversion."""
        result = SearchResult(
            note_path="test.md",
            title="Test",
            score=1.0,
            snippet="Test",
        )
        data = result.model_dump()
        assert isinstance(data, dict)
        assert "note_path" in data

    def test_models_json_schema_generation(self) -> None:
        """All models should generate JSON schema."""
        schema = SearchResult.model_json_schema()
        assert "properties" in schema
        assert "note_path" in schema["properties"]
        assert "title" in schema["properties"]

    def test_answer_result_with_search_results(self) -> None:
        """AnswerResult sources should be compatible with search results."""
        source = SourceReference(
            note_path="note.md",
            title="Note",
            relevance_score=0.8,
            snippet="Content",
        )
        answer = AnswerResult(
            question="Q?",
            answer="A",
            sources=[source],
        )
        assert answer.sources[0].note_path == "note.md"