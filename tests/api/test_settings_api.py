"""Tests for Settings API endpoints (TDD RED phase)."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


class TestSettingsAPI:
    """Tests for Settings API endpoints."""

    @pytest.fixture(autouse=True)
    def reset_settings_state(self):
        """Reset the settings module state before each test."""
        import markwritter.api.routes.settings as settings_module

        settings_module._data_dir = None
        settings_module._settings_cache = {
            "theme": "system",
            "language": "en",
            "vault_path": "",
        }

    @pytest.fixture
    def app(self):
        """Create test FastAPI app with settings router."""
        from markwritter.api.routes.settings import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/settings", tags=["Settings"])
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    # =========================================================================
    # GET /api/v1/settings
    # =========================================================================

    def test_get_settings_returns_defaults(self, client):
        """GET /api/v1/settings returns default values."""
        response = client.get("/api/v1/settings")

        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "system"
        assert data["language"] == "en"
        assert data["vault_path"] == ""

    # =========================================================================
    # PUT /api/v1/settings - Update operations
    # =========================================================================

    def test_update_theme(self, client):
        """PUT /api/v1/settings with {theme: 'dark'} updates theme."""
        response = client.put("/api/v1/settings", json={"theme": "dark"})
        assert response.status_code == 200
        assert response.json()["theme"] == "dark"

        # Verify via GET
        response = client.get("/api/v1/settings")
        assert response.json()["theme"] == "dark"

    def test_update_language(self, client):
        """PUT /api/v1/settings with {language: 'zh'} updates language."""
        response = client.put("/api/v1/settings", json={"language": "zh"})
        assert response.status_code == 200
        assert response.json()["language"] == "zh"

        # Verify via GET
        response = client.get("/api/v1/settings")
        assert response.json()["language"] == "zh"

    def test_partial_update_preserves_other(self, client):
        """PUT only theme, language remains unchanged."""
        # First set language to zh
        client.put("/api/v1/settings", json={"language": "zh"})

        # Now update only theme
        response = client.put("/api/v1/settings", json={"theme": "light"})
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "light"
        assert data["language"] == "zh"
        assert data["vault_path"] == ""

    # =========================================================================
    # Validation - 422 Unprocessable Entity
    # =========================================================================

    def test_invalid_theme_returns_422(self, client):
        """PUT with theme='invalid' returns 422."""
        response = client.put("/api/v1/settings", json={"theme": "invalid"})
        assert response.status_code == 422

    def test_empty_language_returns_422(self, client):
        """PUT with language='' returns 422."""
        response = client.put("/api/v1/settings", json={"language": ""})
        assert response.status_code == 422

    def test_whitespace_only_language_returns_422(self, client):
        """PUT with language='   ' returns 422."""
        response = client.put("/api/v1/settings", json={"language": "   "})
        assert response.status_code == 422

    def test_invalid_vault_path_traversal_returns_422(self, client):
        """PUT with vault_path containing '../' returns 422 (Pydantic validation)."""
        response = client.put("/api/v1/settings", json={"vault_path": "../etc/passwd"})
        assert response.status_code == 422

    def test_invalid_vault_path_absolute_returns_422(self, client):
        """PUT with vault_path as absolute path returns 422."""
        response = client.put("/api/v1/settings", json={"vault_path": "/etc/passwd"})
        assert response.status_code == 422

    # =========================================================================
    # Vault path traversal - HTTP level (belt and suspenders)
    # =========================================================================

    def test_vault_path_traversal_blocked(self, client):
        """PUT with vault_path containing '../' is blocked by validation."""
        response = client.put(
            "/api/v1/settings",
            json={"vault_path": "../../../etc/passwd"},
        )
        assert response.status_code == 422

    # =========================================================================
    # Persistence across requests
    # =========================================================================

    def test_settings_persist_across_requests(self, client):
        """Update then GET in same client session returns updated value."""
        client.put("/api/v1/settings", json={"theme": "dark", "language": "ja"})

        response = client.get("/api/v1/settings")
        data = response.json()
        assert data["theme"] == "dark"
        assert data["language"] == "ja"

    # =========================================================================
    # Security - no API keys in response
    # =========================================================================

    def test_get_settings_no_api_keys(self, client):
        """Response never contains api_key or similar fields."""
        response = client.get("/api/v1/settings")
        data = response.json()

        forbidden_keys = ["api_key", "apikey", "secret", "token", "password", "auth"]
        for key in forbidden_keys:
            assert key not in data, f"Response must not contain '{key}'"

    # =========================================================================
    # PUT with empty body (all None) - should still work
    # =========================================================================

    def test_put_with_empty_body(self, client):
        """PUT with empty JSON object returns current settings unchanged."""
        response = client.put("/api/v1/settings", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "system"
        assert data["language"] == "en"
        assert data["vault_path"] == ""

    def test_put_response_matches_get(self, client):
        """PUT response body matches subsequent GET response."""
        client.put("/api/v1/settings", json={"theme": "dark", "language": "zh"})
        put_response = client.put("/api/v1/settings", json={"theme": "light"})
        get_response = client.get("/api/v1/settings")
        assert put_response.json() == get_response.json()


class TestSettingsPersistence:
    """Tests for settings file persistence."""

    @pytest.fixture(autouse=True)
    def reset_settings_state(self):
        """Reset the settings module state before each test."""
        import markwritter.api.routes.settings as settings_module

        settings_module._data_dir = None
        settings_module._settings_cache = {
            "theme": "system",
            "language": "en",
            "vault_path": "",
        }

    def test_settings_persist_to_file(self, tmp_path):
        """Settings are written to and read from the JSON file."""
        from markwritter.api.routes.settings import init_settings, router

        init_settings(str(tmp_path))

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/settings", tags=["Settings"])
        client = TestClient(app)

        # Update settings
        client.put("/api/v1/settings", json={"theme": "dark", "language": "ja"})

        # Verify file was created
        settings_file = tmp_path / ".markwritter" / "settings.json"
        assert settings_file.exists()

        # Verify file contents
        with open(settings_file) as f:
            file_data = json.load(f)
        assert file_data["theme"] == "dark"
        assert file_data["language"] == "ja"

    def test_settings_load_from_existing_file(self, tmp_path):
        """Settings are loaded from an existing JSON file on init."""
        from markwritter.api.routes.settings import init_settings, router

        # Pre-populate settings file
        settings_file = tmp_path / ".markwritter" / "settings.json"
        settings_file.parent.mkdir(parents=True)
        settings_file.write_text(json.dumps({
            "theme": "light",
            "language": "zh",
            "vault_path": "my-vault",
        }))

        init_settings(str(tmp_path))

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/settings", tags=["Settings"])
        client = TestClient(app)

        response = client.get("/api/v1/settings")
        data = response.json()
        assert data["theme"] == "light"
        assert data["language"] == "zh"
        assert data["vault_path"] == "my-vault"

    def test_init_creates_directory_if_missing(self, tmp_path):
        """init_settings creates the .markwritter directory if it does not exist."""
        from markwritter.api.routes.settings import init_settings

        data_dir = tmp_path / "subdir" / ".markwritter"
        assert not data_dir.exists()

        init_settings(str(data_dir.parent))
        assert data_dir.exists()

    def test_corrupted_settings_file_falls_back_to_defaults(self, tmp_path):
        """A corrupted settings file does not crash; falls back to defaults."""
        from markwritter.api.routes.settings import init_settings, router

        # Write corrupted JSON
        settings_file = tmp_path / ".markwritter" / "settings.json"
        settings_file.parent.mkdir(parents=True)
        settings_file.write_text("NOT VALID JSON {{{")

        init_settings(str(tmp_path))

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/settings", tags=["Settings"])
        client = TestClient(app)

        response = client.get("/api/v1/settings")
        assert response.status_code == 200
        data = response.json()
        # Should fall back to defaults
        assert data["theme"] == "system"
        assert data["language"] == "en"

    def test_extra_fields_in_file_are_ignored(self, tmp_path):
        """Extra fields in the settings file are preserved but not exposed."""
        from markwritter.api.routes.settings import init_settings, router

        settings_file = tmp_path / ".markwritter" / "settings.json"
        settings_file.parent.mkdir(parents=True)
        settings_file.write_text(json.dumps({
            "theme": "dark",
            "language": "en",
            "vault_path": "",
            "secret_api_key": "should-not-leak",
            "internal_debug": True,
        }))

        init_settings(str(tmp_path))

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/settings", tags=["Settings"])
        client = TestClient(app)

        response = client.get("/api/v1/settings")
        data = response.json()
        assert "secret_api_key" not in data
        assert "internal_debug" not in data
        assert data["theme"] == "dark"


class TestSettingsRouterRegistration:
    """Tests for settings router registration in the main app."""

    @pytest.fixture(autouse=True)
    def reset_settings_state(self):
        """Reset the settings module state before each test."""
        import markwritter.api.routes.settings as settings_module

        settings_module._data_dir = None
        settings_module._settings_cache = {
            "theme": "system",
            "language": "en",
            "vault_path": "",
        }

    def test_router_registered_in_app(self):
        """Verify settings routes appear in app's route list."""
        from markwritter.api.app import create_app

        app = create_app()
        route_paths = [route.path for route in app.routes]
        assert "/api/v1/settings/" in route_paths

    def test_settings_endpoints_accessible(self):
        """Both GET and PUT settings endpoints are accessible."""
        from markwritter.api.app import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/api/v1/settings/")
        assert response.status_code == 200

        response = client.put("/api/v1/settings/", json={"theme": "dark"})
        assert response.status_code == 200

    def test_settings_routes_have_settings_tag(self):
        """Settings routes are tagged with 'Settings'."""
        from markwritter.api.app import create_app

        app = create_app()
        for route in app.routes:
            if hasattr(route, "path") and "/settings" in route.path:
                if hasattr(route, "tags"):
                    assert "Settings" in route.tags


