"""Tests for Chat API."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class TestChatAPI:
    """Test Chat API endpoints."""

    def test_chat_returns_sse_stream(self):
        """Test POST /api/chat returns SSE stream."""
        from markwritter.api.app import get_app

        with patch("markwritter.api.routes.chat.get_framework") as mock_get_framework:
            mock_framework = MagicMock()
            mock_framework.process_input.return_value = "Hello, world!"
            mock_get_framework.return_value = mock_framework

            app = get_app()
            client = TestClient(app)
            response = client.post("/api/chat/", json={"message": "hello"})
            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]

    def test_chat_stream_contains_events(self):
        """Test that chat stream contains expected events."""
        from markwritter.api.app import get_app

        with patch("markwritter.api.routes.chat.get_framework") as mock_get_framework:
            mock_framework = MagicMock()
            mock_framework.process_input.return_value = "Hi"
            mock_get_framework.return_value = mock_framework

            app = get_app()
            client = TestClient(app)
            response = client.post("/api/chat/", json={"message": "hello"})
            # Read the stream content
            content = response.text
            # Should contain SSE data lines
            assert "data:" in content

    def test_chat_stream_handles_error(self):
        """Test that chat stream handles errors gracefully."""
        from markwritter.api.app import get_app

        with patch("markwritter.api.routes.chat.get_framework") as mock_get_framework:
            mock_framework = MagicMock()
            mock_framework.process_input.side_effect = Exception("Test error")
            mock_get_framework.return_value = mock_framework

            app = get_app()
            client = TestClient(app)
            response = client.post("/api/chat/", json={"message": "hello"})
            assert response.status_code == 200
            content = response.text
            # Should contain error event
            assert "error" in content
