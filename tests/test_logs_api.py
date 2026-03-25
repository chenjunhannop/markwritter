"""Tests for Logs API."""


class TestLogsAPI:
    """Test Logs API endpoints."""

    def test_logs_stream_route_exists(self):
        """Test GET /api/logs/stream route is registered."""
        from markwritter.api.app import get_app

        app = get_app()
        # Check that the route is registered
        routes = [route.path for route in app.routes]
        assert "/api/logs/stream" in routes

    def test_logs_stream_endpoint_configuration(self):
        """Test that logs stream endpoint is properly configured."""
        from markwritter.api.app import get_app

        app = get_app()
        # Find the route
        route = None
        for r in app.routes:
            if hasattr(r, "path") and r.path == "/api/logs/stream":
                route = r
                break

        assert route is not None
        # Check it's a GET route
        if hasattr(route, "methods"):
            assert "GET" in route.methods
