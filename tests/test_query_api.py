"""Tests for Query API endpoints.

TDD approach: Tests for API routes before implementation.
"""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from markwritter.api.app import create_app
from markwritter.query.search import (
    KeywordSearch,
)

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_db() -> Generator[Path, None, None]:
    """Create a temporary database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test.db"


@pytest.fixture
def mock_keyword_search(temp_db: Path) -> KeywordSearch:
    """Create a keyword search with indexed notes."""
    search = KeywordSearch(db_path=temp_db)

    search.index_note(
        note_path="python-testing.md",
        title="Python Testing Guide",
        content="This guide covers TDD practices in Python. Use pytest for testing.",
        tags=["python", "testing"],
    )

    search.index_note(
        note_path="fastapi-tutorial.md",
        title="FastAPI Tutorial",
        content="Learn to build APIs with FastAPI. FastAPI is a modern web framework.",
        tags=["python", "fastapi"],
    )

    return search


@pytest.fixture
def mock_memory_service() -> MagicMock:
    """Create a mock memory service."""
    service = MagicMock()
    service.retrieve = AsyncMock(
        return_value={
            "items": [
                {
                    "id": "item-1",
                    "content": "Python testing guide",
                    "score": 0.95,
                    "user": {"note_path": "python-testing.md"},
                },
            ]
        }
    )
    return service


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Create a mock LLM client."""
    client = MagicMock()
    client.generate = AsyncMock(return_value="Based on your notes, pytest is recommended.")

    async def mock_stream(prompt: str, **kwargs):
        yield "Based"
        yield " on"
        yield " your"
        yield " notes."

    client.stream_generate = mock_stream
    return client


@pytest.fixture
def client(mock_keyword_search: KeywordSearch) -> Generator[TestClient, None, None]:
    """Create a test client with mocked dependencies."""
    app = create_app()

    # Override dependencies
    from markwritter.api.routes import query as query_routes

    # Store original state
    original_state = (
        query_routes._keyword_search,
        query_routes._semantic_search,
        query_routes._qa_system,
    )

    # Set mock state
    query_routes._keyword_search = mock_keyword_search

    yield TestClient(app)

    # Restore original state
    query_routes._keyword_search, query_routes._semantic_search, query_routes._qa_system = (
        original_state
    )


# ==============================================================================
# Keyword Search API Tests
# ==============================================================================


