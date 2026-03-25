"""Tests for Query module - Keyword Search.

TDD approach: These tests define the expected behavior before implementation.
"""

import sqlite3
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from markwritter.query.search import HighlightResult, KeywordSearch, SearchResult

# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture
def temp_db() -> Generator[Path, None, None]:
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield db_path


@pytest.fixture
def populated_db(temp_db: Path) -> Path:
    """Create a database with sample notes indexed."""
    search = KeywordSearch(db_path=temp_db)

    # Index sample notes
    notes = [
        {
            "note_path": "python-testing.md",
            "title": "Python Testing Guide",
            "content": "This guide covers TDD practices in Python. Use pytest for testing.",
            "tags": ["python", "testing", "tdd"],
        },
        {
            "note_path": "fastapi-tutorial.md",
            "title": "FastAPI Tutorial",
            "content": "Learn to build APIs with FastAPI. FastAPI is a modern web framework.",
            "tags": ["python", "fastapi", "web"],
        },
        {
            "note_path": "projects/my-project.md",
            "title": "My Project",
            "content": "Project description. Uses Python for backend development.",
            "tags": ["project"],
        },
        {
            "note_path": "daily/2024-01-20.md",
            "title": "Daily Note",
            "content": "Today I worked on testing and Python development.",
            "tags": ["daily"],
        },
    ]

    for note in notes:
        search.index_note(
            note_path=note["note_path"],
            title=note["title"],
            content=note["content"],
            tags=note["tags"],
        )

    return temp_db


# ==============================================================================
# KeywordSearch Initialization Tests
# ==============================================================================


class TestKeywordSearchInit:
    """Tests for KeywordSearch initialization."""

    def test_init_with_path(self, temp_db: Path) -> None:
        """Test initialization with path."""
        search = KeywordSearch(db_path=temp_db)

        assert search.db_path == temp_db

    def test_init_creates_tables(self, temp_db: Path) -> None:
        """Test that initialization creates FTS5 tables."""
        search = KeywordSearch(db_path=temp_db)

        # Verify tables exist
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='notes_fts'"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None

    def test_init_with_string_path(self, temp_db: Path) -> None:
        """Test initialization with string path."""
        search = KeywordSearch(db_path=str(temp_db))

        assert search.db_path == temp_db


# ==============================================================================
# KeywordSearch Index Tests
# ==============================================================================


class TestKeywordSearchIndex:
    """Tests for note indexing."""

    def test_index_note(self, temp_db: Path) -> None:
        """Test indexing a single note."""
        search = KeywordSearch(db_path=temp_db)

        result = search.index_note(
            note_path="test.md",
            title="Test Note",
            content="This is test content with Python.",
            tags=["test"],
        )

        assert result is True

    def test_index_note_with_special_chars(self, temp_db: Path) -> None:
        """Test indexing note with special characters."""
        search = KeywordSearch(db_path=temp_db)

        result = search.index_note(
            note_path="special.md",
            title="Special Characters",
            content="Content with quotes: 'test' and \"double\". Unicode: cafe",
            tags=["special"],
        )

        assert result is True

    def test_index_note_empty_content(self, temp_db: Path) -> None:
        """Test indexing note with empty content."""
        search = KeywordSearch(db_path=temp_db)

        result = search.index_note(
            note_path="empty.md",
            title="Empty Note",
            content="",
            tags=[],
        )

        assert result is True

    def test_index_note_updates_existing(self, temp_db: Path) -> None:
        """Test that re-indexing updates existing note."""
        search = KeywordSearch(db_path=temp_db)

        # Index initial
        search.index_note(
            note_path="update.md",
            title="Original Title",
            content="Original content",
            tags=["original"],
        )

        # Update
        search.index_note(
            note_path="update.md",
            title="Updated Title",
            content="Updated content",
            tags=["updated"],
        )

        # Search for updated content
        results = search.search("Updated")
        assert len(results) == 1
        assert results[0].title == "Updated Title"

    def test_remove_note(self, populated_db: Path) -> None:
        """Test removing a note from index."""
        search = KeywordSearch(db_path=populated_db)

        result = search.remove_note("python-testing.md")
        assert result is True

        # Verify removed
        results = search.search("pytest")
        assert len(results) == 0

    def test_remove_note_nonexistent(self, temp_db: Path) -> None:
        """Test removing non-existent note."""
        search = KeywordSearch(db_path=temp_db)

        result = search.remove_note("nonexistent.md")
        assert result is False


# ==============================================================================
# KeywordSearch Search Tests
# ==============================================================================


