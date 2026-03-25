"""Tests for FastAPI application skeleton."""

from fastapi.testclient import TestClient


class TestAPIHealth:
    """Test API health check endpoint."""

    def test_health_check_returns_ok(self):
        """Test GET /health returns status ok."""
        from markwritter.api.app import get_app

        app = get_app()
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "0.1.0", "vault_connected": False}

    def test_app_has_correct_metadata(self):
        """Test that FastAPI app has correct title and version."""
        from markwritter.api.app import get_app

        app = get_app()
        assert app.title == "Markwritter API"
        assert app.version == "0.1.0"
