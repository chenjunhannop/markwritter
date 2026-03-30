"""Chat API models."""

from typing import Optional

from pydantic import BaseModel


class Citation(BaseModel):
    """Citation model for source references."""

    file_path: str  # Relative path in Obsidian vault
    page_num: int = 0  # PDF page number, 0 for MD files
    paragraph_idx: int = 0  # Paragraph index
    text_snippet: str  # Original text for highlighting


class ChatRequest(BaseModel):
    """Request model for chat."""

    message: str
    session_id: Optional[str] = None  # Optional session ID for multi-turn conversations


class ChatEvent(BaseModel):
    """SSE event model for chat stream."""

    type: str  # thinking, text_delta, citation, done, error
    content: str = ""
    citation: Optional[Citation] = None  # Present when type == "citation"