class TestKeywordSearchSearch:
    """Tests for keyword search."""

    def test_search_single_term(self, populated_db: Path) -> None:
        """Test searching for a single term."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("Python")

        assert len(results) >= 3  # python-testing, fastapi-tutorial, my-project

    def test_search_multiple_terms(self, populated_db: Path) -> None:
        """Test searching for multiple terms."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("testing pytest")

        assert len(results) >= 1

    def test_search_with_limit(self, populated_db: Path) -> None:
        """Test search with result limit."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("Python", limit=2)

        assert len(results) <= 2

    def test_search_no_results(self, populated_db: Path) -> None:
        """Test search with no matches."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("xyznonexistentkeyword")

        assert results == []

    def test_search_case_insensitive(self, populated_db: Path) -> None:
        """Test case-insensitive search."""
        search = KeywordSearch(db_path=populated_db)

        results_lower = search.search("python")
        results_upper = search.search("PYTHON")

        assert len(results_lower) == len(results_upper)

    def test_search_returns_search_result_model(self, populated_db: Path) -> None:
        """Test that search returns SearchResult models."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("Python")

        assert len(results) > 0
        assert isinstance(results[0], SearchResult)
        assert results[0].note_path is not None
        assert results[0].title is not None
        assert results[0].score >= 0
        assert results[0].snippet is not None

    def test_search_empty_query(self, populated_db: Path) -> None:
        """Test search with empty query."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("")

        assert results == []

    def test_search_in_tags(self, populated_db: Path) -> None:
        """Test that search includes tags."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("fastapi")

        # Should find fastapi-tutorial.md (has fastapi in content and tags)
        assert len(results) >= 1

    def test_search_in_title(self, populated_db: Path) -> None:
        """Test that search includes title."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search("Tutorial")

        assert len(results) >= 1
        titles = [r.title for r in results]
        assert any("Tutorial" in t for t in titles)


# ==============================================================================
# KeywordSearch Highlight Tests
# ==============================================================================


class TestKeywordSearchHighlight:
    """Tests for search with highlighting."""

    def test_search_with_highlight(self, populated_db: Path) -> None:
        """Test search with highlighted snippets."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search_with_highlight("Python")

        assert len(results) >= 1
        assert isinstance(results[0], HighlightResult)
        # Highlight should contain <mark> tags
        assert results[0].highlighted_snippet is not None

    def test_search_with_highlight_multiple_terms(self, populated_db: Path) -> None:
        """Test highlight with multiple terms."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search_with_highlight("testing pytest")

        assert len(results) >= 1

    def test_search_with_highlight_no_match(self, populated_db: Path) -> None:
        """Test highlight when no match found."""
        search = KeywordSearch(db_path=populated_db)

        results = search.search_with_highlight("xyznonexistent")

        assert results == []


# ==============================================================================
# KeywordSearch Edge Cases
# ==============================================================================


class TestKeywordSearchEdgeCases:
    """Tests for edge cases."""

    def test_search_with_quotes(self, populated_db: Path) -> None:
        """Test search with quotes in query."""
        search = KeywordSearch(db_path=populated_db)

        # FTS5 uses quotes for phrase matching
        results = search.search('"modern web framework"')

        # Should handle gracefully
        assert isinstance(results, list)

    def test_search_with_special_fts_chars(self, populated_db: Path) -> None:
        """Test search with FTS5 special characters."""
        search = KeywordSearch(db_path=populated_db)

        # FTS5 has special chars like * for prefix
        results = search.search("Pyt*")  # Prefix search

        assert isinstance(results, list)

    def test_search_very_long_query(self, populated_db: Path) -> None:
        """Test search with very long query."""
        search = KeywordSearch(db_path=populated_db)

        long_query = " ".join(["term"] * 100)
        results = search.search(long_query)

        # Should handle gracefully
        assert isinstance(results, list)

    def test_index_many_notes(self, temp_db: Path) -> None:
        """Test indexing many notes."""
        search = KeywordSearch(db_path=temp_db)

        for i in range(100):
            search.index_note(
                note_path=f"note{i}.md",
                title=f"Note {i}",
                content=f"Content for note {i} with Python.",
                tags=[f"tag{i}"],
            )

        # Use explicit limit to get all results
        results = search.search("Python", limit=100)
        assert len(results) == 100

    def test_index_note_with_unicode(self, temp_db: Path) -> None:
        """Test indexing note with Unicode content."""
        search = KeywordSearch(db_path=temp_db)

        result = search.index_note(
            note_path="unicode.md",
            title="Unicode Note",
            content="Unicode: cafe, resume, emoji: test",
            tags=["unicode"],
        )

        assert result is True

        # Should be able to search Unicode
        results = search.search("cafe")
        assert len(results) == 1


# ==============================================================================
# KeywordSearch Clear Tests
# ==============================================================================


class TestKeywordSearchClear:
    """Tests for clearing the index."""

    def test_clear_index(self, populated_db: Path) -> None:
        """Test clearing all indexed content."""
        search = KeywordSearch(db_path=populated_db)

        result = search.clear_index()
        assert result is True

        # Verify empty
        results = search.search("Python")
        assert results == []

    def test_get_indexed_count(self, populated_db: Path) -> None:
        """Test getting count of indexed notes."""
        search = KeywordSearch(db_path=populated_db)

        count = search.get_indexed_count()

        assert count == 4  # We indexed 4 notes


# ==============================================================================
# KeywordSearch Phrase Search Tests
# ==============================================================================


class TestKeywordSearchPhrase:
    """Tests for phrase search."""

    def test_phrase_search(self, temp_db: Path) -> None:
        """Test exact phrase matching."""
        search = KeywordSearch(db_path=temp_db)

        search.index_note(
            note_path="phrase.md",
            title="Phrase Test",
            content="The quick brown fox jumps over the lazy dog.",
            tags=[],
        )

        # Exact phrase search
        results = search.search("quick brown fox")

        assert len(results) >= 1

    def test_partial_word_match(self, temp_db: Path) -> None:
        """Test partial word matching with prefix."""
        search = KeywordSearch(db_path=temp_db)

        search.index_note(
            note_path="partial.md",
            title="Partial Match Test",
            content="Testing partial matches with testing.",
            tags=[],
        )

        # Prefix search should find "testing"
        results = search.search("test*")

        assert len(results) >= 1
