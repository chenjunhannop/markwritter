"""Tests for Chat API routes."""

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from markwritter.api.app import create_app


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
