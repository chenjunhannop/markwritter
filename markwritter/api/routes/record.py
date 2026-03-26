"""Record API routes.

Provides endpoints for note creation, update, and AI assistance.

Phase 2.1: RESTful Endpoint Refactoring
- POST /notes - Create a new note (returns 201)
- PUT /notes/{note_path} - Update an existing note
- Old endpoints preserved for backward compatibility with deprecation warnings

Phase 3.4: Dependency Injection
- Uses FastAPI Depends() for dependency injection
- Backward compatible with init_record_routes() for global state
"""

from __future__ import annotations

import json
import logging
import warnings
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from markwritter.record.assistant import AutoClassifier, WritingAssistant

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (set by dependency injection or initialization)
# These are kept for backward compatibility with init_record_routes()
_vault: Optional[Any] = None  # ObsidianVault
_writing_assistant: Optional[WritingAssistant] = None
_auto_classifier: Optional[AutoClassifier] = None

# Deprecation message for old endpoints
DEPRECATION_MESSAGE = "This endpoint is deprecated. Use POST /api/v1/notes instead."
DEPRECATION_UPDATE_MESSAGE = "This endpoint is deprecated. Use PUT /api/v1/notes/{note_path} instead."


# ==============================================================================
# Dependency Injection Functions
# ==============================================================================


def get_vault() -> Optional[Any]:
    """Get the vault instance.

    Returns:
        ObsidianVault instance or None if not configured.
    """
    return _vault


def get_writing_assistant() -> Optional[WritingAssistant]:
    """Get the writing assistant instance.

    Returns:
        WritingAssistant instance or None if not configured.
    """
    return _writing_assistant


def get_auto_classifier() -> Optional[AutoClassifier]:
    """Get the auto classifier instance.

    Returns:
        AutoClassifier instance or None if not configured.
    """
    return _auto_classifier


