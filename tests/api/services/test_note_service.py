"""Tests for NoteService.

TDD approach: Tests written before implementation.
"""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from markwritter.obsidian.models import Note
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
def vault(temp_vault: Path) -> ObsidianVault:
    """Create an ObsidianVault instance."""
    return ObsidianVault(temp_vault)


# ==============================================================================
# NoteService Tests
# ==============================================================================


class TestNoteServiceExists:
    """Test that NoteService can be imported."""

    def test_import_note_service(self) -> None:
        """Test that NoteService can be imported."""
        from markwritter.api.services.note_service import NoteService

        assert NoteService is not None


class TestNoteServiceInit:
    """Test NoteService initialization."""

    def test_init_with_vault(self, vault: ObsidianVault) -> None:
        """Test initialization with vault."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)
        assert service.vault == vault

    def test_init_without_vault_raises_error(self) -> None:
        """Test initialization without vault raises error."""
        from markwritter.api.services.note_service import NoteService

        with pytest.raises(ValueError, match="vault"):
            NoteService(vault=None)


class TestNoteServiceCreateNote:
    """Test note creation through NoteService."""

    def test_create_note_basic(self, vault: ObsidianVault) -> None:
        """Test basic note creation."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.create_note(
            path="new-note.md",
            content="# New Note\n\nThis is content.",
        )

        assert result.success is True
        assert result.path == "new-note.md"
        assert vault.note_exists("new-note.md")

    def test_create_note_with_metadata(self, vault: ObsidianVault) -> None:
        """Test note creation with metadata."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.create_note(
            path="meta-note.md",
            content="Content here.",
            metadata={"title": "My Note", "tags": ["python", "testing"]},
        )

        assert result.success is True

        # Read back and verify metadata
        note = vault.read_note("meta-note.md")
        assert note.metadata.get("title") == "My Note"
        assert "python" in note.metadata.get("tags", [])

    def test_create_note_already_exists(self, vault: ObsidianVault) -> None:
        """Test creating note that already exists."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.create_note(
            path="existing-note.md",
            content="New content",
            overwrite=False,
        )

        assert result.success is False
        assert "already exists" in result.message.lower() or "conflict" in result.message.lower()

    def test_create_note_overwrite(self, vault: ObsidianVault) -> None:
        """Test creating note with overwrite."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.create_note(
            path="existing-note.md",
            content="New content",
            overwrite=True,
        )

        assert result.success is True

    def test_create_note_invalid_path(self, vault: ObsidianVault) -> None:
        """Test creating note with invalid path (path traversal)."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.create_note(
            path="../outside-vault.md",
            content="Malicious content",
        )

        assert result.success is False
        assert "invalid" in result.message.lower() or "traversal" in result.message.lower()


class TestNoteServiceUpdateNote:
    """Test note update through NoteService."""

    def test_update_note_basic(self, vault: ObsidianVault) -> None:
        """Test basic note update."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.update_note(
            path="existing-note.md",
            content="Updated content.",
        )

        assert result.success is True

        note = vault.read_note("existing-note.md")
        assert note.content == "Updated content."

    def test_update_note_append(self, vault: ObsidianVault) -> None:
        """Test note update with append mode."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.update_note(
            path="existing-note.md",
            content="Appended content.",
            mode="append",
        )

        assert result.success is True

        note = vault.read_note("existing-note.md")
        assert "Appended content." in note.content

    def test_update_note_prepend(self, vault: ObsidianVault) -> None:
        """Test note update with prepend mode."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.update_note(
            path="existing-note.md",
            content="Prepended content.",
            mode="prepend",
        )

        assert result.success is True

        note = vault.read_note("existing-note.md")
        assert note.content.startswith("Prepended content.")

    def test_update_note_not_found(self, vault: ObsidianVault) -> None:
        """Test updating non-existent note."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.update_note(
            path="nonexistent.md",
            content="Content",
        )

        assert result.success is False
        assert "not found" in result.message.lower()


class TestNoteServiceDeleteNote:
    """Test note deletion through NoteService."""

    def test_delete_note(self, vault: ObsidianVault) -> None:
        """Test note deletion."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.delete_note("existing-note.md")

        assert result.success is True
        assert not vault.note_exists("existing-note.md")

    def test_delete_note_not_found(self, vault: ObsidianVault) -> None:
        """Test deleting non-existent note."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        result = service.delete_note("nonexistent.md")

        assert result.success is False


class TestNoteServiceReadNote:
    """Test note reading through NoteService."""

    def test_read_note(self, vault: ObsidianVault) -> None:
        """Test reading a note."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        note = service.read_note("existing-note.md")

        assert note is not None
        assert "Existing content" in note.content

    def test_read_note_not_found(self, vault: ObsidianVault) -> None:
        """Test reading non-existent note."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        note = service.read_note("nonexistent.md")

        assert note is None

    def test_read_note_invalid_path(self, vault: ObsidianVault) -> None:
        """Test reading note with invalid path."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        note = service.read_note("../outside-vault.md")

        assert note is None


class TestNoteServiceValidation:
    """Test path validation in NoteService."""

    def test_path_traversal_blocked(self, vault: ObsidianVault) -> None:
        """Test that path traversal is blocked."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        invalid_paths = [
            "../outside.md",
            "../../etc/passwd",
            "~/../../outside.md",
            "/etc/passwd",
            "C:\\Windows\\System32",
            "..\\outside.md",
        ]

        for path in invalid_paths:
            assert not service.is_valid_path(path), f"Path {path} should be invalid"

    def test_valid_paths_accepted(self, vault: ObsidianVault) -> None:
        """Test that valid paths are accepted."""
        from markwritter.api.services.note_service import NoteService

        service = NoteService(vault=vault)

        valid_paths = [
            "note.md",
            "folder/note.md",
            "folder/subfolder/note.md",
            "my-note-2024.md",
        ]

        for path in valid_paths:
            assert service.is_valid_path(path), f"Path {path} should be valid"