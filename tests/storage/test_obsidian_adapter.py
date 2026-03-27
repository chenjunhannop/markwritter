"""Tests for ObsidianRepository adapter.

TDD approach: These tests define the expected behavior before implementation.
This adapter wraps the existing ObsidianVault class to implement ContentRepository.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest

from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentType,
    ContentQuery,
    ContentRef,
    StorageBackend,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory with sample notes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Create sample notes
        (vault_path / "note1.md").write_text("""---
title: First Note
tags: [python, testing]
created: 2024-01-15
---

# First Note

This is the content of the first note.

It links to [[note2]] and [[projects/my-project|My Project]].
""")

        (vault_path / "note2.md").write_text("""---
title: Second Note
tags: [python, tutorial]
---

# Second Note

Content with a tag #python and #testing.

Backlink to [[note1]].
""")

        # Create subdirectory with notes
        projects_dir = vault_path / "projects"
        projects_dir.mkdir()

        (projects_dir / "my-project.md").write_text("""---
title: My Project
status: active
---

# My Project

Project description.

Links: [[note1]], [[note2]]
""")

        (projects_dir / "archive.md").write_text("""---
title: Archived Project
status: archived
---

# Archived Project

Old project.
""")

        yield vault_path


# ==============================================================================
# Initialization Tests
# ==============================================================================


class TestObsidianRepositoryInit:
    """Tests for ObsidianRepository initialization."""

    def test_init_with_vault_path(self, temp_vault: Path) -> None:
        """Test initialization with vault path."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        assert repo.backend_type == StorageBackend.OBSIDIAN
        assert ContentType.MARKDOWN in repo.supported_content_types

    def test_init_with_string_path(self, temp_vault: Path) -> None:
        """Test initialization with string path."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=str(temp_vault))

        assert repo.backend_type == StorageBackend.OBSIDIAN

    def test_init_invalid_path_raises_error(self) -> None:
        """Test that invalid path raises error."""
        from markwritter.storage.backends.obsidian import (
            ObsidianRepository,
        )
        from markwritter.storage.base import StorageError

        with pytest.raises(StorageError):
            ObsidianRepository(vault_path="/non/existent/path")

    def test_init_wraps_existing_vault(self, temp_vault: Path) -> None:
        """Test initialization with existing ObsidianVault instance."""
        from markwritter.obsidian.vault import ObsidianVault
        from markwritter.storage.backends.obsidian import ObsidianRepository

        vault = ObsidianVault(temp_vault)
        repo = ObsidianRepository(vault=vault)

        assert repo.backend_type == StorageBackend.OBSIDIAN

    def test_init_without_parameters_raises_error(self) -> None:
        """Test that initialization without parameters raises error."""
        from markwritter.storage.backends.obsidian import (
            ObsidianRepository,
        )
        from markwritter.storage.base import StorageError

        with pytest.raises(StorageError, match="Either vault_path or vault"):
            ObsidianRepository()


# ==============================================================================
# Get Tests
# ==============================================================================


class TestObsidianRepositoryGet:
    """Tests for ObsidianRepository.get method."""

    @pytest.mark.asyncio
    async def test_get_existing_content(self, temp_vault: Path) -> None:
        """Test getting existing content by ID."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        content = await repo.get("note1.md")

        assert content is not None
        assert content.id == "note1.md"
        assert content.title == "First Note"
        assert content.source_type == ContentType.MARKDOWN
        assert content.storage_backend == StorageBackend.OBSIDIAN
        assert "python" in content.tags

    @pytest.mark.asyncio
    async def test_get_nonexistent_content(self, temp_vault: Path) -> None:
        """Test getting non-existent content returns None."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        content = await repo.get("nonexistent.md")

        assert content is None

    @pytest.mark.asyncio
    async def test_get_content_in_subdirectory(self, temp_vault: Path) -> None:
        """Test getting content in subdirectory."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        content = await repo.get("projects/my-project.md")

        assert content is not None
        assert content.id == "projects/my-project.md"
        assert content.title == "My Project"

    @pytest.mark.asyncio
    async def test_get_content_with_links(self, temp_vault: Path) -> None:
        """Test that get returns content with extracted links."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        content = await repo.get("note1.md")

        assert content is not None
        assert "note2" in content.links
        assert "projects/my-project" in content.links

    @pytest.mark.asyncio
    async def test_get_content_with_backlinks(self, temp_vault: Path) -> None:
        """Test that get returns content with backlinks."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        content = await repo.get("note1.md")

        assert content is not None
        assert "note2.md" in content.backlinks


