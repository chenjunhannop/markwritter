"""Tests for Query module - Semantic Search.

TDD approach: These tests define the expected behavior before implementation.
"""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from markwritter.query.search import HybridSearchResult, SearchResult, SemanticSearch

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory with sample notes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)

        # Create sample notes
        (vault_path / "python-testing.md").write_text("""---
title: Python Testing Guide
tags: [python, testing, tdd]
---

# Python Testing Guide

This guide covers TDD practices in Python.
Use pytest for writing unit tests.
""")

        (vault_path / "fastapi-tutorial.md").write_text("""---
title: FastAPI Tutorial
tags: [python, fastapi, web]
---

# FastAPI Tutorial

Learn to build APIs with FastAPI.
FastAPI is a modern web framework for Python.
""")

        (vault_path / "projects").mkdir()
        (vault_path / "projects" / "my-project.md").write_text("""---
title: My Project
tags: [project]
---

# My Project

Project description.
Uses Python for backend.
""")

        yield vault_path


@pytest.fixture
def mock_memory_service() -> MagicMock:
    """Create a mock memory service for semantic search."""
    service = MagicMock()
    service.retrieve = AsyncMock(
        return_value={
            "items": [
                {
                    "id": "item-1",
                    "content": "Python testing guide with pytest",
                    "score": 0.95,
                    "user": {"note_path": "python-testing.md"},
                },
                {
                    "id": "item-2",
                    "content": "FastAPI web framework tutorial",
                    "score": 0.85,
                    "user": {"note_path": "fastapi-tutorial.md"},
                },
            ]
        }
    )
    return service


@pytest.fixture
def mock_vault() -> MagicMock:
    """Create a mock Obsidian vault."""
    vault = MagicMock()

    # Mock read_note
    def mock_read_note(path: str) -> MagicMock:
        note = MagicMock()
        note.path = path
        note.title = path.replace(".md", "").replace("-", " ").title()
        note.content = f"Content for {path}"
        note.metadata = {"tags": ["test"]}
        return note

    vault.read_note.side_effect = mock_read_note
    vault.path = Path("/tmp/vault")

    return vault


# ==============================================================================
# SemanticSearch Initialization Tests
# ==============================================================================


