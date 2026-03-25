"""Data models for Obsidian notes."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class NoteMeta(BaseModel):
    """Metadata for a note (lightweight, for listing)."""

    path: str
    title: Optional[str] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)


class Note(BaseModel):
    """Complete note model with content and metadata."""

    path: str
    content: str
    metadata: dict[str, object] = Field(default_factory=dict)
    links: list[str] = Field(default_factory=list)
    backlinks: list[str] = Field(default_factory=list)
    created: Optional[datetime] = None
    modified: Optional[datetime] = None

    @property
    def title(self) -> Optional[str]:
        """Extract title from metadata or filename."""
        if "title" in self.metadata:
            return str(self.metadata["title"])
        # Fallback to filename without extension
        return Path(self.path).stem


class Frontmatter(BaseModel):
    """Reparsed YAML frontmatter."""

    data: dict[str, object] = Field(default_factory=dict)
    content_start: int = 0  # Line number where content starts