# ==============================================================================
# Get By Path Tests
# ==============================================================================


class TestObsidianRepositoryGetByPath:
    """Tests for ObsidianRepository.get_by_path method."""

    @pytest.mark.asyncio
    async def test_get_by_path_existing(self, temp_vault: Path) -> None:
        """Test getting content by path."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        content = await repo.get_by_path("note1.md")

        assert content is not None
        assert content.id == "note1.md"
        assert content.source_path == "note1.md"

    @pytest.mark.asyncio
    async def test_get_by_path_nonexistent(self, temp_vault: Path) -> None:
        """Test getting non-existent path returns None."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        content = await repo.get_by_path("nonexistent.md")

        assert content is None


# ==============================================================================
# List Tests
# ==============================================================================


class TestObsidianRepositoryList:
    """Tests for ObsidianRepository.list method."""

    @pytest.mark.asyncio
    async def test_list_all_content(self, temp_vault: Path) -> None:
        """Test listing all content."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        result = await repo.list(ContentQuery())

        assert result.total == 4
        assert len(result.items) == 4

    @pytest.mark.asyncio
    async def test_list_with_tag_filter(self, temp_vault: Path) -> None:
        """Test listing content with tag filter."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        result = await repo.list(ContentQuery(tags=["python"]))

        assert result.total >= 2
        for item in result.items:
            assert "python" in item.tags

    @pytest.mark.asyncio
    async def test_list_with_path_prefix(self, temp_vault: Path) -> None:
        """Test listing content with path prefix filter."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        result = await repo.list(ContentQuery(path_prefix="projects/"))

        assert result.total == 2
        for item in result.items:
            assert item.path is not None
            assert item.path.startswith("projects/")

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, temp_vault: Path) -> None:
        """Test listing content with pagination."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        # First page
        result1 = await repo.list(ContentQuery(limit=2, offset=0))
        assert len(result1.items) == 2
        assert result1.has_more is True

        # Second page
        result2 = await repo.list(ContentQuery(limit=2, offset=2))
        assert len(result2.items) == 2
        assert result2.has_more is False

    @pytest.mark.asyncio
    async def test_list_with_keyword_query(self, temp_vault: Path) -> None:
        """Test listing content with keyword search."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        result = await repo.list(ContentQuery(query="python"))

        assert result.total >= 2

    @pytest.mark.asyncio
    async def test_list_returns_refs(self, temp_vault: Path) -> None:
        """Test that list returns ContentRef objects."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)
        result = await repo.list(ContentQuery())

        for item in result.items:
            assert isinstance(item, ContentRef)
            assert item.source_type == ContentType.MARKDOWN
            assert item.storage_backend == StorageBackend.OBSIDIAN


# ==============================================================================
# Save Tests
# ==============================================================================


