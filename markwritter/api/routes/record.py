"""Record API routes.

Provides endpoints for note creation, update, and AI assistance.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from markwritter.record.assistant import AutoClassifier, ClassifyResult, WritingAssistant

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (set by dependency injection or initialization)
_vault: Optional[Any] = None  # ObsidianVault
_writing_assistant: Optional[WritingAssistant] = None
_auto_classifier: Optional[AutoClassifier] = None


def init_record_routes(
    vault: Optional[Any] = None,
    writing_assistant: Optional[WritingAssistant] = None,
    auto_classifier: Optional[AutoClassifier] = None,
) -> None:
    """Initialize record routes with dependencies.

    Args:
        vault: ObsidianVault instance
        writing_assistant: WritingAssistant instance
        auto_classifier: AutoClassifier instance
    """
    global _vault, _writing_assistant, _auto_classifier
    _vault = vault
    _writing_assistant = writing_assistant
    _auto_classifier = auto_classifier


# ==============================================================================
# Request/Response Models
# ==============================================================================


class CreateNoteRequest(BaseModel):
    """Request model for creating a note."""

    path: str = Field(..., description="Relative path for the note")
    content: str = Field(..., description="Note content")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Note metadata")
    overwrite: bool = Field(default=False, description="Overwrite if exists")


class CreateNoteResponse(BaseModel):
    """Response model for note creation."""

    success: bool
    path: str
    message: Optional[str] = None


class UpdateNoteRequest(BaseModel):
    """Request model for updating a note."""

    path: str = Field(..., description="Relative path for the note")
    content: str = Field(..., description="Note content")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Note metadata")
    mode: str = Field(default="replace", description="Update mode: replace, append, prepend")


class UpdateNoteResponse(BaseModel):
    """Response model for note update."""

    success: bool
    path: str
    message: Optional[str] = None


class ContinueWritingRequest(BaseModel):
    """Request model for continue writing."""

    content: str = Field(..., description="Content to continue from")
    max_tokens: Optional[int] = Field(default=500, description="Max tokens for continuation")


class ContinueWritingResponse(BaseModel):
    """Response model for continue writing."""

    continuation: str
    original_length: int


class RewriteRequest(BaseModel):
    """Request model for rewrite."""

    content: str = Field(..., description="Content to rewrite")
    style: str = Field(default="formal", description="Target style")
    max_tokens: Optional[int] = Field(default=500, description="Max tokens for output")


class RewriteResponse(BaseModel):
    """Response model for rewrite."""

    rewritten: str
    style: str


class PolishRequest(BaseModel):
    """Request model for polish."""

    content: str = Field(..., description="Content to polish")
    max_tokens: Optional[int] = Field(default=500, description="Max tokens for output")


class PolishResponse(BaseModel):
    """Response model for polish."""

    polished: str


class ClassifyRequest(BaseModel):
    """Request model for classification."""

    content: str = Field(..., description="Content to classify")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="Existing metadata")


class ClassifyResponse(BaseModel):
    """Response model for classification."""

    category: str
    confidence: float
    reasoning: Optional[str] = None


class SuggestTagsRequest(BaseModel):
    """Request model for tag suggestion."""

    content: str = Field(..., description="Content to analyze")
    existing_tags: Optional[list[str]] = Field(default=None, description="Existing tags")
    max_tags: int = Field(default=5, ge=1, le=10, description="Max tags to return")


class SuggestTagsResponse(BaseModel):
    """Response model for tag suggestion."""

    tags: list[str]


class SuggestFolderRequest(BaseModel):
    """Request model for folder suggestion."""

    content: str = Field(..., description="Content to analyze")
    existing_folders: Optional[list[str]] = Field(default=None, description="Existing folders")


class SuggestFolderResponse(BaseModel):
    """Response model for folder suggestion."""

    folder: str


class SuggestLinksRequest(BaseModel):
    """Request model for link suggestion."""

    content: str = Field(..., description="Content to analyze")
    existing_notes: list[str] = Field(default_factory=list, description="Existing notes")
    max_links: int = Field(default=5, ge=1, le=10, description="Max links to return")


class SuggestLinksResponse(BaseModel):
    """Response model for link suggestion."""

    links: list[str]


# ==============================================================================
# Create/Update Note Endpoints
# ==============================================================================


@router.post(
    "/create",
    response_model=CreateNoteResponse,
    summary="Create a new note",
    description="Create a new note in the vault",
)
async def create_note(request: CreateNoteRequest) -> CreateNoteResponse:
    """Create a new note.

    Args:
        request: Note creation request

    Returns:
        Creation result
    """
    if not _vault:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vault not configured",
        )

    # Validate path (prevent path traversal)
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
            metadata=request.metadata or {},
        )
        _vault.write_note(note, overwrite=request.overwrite)

        return CreateNoteResponse(
            success=True,
            path=request.path,
            message="Note created successfully",
        )
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/update",
    response_model=UpdateNoteResponse,
    summary="Update an existing note",
    description="Update an existing note in the vault",
)
async def update_note(request: UpdateNoteRequest) -> UpdateNoteResponse:
    """Update an existing note.

    Args:
        request: Note update request

    Returns:
        Update result
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
    if not _vault.note_exists(request.path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note not found: {request.path}",
        )

    try:
        from markwritter.obsidian.models import Note

        # Handle different update modes
        if request.mode == "append":
            existing = _vault.read_note(request.path)
            new_content = existing.content + "\n\n" + request.content
        elif request.mode == "prepend":
            existing = _vault.read_note(request.path)
            new_content = request.content + "\n\n" + existing.content
        else:  # replace
            new_content = request.content

        # Merge metadata
        if request.metadata:
            existing = _vault.read_note(request.path)
            merged_metadata = {**existing.metadata, **request.metadata}
        else:
            merged_metadata = request.metadata or {}

        note = Note(
            path=request.path,
            content=new_content,
            metadata=merged_metadata,
        )
        _vault.write_note(note, overwrite=True)

        return UpdateNoteResponse(
            success=True,
            path=request.path,
            message="Note updated successfully",
        )
    except Exception as e:
        logger.error(f"Error updating note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


def _is_safe_path(path: str) -> bool:
    """Check if a path is safe (no path traversal).

    Uses pathlib.Path.resolve() for robust path validation.

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
    if '\x00' in decoded_path or '%00' in path.lower():
        return False

    # Check for dangerous patterns in decoded path
    dangerous_patterns = [
        '..',  # Parent directory
        '~',   # Home directory
    ]

    # Normalize path separators
    normalized = decoded_path.replace('\\', '/')

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
    if len(decoded_path) >= 2 and decoded_path[1] == ':':
        if decoded_path[0].isalpha():
            return False

    # Check for UNC paths (\\server\share)
    if decoded_path.startswith('\\\\') or decoded_path.startswith('//'):
        return False

    # Additional check: ensure no path traversal after normalization
    # This catches cases like "folder/../../../etc/passwd"
    parts = [p for p in normalized.split('/') if p]
    depth = 0
    for part in parts:
        if part == '..':
            depth -= 1
            if depth < 0:
                return False
        elif part != '.':
            depth += 1

    return True


# ==============================================================================
# AI Assistance Endpoints
# ==============================================================================


@router.post(
    "/ai-assist/continue",
    response_model=ContinueWritingResponse,
    summary="Continue writing",
    description="Generate a continuation of the provided text",
)
async def continue_writing(request: ContinueWritingRequest) -> ContinueWritingResponse:
    """Continue writing from given content.

    Args:
        request: Continue writing request

    Returns:
        Continuation text
    """
    if not _writing_assistant:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Writing assistant not configured",
        )

    try:
        continuation = _writing_assistant.continue_writing(
            content=request.content,
            max_tokens=request.max_tokens,
        )

        return ContinueWritingResponse(
            continuation=continuation,
            original_length=len(request.content),
        )
    except Exception as e:
        logger.error(f"Error in continue_writing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/ai-assist/continue/stream",
    summary="Continue writing with streaming",
    description="Generate a continuation with streaming output",
)
async def continue_writing_stream(request: ContinueWritingRequest) -> StreamingResponse:
    """Continue writing with streaming output.

    Args:
        request: Continue writing request

    Returns:
        Streaming response
    """
    if not _writing_assistant:
        async def error_stream():
            yield f"data: {json.dumps({'error': 'Writing assistant not configured'})}\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
        )

    async def generate_stream():
        try:
            async for chunk in _writing_assistant.continue_writing_stream(
                content=request.content,
                max_tokens=request.max_tokens,
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
    )


@router.post(
    "/ai-assist/rewrite",
    response_model=RewriteResponse,
    summary="Rewrite text",
    description="Rewrite text in a different style",
)
async def rewrite(request: RewriteRequest) -> RewriteResponse:
    """Rewrite content in a different style.

    Args:
        request: Rewrite request

    Returns:
        Rewritten text
    """
    if not _writing_assistant:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Writing assistant not configured",
        )

    try:
        rewritten = _writing_assistant.rewrite(
            content=request.content,
            style=request.style,
            max_tokens=request.max_tokens,
        )

        return RewriteResponse(
            rewritten=rewritten,
            style=request.style,
        )
    except Exception as e:
        logger.error(f"Error in rewrite: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/ai-assist/polish",
    response_model=PolishResponse,
    summary="Polish text",
    description="Improve grammar, clarity, and flow",
)
async def polish(request: PolishRequest) -> PolishResponse:
    """Polish content for better quality.

    Args:
        request: Polish request

    Returns:
        Polished text
    """
    if not _writing_assistant:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Writing assistant not configured",
        )

    try:
        polished = _writing_assistant.polish(
            content=request.content,
            max_tokens=request.max_tokens,
        )

        return PolishResponse(polished=polished)
    except Exception as e:
        logger.error(f"Error in polish: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==============================================================================
# Classification Endpoints
# ==============================================================================


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    summary="Classify content",
    description="Automatically classify content into a category",
)
async def classify(request: ClassifyRequest) -> ClassifyResponse:
    """Classify content into a category.

    Args:
        request: Classification request

    Returns:
        Classification result
    """
    if not _auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        result = _auto_classifier.classify(
            content=request.content,
            metadata=request.metadata,
        )

        return ClassifyResponse(
            category=result.category,
            confidence=result.confidence,
            reasoning=result.reasoning,
        )
    except Exception as e:
        logger.error(f"Error in classify: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/suggest/tags",
    response_model=SuggestTagsResponse,
    summary="Suggest tags",
    description="Suggest relevant tags for content",
)
async def suggest_tags(request: SuggestTagsRequest) -> SuggestTagsResponse:
    """Suggest tags for content.

    Args:
        request: Tag suggestion request

    Returns:
        Suggested tags
    """
    if not _auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        tags = _auto_classifier.suggest_tags(
            content=request.content,
            existing_tags=request.existing_tags,
            max_tags=request.max_tags,
        )

        return SuggestTagsResponse(tags=tags)
    except Exception as e:
        logger.error(f"Error in suggest_tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/suggest/folder",
    response_model=SuggestFolderResponse,
    summary="Suggest folder",
    description="Suggest a folder path for the note",
)
async def suggest_folder(request: SuggestFolderRequest) -> SuggestFolderResponse:
    """Suggest a folder for the note.

    Args:
        request: Folder suggestion request

    Returns:
        Suggested folder
    """
    if not _auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        folder = _auto_classifier.suggest_folder(
            content=request.content,
            existing_folders=request.existing_folders,
        )

        return SuggestFolderResponse(folder=folder)
    except Exception as e:
        logger.error(f"Error in suggest_folder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/suggest/links",
    response_model=SuggestLinksResponse,
    summary="Suggest related notes",
    description="Suggest related notes to link to",
)
async def suggest_links(request: SuggestLinksRequest) -> SuggestLinksResponse:
    """Suggest related notes to link to.

    Args:
        request: Link suggestion request

    Returns:
        Suggested links
    """
    if not _auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        links = _auto_classifier.suggest_links(
            content=request.content,
            existing_notes=request.existing_notes,
            max_links=request.max_links,
        )

        return SuggestLinksResponse(links=links)
    except Exception as e:
        logger.error(f"Error in suggest_links: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )