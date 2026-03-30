"""Tests for Chat API routes."""

import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from markwritter.api.app import create_app
from markwritter.api.routes import chat as chat_routes


@pytest.fixture
def app():
    """Create test FastAPI app."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        app = create_app(vault_path=str(vault_path))
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    with TestClient(app=app, base_url="http://test") as c:
        yield c


class TestSourceSelectionAPI:
    """Tests for /api/v1/chat/sources endpoints."""

    def test_select_sources(self, client: TestClient) -> None:
        """Test POST /api/v1/chat/sources - select sources for session."""
        payload = {
            "session_id": "test-session-123",
            "source_paths": ["notes/a.md", "notes/b.md"],
        }

        response = client.post("/api/v1/chat/sources", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert set(data["selected_sources"]) == {"notes/a.md", "notes/b.md"}
        assert data["count"] == 2

    def test_select_sources_empty(self, client: TestClient) -> None:
        """Test POST /api/v1/chat/sources with empty source list."""
        payload = {
            "session_id": "test-session-empty",
            "source_paths": [],
        }

        response = client.post("/api/v1/chat/sources", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-empty"
        assert data["selected_sources"] == []
        assert data["count"] == 0

    def test_get_selected_sources_existing_session(
        self, client: TestClient
    ) -> None:
        """Test GET /api/v1/chat/sources with existing session."""
        # First create session
        client.post(
            "/api/v1/chat/sources",
            json={
                "session_id": "test-session-get",
                "source_paths": ["notes/x.md", "notes/y.md"],
            },
        )

        # Then retrieve
        response = client.get("/api/v1/chat/sources?session_id=test-session-get")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-get"
        assert set(data["selected_sources"]) == {"notes/x.md", "notes/y.md"}
        assert data["count"] == 2

    def test_get_selected_sources_nonexistent_session(
        self, client: TestClient
    ) -> None:
        """Test GET /api/v1/chat/sources with nonexistent session."""
        response = client.get(
            "/api/v1/chat/sources?session_id=nonexistent-session"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "nonexistent-session"
        assert data["selected_sources"] == []
        assert data["count"] == 0

    def test_get_selected_sources_missing_param(
        self, client: TestClient
    ) -> None:
        """Test GET /api/v1/chat/sources without session_id param."""
        # FastAPI should return 422 for missing required query param
        response = client.get("/api/v1/chat/sources")

        assert response.status_code == 422  # Validation error

    def test_clear_sources(self, client: TestClient) -> None:
        """Test DELETE /api/v1/chat/sources - clear session sources."""
        # Create session with sources
        client.post(
            "/api/v1/chat/sources",
            json={
                "session_id": "test-session-clear",
                "source_paths": ["notes/to-clear.md"],
            },
        )

        # Clear sources
        response = client.request(
            "DELETE", "/api/v1/chat/sources", params={"session_id": "test-session-clear"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["session_id"] == "test-session-clear"

        # Verify sources are cleared
        get_response = client.get(
            "/api/v1/chat/sources?session_id=test-session-clear"
        )
        get_data = get_response.json()
        assert get_data["selected_sources"] == []

    def test_update_sources(self, client: TestClient) -> None:
        """Test updating sources for existing session."""
        # Initial selection
        client.post(
            "/api/v1/chat/sources",
            json={
                "session_id": "test-session-update",
                "source_paths": ["original.md"],
            },
        )

        # Update with new sources
        response = client.post(
            "/api/v1/chat/sources",
            json={
                "session_id": "test-session-update",
                "source_paths": ["new-a.md", "new-b.md", "new-c.md"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert set(data["selected_sources"]) == {"new-a.md", "new-b.md", "new-c.md"}
        assert data["count"] == 3

        # Verify update persisted
        get_response = client.get(
            "/api/v1/chat/sources?session_id=test-session-update"
        )
        get_data = get_response.json()
        assert set(get_data["selected_sources"]) == {"new-a.md", "new-b.md", "new-c.md"}

    def test_multiple_sessions_independence(
        self, client: TestClient
    ) -> None:
        """Test that multiple sessions maintain independent sources."""
        # Create session A
        client.post(
            "/api/v1/chat/sources",
            json={"session_id": "session-a", "source_paths": ["a1.md", "a2.md"]},
        )

        # Create session B
        client.post(
            "/api/v1/chat/sources",
            json={"session_id": "session-b", "source_paths": ["b1.md"]},
        )

        # Verify session A
        response_a = client.get("/api/v1/chat/sources?session_id=session-a")
        data_a = response_a.json()
        assert set(data_a["selected_sources"]) == {"a1.md", "a2.md"}

        # Verify session B
        response_b = client.get("/api/v1/chat/sources?session_id=session-b")
        data_b = response_b.json()
        assert data_b["selected_sources"] == ["b1.md"]


class TestChatEndpoint:
    """Tests for POST /api/v1/chat endpoint."""

    def test_chat_basic(self, client: TestClient) -> None:
        """Test POST /api/v1/chat - basic chat request."""
        payload = {"message": "Hello, world!"}

        response = client.post("/api/v1/chat", json=payload)

        # Should return SSE stream
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_chat_with_session_id(self, client: TestClient) -> None:
        """Test POST /api/v1/chat with session_id for multi-turn."""
        payload = {"message": "Continue our conversation", "session_id": "existing-session"}

        response = client.post("/api/v1/chat", json=payload)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_chat_empty_message(self, client: TestClient) -> None:
        """Test POST /api/v1/chat with empty message."""
        payload = {"message": ""}

        response = client.post("/api/v1/chat", json=payload)

        # Should still process (may return empty response or error)
        assert response.status_code == 200

    def test_chat_streams_tokens_and_citations(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test chat endpoint streams LLM tokens and citation event."""

        class FakeChatDB:
            def __init__(self) -> None:
                self.saved_messages: list[tuple[str, int, str, str]] = []

            async def get_sources(self, session_id: str) -> list[str]:
                return []

            async def get_conversation_history(self, session_id: str) -> list[dict]:
                return []

            async def save_session(self, session_id: str, sources: list[str]) -> None:
                return None

            async def save_message(
                self, session_id: str, message_index: int, role: str, content: str
            ) -> None:
                self.saved_messages.append((session_id, message_index, role, content))

        class FakeRAGTool:
            async def search(self, query: str, source_paths=None, limit: int = 5):
                chunk = SimpleNamespace(
                    text="Source snippet",
                    file_path="notes/a.md",
                    page_num=0,
                    paragraph_idx=0,
                    score=1.0,
                    content_id="notes/a.md",
                )
                return SimpleNamespace(chunks=[chunk])

        class FakeLLMService:
            def __init__(self) -> None:
                self.messages: list[dict[str, str]] | None = None

            async def stream_complete(self, messages):
                self.messages = messages
                for token in ["Hello", " world"]:
                    yield token

        fake_db = FakeChatDB()
        fake_llm = FakeLLMService()

        async def fake_get_chat_db():
            return fake_db

        async def fake_get_rag_tool():
            return FakeRAGTool()

        monkeypatch.setattr(chat_routes, "get_chat_db", fake_get_chat_db)
        monkeypatch.setattr(chat_routes, "get_rag_tool", fake_get_rag_tool)
        monkeypatch.setattr(chat_routes, "get_llm_service", lambda: fake_llm)

        response = client.post(
            "/api/v1/chat",
            json={
                "message": "Summarize this",
                "session_id": "session-1",
                "sources": ["notes/a.md"],
                "conversation_history": [{"role": "user", "content": "Earlier"}],
            },
        )

        assert response.status_code == 200
        assert '"type":"text_delta","content":"Hello"' in response.text
        assert '"type":"text_delta","content":" world"' in response.text
        assert '"type":"citation"' in response.text
        assert fake_llm.messages is not None
        assert fake_llm.messages[1] == {"role": "user", "content": "Earlier"}
        assert fake_db.saved_messages[-1] == (
            "session-1",
            1,
            "assistant",
            "Hello world",
        )

    def test_chat_uses_database_sources_when_request_omits_them(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test chat falls back to persisted selected sources."""

        class FakeChatDB:
            async def get_sources(self, session_id: str) -> list[str]:
                return ["notes/persisted.md"]

            async def get_conversation_history(self, session_id: str) -> list[dict]:
                return []

            async def save_session(self, session_id: str, sources: list[str]) -> None:
                return None

            async def save_message(
                self, session_id: str, message_index: int, role: str, content: str
            ) -> None:
                return None

        class FakeRAGTool:
            def __init__(self) -> None:
                self.source_paths = None

            async def search(self, query: str, source_paths=None, limit: int = 5):
                self.source_paths = source_paths
                return SimpleNamespace(chunks=[])

        class FakeLLMService:
            async def stream_complete(self, messages):
                yield "Done"

        fake_rag_tool = FakeRAGTool()

        async def fake_get_chat_db():
            return FakeChatDB()

        async def fake_get_rag_tool():
            return fake_rag_tool

        monkeypatch.setattr(chat_routes, "get_chat_db", fake_get_chat_db)
        monkeypatch.setattr(chat_routes, "get_rag_tool", fake_get_rag_tool)
        monkeypatch.setattr(chat_routes, "get_llm_service", lambda: FakeLLMService())

        response = client.post(
            "/api/v1/chat",
            json={"message": "Question", "session_id": "session-2"},
        )

        assert response.status_code == 200
        assert fake_rag_tool.source_paths == ["notes/persisted.md"]


class TestSSEStreamParsing:
    """Tests for SSE stream format."""

    def test_chat_sse_format(self, client: TestClient) -> None:
        """Test that chat endpoint returns properly formatted SSE events."""
        payload = {"message": "Test message"}

        response = client.post("/api/v1/chat", json=payload)

        content = response.text

        # SSE events should be separated by double newlines
        assert "\n\n" in content

        # Should contain event data
        assert "data:" in content
