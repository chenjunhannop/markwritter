"""Content API routes.

Provides unified endpoints for content management across multiple backends
(Obsidian, Database, Object Store).

Phase 4: API integration with new storage system.
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from markwritter.api.models.content import (
    ContentDeleteResponse,
    ContentListResponse,
    ContentResponse,
    IngestRequest,
    IngestResponse,
)
from markwritter.storage import Content, ContentQuery, ContentType
from markwritter.storage.models import ContentRef
from markwritter.storage.ingestion import ContentIngestResult, IngestionPipeline

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (set by dependency injection)
_ingestion_pipeline: Optional[IngestionPipeline] = None
# In-memory storage for demo (replace with real registry in production)
_content_store: dict[str, Content] = {}


def init_content_routes() -> None:
    """Initialize content routes."""
    global _ingestion_pipeline
    _ingestion_pipeline = IngestionPipeline()


def _get_pipeline() -> IngestionPipeline:
    """Get ingestion pipeline (creates if needed)."""
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        _ingestion_pipeline = IngestionPipeline()
    return _ingestion_pipeline


# ==============================================================================
# Content Ingestion
# ==============================================================================


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Ingest content",
    description="Ingest content from URL, file path, or other source",
)
async def ingest_content(request: IngestRequest) -> IngestResponse:
    """Ingest content from a source.

    Args:
        request: Ingestion request with source and options

    Returns:
        Ingestion result with content ID and metadata
    """
    start_time = time.time()

    try:
        pipeline = _get_pipeline()

        # Ingest using pipeline
        result = await pipeline.ingest(request.source)

        if not result.success:
            return IngestResponse(
                success=False,
                error=result.error,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        content_ref: Optional[ContentRef] = None

        # Apply tags and metadata
        if result.content:
            if request.tags:
                result.content.tags = list(set(result.content.tags + request.tags))
            if request.metadata:
                result.content.metadata = {**result.content.metadata, **request.metadata}

            # Generate ID if not set
            if not result.content.id:
                result.content.id = str(uuid.uuid4())

            # Store content
            _content_store[result.content.id] = result.content

            # Build ContentRef for response
            content_ref = result.content.to_ref()
            bytes_processed = len(result.content.text_content.encode("utf-8")) if result.content.text_content else 0
        else:
            bytes_processed = 0

        return IngestResponse(
            success=True,
            content_id=result.content.id if result.content else None,
            content=content_ref,
            warnings=result.warnings,
            bytes_processed=bytes_processed,
            processing_time_ms=(time.time() - start_time) * 1000,
        )

    except Exception as e:
        logger.exception("Ingestion failed for %s", request.source)
        return IngestResponse(
            success=False,
            error=str(e),
            processing_time_ms=(time.time() - start_time) * 1000,
        )


# ==============================================================================
# Content Search (MUST be before /{content_id})
# ==============================================================================


@router.get(
    "/search",
    summary="Search content",
    description="Full-text search across all content",
)
async def search_content(
    q: str = Query(..., description="Search query", min_length=1),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
):
    """Search content by keyword.

    Args:
        q: Search query
        limit: Maximum results

    Returns:
        List of matching content references
    """
    results = []
    query_lower = q.lower()

    for content in _content_store.values():
        # Search in title and text content
        if (content.title and query_lower in content.title.lower()) or \
           (content.text_content and query_lower in content.text_content.lower()):
            results.append(content.to_ref())

        if len(results) >= limit:
            break

    return {
        "query": q,
        "items": results,
        "total": len(results),
    }


# ==============================================================================
# Content List
# ==============================================================================


@router.get(
    "",
    response_model=ContentListResponse,
    summary="List content",
    description="List all content with optional filtering",
)
async def list_content(
    content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
) -> ContentListResponse:
    """List content with optional filtering.

    Args:
        content_type: Filter by content type
        tag: Filter by tag
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        Paginated list of content
    """
    # Filter content
    items: list[ContentRef] = []
    for content in _content_store.values():
        # Apply filters
        if content_type and content.source_type != content_type:
            continue
        if tag and tag not in content.tags:
            continue

        items.append(content.to_ref())

    # Apply pagination
    total = len(items)
    paginated = items[offset:offset + limit]

    return ContentListResponse(
        items=paginated,
        total=total,
        limit=limit,
        offset=offset,
    )


# ==============================================================================
# Content CRUD (with path parameters)
# ==============================================================================


@router.get(
    "/{content_id}",
    response_model=ContentResponse,
    summary="Get content",
    description="Get a specific content by ID",
)
async def get_content(content_id: str) -> ContentResponse:
    """Get content by ID.

    Args:
        content_id: Content ID to retrieve

    Returns:
        Content details

    Raises:
        HTTPException: If content not found
    """
    content = _content_store.get(content_id)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content not found: {content_id}",
        )

    return ContentResponse(content=content)


@router.delete(
    "/{content_id}",
    response_model=ContentDeleteResponse,
    summary="Delete content",
    description="Delete content by ID",
)
async def delete_content(content_id: str) -> ContentDeleteResponse:
    """Delete content by ID.

    Args:
        content_id: Content ID to delete

    Returns:
        Deletion result

    Raises:
        HTTPException: If content not found
    """
    if content_id not in _content_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Content not found: {content_id}",
        )

    del _content_store[content_id]

    return ContentDeleteResponse(success=True, content_id=content_id)


__all__ = ["router", "init_content_routes"]
