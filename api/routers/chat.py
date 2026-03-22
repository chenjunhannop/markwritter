"""Chat API router with SSE streaming."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.models.chat import ChatEvent, ChatRequest
from api.services.framework_bridge import get_framework

router = APIRouter(prefix="/api/chat", tags=["chat"])


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
