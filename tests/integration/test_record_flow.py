"""
Integration tests for Record Flow.

Tests the complete record workflow:
1. Create notes with AI assistance
2. Save notes to vault
3. Auto-classification
4. Edit and update notes

These tests verify the full integration between components.
"""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from markwritter.api.app import create_app
from markwritter.obsidian.vault import ObsidianVault
from markwritter.record.assistant import (
    AutoClassifier,
    ClassifyResult,
    WritingAssistant,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Create existing notes for linking tests
        (vault_path / "existing-note.md").write_text("""---
title: Existing Note
tags: [reference]
---

# Existing Note

This note exists for testing links.
""")

        (vault_path / "python-reference.md").write_text("""---
title: Python Reference
tags: [python, reference]
---

# Python Reference

A reference note for Python programming.
""")

        yield vault_path


@pytest.fixture
def mock_writing_assistant() -> MagicMock:
    """Create a mock WritingAssistant."""
    assistant = MagicMock(spec=WritingAssistant)

    assistant.continue_writing = MagicMock(
        return_value="This is the continued text from AI."
    )
    assistant.rewrite = MagicMock(
        return_value="This is the rewritten text from AI."
    )
    assistant.polish = MagicMock(
        return_value="This is the polished text from AI."
    )

    async def mock_continue_stream(*args, **kwargs):
        yield "Continued "
        yield "text "
        yield "from "
        yield "AI."

    assistant.continue_writing_stream = mock_continue_stream

    return assistant


@pytest.fixture
def mock_auto_classifier() -> MagicMock:
    """Create a mock AutoClassifier."""
    classifier = MagicMock(spec=AutoClassifier)

    classifier.classify = MagicMock(
        return_value=ClassifyResult(
            category="programming",
            confidence=0.92,
            reasoning="Contains code and technical terms",
        )
    )

    classifier.suggest_tags = MagicMock(
        return_value=["python", "programming", "tutorial"]
    )

    classifier.suggest_folder = MagicMock(
        return_value="programming/python"
    )

    classifier.suggest_links = MagicMock(
        return_value=["python-reference.md", "existing-note.md"]
    )

    return classifier


@pytest.fixture
def client(
    temp_vault: Path,
    mock_writing_assistant: MagicMock,
    mock_auto_classifier: MagicMock,
) -> Generator[TestClient, None, None]:
    """Create a test client with configured dependencies."""
    app = create_app()

    # Set up vault
    from markwritter.api.routes import record as record_routes
    record_routes._vault = ObsidianVault(str(temp_vault))
    record_routes._writing_assistant = mock_writing_assistant
    record_routes._auto_classifier = mock_auto_classifier

    yield TestClient(app)


# ==============================================================================
# Create Flow Integration Tests
# ==============================================================================


class TestCreateFlowIntegration:
    """Integration tests for note creation flow."""

    def test_create_simple_note(self, client: TestClient, temp_vault: Path) -> None:
        """Test creating a simple note."""
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "simple-note.md",
                "content": "# Simple Note\n\nThis is a simple note.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "path" in data

        # Verify file was created
        note_path = temp_vault / "simple-note.md"
        assert note_path.exists()
        assert "Simple Note" in note_path.read_text()

    def test_create_note_with_frontmatter(
        self, client: TestClient, temp_vault: Path
    ) -> None:
        """Test creating a note with frontmatter."""
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "frontmatter-note.md",
                "content": "---\ntitle: Custom Title\ntags: [custom, test]\n---\n\n# Content",
                "auto_frontmatter": False,
            },
        )

        assert response.status_code == 200

        # Verify frontmatter was preserved
        note_path = temp_vault / "frontmatter-note.md"
        content = note_path.read_text()
        assert "title: Custom Title" in content
        assert "tags: [custom, test]" in content

    def test_create_note_with_auto_frontmatter(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test creating a note with auto-generated frontmatter."""
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "auto-note.md",
                "content": "# Python Tutorial\n\nLearn Python programming basics.",
                "auto_frontmatter": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_create_note_in_subfolder(
        self, client: TestClient, temp_vault: Path
    ) -> None:
        """Test creating a note in a subfolder."""
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "subfolder/nested/note.md",
                "content": "# Nested Note",
            },
        )

        assert response.status_code == 200

        # Verify folder structure was created
        note_path = temp_vault / "subfolder" / "nested" / "note.md"
        assert note_path.exists()

    def test_create_duplicate_note(self, client: TestClient) -> None:
        """Test creating a duplicate note."""
        # First create
        client.post(
            "/api/v1/record/create",
            json={
                "path": "duplicate.md",
                "content": "# Original",
            },
        )

        # Try to create again
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "duplicate.md",
                "content": "# Duplicate",
            },
        )

        # Should handle gracefully (either overwrite or error)
        assert response.status_code in [200, 409]


class TestAIAssistanceIntegration:
    """Integration tests for AI assistance in record flow."""

    @pytest.mark.skip(reason="AI continue endpoint not implemented yet")
    def test_continue_writing(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test AI continue writing feature."""
        response = client.post(
            "/api/v1/record/ai/continue",
            json={
                "content": "# Python Basics\n\nPython is a programming language.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "continuation" in data
        assert len(data["continuation"]) > 0

    @pytest.mark.skip(reason="AI streaming endpoint not implemented yet")
    def test_continue_writing_streaming(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test AI continue writing with streaming."""
        response = client.post(
            "/api/v1/record/ai/continue/stream",
            json={
                "content": "# Starting point",
            },
            headers={"Accept": "text/event-stream"},
        )

        assert response.status_code == 200

    @pytest.mark.skip(reason="AI rewrite endpoint not implemented yet")
    def test_rewrite_content(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test AI rewrite feature."""
        response = client.post(
            "/api/v1/record/ai/rewrite",
            json={
                "content": "This is some content to rewrite.",
                "instructions": "Make it more formal",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "rewritten" in data

    @pytest.mark.skip(reason="AI polish endpoint not implemented yet")
    def test_polish_content(
        self, client: TestClient, mock_writing_assistant: MagicMock
    ) -> None:
        """Test AI polish feature."""
        response = client.post(
            "/api/v1/record/ai/polish",
            json={
                "content": "rough draft content with errors.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "polished" in data


class TestAutoClassificationIntegration:
    """Integration tests for auto-classification."""

    def test_classify_content(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test content classification."""
        response = client.post(
            "/api/v1/record/classify",
            json={
                "content": "def hello():\n    print('Hello, World!')",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "category" in data
        assert "confidence" in data

    @pytest.mark.skip(reason="Tag suggestions endpoint not implemented yet")
    def test_suggest_tags(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test tag suggestions."""
        response = client.post(
            "/api/v1/record/suggest-tags",
            json={
                "content": "A comprehensive guide to Python testing with pytest.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert isinstance(data["tags"], list)

    @pytest.mark.skip(reason="Folder suggestions endpoint not implemented yet")
    def test_suggest_folder(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test folder suggestions."""
        response = client.post(
            "/api/v1/record/suggest-folder",
            json={
                "content": "# API Design\n\nHow to design REST APIs.",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "folder" in data

    @pytest.mark.skip(reason="Link suggestions endpoint not implemented yet")
    def test_suggest_links(
        self, client: TestClient, mock_auto_classifier: MagicMock
    ) -> None:
        """Test link suggestions."""
        response = client.post(
            "/api/v1/record/suggest-links",
            json={
                "content": "Learn Python programming basics.",
                "vault_path": "",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "links" in data
        assert isinstance(data["links"], list)


class TestEditFlowIntegration:
    """Integration tests for note editing flow."""

    @pytest.mark.skip(reason="Read note endpoint not implemented yet")
    def test_read_note(self, client: TestClient, temp_vault: Path) -> None:
        """Test reading an existing note."""
        response = client.get(
            "/api/v1/record/read",
            params={"path": "existing-note.md"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "Existing Note" in data["content"]

    def test_update_note(self, client: TestClient, temp_vault: Path) -> None:
        """Test updating an existing note."""
        # First create a note
        client.post(
            "/api/v1/record/create",
            json={
                "path": "update-test.md",
                "content": "# Original Content",
            },
        )

        # Then update it
        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "update-test.md",
                "content": "# Updated Content\n\nThis has been updated.",
            },
        )

        assert response.status_code == 200

        # Verify update
        note_path = temp_vault / "update-test.md"
        assert "Updated Content" in note_path.read_text()

    @pytest.mark.skip(reason="Delete note endpoint not implemented yet")
    def test_delete_note(self, client: TestClient, temp_vault: Path) -> None:
        """Test deleting a note."""
        # First create a note
        client.post(
            "/api/v1/record/create",
            json={
                "path": "delete-test.md",
                "content": "# To be deleted",
            },
        )

        # Verify it exists
        assert (temp_vault / "delete-test.md").exists()

        # Delete it
        response = client.delete(
            "/api/v1/record/delete",
            params={"path": "delete-test.md"},
        )

        assert response.status_code == 200

        # Verify it's gone
        assert not (temp_vault / "delete-test.md").exists()

    @pytest.mark.skip(reason="List notes endpoint not implemented yet")
    def test_list_notes(self, client: TestClient) -> None:
        """Test listing notes in vault."""
        response = client.get("/api/v1/record/list")

        assert response.status_code == 200
        data = response.json()
        assert "notes" in data
        assert isinstance(data["notes"], list)


class TestRecordErrorHandling:
    """Test error handling in record flow."""

    def test_read_nonexistent_note(self, client: TestClient) -> None:
        """Test reading a note that doesn't exist."""
        response = client.get(
            "/api/v1/record/read",
            params={"path": "nonexistent.md"},
        )

        assert response.status_code == 404

    def test_delete_nonexistent_note(self, client: TestClient) -> None:
        """Test deleting a note that doesn't exist."""
        response = client.delete(
            "/api/v1/record/delete",
            params={"path": "nonexistent.md"},
        )

        assert response.status_code == 404

    def test_create_with_invalid_path(self, client: TestClient) -> None:
        """Test creating a note with invalid path."""
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "../../../etc/passwd",
                "content": "Malicious content",
            },
        )

        # Should reject path traversal attempts
        assert response.status_code in [400, 403, 422]

    def test_update_nonexistent_note(self, client: TestClient) -> None:
        """Test updating a note that doesn't exist."""
        response = client.put(
            "/api/v1/record/update",
            json={
                "path": "nonexistent.md",
                "content": "New content",
            },
        )

        assert response.status_code == 404


class TestRecordMetadata:
    """Test metadata handling in record flow."""

    def test_create_with_metadata(self, client: TestClient, temp_vault: Path) -> None:
        """Test creating a note with metadata."""
        response = client.post(
            "/api/v1/record/create",
            json={
                "path": "metadata-note.md",
                "content": "# Note with Metadata",
                "metadata": {
                    "author": "Test Author",
                    "created_at": "2024-01-01",
                },
            },
        )

        assert response.status_code == 200

    @pytest.mark.skip(reason="Note info endpoint not implemented yet")
    def test_get_note_info(self, client: TestClient) -> None:
        """Test getting note information."""
        response = client.get(
            "/api/v1/record/info",
            params={"path": "existing-note.md"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "path" in data
        assert "size" in data or "modified" in data