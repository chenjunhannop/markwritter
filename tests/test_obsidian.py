"""Tests for Obsidian vault management.

TDD approach: These tests define the expected behavior before implementation.
"""

import tempfile
from pathlib import Path
from typing import Generator

import pytest

from markwritter.obsidian.models import Frontmatter, Note, NoteMeta
from markwritter.obsidian.parser import NoteParser
from markwritter.obsidian.vault import (
    InvalidVaultError,
    NoteNotFoundError,
    ObsidianVault,
    VaultError,
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
        (vault_path / "note1.md").write_text(
            """---
title: First Note
tags: [python, testing]
created: 2024-01-15
---

# First Note

This is the content of the first note.

It links to [[note2]] and [[projects/my-project|My Project]].
"""
        )

        (vault_path / "note2.md").write_text(
            """---
title: Second Note
tags: [python, tutorial]
---

# Second Note

Content with a tag #python and #testing.

Backlink to [[note1]].
"""
        )

        # Create subdirectory with notes
        projects_dir = vault_path / "projects"
        projects_dir.mkdir()

        (projects_dir / "my-project.md").write_text(
            """---
title: My Project
status: active
---

# My Project

Project description.

Links: [[note1]], [[note2]]
"""
        )

        (projects_dir / "archive.md").write_text(
            """---
title: Archived Project
status: archived
---

# Archived Project

Old project.
"""
        )

        yield vault_path


@pytest.fixture
def parser(temp_vault: Path) -> NoteParser:
    """Create a NoteParser instance."""
    return NoteParser(temp_vault)


@pytest.fixture
def vault(temp_vault: Path) -> ObsidianVault:
    """Create an ObsidianVault instance."""
    return ObsidianVault(temp_vault)


# ==============================================================================
# NoteParser Tests
# ==============================================================================


class TestNoteParserFrontmatter:
    """Tests for frontmatter parsing."""

    def test_parse_simple_frontmatter(self, parser: NoteParser, temp_vault: Path) -> None:
        """Test parsing simple YAML frontmatter."""
        content = """---
title: Test Note
author: John
---

Content here.
"""
        result = parser.parse_frontmatter(content)

        assert isinstance(result, Frontmatter)
        assert result.data.get("title") == "Test Note"
        assert result.data.get("author") == "John"

    def test_parse_frontmatter_with_list(self, parser: NoteParser) -> None:
        """Test parsing frontmatter with list values."""
        content = """---
title: Test
tags: [python, testing, tdd]
---

Content.
"""
        result = parser.parse_frontmatter(content)

        assert result.data.get("tags") == ["python", "testing", "tdd"]

    def test_parse_frontmatter_with_multiline_list(self, parser: NoteParser) -> None:
        """Test parsing frontmatter with multiline list."""
        content = """---
title: Test
tags:
  - python
  - testing
  - tdd
---

Content.
"""
        result = parser.parse_frontmatter(content)

        assert result.data.get("tags") == ["python", "testing", "tdd"]

    def test_parse_no_frontmatter(self, parser: NoteParser) -> None:
        """Test content without frontmatter returns empty dict."""
        content = "# Just a title\n\nNo frontmatter here."
        result = parser.parse_frontmatter(content)

        assert result.data == {}
        assert result.content_start == 0

    def test_parse_empty_frontmatter(self, parser: NoteParser) -> None:
        """Test empty frontmatter."""
        content = "---\n---\n\nContent."
        result = parser.parse_frontmatter(content)

        assert result.data == {}

    def test_parse_frontmatter_with_date(self, parser: NoteParser) -> None:
        """Test parsing frontmatter with date values."""
        content = """---
title: Test
created: 2024-01-15
modified: 2024-01-20T10:30:00
---

Content.
"""
        result = parser.parse_frontmatter(content)

        # YAML parses dates as datetime objects
        assert result.data.get("created") is not None
        assert result.data.get("modified") is not None
        # Verify they can be converted to strings
        assert str(result.data.get("created")).startswith("2024-01-15")

    def test_parse_frontmatter_with_special_chars(self, parser: NoteParser) -> None:
        """Test parsing frontmatter with special characters in values."""
        content = """---
title: "Test: A Special Title"
description: "Contains: colons, 'quotes', and special chars!"
---

Content.
"""
        result = parser.parse_frontmatter(content)

        assert "Special Title" in str(result.data.get("title"))


class TestNoteParserWikilinks:
    """Tests for wikilink extraction."""

    def test_extract_simple_wikilink(self, parser: NoteParser) -> None:
        """Test extracting simple wikilink."""
        content = "This links to [[note1]]."
        links = parser.extract_wikilinks(content)

        assert links == ["note1"]

    def test_extract_wikilink_with_alias(self, parser: NoteParser) -> None:
        """Test extracting wikilink with alias."""
        content = "Link to [[my-project|My Project]]."
        links = parser.extract_wikilinks(content)

        assert links == ["my-project"]

    def test_extract_multiple_wikilinks(self, parser: NoteParser) -> None:
        """Test extracting multiple wikilinks."""
        content = "Links to [[note1]], [[note2]], and [[projects/my-project|Project]]."
        links = parser.extract_wikilinks(content)

        assert len(links) == 3
        assert "note1" in links
        assert "note2" in links
        assert "projects/my-project" in links

    def test_extract_no_wikilinks(self, parser: NoteParser) -> None:
        """Test content with no wikilinks."""
        content = "No links here, just #tags."
        links = parser.extract_wikilinks(content)

        assert links == []

    def test_extract_wikilinks_with_spaces(self, parser: NoteParser) -> None:
        """Test wikilinks with spaces in path."""
        content = "Link to [[my notes/daily note]]."
        links = parser.extract_wikilinks(content)

        assert links == ["my notes/daily note"]


class TestNoteParserTags:
    """Tests for tag extraction."""

    def test_extract_simple_tag(self, parser: NoteParser) -> None:
        """Test extracting simple tag."""
        content = "This has a #python tag."
        tags = parser.extract_tags(content)

        assert "python" in tags

    def test_extract_multiple_tags(self, parser: NoteParser) -> None:
        """Test extracting multiple tags."""
        content = "Tags: #python #testing #tdd"
        tags = parser.extract_tags(content)

        assert "python" in tags
        assert "testing" in tags
        assert "tdd" in tags

    def test_extract_nested_tag(self, parser: NoteParser) -> None:
        """Test extracting nested tag."""
        content = "Nested tag: #project/active/important"
        tags = parser.extract_tags(content)

        assert "project/active/important" in tags

    def test_extract_tag_with_hyphen(self, parser: NoteParser) -> None:
        """Test extracting tag with hyphen."""
        content = "Tag: #my-project"
        tags = parser.extract_tags(content)

        assert "my-project" in tags

    def test_extract_no_tags(self, parser: NoteParser) -> None:
        """Test content with no tags."""
        content = "No tags here, just [[links]]."
        tags = parser.extract_tags(content)

        assert tags == []


class TestNoteParserNoteParsing:
    """Tests for full note parsing."""

    def test_parse_note_full(self, parser: NoteParser, temp_vault: Path) -> None:
        """Test parsing a complete note."""
        note = parser.parse_note(temp_vault / "note1.md")

        assert isinstance(note, Note)
        assert note.path == "note1.md"
        assert note.title == "First Note"
        assert "python" in note.metadata.get("tags", [])
        assert "note2" in note.links

    def test_parse_note_without_frontmatter(
        self, parser: NoteParser, temp_vault: Path
    ) -> None:
        """Test parsing note without frontmatter."""
        # Create note without frontmatter
        (temp_vault / "no-fm.md").write_text("# Plain Note\n\nNo frontmatter.")

        note = parser.parse_note(temp_vault / "no-fm.md")

        # No custom metadata from frontmatter (only auto-added tags list)
        assert note.metadata.get("title") is None
        assert note.metadata.get("tags") == []  # Empty tags list
        assert note.title == "no-fm"  # Falls back to filename

    def test_parse_note_meta(self, parser: NoteParser, temp_vault: Path) -> None:
        """Test parsing lightweight note metadata."""
        meta = parser.parse_note_meta(temp_vault / "note1.md")

        assert isinstance(meta, NoteMeta)
        assert meta.path == "note1.md"
        assert meta.title == "First Note"


# ==============================================================================
# ObsidianVault Tests
# ==============================================================================


class TestObsidianVaultInit:
    """Tests for vault initialization."""

    def test_init_with_path_object(self, temp_vault: Path) -> None:
        """Test initialization with Path object."""
        vault = ObsidianVault(temp_vault)

        assert vault.path == temp_vault

    def test_init_with_string_path(self, temp_vault: Path) -> None:
        """Test initialization with string path."""
        vault = ObsidianVault(str(temp_vault))

        assert vault.path == temp_vault

    def test_init_invalid_path_raises_error(self) -> None:
        """Test that non-existent path raises InvalidVaultError."""
        with pytest.raises(InvalidVaultError):
            ObsidianVault("/non/existent/path")

    def test_init_file_path_raises_error(self, tmp_path: Path) -> None:
        """Test that file path (not directory) raises InvalidVaultError."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        with pytest.raises(InvalidVaultError):
            ObsidianVault(file_path)


class TestObsidianVaultListNotes:
    """Tests for listing notes."""

    def test_list_all_notes(self, vault: ObsidianVault) -> None:
        """Test listing all notes in vault."""
        notes = vault.list_notes()

        assert len(notes) == 4  # note1, note2, projects/my-project, projects/archive
        paths = [n.path for n in notes]
        assert "note1.md" in paths
        assert "note2.md" in paths
        assert "projects/my-project.md" in paths

    def test_list_notes_non_recursive(self, vault: ObsidianVault) -> None:
        """Test listing notes without recursion."""
        notes = vault.list_notes(recursive=False)

        # Should only get notes in root directory
        paths = [n.path for n in notes]
        assert "note1.md" in paths
        assert "note2.md" in paths
        assert "projects/my-project.md" not in paths

    def test_list_notes_in_subdirectory(self, vault: ObsidianVault) -> None:
        """Test listing notes in specific subdirectory."""
        notes = vault.list_notes(directory="projects")

        assert len(notes) == 2
        paths = [n.path for n in notes]
        assert "projects/my-project.md" in paths
        assert "projects/archive.md" in paths

    def test_list_notes_empty_directory(self, vault: ObsidianVault) -> None:
        """Test listing notes in empty directory."""
        notes = vault.list_notes(directory="nonexistent")

        assert notes == []

    def test_list_notes_excludes_non_markdown(self, temp_vault: Path) -> None:
        """Test that non-markdown files are excluded."""
        (temp_vault / "image.png").write_bytes(b"fake image")
        (temp_vault / "data.json").write_text("{}")

        vault = ObsidianVault(temp_vault)
        notes = vault.list_notes()

        paths = [n.path for n in notes]
        assert "image.png" not in paths
        assert "data.json" not in paths


class TestObsidianVaultReadNote:
    """Tests for reading notes."""

    def test_read_note_success(self, vault: ObsidianVault) -> None:
        """Test reading an existing note."""
        note = vault.read_note("note1.md")

        assert isinstance(note, Note)
        assert note.path == "note1.md"
        assert note.title == "First Note"
        assert "python" in note.metadata.get("tags", [])
        assert "# First Note" in note.content

    def test_read_note_in_subdirectory(self, vault: ObsidianVault) -> None:
        """Test reading note in subdirectory."""
        note = vault.read_note("projects/my-project.md")

        assert note.path == "projects/my-project.md"
        assert note.title == "My Project"

    def test_read_note_not_found_raises_error(self, vault: ObsidianVault) -> None:
        """Test reading non-existent note raises error."""
        with pytest.raises(NoteNotFoundError):
            vault.read_note("nonexistent.md")

    def test_read_note_extracts_links(self, vault: ObsidianVault) -> None:
        """Test that links are extracted when reading."""
        note = vault.read_note("note1.md")

        assert "note2" in note.links
        assert "projects/my-project" in note.links


class TestObsidianVaultWriteNote:
    """Tests for writing notes."""

    def test_write_new_note(self, vault: ObsidianVault) -> None:
        """Test writing a new note."""
        note = Note(
            path="new-note.md",
            content="# New Note\n\nCreated by test.",
            metadata={"title": "New Note", "tags": ["test"]},
        )

        vault.write_note(note)

        # Verify note was written
        read_note = vault.read_note("new-note.md")
        assert read_note.title == "New Note"
        assert "Created by test" in read_note.content

    def test_write_note_overwrite(self, vault: ObsidianVault) -> None:
        """Test overwriting existing note."""
        # Read existing note
        note = vault.read_note("note1.md")
        note.content = "# Updated Content\n\nNew content."

        vault.write_note(note)

        # Verify overwrite
        updated = vault.read_note("note1.md")
        assert "Updated Content" in updated.content

    def test_write_note_no_overwrite_raises_error(self, vault: ObsidianVault) -> None:
        """Test that writing existing note without overwrite raises error."""
        note = Note(
            path="note1.md",  # Already exists
            content="# Duplicate",
        )

        with pytest.raises(VaultError):
            vault.write_note(note, overwrite=False)

    def test_write_note_creates_directories(self, vault: ObsidianVault) -> None:
        """Test that writing creates parent directories."""
        note = Note(
            path="new/sub/dir/note.md",
            content="# Nested Note",
        )

        vault.write_note(note)

        # Verify nested note exists
        read_note = vault.read_note("new/sub/dir/note.md")
        assert read_note.title == "note"

    def test_write_note_preserves_frontmatter(self, vault: ObsidianVault) -> None:
        """Test that writing preserves frontmatter."""
        note = Note(
            path="fm-note.md",
            content="Body content",
            metadata={
                "title": "FM Note",
                "tags": ["test", "frontmatter"],
                "custom": "value",
            },
        )

        vault.write_note(note)

        # Read back and verify
        read_note = vault.read_note("fm-note.md")
        assert read_note.metadata.get("title") == "FM Note"
        assert "test" in read_note.metadata.get("tags", [])


class TestObsidianVaultDeleteNote:
    """Tests for deleting notes."""

    def test_delete_existing_note(self, vault: ObsidianVault) -> None:
        """Test deleting an existing note."""
        vault.delete_note("note1.md")

        with pytest.raises(NoteNotFoundError):
            vault.read_note("note1.md")

    def test_delete_nonexistent_raises_error(self, vault: ObsidianVault) -> None:
        """Test deleting non-existent note raises error."""
        with pytest.raises(NoteNotFoundError):
            vault.delete_note("nonexistent.md")


class TestObsidianVaultSearch:
    """Tests for searching notes."""

    def test_search_by_keyword(self, vault: ObsidianVault) -> None:
        """Test searching notes by keyword."""
        results = vault.search_by_keyword("python")

        assert len(results) >= 2  # note1 and note2 mention python
        paths = [r.path for r in results]
        assert "note1.md" in paths
        assert "note2.md" in paths

    def test_search_by_keyword_no_results(self, vault: ObsidianVault) -> None:
        """Test search with no matches."""
        results = vault.search_by_keyword("xyznonexistentkeyword")

        assert results == []

    def test_search_by_keyword_case_insensitive(self, vault: ObsidianVault) -> None:
        """Test case-insensitive keyword search."""
        results_lower = vault.search_by_keyword("python")
        results_upper = vault.search_by_keyword("PYTHON")

        assert len(results_lower) == len(results_upper)

    def test_search_by_tag(self, vault: ObsidianVault) -> None:
        """Test searching notes by tag."""
        results = vault.search_by_tag("python")

        assert len(results) >= 2
        paths = [r.path for r in results]
        assert "note1.md" in paths

    def test_search_by_tag_with_hash_prefix(self, vault: ObsidianVault) -> None:
        """Test tag search with # prefix."""
        results_with_hash = vault.search_by_tag("#python")
        results_without_hash = vault.search_by_tag("python")

        assert len(results_with_hash) == len(results_without_hash)

    def test_search_by_tag_no_results(self, vault: ObsidianVault) -> None:
        """Test tag search with no matches."""
        results = vault.search_by_tag("nonexistenttag")

        assert results == []


class TestObsidianVaultBacklinks:
    """Tests for backlink tracking."""

    def test_get_backlinks(self, vault: ObsidianVault) -> None:
        """Test getting backlinks for a note."""
        # note2 links to note1
        backlinks = vault.get_backlinks("note1.md")

        assert "note2.md" in backlinks

    def test_get_backlinks_multiple(self, vault: ObsidianVault) -> None:
        """Test getting multiple backlinks."""
        # my-project links to both note1 and note2
        backlinks_note1 = vault.get_backlinks("note1.md")
        backlinks_note2 = vault.get_backlinks("note2.md")

        assert "projects/my-project.md" in backlinks_note1
        assert "projects/my-project.md" in backlinks_note2

    def test_get_backlinks_none(self, vault: ObsidianVault) -> None:
        """Test backlinks for note with no incoming links."""
        backlinks = vault.get_backlinks("projects/archive.md")

        assert backlinks == []


class TestObsidianVaultNoteExists:
    """Tests for note existence check."""

    def test_note_exists_true(self, vault: ObsidianVault) -> None:
        """Test that existing note returns True."""
        assert vault.note_exists("note1.md") is True

    def test_note_exists_false(self, vault: ObsidianVault) -> None:
        """Test that non-existing note returns False."""
        assert vault.note_exists("nonexistent.md") is False

    def test_note_exists_in_subdirectory(self, vault: ObsidianVault) -> None:
        """Test existence check for note in subdirectory."""
        assert vault.note_exists("projects/my-project.md") is True


# ==============================================================================
# Edge Cases and Error Handling
# ==============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_vault(self, tmp_path: Path) -> None:
        """Test operations on empty vault."""
        vault = ObsidianVault(tmp_path)

        assert vault.list_notes() == []
        assert vault.search_by_keyword("anything") == []

    def test_special_characters_in_content(self, temp_vault: Path) -> None:
        """Test handling special characters in note content."""
        special_note = temp_vault / "special.md"
        special_note.write_text(
            """---
title: Special Characters
---

# Special Characters

Unicode: cafe, resume, emoji: test

Code: `x = y` and **bold** and *italic*

Links: [[note with spaces]] and [[日本語]]
"""
        )

        vault = ObsidianVault(temp_vault)
        note = vault.read_note("special.md")

        assert "cafe" in note.content
        assert "[[note with spaces]]" in note.content

    def test_very_long_content(self, temp_vault: Path) -> None:
        """Test handling large note content."""
        long_note = temp_vault / "long.md"
        long_content = "# Long Note\n\n" + "x" * 100000  # 100KB
        long_note.write_text(long_content)

        vault = ObsidianVault(temp_vault)
        note = vault.read_note("long.md")

        assert len(note.content) == len(long_content)

    def test_concurrent_note_operations(self, vault: ObsidianVault) -> None:
        """Test that operations work correctly in sequence."""
        # Write
        note1 = Note(path="concurrent1.md", content="Content 1")
        note2 = Note(path="concurrent2.md", content="Content 2")
        vault.write_note(note1)
        vault.write_note(note2)

        # Read both
        r1 = vault.read_note("concurrent1.md")
        r2 = vault.read_note("concurrent2.md")
        assert r1.content == "Content 1"
        assert r2.content == "Content 2"

        # Delete one
        vault.delete_note("concurrent1.md")
        assert vault.note_exists("concurrent1.md") is False
        assert vault.note_exists("concurrent2.md") is True

    def test_symlink_handling(self, temp_vault: Path) -> None:
        """Test handling of symlinks (should be skipped)."""
        # Create a symlink to a file outside vault
        external_file = temp_vault.parent / "external.md"
        external_file.write_text("# External")

        symlink = temp_vault / "link.md"
        symlink.symlink_to(external_file)

        vault = ObsidianVault(temp_vault)
        # Symlinks are regular files, so they may be included
        # This test verifies that symlinks don't cause errors
        notes = vault.list_notes()
        # Should at least have the original notes
        assert len(notes) >= 4

    def test_hidden_files_excluded(self, temp_vault: Path) -> None:
        """Test that hidden files (starting with .) are excluded."""
        (temp_vault / ".hidden.md").write_text("# Hidden")
        (temp_vault / ".obsidian").mkdir()
        (temp_vault / ".obsidian" / "config").write_text("{}")

        vault = ObsidianVault(temp_vault)
        notes = vault.list_notes()
        paths = [n.path for n in notes]

        assert ".hidden.md" not in paths
