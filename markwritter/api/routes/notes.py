"""Notes API routes.

Provides endpoints for managing Obsidian notes through the API.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter()


class NoteResponse(BaseModel):
    """Response model for a single note."""

    path: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    backlinks: list[str] = Field(default_factory=list)


class NoteListResponse(BaseModel):
    """Response model for note list."""

    notes: list[dict[str, Any]]
    total: int


class NoteCreateRequest(BaseModel):
    """Request model for creating a note."""

    path: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    overwrite: bool = False


class NoteUpdateRequest(BaseModel):
    """Request model for updating a note."""

    content: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


@router.get(
    "/notes",
    response_model=NoteListResponse,
    summary="List all notes",
    description="List all notes in the vault with optional filtering",
)
async def list_notes(
    directory: Optional[str] = Query(None, description="Filter by directory"),
    recursive: bool = Query(True, description="Include subdirectories"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
) -> NoteListResponse:
    """List all notes in the vault.

    Args:
        directory: Optional directory filter
        recursive: Whether to include subdirectories
        tag: Optional tag filter
        limit: Maximum number of results

    Returns:
        List of notes
    """
    # This will be implemented with actual vault integration
    # For now, return empty list as placeholder
    return NoteListResponse(notes=[], total=0)


@router.get(
    "/notes/{note_path:path}",
    response_model=NoteResponse,
    summary="Get a note",
    description="Get a specific note by its path",
)
async def get_note(note_path: str) -> NoteResponse:
    """Get a specific note.

    Args:
        note_path: Path to the note

    Returns:
        Note details

    Raises:
        HTTPException: If note not found
    """
    # Placeholder - will be implemented with actual vault integration
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Note not found: {note_path}",
    )


@router.post(
    "/notes",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
    description="Create a new note in the vault",
)
async def create_note(request: NoteCreateRequest) -> NoteResponse:
    """Create a new note.

    Args:
        request: Note creation request

    Returns:
        Created note

    Raises:
        HTTPException: If note already exists and overwrite=False
    """
    # Placeholder - will be implemented with actual vault integration
    return NoteResponse(
        path=request.path,
        title=request.path.split("/")[-1].replace(".md", ""),
        content=request.content,
        metadata=request.metadata,
    )


@router.put(
    "/notes/{note_path:path}",
    response_model=NoteResponse,
    summary="Update a note",
    description="Update an existing note",
)
async def update_note(
    note_path: str,
    request: NoteUpdateRequest,
) -> NoteResponse:
    """Update an existing note.

    Args:
        note_path: Path to the note
        request: Update request

    Returns:
        Updated note

    Raises:
        HTTPException: If note not found
    """
    # Placeholder - will be implemented with actual vault integration
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Note not found: {note_path}",
    )


@router.get(
    "/notes/{note_path:path}/backlinks",
    response_model=list[str],
    summary="Get note backlinks",
    description="Get all notes that link to this note",
)
async def get_backlinks(note_path: str) -> list[str]:
    """Get backlinks for a note.

    Args:
        note_path: Path to the note

    Returns:
        List of note paths that link to this note
    """
    # Placeholder - will be implemented with actual vault integration
    return []


@router.delete(
    "/notes/{note_path:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Delete a note from the vault",
)
async def delete_note(note_path: str) -> None:
    """Delete a note.

    Args:
        note_path: Path to the note

    Raises:
        HTTPException: If note not found
    """
    # Placeholder - will be implemented with actual vault integration
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Note not found: {note_path}",
    )
