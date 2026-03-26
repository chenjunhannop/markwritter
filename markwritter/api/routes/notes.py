"""Notes API routes.

Provides endpoints for managing Obsidian notes through the API.

Phase 2.1: RESTful endpoints with real vault integration.
- POST /notes - Create a new note (returns 201)
- PUT /notes/{note_path} - Update an existing note
- GET /notes - List notes
- GET /notes/{note_path} - Get a specific note
- DELETE /notes/{note_path} - Delete a note
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

router = APIRouter()

# Global vault instance (set by dependency injection or initialization)
_vault: Optional[Any] = None  # ObsidianVault


def init_notes_routes(vault: Optional[Any] = None) -> None:
    """Initialize notes routes with dependencies.

    Args:
        vault: ObsidianVault instance
    """
    global _vault
    _vault = vault


# ==============================================================================
# Helper Functions
# ==============================================================================


def _is_safe_path(path: str) -> bool:
    """Check if a path is safe (no path traversal).

    Args:
        path: Path to check

    Returns:
        True if path is safe
    """
    import urllib.parse
    from pathlib import PurePath

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

    # Check for UNC paths (\\server\share)
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


# ==============================================================================
# Response Models
# ==============================================================================


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

    path: str = Field(..., description="Relative path for the note")
    content: str = Field(..., description="Note content")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Note metadata")
    overwrite: bool = Field(default=False, description="Overwrite if exists")


class NoteCreateResponse(BaseModel):
    """Response model for note creation."""

    success: bool
    path: str
    message: Optional[str] = None


class NoteUpdateRequest(BaseModel):
    """Request model for updating a note."""

    content: Optional[str] = Field(default=None, description="Note content")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Note metadata")
    mode: str = Field(default="replace", description="Update mode: replace, append, prepend")


class NoteUpdateResponse(BaseModel):
    """Response model for note update."""

    success: bool
    path: str
    message: Optional[str] = None


# ==============================================================================
# Endpoints
# ==============================================================================


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
    if not _vault:
        # Return empty list if vault not configured
        return NoteListResponse(notes=[], total=0)

    try:
        # Get notes from vault
        notes = _vault.list_notes(
            directory=directory,
            recursive=recursive,
            tag=tag,
            limit=limit,
        )
        return NoteListResponse(
            notes=[{"path": n.path, "title": n.title} for n in notes],
            total=len(notes),
        )
    except Exception:
        # Return empty list on error
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
    if not _vault:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not configured",
        )

    # Validate path
    if not _is_safe_path(note_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid path: path traversal not allowed",
        )

    # Check if note exists
    if not _vault.note_exists(note_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note not found: {note_path}",
        )

    try:
        note = _vault.read_note(note_path)
        return NoteResponse(
            path=note.path,
            title=note.metadata.get("title", note.path.split("/")[-1].replace(".md", "")),
            content=note.content,
            metadata=note.metadata,
            tags=note.metadata.get("tags", []),
            links=[],  # TODO: Extract links from content
            backlinks=[],  # TODO: Get from graph
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/notes",
    response_model=NoteCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
    description="Create a new note in the vault. Returns 201 on success.",
)
async def create_note(
    request: NoteCreateRequest,
    response: Response,
) -> NoteCreateResponse:
    """Create a new note.

    Args:
        request: Note creation request
        response: FastAPI response object

    Returns:
        Created note info with 201 status code

    Raises:
        HTTPException: If note already exists and overwrite=False
    """
    if not _vault:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not configured",
        )

    # Validate path
    if not _is_safe_path(request.path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid path: path traversal not allowed",
        )

    # Check if note exists
    if _vault.note_exists(request.path) and not request.overwrite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Note already exists: {request.path}. Use overwrite=true to replace.",
        )

    try:
        from markwritter.obsidian.models import Note

        note = Note(
            path=request.path,
            content=request.content,
            metadata=request.metadata,
        )
        _vault.write_note(note, overwrite=request.overwrite)

        return NoteCreateResponse(
            success=True,
            path=request.path,
            message="Note created successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/notes/{note_path:path}",
    response_model=NoteUpdateResponse,
    summary="Update a note",
    description="Update an existing note. Path is taken from URL.",
)
async def update_note(
    note_path: str,
    request: NoteUpdateRequest,
) -> NoteUpdateResponse:
    """Update an existing note.

    Args:
        note_path: Path to the note (from URL)
        request: Update request

    Returns:
        Updated note info

    Raises:
        HTTPException: If note not found
    """
    if not _vault:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not configured",
        )

    # Validate path
    if not _is_safe_path(note_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid path: path traversal not allowed",
        )

    # Check if note exists
    if not _vault.note_exists(note_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note not found: {note_path}",
        )

    try:
        from markwritter.obsidian.models import Note

        existing = _vault.read_note(note_path)

        # Handle content update
        if request.content is not None:
            if request.mode == "append":
                new_content = existing.content + "\n\n" + request.content
            elif request.mode == "prepend":
                new_content = request.content + "\n\n" + existing.content
            else:  # replace
                new_content = request.content
        else:
            new_content = existing.content

        # Handle metadata update
        if request.metadata:
            merged_metadata = {**existing.metadata, **request.metadata}
        else:
            merged_metadata = existing.metadata

        note = Note(
            path=note_path,
            content=new_content,
            metadata=merged_metadata,
        )
        _vault.write_note(note, overwrite=True)

        return NoteUpdateResponse(
            success=True,
            path=note_path,
            message="Note updated successfully",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
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
    if not _vault:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not configured",
        )

    # Validate path
    if not _is_safe_path(note_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid path: path traversal not allowed",
        )

    # Check if note exists
    if not _vault.note_exists(note_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note not found: {note_path}",
        )

    try:
        _vault.delete_note(note_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )