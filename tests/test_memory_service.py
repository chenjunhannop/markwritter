"""Tests for Memory service integration.

TDD approach: These tests define the expected behavior before implementation.
"""

import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from markwritter.memory.config import MemoryConfig
from markwritter.memory.service import NoteMemoryService
from markwritter.obsidian.vault import ObsidianVault


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory with sample notes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Create sample notes
        (vault_path / "note1.md").write_text(
            """---
title: Python Testing Guide
tags: [python, testing, tdd]
created: 2024-01-15
---

# Python Testing Guide

This guide covers TDD practices in Python.

## Unit Tests

Write unit tests first, then implement.

## pytest

Use pytest for testing.
"""
        )

        (vault_path / "note2.md").write_text(
            """---
title: FastAPI Tutorial
tags: [python, fastapi, web]
---

# FastAPI Tutorial

Learn to build APIs with FastAPI.

FastAPI is a modern web framework.
"""
        )

        # Create subdirectory with notes
        projects_dir = vault_path / "projects"
        projects_dir.mkdir()

        (projects_dir / "my-project.md").write_text(
            """---
title: My Project
status: active
tags: [project]
---

# My Project

Project description and notes.

Links to [[note1]] for testing info.
"""
        )

        (projects_dir / "daily-2024-01-20.md").write_text(
            """---
title: Daily Note 2024-01-20
tags: [daily]
---

# Daily Note

Today I worked on testing.
"""
        )

        yield vault_path


@pytest.fixture
def memory_config(temp_vault: Path) -> MemoryConfig:
    """Create a MemoryConfig instance."""
    return MemoryConfig(
        vault_path=temp_vault,
        llm_base_url="http://localhost:11434/v1",
        embed_model="nomic-embed-text",
        chat_model="llama3",
    )


@pytest.fixture
def vault(temp_vault: Path) -> ObsidianVault:
    """Create an ObsidianVault instance."""
    return ObsidianVault(temp_vault)


@pytest.fixture
def mock_memory_service() -> MagicMock:
    """Create a mock memU MemoryService."""
    service = MagicMock()
    service.memorize = AsyncMock(return_value={"id": "test-id"})
    service.retrieve = AsyncMock(return_value={
        "items": [
            {
                "id": "item-1",
                "content": "Python testing guide",
                "score": 0.95,
                "user": {"note_path": "note1.md"},
            }
        ]
    })
    service.create_memory_item = AsyncMock(return_value={
        "memory_item": {"id": "new-item-id"},
        "category_updates": [],
    })
    service.list_memory_items = AsyncMock(return_value={"items": []})
    service.clear_memory = AsyncMock(return_value={"deleted_items": {}})
    return service


# ==============================================================================
# MemoryConfig Tests
# ==============================================================================


class TestMemoryConfig:
    """Tests for MemoryConfig."""

    def test_config_creation(self, temp_vault: Path) -> None:
        """Test creating a MemoryConfig instance."""
        config = MemoryConfig(vault_path=temp_vault)

        assert config.vault_path == temp_vault
        assert config.llm_base_url == "http://localhost:11434/v1"
        assert config.embed_model == "nomic-embed-text"
        assert config.chat_model == "llama3"

    def test_config_default_db_path(self, temp_vault: Path) -> None:
        """Test that db_path defaults to vault_path/.memory/memory.db."""
        config = MemoryConfig(vault_path=temp_vault)

        assert config.db_path == temp_vault / ".memory" / "memory.db"

    def test_config_custom_db_path(self, temp_vault: Path, tmp_path: Path) -> None:
        """Test custom db_path."""
        custom_db = tmp_path / "custom" / "memory.db"
        config = MemoryConfig(vault_path=temp_vault, db_path=custom_db)

        assert config.db_path == custom_db

    def test_config_default_categories(self, temp_vault: Path) -> None:
        """Test default memory categories."""
        config = MemoryConfig(vault_path=temp_vault)

        assert "concepts" in config.memory_categories
        assert "projects" in config.memory_categories
        assert "people" in config.memory_categories

    def test_config_custom_categories(self, temp_vault: Path) -> None:
        """Test custom memory categories."""
        config = MemoryConfig(
            vault_path=temp_vault,
            memory_categories=["work", "personal", "ideas"],
        )

        assert config.memory_categories == ["work", "personal", "ideas"]

    def test_config_path_serialization(self, temp_vault: Path) -> None:
        """Test that Path objects are handled correctly."""
        config = MemoryConfig(vault_path=temp_vault)

        # Verify path is preserved
        assert isinstance(config.vault_path, Path)
        assert config.vault_path.exists()


# ==============================================================================
# NoteMemoryService Initialization Tests
# ==============================================================================


class TestNoteMemoryServiceInit:
    """Tests for NoteMemoryService initialization."""

    def test_init_with_config(self, memory_config: MemoryConfig) -> None:
        """Test initialization with MemoryConfig."""
        service = NoteMemoryService(memory_config)

        assert service.config == memory_config
        assert service.vault is not None
        assert service.is_initialized is False

    def test_init_with_vault(
        self, memory_config: MemoryConfig, vault: ObsidianVault
    ) -> None:
        """Test initialization with provided vault."""
        service = NoteMemoryService(memory_config, vault=vault)

        assert service.vault == vault

    def test_init_with_memory_service(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test initialization with provided memory service."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        assert service.is_initialized is False


# ==============================================================================
# NoteMemoryService Index Tests
# ==============================================================================


class TestNoteMemoryServiceIndex:
    """Tests for note indexing."""

    @pytest.mark.asyncio
    async def test_initialize_creates_service(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test that initialize sets up the memory service."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        assert service.is_initialized is False
        await service.initialize()
        assert service.is_initialized is True

    @pytest.mark.asyncio
    async def test_index_vault(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test indexing all notes in vault."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        result = await service.index_vault()

        assert "indexed" in result
        assert "skipped" in result
        assert "errors" in result
        assert result["indexed"] >= 1

    @pytest.mark.asyncio
    async def test_index_vault_calls_create_memory_item(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test that index_vault calls create_memory_item for each note."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        await service.index_vault()

        # Should be called for each note
        assert mock_memory_service.create_memory_item.call_count >= 1

    @pytest.mark.asyncio
    async def test_index_vault_with_overwrite(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test indexing with overwrite clears existing index."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        result = await service.index_vault(overwrite=True)

        # clear_memory should be called when overwrite is True
        mock_memory_service.clear_memory.assert_called_once()
        assert "indexed" in result

    @pytest.mark.asyncio
    async def test_index_note(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test indexing a single note."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        result = await service.index_note("note1.md")

        assert result["indexed"] == 1
        assert result["note_path"] == "note1.md"
        assert "category" in result

    @pytest.mark.asyncio
    async def test_index_note_nonexistent(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test indexing a non-existent note raises error."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        from markwritter.obsidian.vault import NoteNotFoundError

        with pytest.raises(NoteNotFoundError):
            await service.index_note("nonexistent.md")


# ==============================================================================
# NoteMemoryService Search Tests
# ==============================================================================


class TestNoteMemoryServiceSearch:
    """Tests for semantic search."""

    @pytest.mark.asyncio
    async def test_search_returns_results(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test that search returns formatted results."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        results = await service.search("python testing")

        assert isinstance(results, list)
        assert len(results) >= 1
        assert "note_path" in results[0]
        assert "title" in results[0]
        assert "score" in results[0]

    @pytest.mark.asyncio
    async def test_search_calls_retrieve(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test that search calls retrieve on memory service."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        await service.search("python testing", top_k=10)

        mock_memory_service.retrieve.assert_called_once()
        call_args = mock_memory_service.retrieve.call_args
        assert call_args[0][0] == "python testing"
        assert call_args[1]["top_k"] == 10

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test search with no results."""
        mock_memory_service.retrieve = AsyncMock(return_value={"items": []})

        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        results = await service.search("nonexistent query")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_top_k_parameter(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test that top_k is passed to retrieve."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        await service.search("test", top_k=20)

        call_kwargs = mock_memory_service.retrieve.call_args[1]
        assert call_kwargs["top_k"] == 20


# ==============================================================================
# NoteMemoryService Ask Tests
# ==============================================================================


class TestNoteMemoryServiceAsk:
    """Tests for Q&A functionality."""

    @pytest.mark.asyncio
    async def test_ask_returns_answer(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test that ask returns an answer."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        result = await service.ask("What is Python testing?")

        assert "answer" in result
        assert "sources" in result

    @pytest.mark.asyncio
    async def test_ask_includes_sources(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test that ask includes source notes."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        result = await service.ask("What is Python testing?")

        assert isinstance(result["sources"], list)

    @pytest.mark.asyncio
    async def test_ask_no_results(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test ask when no relevant notes found."""
        mock_memory_service.retrieve = AsyncMock(return_value={"items": []})

        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        result = await service.ask("What is xyz?")

        assert "answer" in result
        assert result["sources"] == []


# ==============================================================================
# NoteMemoryService Category Tests
# ==============================================================================


class TestNoteMemoryServiceCategory:
    """Tests for category determination."""

    def test_determine_category_by_path_projects(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test category determination from path - projects."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        # Create mock note
        note = MagicMock()
        note.path = "projects/my-project.md"
        note.metadata = {"tags": []}

        category = service._determine_category(note)
        assert category == "projects"

    def test_determine_category_by_path_daily(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test category determination from path - daily notes."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        note = MagicMock()
        note.path = "daily/2024-01-20.md"
        note.metadata = {"tags": []}

        category = service._determine_category(note)
        assert category == "daily_notes"

    def test_determine_category_by_tag(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test category determination from tags."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        note = MagicMock()
        note.path = "notes/something.md"
        note.metadata = {"tags": ["people", "contact"]}

        category = service._determine_category(note)
        assert category == "people"

    def test_determine_category_default(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test default category for unmatched notes."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        note = MagicMock()
        note.path = "random/note.md"
        note.metadata = {"tags": ["misc"]}

        category = service._determine_category(note)
        assert category == "concepts"


# ==============================================================================
# NoteMemoryService Clear Tests
# ==============================================================================


class TestNoteMemoryServiceClear:
    """Tests for clearing the index."""

    @pytest.mark.asyncio
    async def test_clear_index(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test clearing the memory index."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        result = await service.clear_index()

        mock_memory_service.clear_memory.assert_called_once()
        assert result["cleared"] is True


# ==============================================================================
# Edge Cases
# ==============================================================================


class TestNoteMemoryServiceEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_memu_not_installed(
        self, memory_config: MemoryConfig
    ) -> None:
        """Test handling when memU is not installed."""
        service = NoteMemoryService(memory_config)

        with patch.dict("sys.modules", {"memu": None}):
            with patch("builtins.__import__", side_effect=ImportError("No memu")):
                with pytest.raises(ImportError) as exc_info:
                    service._get_memory_service()

                assert "memU is not installed" in str(exc_info.value)

    def test_build_indexable_content(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test building indexable content from note."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        note = MagicMock()
        note.title = "Test Note"
        note.content = "This is the content."
        note.metadata = {"tags": ["python", "testing"]}

        content = service._build_indexable_content(note)

        assert "# Test Note" in content
        assert "python, testing" in content
        assert "This is the content." in content

    def test_build_indexable_content_no_tags(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test building indexable content without tags."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        note = MagicMock()
        note.title = "No Tags Note"
        note.content = "Just content."
        note.metadata = {}

        content = service._build_indexable_content(note)

        assert "# No Tags Note" in content
        assert "Tags:" not in content

    def test_get_snippet_found(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test snippet extraction when query is found."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        content = "This is a long piece of content with python testing information."
        snippet = service._get_snippet(content, "python", max_length=30)

        assert "python" in snippet.lower()

    def test_get_snippet_not_found(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test snippet extraction when query is not found."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        content = "This is some content without the query."
        snippet = service._get_snippet(content, "xyznonexistent", max_length=50)

        assert len(snippet) <= 53  # max_length + "..."

    def test_build_memu_config(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test building memU configuration."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        config = service._build_memu_config()

        assert "llm_profiles" in config
        assert "default" in config["llm_profiles"]
        assert "embedding" in config["llm_profiles"]
        assert config["llm_profiles"]["default"]["chat_model"] == "llama3"

    def test_build_memu_config_creates_db_dir(
        self, temp_vault: Path, mock_memory_service: MagicMock
    ) -> None:
        """Test that _build_memu_config creates db directory."""
        config = MemoryConfig(vault_path=temp_vault)
        service = NoteMemoryService(config, memory_service=mock_memory_service)

        # Call build_memu_config which should create the directory
        service._build_memu_config()

        # Check db directory exists
        assert config.db_path is not None
        assert config.db_path.parent.exists()


# ==============================================================================
# Integration Tests (with mock memU)
# ==============================================================================


class TestNoteMemoryServiceIntegration:
    """Integration tests using mock memU service."""

    @pytest.mark.asyncio
    async def test_full_index_search_workflow(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test complete workflow: index vault, then search."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )

        # Initialize
        await service.initialize()
        assert service.is_initialized

        # Index vault
        index_result = await service.index_vault()
        assert index_result["indexed"] >= 1

        # Search
        search_results = await service.search("python testing")
        assert isinstance(search_results, list)

    @pytest.mark.asyncio
    async def test_index_then_clear(
        self, memory_config: MemoryConfig, mock_memory_service: MagicMock
    ) -> None:
        """Test indexing and then clearing."""
        service = NoteMemoryService(
            memory_config, memory_service=mock_memory_service
        )
        await service.initialize()

        # Index
        await service.index_vault()
        assert mock_memory_service.create_memory_item.call_count >= 1

        # Clear
        await service.clear_index()
        mock_memory_service.clear_memory.assert_called_once()