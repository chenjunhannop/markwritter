"""Chat API models."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request model for chat."""

    message: str


class ChatEvent(BaseModel):
    """SSE event model for chat stream."""

    type: str  # thinking, text_delta, done, error
    content: str = ""
