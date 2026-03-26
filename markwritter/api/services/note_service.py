"""Note service for note operations.

Phase 3.3: Service layer implementation for note operations.
Provides a clean interface for note CRUD operations with proper error handling.
"""

from __future__ import annotations

import logging
import urllib.parse
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from markwritter.obsidian.vault import ObsidianVault

logger = logging.getLogger(__name__)


class NoteResult(BaseModel):
    """Result of a note operation."""

    success: bool
    path: str
    message: str = ""


class NoteService:
    """Service for note operations.

    Provides a clean interface for note CRUD operations with:
    - Path validation (prevents path traversal)
    - Proper error handling
    - Dependency injection support
    """

    def __init__(self, vault: Optional[ObsidianVault] = None) -> None:
        """Initialize the note service.

        Args:
            vault: ObsidianVault instance for note operations.

        Raises:
            ValueError: If vault is None.
        """
        if vault is None:
            raise ValueError("vault is required for NoteService")
        self._vault = vault

    @property
    def vault(self) -> ObsidianVault:
        """Get the vault instance."""
        return self._vault

    def is_valid_path(self, path: str) -> bool:
        """Check if a path is safe (no path traversal).

        Uses pathlib.Path.resolve() for robust path validation.

        Args:
            path: Path to check

        Returns:
            True if path is safe
        """
        if not path:
            return False

        # Decode URL encoding (handle double encoding)
        decoded_path = path
        for _ in range(3):  # Handle up to triple encoding
            try:
                new_decoded = urllib.parse.unquote(decoded_path)
                if new_decoded == decoded_path:
                    break
                decoded_path = new_decoded
            except Exception:
                return False

        # Check for null bytes
        if "\x00" in decoded_path or "%00" in path.lower():
            return False

        # Check for dangerous patterns in decoded path
        dangerous_patterns = [
            "..",  # Parent directory
            "~",  # Home directory
        ]

        # Normalize path separators
        normalized = decoded_path.replace("\\", "/")

        for pattern in dangerous_patterns:
            if pattern in normalized:
                return False

        # Check for absolute paths (Unix and Windows)
        try:
            pure_path = PurePath(decoded_path)
            if pure_path.is_absolute():
                return False
        except Exception:
            return False

        # Check for Windows drive letters (e.g., C:)
        if len(decoded_path) >= 2 and decoded_path[1] == ":":
            if decoded_path[0].isalpha():
                return False

        # Check for UNC paths (\\\\server\\share)
        if decoded_path.startswith("\\\\") or decoded_path.startswith("//"):
            return False

        # Additional check: ensure no path traversal after normalization
        parts = [p for p in normalized.split("/") if p]
        depth = 0
        for part in parts:
            if part == "..":
                depth -= 1
                if depth < 0:
                    return False
            elif part != ".":
                depth += 1

        return True

    def create_note(
        self,
        path: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        overwrite: bool = False,
    ) -> NoteResult:
        """Create a new note.

        Args:
            path: Relative path for the note
            content: Note content
            metadata: Optional metadata for the note
            overwrite: Whether to overwrite existing note

        Returns:
            NoteResult with operation status
        """
        # Validate path
        if not self.is_valid_path(path):
            return NoteResult(
                success=False,
                path=path,
                message="Invalid path: path traversal not allowed",
            )

        # Check if note exists
        if self._vault.note_exists(path) and not overwrite:
            return NoteResult(
                success=False,
                path=path,
                message=f"Note already exists: {path}. Use overwrite=True to replace.",
            )

        try:
            from markwritter.obsidian.models import Note

            note = Note(
                path=path,
                content=content,
                metadata=metadata or {},
            )
            self._vault.write_note(note, overwrite=overwrite)

            return NoteResult(
                success=True,
                path=path,
                message="Note created successfully",
            )
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            return NoteResult(
                success=False,
                path=path,
                message=str(e),
            )

    def update_note(
        self,
        path: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        mode: str = "replace",
    ) -> NoteResult:
        """Update an existing note.

        Args:
            path: Relative path for the note
            content: Note content
            metadata: Optional metadata to merge
            mode: Update mode (replace, append, prepend)

        Returns:
            NoteResult with operation status
        """
        # Validate path
        if not self.is_valid_path(path):
            return NoteResult(
                success=False,
                path=path,
                message="Invalid path: path traversal not allowed",
            )

        # Check if note exists
        if not self._vault.note_exists(path):
            return NoteResult(
                success=False,
                path=path,
                message=f"Note not found: {path}",
            )

        try:
            from markwritter.obsidian.models import Note

            # Handle different update modes
            if mode == "append":
                existing = self._vault.read_note(path)
                new_content = existing.content + "\n\n" + content
            elif mode == "prepend":
                existing = self._vault.read_note(path)
                new_content = content + "\n\n" + existing.content
            else:  # replace
                new_content = content

            # Merge metadata
            if metadata:
                existing = self._vault.read_note(path)
                merged_metadata = {**existing.metadata, **metadata}
            else:
                merged_metadata = metadata or {}

            note = Note(
                path=path,
                content=new_content,
                metadata=merged_metadata,
            )
            self._vault.write_note(note, overwrite=True)

            return NoteResult(
                success=True,
                path=path,
                message="Note updated successfully",
            )
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            return NoteResult(
                success=False,
                path=path,
                message=str(e),
            )

    def delete_note(self, path: str) -> NoteResult:
        """Delete a note.

        Args:
            path: Relative path for the note

        Returns:
            NoteResult with operation status
        """
        # Validate path
        if not self.is_valid_path(path):
            return NoteResult(
                success=False,
                path=path,
                message="Invalid path: path traversal not allowed",
            )

        # Check if note exists
        if not self._vault.note_exists(path):
            return NoteResult(
                success=False,
                path=path,
                message=f"Note not found: {path}",
            )

        try:
            self._vault.delete_note(path)
            return NoteResult(
                success=True,
                path=path,
                message="Note deleted successfully",
            )
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return NoteResult(
                success=False,
                path=path,
                message=str(e),
            )

    def read_note(self, path: str) -> Optional[Any]:
        """Read a note.

        Args:
            path: Relative path for the note

        Returns:
            Note object or None if not found
        """
        # Validate path
        if not self.is_valid_path(path):
            return None

        try:
            return self._vault.read_note(path)
        except Exception:
            return None