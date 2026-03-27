"""Storage models for content abstraction.

This module defines the core data models for the storage abstraction layer:
- ContentType: Enum for supported content types
- StorageBackend: Enum for storage backends
- ContentRef: Lightweight reference to content
- Content: Full content representation
- ContentQuery: Query parameters for listing content
- ContentListResult: Paginated result of content listing
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from markwritter.obsidian.models import Note


class ContentType(str, Enum):
    """Supported content types."""

    MARKDOWN = "markdown"
    PDF = "pdf"
    URL = "url"
    IMAGE = "image"
    HTML = "html"
    PLAINTEXT = "plaintext"


class StorageBackend(str, Enum):
    """Supported storage backends."""

    OBSIDIAN = "obsidian"
    DATABASE = "database"
    OBJECT_STORE = "object_store"


class ContentRef(BaseModel):
    """Lightweight reference to content.

    Used for listing and search results where full content is not needed.
    """

    id: str
    source_type: ContentType
    storage_backend: StorageBackend
    title: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)
    path: Optional[str] = None


class Content(BaseModel):
    """Full content representation.

    Contains all data including text content, metadata, links, and backlinks.
    """

    id: str
    source_type: ContentType
    storage_backend: StorageBackend
    text_content: Optional[str] = None
    raw_content: Optional[bytes] = None
    title: Optional[str] = None
    source_path: Optional[str] = None
    source_url: Optional[str] = None
    storage_path: Optional[str] = None
    metadata: dict[str, object] = Field(default_factory=dict)
    links: list[str] = Field(default_factory=list)
    backlinks: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    content_hash: Optional[str] = None
    mime_type: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    indexed_at: Optional[datetime] = None

    def to_ref(self) -> ContentRef:
        """Convert to lightweight ContentRef.

        Returns:
            ContentRef with basic info
        """
        return ContentRef(
            id=self.id,
            source_type=self.source_type,
            storage_backend=self.storage_backend,
            title=self.title,
            created=self.created,
            modified=self.modified,
            tags=self.tags,
            path=self.source_path,
        )

    @classmethod
    def from_obsidian_note(cls, note: "Note") -> "Content":
        """Create Content from Obsidian Note model.

        Args:
            note: Obsidian Note object

        Returns:
            Content instance with data from note
        """
        # Import here to avoid circular imports
        from markwritter.obsidian.models import Note as ObsidianNote

        if not isinstance(note, ObsidianNote):
            raise TypeError(f"Expected Note, got {type(note)}")

        # Extract tags from metadata
        metadata_tags = note.metadata.get("tags", [])
        if isinstance(metadata_tags, str):
            tags = [metadata_tags]
        else:
            tags = list(metadata_tags) if metadata_tags else []

        return cls(
            id=note.path,
            source_type=ContentType.MARKDOWN,
            storage_backend=StorageBackend.OBSIDIAN,
            text_content=note.content,
            title=note.title,
            source_path=note.path,
            metadata=dict(note.metadata),
            links=list(note.links),
            backlinks=list(note.backlinks),
            tags=tags,
            created=note.created,
            modified=note.modified,
        )


class ContentQuery(BaseModel):
    """Query parameters for listing content."""

    query: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    source_types: list[ContentType] = Field(default_factory=list)
    storage_backends: list[StorageBackend] = Field(default_factory=list)
    path_prefix: Optional[str] = None
    limit: int = Field(default=100, ge=0)
    offset: int = Field(default=0, ge=0)


class ContentListResult(BaseModel):
    """Paginated result of content listing."""

    items: list[ContentRef]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Check if there are more results.

        Returns:
            True if there are more results available
        """
        return self.offset + len(self.items) < self.total


__all__ = [
    "ContentType",
    "StorageBackend",
    "ContentRef",
    "Content",
    "ContentQuery",
    "ContentListResult",
]