class TestSemanticSearchInit:
    """Tests for SemanticSearch initialization."""

    def test_init_with_memory_service(self, mock_memory_service: MagicMock) -> None:
        """Test initialization with memory service."""
        search = SemanticSearch(memory_service=mock_memory_service)

        assert search.memory_service == mock_memory_service

    def test_init_with_vault(self, mock_memory_service: MagicMock, mock_vault: MagicMock) -> None:
        """Test initialization with vault."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        assert search.vault == mock_vault


# ==============================================================================
# SemanticSearch Search Tests
# ==============================================================================


class TestSemanticSearchSearch:
    """Tests for semantic search."""

    @pytest.mark.asyncio
    async def test_search_returns_results(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that search returns results."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("python testing")

        assert isinstance(results, list)
        assert len(results) >= 1
        assert isinstance(results[0], SearchResult)

    @pytest.mark.asyncio
    async def test_search_calls_retrieve(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that search calls retrieve on memory service."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        await search.search("python testing", top_k=10)

        mock_memory_service.retrieve.assert_called_once()
        call_args = mock_memory_service.retrieve.call_args
        assert call_args[0][0] == "python testing"
        assert call_args[1]["top_k"] == 10

    @pytest.mark.asyncio
    async def test_search_with_top_k(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test search with top_k parameter."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        await search.search("test", top_k=5)

        call_kwargs = mock_memory_service.retrieve.call_args[1]
        assert call_kwargs["top_k"] == 5

    @pytest.mark.asyncio
    async def test_search_empty_results(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test search with no results."""
        mock_memory_service.retrieve = AsyncMock(return_value={"items": []})

        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("nonexistent")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_result_has_required_fields(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that search results have required fields."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("python")

        assert len(results) > 0
        result = results[0]
        assert result.note_path is not None
        assert result.title is not None
        assert result.score >= 0
        assert result.snippet is not None

    @pytest.mark.asyncio
    async def test_search_handles_missing_note(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test search handles notes that no longer exist."""
        # Mock vault to raise error for missing note
        from markwritter.obsidian.vault import NoteNotFoundError

        def mock_read_note(path: str) -> MagicMock:
            if path == "python-testing.md":
                note = MagicMock()
                note.path = path
                note.title = "Python Testing"
                note.content = "Test content"
                note.metadata = {}
                return note
            raise NoteNotFoundError(f"Not found: {path}")

        mock_vault.read_note.side_effect = mock_read_note

        # Return item for missing note
        mock_memory_service.retrieve = AsyncMock(
            return_value={
                "items": [
                    {
                        "id": "item-1",
                        "content": "Test",
                        "score": 0.9,
                        "user": {"note_path": "missing-note.md"},
                    },
                ]
            }
        )

        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("test")

        # Should handle gracefully, returning empty or skipping missing
        assert isinstance(results, list)


# ==============================================================================
# SemanticSearch Hybrid Search Tests
# ==============================================================================


class TestSemanticSearchHybrid:
    """Tests for hybrid search (keyword + semantic)."""

    @pytest.mark.asyncio
    async def test_hybrid_search_combines_results(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that hybrid search combines keyword and semantic results."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        # Mock keyword search
        with patch.object(search, "_keyword_search") as mock_kw:
            mock_kw.return_value = [
                SearchResult(
                    note_path="kw-result.md",
                    title="Keyword Result",
                    score=0.8,
                    snippet="Keyword match",
                )
            ]

            results = await search.hybrid_search("python testing", mode="balanced")

            assert isinstance(results, list)
            assert isinstance(results[0], HybridSearchResult)

    @pytest.mark.asyncio
    async def test_hybrid_search_mode_keyword(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test hybrid search with keyword mode."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.hybrid_search("python", mode="keyword")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_hybrid_search_mode_semantic(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test hybrid search with semantic mode."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.hybrid_search("python", mode="semantic")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_hybrid_search_deduplicates(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that hybrid search deduplicates results."""
        # Both searches return same note
        mock_memory_service.retrieve = AsyncMock(
            return_value={
                "items": [
                    {
                        "id": "item-1",
                        "content": "Python testing",
                        "score": 0.95,
                        "user": {"note_path": "python-testing.md"},
                    },
                ]
            }
        )

        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        with patch.object(search, "_keyword_search") as mock_kw:
            mock_kw.return_value = [
                SearchResult(
                    note_path="python-testing.md",  # Same as semantic
                    title="Python Testing",
                    score=0.8,
                    snippet="Match",
                )
            ]

            results = await search.hybrid_search("python testing", mode="balanced")

            # Should deduplicate
            paths = [r.note_path for r in results]
            assert paths.count("python-testing.md") <= 1

    @pytest.mark.asyncio
    async def test_hybrid_search_reranks(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test that hybrid search re-ranks combined results."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.hybrid_search("python", mode="balanced")

        # Results should be sorted by combined score
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].combined_score >= results[i + 1].combined_score


# ==============================================================================
# SemanticSearch Edge Cases
# ==============================================================================


class TestSemanticSearchEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_search_with_empty_query(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test search with empty query."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_with_very_long_query(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test search with very long query."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        long_query = " ".join(["python"] * 100)
        results = await search.search(long_query)

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_with_unicode(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test search with Unicode characters."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("cafe resume")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_handles_memory_service_error(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test search handles memory service errors."""
        mock_memory_service.retrieve = AsyncMock(side_effect=Exception("Service error"))

        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("test")

        # Should handle gracefully
        assert results == []

    @pytest.mark.asyncio
    async def test_search_snippet_extraction(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test snippet extraction from long content."""
        mock_vault.read_note.return_value = MagicMock(
            path="test.md",
            title="Test",
            content="A" * 1000 + "python testing" + "B" * 1000,
            metadata={},
        )

        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        results = await search.search("python testing")

        if results:
            # Snippet should be truncated
            assert len(results[0].snippet) < 1000


# ==============================================================================
# SemanticSearch Integration Tests
# ==============================================================================


class TestSemanticSearchIntegration:
    """Integration tests with mock components."""

    @pytest.mark.asyncio
    async def test_full_search_workflow(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test complete search workflow."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        # Search
        results = await search.search("python testing", top_k=5)

        assert len(results) >= 1
        assert all(isinstance(r, SearchResult) for r in results)

    @pytest.mark.asyncio
    async def test_hybrid_workflow(
        self, mock_memory_service: MagicMock, mock_vault: MagicMock
    ) -> None:
        """Test hybrid search workflow."""
        search = SemanticSearch(
            memory_service=mock_memory_service,
            vault=mock_vault,
        )

        # Hybrid search
        results = await search.hybrid_search("python", mode="balanced")

        assert isinstance(results, list)
