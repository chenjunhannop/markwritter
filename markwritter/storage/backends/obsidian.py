"""Obsidian storage backend adapter.

This module provides ObsidianRepository, which wraps the existing
ObsidianVault class to implement the ContentRepository protocol.
"""

from pathlib import Path
from typing import Optional

from markwritter.exceptions import InvalidVaultError
from markwritter.obsidian.models import Note
from markwritter.obsidian.vault import ObsidianVault
from markwritter.storage.base import StorageError
from markwritter.storage.models import (
    Content,
    ContentListResult,
    ContentQuery,
    ContentRef,
    ContentType,
    StorageBackend,
)


class ObsidianRepository:
    """Adapter that wraps ObsidianVault to implement ContentRepository.

    This class translates between the generic Content model and
    the Obsidian-specific Note model, allowing Obsidian vaults
    to be used through the storage abstraction layer.
    """

    def __init__(
        self,
        vault_path: Optional[Path | str] = None,
        vault: Optional[ObsidianVault] = None,
    ):
        """Initialize Obsidian repository.

        Args:
            vault_path: Path to Obsidian vault
            vault: Existing ObsidianVault instance (takes precedence)

        Raises:
            StorageError: If neither vault_path nor vault is provided
        """
        if vault is not None:
            self._vault = vault
        elif vault_path is not None:
            try:
                self._vault = ObsidianVault(vault_path)
            except InvalidVaultError as e:
                raise StorageError(str(e)) from e
        else:
            raise StorageError("Either vault_path or vault must be provided")

    @property
    def backend_type(self) -> StorageBackend:
        """Return OBSIDIAN backend type."""
        return StorageBackend.OBSIDIAN

    @property
    def supported_content_types(self) -> list[ContentType]:
        """Return supported content types (only MARKDOWN for Obsidian)."""
        return [ContentType.MARKDOWN]

    async def get(self, content_id: str) -> Content | None:
        """Get content by ID (note path).

        Args:
            content_id: Path to the note relative to vault root

        Returns:
            Content object if found, None otherwise
        """
        try:
            note = self._vault.read_note(content_id)
            return Content.from_obsidian_note(note)
        except Exception:
            return None

    async def get_by_path(self, path: str) -> Content | None:
        """Get content by path (alias for get).

        Args:
            path: Path to the note

        Returns:
            Content object if found, None otherwise
        """
        return await self.get(path)

    async def list(self, query: ContentQuery) -> ContentListResult:
        """List content matching query parameters.

        Args:
            query: Query parameters for filtering

        Returns:
            Paginated result with ContentRef items
        """
        # Get all notes first (we'll filter in memory for now)
        # TODO: Optimize for large vaults with indexing
        all_notes = self._vault.list_notes(
            directory=query.path_prefix.rstrip("/") if query.path_prefix else None,
            recursive=True,
        )

        # Filter by keyword query
        if query.query:
            matching_paths = {
                m.path for m in self._vault.search_by_keyword(query.query)
            }
            all_notes = [n for n in all_notes if n.path in matching_paths]

        # Filter by tags
        if query.tags:
            all_notes = [
                n
                for n in all_notes
                if any(tag in n.tags for tag in query.tags)
            ]

        # Convert to ContentRef
        refs = []
        for note_meta in all_notes:
            ref = ContentRef(
                id=note_meta.path,
                source_type=ContentType.MARKDOWN,
                storage_backend=StorageBackend.OBSIDIAN,
                title=note_meta.title,
                created=note_meta.created,
                modified=note_meta.modified,
                tags=note_meta.tags,
                path=note_meta.path,
            )
            refs.append(ref)

        # Sort by path for consistent ordering
        refs.sort(key=lambda r: r.id)

        # Apply pagination
        total = len(refs)
        paginated_refs = refs[query.offset : query.offset + query.limit]

        return ContentListResult(
            items=paginated_refs,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )

    async def save(self, content: Content) -> Content:
        """Save content to the vault.

        Args:
            content: Content to save

        Returns:
            Saved content object
        """
        # Convert Content to Note
        note = Note(
            path=content.id,
            content=content.text_content or "",
            metadata={
                **content.metadata,
                "title": content.title,
                "tags": content.tags,
            },
            links=content.links,
            backlinks=content.backlinks,
            created=content.created,
            modified=content.modified,
        )

        # Write to vault
        self._vault.write_note(note, overwrite=True)

        # Return the saved content
        return await self.get(content.id) or content

    async def delete(self, content_id: str) -> bool:
        """Delete content by ID.

        Args:
            content_id: Path to the note to delete

        Returns:
            True if deleted, False if not found
        """
        if not await self.exists(content_id):
            return False

        try:
            self._vault.delete_note(content_id)
            return True
        except Exception:
            return False

    async def exists(self, content_id: str) -> bool:
        """Check if content exists.

        Args:
            content_id: Path to check

        Returns:
            True if note exists, False otherwise
        """
        return self._vault.note_exists(content_id)


__all__ = ["ObsidianRepository"]
