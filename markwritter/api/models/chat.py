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
    sources: Optional[list[str]] = None
    conversation_history: Optional[list[dict[str, str]]] = None


class ChatEvent(BaseModel):
    """SSE event model for chat stream."""

    type: str  # thinking, text_delta, citation, done, error
    content: str = ""
    citation: Optional[Citation] = None  # Present when type == "citation"


class SourceSelectionRequest(BaseModel):
    """Request model for selecting sources."""

    session_id: str
    source_paths: list[str]  # List of file paths to select


class SourceSelectionResponse(BaseModel):
    """Response model for source selection."""

    session_id: str
    selected_sources: list[str]  # List of selected file paths
    count: int


class ChatState:
    """LangGraph state for chat conversations.

    Maintains the state for a single chat session including:
    - Selected sources for RAG retrieval
    - Conversation history
    - Retrieved chunks context
    - Current response being generated
    """

    def __init__(
        self,
        session_id: str,
        query: str = "",
        selected_source_paths: list[str] | None = None,
        retrieved_chunks: list[dict] | None = None,
        conversation_history: list[dict] | None = None,
        response: str = "",
        citations: list[Citation] | None = None,
    ):
        self.session_id = session_id
        self.query = query
        self.selected_source_paths = selected_source_paths or []
        self.retrieved_chunks = retrieved_chunks or []
        self.conversation_history = conversation_history or []
        self.response = response
        self.citations = citations or []

    def to_dict(self) -> dict:
        """Convert state to dictionary for LangGraph."""
        return {
            "session_id": self.session_id,
            "query": self.query,
            "selected_source_paths": self.selected_source_paths,
            "retrieved_chunks": self.retrieved_chunks,
            "conversation_history": self.conversation_history,
            "response": self.response,
            "citations": self.citations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatState":
        """Create state from dictionary."""
        return cls(
            session_id=data.get("session_id", ""),
            query=data.get("query", ""),
            selected_source_paths=data.get("selected_source_paths", []),
            retrieved_chunks=data.get("retrieved_chunks", []),
            conversation_history=data.get("conversation_history", []),
            response=data.get("response", ""),
            citations=data.get("citations", []),
        )
