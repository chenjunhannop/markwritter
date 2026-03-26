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
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "vault_connected" in data

    def test_app_has_correct_metadata(self):
        """Test that FastAPI app has correct title and version."""
        from markwritter.api.app import get_app

        # Reset singleton to get fresh app with default settings
        import markwritter.api.app as app_module

        app_module._app = None

        app = get_app()
        assert app.title == "Markwritter API"
        assert app.version == "0.1.0"