def init_record_routes(
    vault: Optional[Any] = None,
    writing_assistant: Optional[WritingAssistant] = None,
    auto_classifier: Optional[AutoClassifier] = None,
) -> None:
    """Initialize record routes with dependencies.

    This function is kept for backward compatibility.
    New code should use dependency injection via FastAPI's dependency_overrides.

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

    path: str = Field(default="", description="Relative path for the note (ignored in new endpoint)")
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
# Helper Functions
# ==============================================================================


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
    # This catches cases like "folder/../../../etc/passwd"
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


def _add_deprecation_header(response: Response, message: str) -> Response:
    """Add deprecation warning header to response.

    Args:
        response: FastAPI response object
        message: Deprecation message

    Returns:
        Response with deprecation headers
    """
    response.headers["Deprecation"] = "true"
    response.headers["Warning"] = message
    return response


# ==============================================================================
# Deprecated Create Note Endpoint (Backward Compatibility)
# ==============================================================================


@router.post(
    "/create",
    response_model=CreateNoteResponse,
    summary="Create a new note (DEPRECATED)",
    description="DEPRECATED: Use POST /api/v1/notes instead. Create a new note in the vault",
    deprecated=True,
)
async def create_note(
    request: CreateNoteRequest,
    response: Response,
    vault: Optional[Any] = Depends(get_vault),
) -> CreateNoteResponse:
    """Create a new note (deprecated endpoint).

    This endpoint is deprecated. Use POST /api/v1/notes instead.

    Args:
        request: Note creation request
        response: FastAPI response object
        vault: Injected ObsidianVault instance

    Returns:
        Creation result
    """
    # Issue deprecation warning
    warnings.warn(
        DEPRECATION_MESSAGE,
        DeprecationWarning,
        stacklevel=2,
    )

    if not vault:
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
    if vault.note_exists(request.path) and not request.overwrite:
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
        vault.write_note(note, overwrite=request.overwrite)

        # Add deprecation header
        _add_deprecation_header(response, DEPRECATION_MESSAGE)

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


# ==============================================================================
# Deprecated Update Note Endpoint (Backward Compatibility)
# ==============================================================================


@router.put(
    "/update",
    response_model=UpdateNoteResponse,
    summary="Update an existing note (DEPRECATED)",
    description="DEPRECATED: Use PUT /api/v1/notes/{note_path} instead. Update an existing note in the vault",
    deprecated=True,
)
async def update_note(
    request: UpdateNoteRequest,
    response: Response,
    vault: Optional[Any] = Depends(get_vault),
) -> UpdateNoteResponse:
    """Update an existing note (deprecated endpoint).

    This endpoint is deprecated. Use PUT /api/v1/notes/{note_path} instead.

    Args:
        request: Note update request
        response: FastAPI response object
        vault: Injected ObsidianVault instance

    Returns:
        Update result
    """
    # Issue deprecation warning
    warnings.warn(
        DEPRECATION_UPDATE_MESSAGE,
        DeprecationWarning,
        stacklevel=2,
    )

    if not vault:
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
    if not vault.note_exists(request.path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note not found: {request.path}",
        )

    try:
        from markwritter.obsidian.models import Note

        # Handle different update modes
        if request.mode == "append":
            existing = vault.read_note(request.path)
            new_content = existing.content + "\n\n" + request.content
        elif request.mode == "prepend":
            existing = vault.read_note(request.path)
            new_content = request.content + "\n\n" + existing.content
        else:  # replace
            new_content = request.content

        # Merge metadata
        if request.metadata:
            existing = vault.read_note(request.path)
            merged_metadata = {**existing.metadata, **request.metadata}
        else:
            merged_metadata = request.metadata or {}

        note = Note(
            path=request.path,
            content=new_content,
            metadata=merged_metadata,
        )
        vault.write_note(note, overwrite=True)

        # Add deprecation header
        _add_deprecation_header(response, DEPRECATION_UPDATE_MESSAGE)

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


# ==============================================================================
# AI Assistance Endpoints
# ==============================================================================


@router.post(
    "/ai-assist/continue",
    response_model=ContinueWritingResponse,
    summary="Continue writing",
    description="Generate a continuation of the provided text",
)
async def continue_writing(
    request: ContinueWritingRequest,
    writing_assistant: Optional[WritingAssistant] = Depends(get_writing_assistant),
) -> ContinueWritingResponse:
    """Continue writing from given content.

    Args:
        request: Continue writing request
        writing_assistant: Injected WritingAssistant instance

    Returns:
        Continuation text
    """
    if not writing_assistant:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Writing assistant not configured",
        )

    try:
        continuation = writing_assistant.continue_writing(
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
async def continue_writing_stream(
    request: ContinueWritingRequest,
    writing_assistant: Optional[WritingAssistant] = Depends(get_writing_assistant),
) -> StreamingResponse:
    """Continue writing with streaming output.

    Args:
        request: Continue writing request
        writing_assistant: Injected WritingAssistant instance

    Returns:
        Streaming response
    """
    if not writing_assistant:

        async def error_stream():
            yield f"data: {json.dumps({'error': 'Writing assistant not configured'})}\n\n"

        return StreamingResponse(
            error_stream(),
            media_type="text/event-stream",
        )

    async def generate_stream():
        try:
            async for chunk in writing_assistant.continue_writing_stream(
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
async def rewrite(
    request: RewriteRequest,
    writing_assistant: Optional[WritingAssistant] = Depends(get_writing_assistant),
) -> RewriteResponse:
    """Rewrite content in a different style.

    Args:
        request: Rewrite request
        writing_assistant: Injected WritingAssistant instance

    Returns:
        Rewritten text
    """
    if not writing_assistant:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Writing assistant not configured",
        )

    try:
        rewritten = writing_assistant.rewrite(
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
async def polish(
    request: PolishRequest,
    writing_assistant: Optional[WritingAssistant] = Depends(get_writing_assistant),
) -> PolishResponse:
    """Polish content for better quality.

    Args:
        request: Polish request
        writing_assistant: Injected WritingAssistant instance

    Returns:
        Polished text
    """
    if not writing_assistant:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Writing assistant not configured",
        )

    try:
        polished = writing_assistant.polish(
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
async def classify(
    request: ClassifyRequest,
    auto_classifier: Optional[AutoClassifier] = Depends(get_auto_classifier),
) -> ClassifyResponse:
    """Classify content into a category.

    Args:
        request: Classification request
        auto_classifier: Injected AutoClassifier instance

    Returns:
        Classification result
    """
    if not auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        result = auto_classifier.classify(
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
async def suggest_tags(
    request: SuggestTagsRequest,
    auto_classifier: Optional[AutoClassifier] = Depends(get_auto_classifier),
) -> SuggestTagsResponse:
    """Suggest tags for content.

    Args:
        request: Tag suggestion request
        auto_classifier: Injected AutoClassifier instance

    Returns:
        Suggested tags
    """
    if not auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        tags = auto_classifier.suggest_tags(
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
async def suggest_folder(
    request: SuggestFolderRequest,
    auto_classifier: Optional[AutoClassifier] = Depends(get_auto_classifier),
) -> SuggestFolderResponse:
    """Suggest a folder for the note.

    Args:
        request: Folder suggestion request
        auto_classifier: Injected AutoClassifier instance

    Returns:
        Suggested folder
    """
    if not auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        folder = auto_classifier.suggest_folder(
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
async def suggest_links(
    request: SuggestLinksRequest,
    auto_classifier: Optional[AutoClassifier] = Depends(get_auto_classifier),
) -> SuggestLinksResponse:
    """Suggest related notes to link to.

    Args:
        request: Link suggestion request
        auto_classifier: Injected AutoClassifier instance

    Returns:
        Suggested links
    """
    if not auto_classifier:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auto classifier not configured",
        )

    try:
        links = auto_classifier.suggest_links(
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