class TestSettingsEdgeCases:
    """Edge case tests for settings API."""

    @pytest.fixture(autouse=True)
    def reset_settings_state(self):
        """Reset the settings module state before each test."""
        import markwritter.api.routes.settings as settings_module

        settings_module._data_dir = None
        settings_module._settings_cache = {
            "theme": "system",
            "language": "en",
            "vault_path": "",
        }

    @pytest.fixture
    def app(self):
        """Create test FastAPI app with settings router."""
        from markwritter.api.routes.settings import router

        app = FastAPI()
        app.include_router(router, prefix="/api/v1/settings", tags=["Settings"])
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_update_all_valid_themes(self, client):
        """All three valid theme values are accepted."""
        for theme in ["light", "dark", "system"]:
            response = client.put("/api/v1/settings", json={"theme": theme})
            assert response.status_code == 200, f"Theme '{theme}' should be valid"
            assert response.json()["theme"] == theme

    def test_update_vault_path_valid_relative(self, client):
        """A valid relative vault_path is accepted."""
        response = client.put("/api/v1/settings", json={"vault_path": "my-vault"})
        assert response.status_code == 200
        assert response.json()["vault_path"] == "my-vault"

    def test_update_vault_path_with_subdirectory(self, client):
        """A vault_path with subdirectories is accepted."""
        response = client.put(
            "/api/v1/settings",
            json={"vault_path": "notes/my-vault"},
        )
        assert response.status_code == 200
        assert response.json()["vault_path"] == "notes/my-vault"

    def test_language_with_surrounding_whitespace(self, client):
        """Language value is trimmed of surrounding whitespace."""
        response = client.put("/api/v1/settings", json={"language": "  zh  "})
        assert response.status_code == 200
        assert response.json()["language"] == "zh"

    def test_get_response_is_json_object(self, client):
        """GET response is a valid JSON object with exactly the expected keys."""
        response = client.get("/api/v1/settings")
        data = response.json()
        expected_keys = {"theme", "language", "vault_path"}
        assert set(data.keys()) == expected_keys

    def test_multiple_sequential_updates(self, client):
        """Multiple sequential updates accumulate correctly."""
        client.put("/api/v1/settings", json={"theme": "dark"})
        client.put("/api/v1/settings", json={"language": "ja"})
        client.put("/api/v1/settings", json={"vault_path": "test-vault"})

        response = client.get("/api/v1/settings")
        data = response.json()
        assert data["theme"] == "dark"
        assert data["language"] == "ja"
        assert data["vault_path"] == "test-vault"
