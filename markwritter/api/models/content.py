"""Content API request and response models.

Pydantic models for the unified content API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from markwritter.storage.models import Content, ContentRef, ContentType, StorageBackend


# ==============================================================================
# Request Models
# ==============================================================================


class IngestRequest(BaseModel):
    """Request model for content ingestion.

    Attributes:
        source: Source URL or file path to ingest.
        tags: Optional tags to apply to the content.
        metadata: Optional additional metadata.
    """

    source: str = Field(..., min_length=1, description="Source URL or file path to ingest")
    tags: list[str] = Field(default_factory=list, description="Tags to apply")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate source is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("source cannot be empty or whitespace")
        return v.strip()


class ContentQueryRequest(BaseModel):
    """Request model for content queries.

    Attributes:
        query: Search query string.
        tags: Filter by tags.
        content_types: Filter by content types.
        limit: Maximum results.
        offset: Pagination offset.
    """

    query: Optional[str] = Field(None, description="Search query")
    tags: list[str] = Field(default_factory=list, description="Filter by tags")
    content_types: list[ContentType] = Field(
        default_factory=list, description="Filter by content types"
    )
    limit: int = Field(100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(0, ge=0, description="Pagination offset")


# ==============================================================================
# Response Models
# ==============================================================================


class IngestResponse(BaseModel):
    """Response model for content ingestion.

    Attributes:
        success: Whether ingestion succeeded.
        content_id: ID of ingested content (if successful).
        content: Content reference (if successful).
        error: Error message (if failed).
        warnings: Warning messages.
        bytes_processed: Number of bytes processed.
        processing_time_ms: Processing time in milliseconds.
    """

    success: bool
    content_id: Optional[str] = None
    content: Optional[ContentRef] = None
    error: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    bytes_processed: int = 0
    processing_time_ms: float = 0.0


class ContentListResponse(BaseModel):
    """Response model for content list.

    Attributes:
        items: List of content references.
        total: Total number of matching items.
        limit: Requested limit (must be >= 1).
        offset: Requested offset (must be >= 0).
    """

    items: list[ContentRef]
    total: int
    limit: int = Field(..., ge=1, description="Maximum results per page")
    offset: int = Field(..., ge=0, description="Pagination offset")

    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.offset + len(self.items) < self.total


class ContentResponse(BaseModel):
    """Response model for single content.

    Attributes:
        content: Full content object.
    """

    content: Content


class ContentDeleteResponse(BaseModel):
    """Response model for content deletion.

    Attributes:
        success: Whether deletion succeeded.
        content_id: ID of deleted content.
    """

    success: bool
    content_id: str


__all__ = [
    "IngestRequest",
    "ContentQueryRequest",
    "IngestResponse",
    "ContentListResponse",
    "ContentResponse",
    "ContentDeleteResponse",
]
