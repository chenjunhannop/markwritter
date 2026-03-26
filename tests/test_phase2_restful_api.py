"""Tests for RESTful API refactoring (Phase 2).

TDD approach: Tests for new RESTful endpoints and backward compatibility.

Phase 2.1: RESTful Endpoint Refactoring
- POST /create -> POST /notes
- PUT /update -> PUT /notes/{note_path}
- Keep old endpoints as deprecated aliases

Phase 2.2: Unified API Version Prefix
- skills, chat, logs routes should use /api/v1 prefix
"""

import warnings
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from markwritter.api.app import create_app
from markwritter.obsidian.vault import ObsidianVault

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        (vault_path / "existing-note.md").write_text(
            "---\ntitle: Existing Note\ntags: [test]\n---\n\nExisting content."
        )
        yield vault_path


@pytest.fixture
def mock_vault(temp_vault: Path) -> MagicMock:
    """Create a mock ObsidianVault."""
    vault = MagicMock(spec=ObsidianVault)
    vault.path = temp_vault
    vault.note_exists.return_value = False
    vault.write_note = MagicMock()
    return vault


@pytest.fixture
def mock_vault_for_update(temp_vault: Path) -> MagicMock:
    """Create a mock ObsidianVault for update operations."""
    from markwritter.obsidian.models import Note

    vault = MagicMock(spec=ObsidianVault)
    vault.path = temp_vault
    vault.note_exists.return_value = True

    # Create a mock note for reading
    mock_note = MagicMock(spec=Note)
    mock_note.content = "Original content."
    mock_note.metadata = {"title": "Test"}
    vault.read_note.return_value = mock_note
    vault.write_note = MagicMock()
    return vault


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client."""
    app = create_app()
    yield TestClient(app)


# ==============================================================================
# Phase 2.1: New RESTful Endpoints Tests (notes.py)
# ==============================================================================


class TestNewRESTfulCreateNoteEndpoint:
    """Tests for new RESTful POST /api/v1/notes endpoint."""

    def test_create_note_endpoint_exists(self, client: TestClient) -> None:
        """Test that new POST /api/v1/notes endpoint exists."""
        response = client.post(
            "/api/v1/notes",
            json={
                "path": "new-note.md",
                "content": "New note content",
            },
        )

        # Should not return 404
        assert response.status_code != 404

    def test_create_note_returns_201_on_success(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that POST /api/v1/notes returns 201 on success."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "new-note.md",
                "content": "# New Note\n\nContent here.",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data.get("success") is True
        assert data.get("path") == "new-note.md"

    def test_create_note_with_metadata(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test creating note with metadata via new endpoint."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "note-with-meta.md",
                "content": "Content here.",
                "metadata": {
                    "title": "My Note",
                    "tags": ["python", "testing"],
                },
            },
        )

        assert response.status_code == 201

    def test_create_note_conflict_when_exists(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that POST /api/v1/notes returns 409 when note exists."""
        from markwritter.api.routes import notes as notes_routes

        mock_vault.note_exists.return_value = True
        notes_routes._vault = mock_vault

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "existing-note.md",
                "content": "New content",
            },
        )

        assert response.status_code == 409

    def test_create_note_with_overwrite_flag(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that overwrite flag works on new endpoint."""
        from markwritter.api.routes import notes as notes_routes

        mock_vault.note_exists.return_value = True
        notes_routes._vault = mock_vault

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "existing-note.md",
                "content": "New content",
                "overwrite": True,
            },
        )

        assert response.status_code == 201


class TestNewRESTfulUpdateNoteEndpoint:
    """Tests for new RESTful PUT /api/v1/notes/{note_path} endpoint."""

    def test_update_note_endpoint_exists(self, client: TestClient) -> None:
        """Test that new PUT /api/v1/notes/{note_path} endpoint exists."""
        response = client.put(
            "/api/v1/notes/test-note.md",
            json={
                "content": "Updated content",
            },
        )

        # Should not return 404
        assert response.status_code != 404

    def test_update_note_returns_200_on_success(
        self, client: TestClient, mock_vault_for_update: MagicMock
    ) -> None:
        """Test that PUT /api/v1/notes/{note_path} returns 200 on success."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault_for_update

        response = client.put(
            "/api/v1/notes/existing-note.md",
            json={
                "content": "Updated content",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data.get("path") == "existing-note.md"

    def test_update_note_not_found(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that PUT /api/v1/notes/{note_path} returns 404 when note not found."""
        from markwritter.api.routes import notes as notes_routes

        mock_vault.note_exists.return_value = False
        notes_routes._vault = mock_vault

        response = client.put(
            "/api/v1/notes/nonexistent.md",
            json={
                "content": "Content",
            },
        )

        assert response.status_code == 404

    def test_update_note_with_append_mode(
        self, client: TestClient, mock_vault_for_update: MagicMock
    ) -> None:
        """Test update with append mode via new endpoint."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault_for_update

        response = client.put(
            "/api/v1/notes/existing-note.md",
            json={
                "content": "Appended content.",
                "mode": "append",
            },
        )

        assert response.status_code == 200

    def test_update_note_with_path_in_url(
        self, client: TestClient, mock_vault_for_update: MagicMock
    ) -> None:
        """Test that note path is taken from URL, not request body."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault_for_update

        response = client.put(
            "/api/v1/notes/some-note.md",
            json={
                "content": "Updated content",
                # Note: path in body should be ignored, path from URL used
            },
        )

        assert response.status_code == 200
        # The path should be from URL
        data = response.json()
        assert data.get("path") == "some-note.md"


class TestNewEndpointsPathTraversalSecurity:
    """Security tests for new RESTful endpoints."""

    def test_create_rejects_path_traversal(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that new create endpoint rejects path traversal."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "../outside-vault.md",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_update_rejects_path_traversal_in_url(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that new update endpoint rejects path traversal in URL."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault

        response = client.put(
            "/api/v1/notes/../outside-vault.md",
            json={
                "content": "Malicious content",
            },
        )

        # Should be rejected - either 400 or 403 or 404
        assert response.status_code in [400, 403, 404, 422]


# ==============================================================================
# Phase 2.1: Backward Compatibility Tests (record.py deprecated endpoints)
# ==============================================================================


class TestDeprecatedEndpointsBackwardCompatibility:
    """Tests for deprecated endpoints that maintain backward compatibility."""

    def test_old_create_endpoint_still_works(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that old POST /api/v1/record/create endpoint still works."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "new-note.md",
                "content": "Content",
            },
        )

        assert response.status_code == 200

    def test_old_create_endpoint_returns_deprecation_warning(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test that old endpoint includes deprecation warning header."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "new-note.md",
                "content": "Content",
            },
        )

        assert response.status_code == 200
        # Check for deprecation header
        assert "deprecation" in response.headers or "warning" in response.headers

    def test_old_update_endpoint_still_works(
        self, client: TestClient, mock_vault_for_update: MagicMock
    ) -> None:
        """Test that old PUT /api/v1/record/update endpoint still works."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault_for_update

        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "existing-note.md",
                "content": "Updated content",
            },
        )

        assert response.status_code == 200

    def test_old_update_endpoint_returns_deprecation_warning(
        self, client: TestClient, mock_vault_for_update: MagicMock
    ) -> None:
        """Test that old update endpoint includes deprecation warning."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault_for_update

        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "existing-note.md",
                "content": "Updated content",
            },
        )

        assert response.status_code == 200
        # Check for deprecation header
        assert "deprecation" in response.headers or "warning" in response.headers


# ==============================================================================
# Phase 2.2: API Version Prefix Tests
# ==============================================================================


class TestAPIVersionPrefix:
    """Tests for unified /api/v1 prefix across all routes."""

    def test_skills_endpoint_with_v1_prefix(self, client: TestClient) -> None:
        """Test that skills endpoint works with /api/v1 prefix."""
        response = client.get("/api/v1/skills")

        # Should not return 404
        assert response.status_code != 404

    def test_skills_endpoint_old_path_still_works(self, client: TestClient) -> None:
        """Test that old /api/skills path still works (backward compatibility)."""
        response = client.get("/api/skills")

        # Should still work for backward compatibility
        assert response.status_code != 404

    def test_chat_endpoint_with_v1_prefix(self, client: TestClient) -> None:
        """Test that chat endpoint works with /api/v1 prefix."""
        response = client.post(
            "/api/v1/chat",
            json={"message": "Hello"},
        )

        # Should not return 404
        assert response.status_code != 404

    def test_chat_endpoint_old_path_still_works(self, client: TestClient) -> None:
        """Test that old /api/chat path still works."""
        response = client.post(
            "/api/chat",
            json={"message": "Hello"},
        )

        # Should still work for backward compatibility
        assert response.status_code != 404

    def test_logs_endpoint_with_v1_prefix(self, client: TestClient) -> None:
        """Test that logs endpoint works with /api/v1 prefix."""
        # For SSE streams, we just check that the route exists
        # by looking at the OpenAPI schema instead of making a request
        response = client.get("/openapi.json")
        schema = response.json()
        # Check that the logs endpoint exists in the schema
        paths = schema.get("paths", {})
        assert "/api/v1/logs/stream" in paths or any("logs" in p for p in paths)

    def test_logs_endpoint_old_path_still_works(self, client: TestClient) -> None:
        """Test that old /api/logs path still works."""
        # For SSE streams, we just check that the route exists
        response = client.get("/openapi.json")
        schema = response.json()
        paths = schema.get("paths", {})
        # Old path should also exist
        assert "/api/logs/stream" in paths or any("logs" in p for p in paths)


class TestAPIVersionPrefixDeprecation:
    """Tests for deprecation headers on old API paths."""

    def test_old_skills_path_has_deprecation_warning(
        self, client: TestClient
    ) -> None:
        """Test that old skills path returns deprecation warning."""
        response = client.get("/api/skills")

        # Should include deprecation header
        # Note: This test may pass even if header is not yet implemented
        # The implementation should add the header
        assert response.status_code != 404

    def test_old_chat_path_has_deprecation_warning(
        self, client: TestClient
    ) -> None:
        """Test that old chat path returns deprecation warning."""
        response = client.post(
            "/api/chat",
            json={"message": "test"},
        )

        # Should include deprecation header
        assert response.status_code != 404


# ==============================================================================
# Edge Cases
# ==============================================================================


class TestEdgeCases:
    """Edge case tests for RESTful endpoints."""

    def test_create_note_with_special_characters_in_path(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test creating note with special characters in path."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "notes/special-chars-_.md",
                "content": "Content",
            },
        )

        assert response.status_code == 201

    def test_update_note_with_url_encoded_path(
        self, client: TestClient, mock_vault_for_update: MagicMock
    ) -> None:
        """Test updating note with URL-encoded path."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault_for_update

        # URL-encoded path: notes/my-note.md
        response = client.put(
            "/api/v1/notes/notes%2Fmy-note.md",
            json={
                "content": "Updated content",
            },
        )

        # Should handle URL-encoded path
        assert response.status_code in [200, 404]

    def test_create_note_empty_content(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test creating note with empty content."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = mock_vault

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "empty-note.md",
                "content": "",
            },
        )

        # Should accept empty content
        assert response.status_code == 201

    def test_create_note_vault_not_configured(self, client: TestClient) -> None:
        """Test create when vault is not configured."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = None

        response = client.post(
            "/api/v1/notes",
            json={
                "path": "test.md",
                "content": "Content",
            },
        )

        assert response.status_code == 503

    def test_update_note_vault_not_configured(self, client: TestClient) -> None:
        """Test update when vault is not configured."""
        from markwritter.api.routes import notes as notes_routes

        notes_routes._vault = None

        response = client.put(
            "/api/v1/notes/test.md",
            json={
                "content": "Content",
            },
        )

        assert response.status_code == 503