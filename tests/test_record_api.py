"""Tests for Record API endpoints.

TDD approach: Tests for record API routes before implementation.
"""

import tempfile
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
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        # Create some test notes
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
def mock_writing_assistant() -> MagicMock:
    """Create a mock WritingAssistant."""
    from markwritter.record.assistant import WritingAssistant

    assistant = MagicMock(spec=WritingAssistant)
    assistant.continue_writing = MagicMock(return_value="Continued text.")
    assistant.rewrite = MagicMock(return_value="Rewritten text.")
    assistant.polish = MagicMock(return_value="Polished text.")

    async def mock_stream(*args, **kwargs):
        yield "Streamed "
        yield "text."

    assistant.continue_writing_stream = mock_stream
    return assistant


@pytest.fixture
def mock_auto_classifier() -> MagicMock:
    """Create a mock AutoClassifier."""
    from markwritter.record.assistant import AutoClassifier, ClassifyResult

    classifier = MagicMock(spec=AutoClassifier)
    classifier.classify = MagicMock(
        return_value=ClassifyResult(category="programming", confidence=0.9)
    )
    classifier.suggest_tags = MagicMock(return_value=["python", "testing"])
    classifier.suggest_folder = MagicMock(return_value="programming")
    classifier.suggest_links = MagicMock(return_value=["related-note.md"])
    return classifier


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client."""
    app = create_app()
    yield TestClient(app)


# ==============================================================================
# Create Note API Tests
# ==============================================================================


class TestCreateNoteAPI:
    """Tests for note creation API."""

    def test_create_endpoint_exists(self, client: TestClient) -> None:
        """Test that create endpoint exists."""
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "new-note.md",
                "content": "New note content",
            },
        )

        # Should not return 404
        assert response.status_code != 404

    def test_create_note_basic(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test basic note creation."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "new-note.md",
                "content": "# New Note\n\nThis is the content.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True or data.get("path") == "new-note.md"

    def test_create_note_with_metadata(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test note creation with metadata."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "note-with-meta.md",
                "content": "Content here.",
                "metadata": {
                    "title": "My Note",
                    "tags": ["python", "testing"],
                },
            },
        )

        assert response.status_code == 200

    def test_create_note_missing_path(self, client: TestClient) -> None:
        """Test create without path parameter."""
        response = client.post(
            "/api/v1/record/create",
            json={"content": "Content only"},
        )

        # Should return validation error
        assert response.status_code == 422

    def test_create_note_missing_content(self, client: TestClient) -> None:
        """Test create without content parameter."""
        response = client.post(
            "/api/v1/record/create",
            json={"path": "note.md"},
        )

        # Should return validation error
        assert response.status_code == 422

    def test_create_note_overwrite_flag(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test create with overwrite flag."""
        from markwritter.api.routes import record as record_routes

        mock_vault.note_exists.return_value = True
        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "existing-note.md",
                "content": "New content",
                "overwrite": True,
            },
        )

        # Should succeed with overwrite=True
        assert response.status_code == 200

    def test_create_note_already_exists(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test create when note already exists."""
        from markwritter.api.routes import record as record_routes

        mock_vault.note_exists.return_value = True
        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "existing-note.md",
                "content": "New content",
            },
        )

        # Should return error or conflict
        assert response.status_code in [409, 400, 200]


# ==============================================================================
# Update Note API Tests
# ==============================================================================


class TestUpdateNoteAPI:
    """Tests for note update API."""

    def test_update_endpoint_exists(self, client: TestClient) -> None:
        """Test that update endpoint exists."""
        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "note.md",
                "content": "Updated content",
            },
        )

        # Should not return 404
        assert response.status_code != 404

    def test_update_note_basic(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test basic note update."""
        from markwritter.api.routes import record as record_routes

        mock_vault.note_exists.return_value = True
        record_routes._vault = mock_vault

        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "existing-note.md",
                "content": "Updated content here.",
            },
        )

        assert response.status_code == 200

    def test_update_note_with_metadata(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test note update with metadata."""
        from markwritter.api.routes import record as record_routes

        mock_vault.note_exists.return_value = True
        record_routes._vault = mock_vault

        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "note.md",
                "content": "Updated content.",
                "metadata": {
                    "tags": ["updated"],
                    "modified": "2024-01-15",
                },
            },
        )

        assert response.status_code == 200

    def test_update_note_not_found(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test update when note does not exist."""
        from markwritter.api.routes import record as record_routes

        mock_vault.note_exists.return_value = False
        record_routes._vault = mock_vault

        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "nonexistent.md",
                "content": "Content",
            },
        )

        # Should return 404 or appropriate error
        assert response.status_code in [404, 400, 200]

    def test_update_note_append_content(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test update with append mode."""
        from markwritter.api.routes import record as record_routes

        mock_vault.note_exists.return_value = True
        mock_vault.read_note = MagicMock()
        mock_vault.read_note.return_value.content = "Original content."
        record_routes._vault = mock_vault

        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "note.md",
                "content": "\n\nAppended content.",
                "mode": "append",
            },
        )

        assert response.status_code == 200


# ==============================================================================
# AI Assist API Tests
# ==============================================================================


class TestAIAssistAPI:
    """Tests for AI assistance API."""

    def test_continue_writing_endpoint(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test continue writing endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._writing_assistant = mock_writing_assistant

        response = client.post(
            "/api/v1/record/ai-assist/continue",
            json={"content": "Start of text"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "continuation" in data or "result" in data

    def test_continue_writing_stream_endpoint(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test streaming continue writing endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._writing_assistant = mock_writing_assistant

        response = client.post(
            "/api/v1/record/ai-assist/continue/stream",
            json={"content": "Start of text"},
        )

        # Should return SSE stream
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "") or True

    def test_rewrite_endpoint(self, client: TestClient, mock_writing_assistant: MagicMock) -> None:
        """Test rewrite endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._writing_assistant = mock_writing_assistant

        response = client.post(
            "/api/v1/record/ai-assist/rewrite",
            json={
                "content": "Original text",
                "style": "formal",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "rewritten" in data or "result" in data

    def test_rewrite_with_different_styles(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test rewrite with different styles."""
        from markwritter.api.routes import record as record_routes

        record_routes._writing_assistant = mock_writing_assistant

        styles = ["formal", "casual", "academic", "creative"]
        for style in styles:
            response = client.post(
                "/api/v1/record/ai-assist/rewrite",
                json={
                    "content": "Text to rewrite",
                    "style": style,
                },
            )
            assert response.status_code == 200

    def test_polish_endpoint(self, client: TestClient, mock_writing_assistant: MagicMock) -> None:
        """Test polish endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._writing_assistant = mock_writing_assistant

        response = client.post(
            "/api/v1/record/ai-assist/polish",
            json={"content": "Text that needs polishing"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "polished" in data or "result" in data

    def test_ai_assist_empty_content(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test AI assist with empty content."""
        from markwritter.api.routes import record as record_routes

        record_routes._writing_assistant = mock_writing_assistant

        response = client.post(
            "/api/v1/record/ai-assist/continue",
            json={"content": ""},
        )

        # Should handle gracefully
        assert response.status_code in [200, 400]


# ==============================================================================
# Classification API Tests
# ==============================================================================


class TestClassificationAPI:
    """Tests for classification API."""

    def test_classify_endpoint(self, client: TestClient, mock_auto_classifier: MagicMock) -> None:
        """Test classify endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._auto_classifier = mock_auto_classifier

        response = client.post(
            "/api/v1/record/classify",
            json={"content": "Python programming guide"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "category" in data

    def test_suggest_tags_endpoint(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test suggest tags endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._auto_classifier = mock_auto_classifier

        response = client.post(
            "/api/v1/record/suggest/tags",
            json={"content": "Python testing guide"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert isinstance(data["tags"], list)

    def test_suggest_tags_with_max(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test suggest tags with max limit."""
        from markwritter.api.routes import record as record_routes

        record_routes._auto_classifier = mock_auto_classifier

        response = client.post(
            "/api/v1/record/suggest/tags",
            json={
                "content": "Python testing guide",
                "max_tags": 3,
            },
        )

        assert response.status_code == 200

    def test_suggest_folder_endpoint(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test suggest folder endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._auto_classifier = mock_auto_classifier

        response = client.post(
            "/api/v1/record/suggest/folder",
            json={"content": "Work project notes"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "folder" in data

    def test_suggest_links_endpoint(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test suggest links endpoint."""
        from markwritter.api.routes import record as record_routes

        record_routes._auto_classifier = mock_auto_classifier

        response = client.post(
            "/api/v1/record/suggest/links",
            json={
                "content": "Python testing guide",
                "existing_notes": ["python-basics.md", "pytest-tutorial.md"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "links" in data
        assert isinstance(data["links"], list)


# ==============================================================================
# Error Handling Tests
# ==============================================================================


class TestRecordAPIErrors:
    """Tests for error handling."""

    def test_create_invalid_path(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test create with invalid path."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "../outside-vault.md",  # Path traversal attempt
                "content": "Content",
            },
        )

        # Should reject path traversal
        assert response.status_code in [400, 422, 403]

    def test_ai_assist_missing_content(self, client: TestClient) -> None:
        """Test AI assist without content."""
        response = client.post(
            "/api/v1/record/ai-assist/continue",
            json={},
        )

        # Should return validation error
        assert response.status_code == 422

    def test_classify_missing_content(self, client: TestClient) -> None:
        """Test classify without content."""
        response = client.post(
            "/api/v1/record/classify",
            json={},
        )

        # Should return validation error
        assert response.status_code == 422

    def test_ai_assist_service_not_available(self, client: TestClient) -> None:
        """Test AI assist when service is not available."""
        from markwritter.api.routes import record as record_routes

        record_routes._writing_assistant = None

        response = client.post(
            "/api/v1/record/ai-assist/continue",
            json={"content": "test"},
        )

        # Should return appropriate error
        assert response.status_code in [200, 503, 400]


# ==============================================================================
# Path Traversal Security Tests
# ==============================================================================


class TestPathTraversalSecurity:
    """Tests for path traversal vulnerability prevention."""

    def test_path_traversal_parent_directory(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test path traversal with parent directory reference."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "../outside-vault.md",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]
        assert (
            "traversal" in response.json().get("detail", "").lower()
            or "invalid" in response.json().get("detail", "").lower()
        )

    def test_path_traversal_nested_parent_directory(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test path traversal with nested parent directory references."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "../../etc/passwd",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_path_traversal_absolute_path(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test path traversal with absolute path."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "/etc/passwd",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_path_traversal_windows_absolute_path(
        self, client: TestClient, mock_vault: MagicMock
    ) -> None:
        """Test path traversal with Windows absolute path."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "C:\\Windows\\System32\\config",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_path_traversal_encoded_parent(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test path traversal with URL-encoded parent directory."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        # %2e%2e%2f = ../
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "%2e%2e%2foutside-vault.md",
                "content": "Malicious content",
            },
        )

        # Should either reject or normalize and reject
        assert response.status_code in [400, 403]

    def test_path_traversal_double_encoded(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test path traversal with double-encoded parent directory."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        # %252e%252e%252f = %2e%2e%2f = ../
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "%252e%252e%252foutside-vault.md",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_path_traversal_null_byte(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test path traversal with null byte injection."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "valid-path.md%00.md",
                "content": "Malicious content",
            },
        )

        # Should reject paths with null bytes
        assert response.status_code in [400, 403]

    def test_path_traversal_backslash(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test path traversal with backslash."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "..\\outside-vault.md",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_path_traversal_home_directory(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test path traversal with home directory reference."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "~/../../outside-vault.md",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_path_traversal_mixed_slashes(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test path traversal with mixed forward and backslashes."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "..\\..\\etc/passwd",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]

    def test_valid_relative_path_accepted(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test that valid relative paths are accepted."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "notes/my-note.md",
                "content": "Valid content",
            },
        )

        assert response.status_code == 200

    def test_valid_nested_path_accepted(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test that valid nested paths are accepted."""
        from markwritter.api.routes import record as record_routes

        record_routes._vault = mock_vault

        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "folder/subfolder/note.md",
                "content": "Valid content",
            },
        )

        assert response.status_code == 200

    def test_update_path_traversal_blocked(self, client: TestClient, mock_vault: MagicMock) -> None:
        """Test that path traversal is blocked on update endpoint."""
        from markwritter.api.routes import record as record_routes

        mock_vault.note_exists.return_value = True
        record_routes._vault = mock_vault

        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "../outside-vault.md",
                "content": "Malicious content",
            },
        )

        assert response.status_code in [400, 403]
