"""Obsidian vault management."""

import os
from pathlib import Path
from typing import Optional

from markwritter.exceptions import InvalidVaultError, NoteNotFoundError, VaultError
from markwritter.obsidian.models import Note, NoteMeta
from markwritter.obsidian.parser import NoteParser


class ObsidianVault:
    """Manages an Obsidian vault.

    Provides:
    - Note CRUD operations
    - Directory traversal
    - Full-text search
    - Backlink tracking
    """

    def __init__(self, vault_path: Path | str):
        """Initialize vault manager.

        Args:
            vault_path: Path to the Obsidian vault root

        Raises:
            InvalidVaultError: If vault path doesn't exist or isn't a directory
        """
        self._path = Path(vault_path)
        self._parser = NoteParser(self._path)

        if not self._path.exists():
            raise InvalidVaultError(f"Vault path does not exist: {self._path}")
        if not self._path.is_dir():
            raise InvalidVaultError(f"Vault path is not a directory: {self._path}")

    @property
    def path(self) -> Path:
        """Return vault root path."""
        return self._path

    def _is_valid_note(self, path: Path) -> bool:
        """Check if a path is a valid markdown note.

        Args:
            path: Path to check

        Returns:
            True if path is a valid markdown note
        """
        # Must be a file
        if not path.is_file():
            return False

        # Must have .md extension
        if path.suffix.lower() != ".md":
            return False

        # Must not be hidden (starting with .)
        if path.name.startswith("."):
            return False

        # Skip files in hidden directories (like .obsidian)
        try:
            relative = path.relative_to(self._path)
            for part in relative.parts:
                if part.startswith("."):
                    return False
        except ValueError:
            return False

        return True

    def _resolve_note_path(self, note_path: str) -> Path:
        """Resolve a relative note path to absolute path.

        Args:
            note_path: Relative path to the note

        Returns:
            Absolute path to the note
        """
        return self._path / note_path

    def list_notes(
        self,
        directory: Optional[str] = None,
        recursive: bool = True,
    ) -> list[NoteMeta]:
        """List all notes in vault or specific directory.

        Args:
            directory: Subdirectory path (relative to vault root)
            recursive: Whether to search recursively

        Returns:
            List of NoteMeta objects
        """
        if directory:
            base_path = self._path / directory
            if not base_path.exists():
                return []
        else:
            base_path = self._path

        notes: list[NoteMeta] = []

        if recursive:
            # Walk all subdirectories
            for root, dirs, files in os.walk(base_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith(".")]

                for filename in files:
                    file_path = Path(root) / filename
                    if self._is_valid_note(file_path):
                        try:
                            meta = self._parser.parse_note_meta(file_path)
                            notes.append(meta)
                        except Exception:
                            # Skip notes that can't be parsed
                            continue
        else:
            # Only list notes in the specified directory (non-recursive)
            for item in base_path.iterdir():
                if self._is_valid_note(item):
                    try:
                        meta = self._parser.parse_note_meta(item)
                        notes.append(meta)
                    except Exception:
                        continue

        # Sort by path for consistent ordering
        notes.sort(key=lambda n: n.path)
        return notes

    def read_note(self, note_path: str) -> Note:
        """Read a note from the vault.

        Args:
            note_path: Relative path to the note (from vault root)

        Returns:
            Complete Note object

        Raises:
            NoteNotFoundError: If note doesn't exist
        """
        full_path = self._resolve_note_path(note_path)

        if not full_path.exists():
            raise NoteNotFoundError(f"Note not found: {note_path}")

        if not self._is_valid_note(full_path):
            raise NoteNotFoundError(f"Not a valid note: {note_path}")

        note = self._parser.parse_note(full_path)

        # Compute backlinks
        note.backlinks = self.get_backlinks(note_path)

        return note

    def write_note(self, note: Note, overwrite: bool = True) -> None:
        """Write a note to the vault.

        Args:
            note: Note object to write
            overwrite: Whether to overwrite existing note

        Raises:
            VaultError: If note exists and overwrite=False
        """
        full_path = self._resolve_note_path(note.path)

        # Check if note exists
        if full_path.exists() and not overwrite:
            raise VaultError(f"Note already exists: {note.path}")

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Build content with frontmatter
        content = self._build_content(note)

        # Write the note
        full_path.write_text(content, encoding="utf-8")

    def _build_content(self, note: Note) -> str:
        """Build note content with YAML frontmatter.

        Args:
            note: Note object

        Returns:
            Complete content string with frontmatter
        """
        if note.metadata:
            # Build YAML frontmatter
            import yaml

            frontmatter = yaml.dump(
                note.metadata,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            ).strip()
            return f"---\n{frontmatter}\n---\n{note.content}"
        else:
            return note.content

    def delete_note(self, note_path: str) -> None:
        """Delete a note from the vault.

        Args:
            note_path: Relative path to the note

        Raises:
            NoteNotFoundError: If note doesn't exist
        """
        full_path = self._resolve_note_path(note_path)

        if not full_path.exists():
            raise NoteNotFoundError(f"Note not found: {note_path}")

        full_path.unlink()

    def search_by_keyword(self, query: str) -> list[NoteMeta]:
        """Search notes by keyword.

        Args:
            query: Search query string

        Returns:
            List of matching NoteMeta objects
        """
        query_lower = query.lower()
        results: list[NoteMeta] = []

        for meta in self.list_notes():
            full_path = self._resolve_note_path(meta.path)
            try:
                content = full_path.read_text(encoding="utf-8").lower()
                if query_lower in content:
                    results.append(meta)
            except Exception:
                continue

        return results

    def search_by_tag(self, tag: str) -> list[NoteMeta]:
        """Search notes by tag.

        Args:
            tag: Tag to search for (with or without # prefix)

        Returns:
            List of matching NoteMeta objects
        """
        # Remove # prefix if present
        tag = tag.lstrip("#")

        results: list[NoteMeta] = []

        for meta in self.list_notes():
            if tag in meta.tags:
                results.append(meta)

        return results

    def get_backlinks(self, note_path: str) -> list[str]:
        """Get all notes that link to the specified note.

        Args:
            note_path: Relative path to the note

        Returns:
            List of paths to notes that link to this note
        """
        # Extract the note name without extension for linking
        note_name = Path(note_path).stem
        note_name_lower = note_name.lower()

        backlinks: list[str] = []

        # Search all notes for links to this note
        for meta in self.list_notes():
            if meta.path == note_path:
                continue  # Skip self

            full_path = self._resolve_note_path(meta.path)
            try:
                content = full_path.read_text(encoding="utf-8")
                links = self._parser.extract_wikilinks(content)

                # Check if any link matches this note
                for link in links:
                    link_stem = Path(link).stem.lower()
                    # Match by stem name or full path
                    if link_stem == note_name_lower or link.lower() == note_path.lower():
                        backlinks.append(meta.path)
                        break
            except Exception:
                continue

        return backlinks

    def note_exists(self, note_path: str) -> bool:
        """Check if a note exists.

        Args:
            note_path: Relative path to the note

        Returns:
            True if note exists
        """
        full_path = self._resolve_note_path(note_path)
        return self._is_valid_note(full_path)
