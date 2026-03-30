"""Chat API router with SSE streaming and source management."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from markwritter.api.models.chat import (
    ChatEvent,
    ChatRequest,
    SourceSelectionRequest,
    SourceSelectionResponse,
)
from markwritter.api.services.framework_bridge import get_framework
from markwritter.storage.chat_db import ChatSessionDB

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Global instance for session DB (initialized on first use)
_chat_db: Optional[ChatSessionDB] = None
_init_lock = asyncio.Lock()


async def get_chat_db() -> ChatSessionDB:
    """Get or create ChatSessionDB singleton with proper initialization."""
    global _chat_db
    if _chat_db is None:
        async with _init_lock:
            # Double-check locking pattern
            if _chat_db is None:
                _chat_db = ChatSessionDB(Path("chat_sessions.db"))
                await _chat_db.initialize()
                logger.info("Initialized chat session database")
    return _chat_db


@router.post("/sources")
async def select_sources(request: SourceSelectionRequest) -> SourceSelectionResponse:
    """Select sources for a chat session.

    Args:
        request: Source selection request with session_id and source_paths

    Returns:
        SourceSelectionResponse with selected sources

    Raises:
        HTTPException: If session_id is invalid or sources cannot be saved
    """
    chat_db = await get_chat_db()

    try:
        # Save session with selected sources
        # Note: We don't validate path existence here to allow selecting sources
        # before they're indexed. Validation happens during RAG retrieval.
        await chat_db.save_session(request.session_id, request.source_paths)

        logger.info(
            f"Saved session {request.session_id} with {len(request.source_paths)} sources"
        )

        return SourceSelectionResponse(
            session_id=request.session_id,
            selected_sources=request.source_paths,
            count=len(request.source_paths),
        )
    except Exception as e:
        logger.error(f"Error selecting sources: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save source selection: {str(e)}",
        )


@router.get("/sources")
async def get_selected_sources(session_id: str) -> SourceSelectionResponse:
    """Get selected sources for a chat session.

    Args:
        session_id: Session identifier

    Returns:
        SourceSelectionResponse with selected sources

    Raises:
        HTTPException: If session is not found
    """
    chat_db = await get_chat_db()

    try:
        sources = await chat_db.get_sources(session_id)

        if not sources:
            # Return empty response instead of 404 for better UX
            # Frontend can handle empty state gracefully
            return SourceSelectionResponse(
                session_id=session_id,
                selected_sources=[],
                count=0,
            )

        return SourceSelectionResponse(
            session_id=session_id,
            selected_sources=sources,
            count=len(sources),
        )
    except Exception as e:
        logger.error(f"Error getting selected sources: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve selected sources: {str(e)}",
        )


@router.delete("/sources")
async def clear_sources(session_id: str) -> dict:
    """Clear selected sources for a chat session (without deleting conversation).

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    chat_db = await get_chat_db()

    try:
        # Save session with empty sources list
        await chat_db.save_session(session_id, [])

        logger.info(f"Cleared sources for session {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "message": "Sources cleared",
        }
    except Exception as e:
        logger.error(f"Error clearing sources: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear sources: {str(e)}",
        )


@router.post("/")
async def chat(request: ChatRequest):
    """Handle chat message and return SSE stream."""

    async def event_generator():
        framework = get_framework()

        # Send thinking status
        yield f"data: {json.dumps({'type': 'thinking'})}\n\n"

        try:
            # Process input through framework
            result = framework.process_input(request.message)

            # Stream the response character by character
            for char in result:
                event = ChatEvent(type="text_delta", content=char)
                yield f"data: {event.model_dump_json()}\n\n"

            # Send done event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            # Send error event
            event = ChatEvent(type="error", content=str(e))
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