class TestObsidianRepositorySave:
    """Tests for ObsidianRepository.save method."""

    @pytest.mark.asyncio
    async def test_save_new_content(self, temp_vault: Path) -> None:
        """Test saving new content."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        content = Content(
            id="new-note.md",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content="# New Note\n\nCreated by test.",
            title="New Note",
            source_path="new-note.md",
            tags=["test"],
        )

        saved = await repo.save(content)

        assert saved.id == "new-note.md"
        assert saved.title == "New Note"

        # Verify it was actually saved
        retrieved = await repo.get("new-note.md")
        assert retrieved is not None
        assert "New Note" in retrieved.text_content

    @pytest.mark.asyncio
    async def test_save_update_existing_content(self, temp_vault: Path) -> None:
        """Test updating existing content."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        # Get existing
        content = await repo.get("note1.md")
        assert content is not None

        # Modify
        content.text_content = "# Updated\n\nNew content."

        # Save
        saved = await repo.save(content)

        assert saved.text_content == "# Updated\n\nNew content."

    @pytest.mark.asyncio
    async def test_save_creates_directories(self, temp_vault: Path) -> None:
        """Test that save creates parent directories."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        content = Content(
            id="new/deep/dir/note.md",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content="# Nested Note",
            source_path="new/deep/dir/note.md",
        )

        saved = await repo.save(content)
        assert saved.id == "new/deep/dir/note.md"

        # Verify it exists
        assert await repo.exists("new/deep/dir/note.md")


# ==============================================================================
# Delete Tests
# ==============================================================================


class TestObsidianRepositoryDelete:
    """Tests for ObsidianRepository.delete method."""

    @pytest.mark.asyncio
    async def test_delete_existing_content(self, temp_vault: Path) -> None:
        """Test deleting existing content."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        result = await repo.delete("note1.md")

        assert result is True
        assert await repo.exists("note1.md") is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent_content(self, temp_vault: Path) -> None:
        """Test deleting non-existent content returns False."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        result = await repo.delete("nonexistent.md")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_handles_exception(self, temp_vault: Path) -> None:
        """Test delete handles exceptions gracefully."""
        from unittest.mock import MagicMock, patch

        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        # Mock the vault to raise an exception during delete
        with patch.object(repo._vault, "delete_note", side_effect=Exception("Error")):
            result = await repo.delete("note1.md")

        assert result is False


# ==============================================================================
# Exists Tests
# ==============================================================================


class TestObsidianRepositoryExists:
    """Tests for ObsidianRepository.exists method."""

    @pytest.mark.asyncio
    async def test_exists_true(self, temp_vault: Path) -> None:
        """Test exists returns True for existing content."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        assert await repo.exists("note1.md") is True
        assert await repo.exists("projects/my-project.md") is True

    @pytest.mark.asyncio
    async def test_exists_false(self, temp_vault: Path) -> None:
        """Test exists returns False for non-existing content."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        assert await repo.exists("nonexistent.md") is False


# ==============================================================================
# Protocol Compliance Tests
# ==============================================================================


class TestObsidianRepositoryProtocolCompliance:
    """Tests that ObsidianRepository satisfies ContentRepository protocol."""

    def test_satisfies_protocol(self, temp_vault: Path) -> None:
        """Test that ObsidianRepository satisfies ContentRepository protocol."""
        from markwritter.storage.backends.obsidian import ObsidianRepository
        from markwritter.storage.base import ContentRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        # Should be able to use as ContentRepository
        assert isinstance(repo, ContentRepository)

        # Check properties
        assert repo.backend_type == StorageBackend.OBSIDIAN
        assert ContentType.MARKDOWN in repo.supported_content_types


# ==============================================================================
# Edge Cases
# ==============================================================================


class TestObsidianRepositoryEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_vault(self, tmp_path: Path) -> None:
        """Test operations on empty vault."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=tmp_path)

        result = await repo.list(ContentQuery())
        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_special_characters_in_content(self, temp_vault: Path) -> None:
        """Test handling special characters in content."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        content = Content(
            id="special.md",
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content="# Test\n\nUnicode: cafe, resume\n\nCode: `x = y`",
            source_path="special.md",
        )

        await repo.save(content)
        retrieved = await repo.get("special.md")

        assert retrieved is not None
        assert "cafe" in retrieved.text_content

    @pytest.mark.asyncio
    async def test_unsupported_content_type(self, temp_vault: Path) -> None:
        """Test that unsupported content types are handled."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        content = Content(
            id="test.pdf",
            source_type=ContentType.PDF,  # Not supported by Obsidian
            storage_backend=StorageBackend.OBSIDIAN,
        )

        # Should handle gracefully (either convert or raise appropriate error)
        # For now, we expect it to be saved as markdown
        saved = await repo.save(content)
        assert saved.id == "test.pdf"

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, temp_vault: Path) -> None:
        """Test sequential operations work correctly."""
        from markwritter.storage.backends.obsidian import ObsidianRepository

        repo = ObsidianRepository(vault_path=temp_vault)

        # Write multiple
        for i in range(3):
            content = Content(
                id=f"concurrent{i}.md",
                source_type=ContentType.MARKDOWN,
                storage_backend=StorageBackend.OBSIDIAN,
                text_content=f"Content {i}",
                source_path=f"concurrent{i}.md",
            )
            await repo.save(content)

        # Read all
        for i in range(3):
            retrieved = await repo.get(f"concurrent{i}.md")
            assert retrieved is not None
            assert f"Content {i}" in retrieved.text_content

        # Delete one
        await repo.delete("concurrent0.md")
        assert await repo.exists("concurrent0.md") is False
        assert await repo.exists("concurrent1.md") is True