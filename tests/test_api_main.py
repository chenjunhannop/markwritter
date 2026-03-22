"""Tests for FastAPI application skeleton."""

from fastapi.testclient import TestClient


class TestAPIHealth:
    """Test API health check endpoint."""

    def test_health_check_returns_ok(self):
        """Test GET /health returns status ok."""
        from api.main import app

        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_app_has_correct_metadata(self):
        """Test that FastAPI app has correct title and version."""
        from api.main import app

        assert app.title == "Markwritter API"
        assert app.version == "0.1.0"