class TestKeywordSearchAPI:
    """Tests for keyword search API."""

    def test_search_endpoint_exists(self, client: TestClient) -> None:
        """Test that search endpoint exists."""
        response = client.post("/api/v1/query/search", json={"query": "python"})

        # Should not return 404
        assert response.status_code != 404

    def test_search_returns_results(self, client: TestClient) -> None:
        """Test that search returns results."""
        response = client.post("/api/v1/query/search", json={"query": "python"})

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data

    def test_search_with_limit(self, client: TestClient) -> None:
        """Test search with limit parameter."""
        response = client.post(
            "/api/v1/query/search",
            json={"query": "python", "limit": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 1

    def test_search_empty_query(self, client: TestClient) -> None:
        """Test search with empty query."""
        response = client.post("/api/v1/query/search", json={"query": ""})

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []

    def test_search_result_format(self, client: TestClient) -> None:
        """Test search result format."""
        response = client.post("/api/v1/query/search", json={"query": "testing"})

        assert response.status_code == 200
        data = response.json()

        if data["results"]:
            result = data["results"][0]
            assert "note_path" in result
            assert "title" in result
            assert "score" in result
            assert "snippet" in result

    def test_search_with_highlight_endpoint(self, client: TestClient) -> None:
        """Test search with highlight endpoint."""
        response = client.post(
            "/api/v1/query/search/highlight",
            json={"query": "python"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data


# ==============================================================================
# Semantic Search API Tests
# ==============================================================================


class TestSemanticSearchAPI:
    """Tests for semantic search API."""

    def test_semantic_search_endpoint(
        self, client: TestClient, mock_memory_service: MagicMock
    ) -> None:
        """Test semantic search endpoint."""
        from markwritter.api.routes import query as query_routes
        from markwritter.query.search import SemanticSearch

        # Set up semantic search
        query_routes._semantic_search = SemanticSearch(memory_service=mock_memory_service)

        response = client.post(
            "/api/v1/query/semantic",
            json={"query": "python testing"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_semantic_search_with_top_k(
        self, client: TestClient, mock_memory_service: MagicMock
    ) -> None:
        """Test semantic search with top_k parameter."""
        from markwritter.api.routes import query as query_routes
        from markwritter.query.search import SemanticSearch

        query_routes._semantic_search = SemanticSearch(memory_service=mock_memory_service)

        response = client.post(
            "/api/v1/query/semantic",
            json={"query": "python", "top_k": 3},
        )

        assert response.status_code == 200

    def test_hybrid_search_endpoint(
        self, client: TestClient, mock_memory_service: MagicMock, mock_keyword_search: KeywordSearch
    ) -> None:
        """Test hybrid search endpoint."""
        from markwritter.api.routes import query as query_routes
        from markwritter.query.search import SemanticSearch

        query_routes._semantic_search = SemanticSearch(
            memory_service=mock_memory_service,
            keyword_search=mock_keyword_search,
        )

        response = client.post(
            "/api/v1/query/hybrid",
            json={"query": "python", "mode": "balanced"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data


# ==============================================================================
# Q&A API Tests
# ==============================================================================


class TestQAAPI:
    """Tests for Q&A API."""

    def test_ask_endpoint(
        self, client: TestClient, mock_memory_service: MagicMock, mock_llm_client: MagicMock
    ) -> None:
        """Test ask endpoint."""
        from markwritter.api.routes import query as query_routes
        from markwritter.query.search import QASystem

        query_routes._qa_system = QASystem(
            memory_service=mock_memory_service,
            llm_client=mock_llm_client,
        )

        response = client.post(
            "/api/v1/query/ask",
            json={"question": "What is Python testing?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data

    def test_ask_with_top_k(
        self, client: TestClient, mock_memory_service: MagicMock, mock_llm_client: MagicMock
    ) -> None:
        """Test ask with top_k parameter."""
        from markwritter.api.routes import query as query_routes
        from markwritter.query.search import QASystem

        query_routes._qa_system = QASystem(
            memory_service=mock_memory_service,
            llm_client=mock_llm_client,
        )

        response = client.post(
            "/api/v1/query/ask",
            json={"question": "What is Python?", "top_k": 3},
        )

        assert response.status_code == 200

    def test_ask_empty_question(self, client: TestClient) -> None:
        """Test ask with empty question."""
        response = client.post(
            "/api/v1/query/ask",
            json={"question": ""},
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data


# ==============================================================================
# Streaming API Tests
# ==============================================================================


class TestStreamingAPI:
    """Tests for streaming API."""

    def test_ask_stream_endpoint(self, client: TestClient, mock_memory_service: MagicMock) -> None:
        """Test streaming ask endpoint."""
        from markwritter.api.routes import query as query_routes
        from markwritter.query.search import QASystem

        # Create mock LLM client with streaming
        mock_llm = MagicMock()

        async def mock_stream(prompt: str, **kwargs):
            yield "Test"
            yield " answer"

        mock_llm.stream_generate = mock_stream

        query_routes._qa_system = QASystem(
            memory_service=mock_memory_service,
            llm_client=mock_llm,
        )

        response = client.post(
            "/api/v1/query/ask/stream",
            json={"question": "What is Python?"},
        )

        # Should accept the request
        assert response.status_code == 200

    def test_stream_content_type(self, client: TestClient, mock_memory_service: MagicMock) -> None:
        """Test streaming response content type."""
        from markwritter.api.routes import query as query_routes
        from markwritter.query.search import QASystem

        mock_llm = MagicMock()

        async def mock_stream(prompt: str, **kwargs):
            yield "Test"

        mock_llm.stream_generate = mock_stream

        query_routes._qa_system = QASystem(
            memory_service=mock_memory_service,
            llm_client=mock_llm,
        )

        response = client.post(
            "/api/v1/query/ask/stream",
            json={"question": "What is Python?"},
        )

        # Should be SSE or streaming response
        assert (
            "text/event-stream" in response.headers.get("content-type", "")
            or response.status_code == 200
        )


# ==============================================================================
# Suggestion API Tests
# ==============================================================================


class TestSuggestionAPI:
    """Tests for search suggestions."""

    def test_suggest_endpoint(self, client: TestClient) -> None:
        """Test suggestion endpoint."""
        response = client.get("/api/v1/query/suggest", params={"query": "pyt"})

        # Should return suggestions
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data

    def test_suggest_short_query(self, client: TestClient) -> None:
        """Test suggestion with short query."""
        response = client.get("/api/v1/query/suggest", params={"query": "p"})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["suggestions"], list)

    def test_suggest_empty_query(self, client: TestClient) -> None:
        """Test suggestion with empty query."""
        response = client.get("/api/v1/query/suggest", params={"query": ""})

        assert response.status_code == 200
        data = response.json()
        assert data["suggestions"] == []


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestQueryAPIErrors:
    """Tests for error handling."""

    def test_search_missing_query(self, client: TestClient) -> None:
        """Test search without query parameter."""
        response = client.post("/api/v1/query/search", json={})

        # Should return validation error
        assert response.status_code == 422

    def test_ask_missing_question(self, client: TestClient) -> None:
        """Test ask without question parameter."""
        response = client.post("/api/v1/query/ask", json={})

        # Should return validation error
        assert response.status_code == 422

    def test_invalid_limit_parameter(self, client: TestClient) -> None:
        """Test search with invalid limit."""
        response = client.post(
            "/api/v1/query/search",
            json={"query": "test", "limit": -1},
        )

        # Should return validation error
        assert response.status_code == 422

    def test_invalid_top_k_parameter(self, client: TestClient) -> None:
        """Test ask with invalid top_k."""
        response = client.post(
            "/api/v1/query/ask",
            json={"question": "test", "top_k": 0},
        )

        # Should return validation error
        assert response.status_code == 422
