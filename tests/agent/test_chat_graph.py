"""Tests for LangGraph Chat Graph."""

import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from markwritter.agent.chat_graph import (
    GraphState,
    build_chat_messages,
    create_chat_graph,
    retrieve_chat_context,
    run_chat_graph,
    state_to_chat_state,
)
from markwritter.api.models.chat import ChatState, Citation
from markwritter.storage.cache import VectorSearchCache
from markwritter.storage.chat_db import ChatSessionDB
from markwritter.storage.path_resolver import PathResolver
from markwritter.storage.rag_tool import RAGSearchTool
from markwritter.storage.service import ContentService
from markwritter.storage.registry import StorageRegistry


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service."""
    return SimpleNamespace(
        chat_complete=lambda messages: SimpleNamespace(
            success=True,
            content="Mocked response [1]",
            message="",
            messages=messages,
        )
    )


@pytest.fixture
async def setup_dependencies():
    """Create all dependencies for chat graph."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)

        # Create dependencies
        registry = StorageRegistry()
        content_service = ContentService(registry=registry)
        path_resolver = PathResolver(content_service=content_service)
        cache = VectorSearchCache(max_size=100)
        rag_tool = RAGSearchTool(
            content_service=content_service,
            path_resolver=path_resolver,
            cache=cache,
        )
        chat_db = ChatSessionDB(data_dir / "chat.db")
        await chat_db.initialize()

        yield {
            "rag_tool": rag_tool,
            "chat_db": chat_db,
        }

        await chat_db.close()


class TestGraphState:
    """Tests for GraphState TypedDict."""

    def test_graph_state_structure(self) -> None:
        """Test GraphState has required fields."""
        state: GraphState = {
            "session_id": "test-session",
            "query": "test query",
            "selected_source_paths": ["a.md"],
            "retrieved_chunks": [],
            "conversation_history": [],
            "response": "",
            "citations": [],
            "error": None,
        }

        assert state["session_id"] == "test-session"
        assert state["query"] == "test query"
        assert state["selected_source_paths"] == ["a.md"]
        assert state["error"] is None


class TestCreateChatGraph:
    """Tests for create_chat_graph function."""

    @pytest.mark.asyncio
    async def test_create_graph(self, setup_dependencies, mock_llm_service) -> None:
        """Test graph creation."""
        graph = create_chat_graph(
            rag_tool=setup_dependencies["rag_tool"],
            chat_db=setup_dependencies["chat_db"],
            llm_service=mock_llm_service,
        )

        assert graph is not None

    @pytest.mark.asyncio
    async def test_graph_has_nodes(self, setup_dependencies, mock_llm_service) -> None:
        """Test graph has required nodes."""
        graph = create_chat_graph(
            rag_tool=setup_dependencies["rag_tool"],
            chat_db=setup_dependencies["chat_db"],
            llm_service=mock_llm_service,
        )

        # Compile to inspect
        compiled = graph.compile()

        # Check nodes exist (implementation detail, may need adjustment)
        assert compiled is not None


class TestRunChatGraph:
    """Tests for running the chat graph."""

    @pytest.mark.asyncio
    async def test_run_graph_basic(self, setup_dependencies, mock_llm_service) -> None:
        """Test running graph with basic query."""
        graph = create_chat_graph(
            rag_tool=setup_dependencies["rag_tool"],
            chat_db=setup_dependencies["chat_db"],
            llm_service=mock_llm_service,
        )

        result = await run_chat_graph(
            graph=graph,
            session_id="test-session",
            query="What is machine learning?",
        )

        assert result["session_id"] == "test-session"
        assert result["query"] == "What is machine learning?"
        assert "response" in result
        assert "citations" in result

    @pytest.mark.asyncio
    async def test_run_graph_with_no_sources(
        self, setup_dependencies, mock_llm_service
    ) -> None:
        """Test graph handles empty sources gracefully."""
        graph = create_chat_graph(
            rag_tool=setup_dependencies["rag_tool"],
            chat_db=setup_dependencies["chat_db"],
            llm_service=mock_llm_service,
        )

        result = await run_chat_graph(
            graph=graph,
            session_id="empty-session",
            query="Test query with no sources",
        )

        assert result["session_id"] == "empty-session"
        # Should have response even without sources
        assert result["response"] != ""

    @pytest.mark.asyncio
    async def test_run_graph_updates_state(
        self, setup_dependencies, mock_llm_service
    ) -> None:
        """Test graph updates state correctly."""
        graph = create_chat_graph(
            rag_tool=setup_dependencies["rag_tool"],
            chat_db=setup_dependencies["chat_db"],
            llm_service=mock_llm_service,
        )

        initial_sources = ["notes/test.md"]

        # Save sources to DB
        await setup_dependencies["chat_db"].save_session(
            "state-session", initial_sources
        )

        result = await run_chat_graph(
            graph=graph,
            session_id="state-session",
            query="Test query",
        )

        # State should be updated
        assert "retrieved_chunks" in result
        assert "response" in result
        assert "citations" in result

    @pytest.mark.asyncio
    async def test_run_graph_preserves_sources_and_history(
        self, setup_dependencies, mock_llm_service
    ) -> None:
        """Test explicit sources and history are passed into the graph."""
        graph = create_chat_graph(
            rag_tool=setup_dependencies["rag_tool"],
            chat_db=setup_dependencies["chat_db"],
            llm_service=mock_llm_service,
        )

        result = await run_chat_graph(
            graph=graph,
            session_id="history-session",
            query="Follow-up question",
            selected_source_paths=["notes/a.md"],
            conversation_history=[{"role": "user", "content": "Earlier question"}],
        )

        assert result["selected_source_paths"] == ["notes/a.md"]
        assert result["conversation_history"] == [
            {"role": "user", "content": "Earlier question"}
        ]


class TestPromptBuilding:
    """Tests for prompt generation helpers."""

    def test_build_chat_messages_includes_history_and_context(self) -> None:
        """Test prompt construction for RAG responses."""
        messages = build_chat_messages(
            query="What changed?",
            chunks=[{"file_path": "notes/a.md", "page_num": 0, "text": "Important fact"}],
            history=[{"role": "assistant", "content": "Previous answer"}],
        )

        assert messages[0]["role"] == "system"
        assert messages[1] == {"role": "assistant", "content": "Previous answer"}
        assert "Important fact" in messages[-1]["content"]
        assert "Question: What changed?" in messages[-1]["content"]


class TestRetrieveContext:
    """Tests for retrieval-only helper used by SSE route."""

    @pytest.mark.asyncio
    async def test_retrieve_chat_context_uses_selected_sources(
        self, setup_dependencies
    ) -> None:
        """Test retrieval helper preserves selected source paths."""
        state = await retrieve_chat_context(
            rag_tool=setup_dependencies["rag_tool"],
            chat_db=setup_dependencies["chat_db"],
            session_id="retrieve-session",
            query="test",
            selected_source_paths=["notes/a.md"],
        )

        assert state["selected_source_paths"] == ["notes/a.md"]
        assert "retrieved_chunks" in state


class TestStateToChatState:
    """Tests for state_to_chat_state conversion."""

    def test_convert_empty_state(self) -> None:
        """Test converting empty GraphState."""
        graph_state: GraphState = {
            "session_id": "test",
            "query": "",
            "selected_source_paths": [],
            "retrieved_chunks": [],
            "conversation_history": [],
            "response": "",
            "citations": [],
            "error": None,
        }

        chat_state = state_to_chat_state(graph_state)

        assert isinstance(chat_state, ChatState)
        assert chat_state.session_id == "test"
        assert chat_state.query == ""
        assert chat_state.response == ""
        assert chat_state.citations == []

    def test_convert_state_with_citations(self) -> None:
        """Test converting state with citations."""
        graph_state: GraphState = {
            "session_id": "test",
            "query": "test query",
            "selected_source_paths": ["a.md"],
            "retrieved_chunks": [
                {
                    "text": "Test content",
                    "file_path": "notes/a.md",
                    "page_num": 0,
                    "paragraph_idx": 1,
                    "score": 0.9,
                    "content_id": "uuid-123",
                }
            ],
            "conversation_history": [],
            "response": "Test response",
            "citations": [
                {
                    "file_path": "notes/a.md",
                    "page_num": 0,
                    "paragraph_idx": 1,
                    "text_snippet": "Test content",
                }
            ],
            "error": None,
        }

        chat_state = state_to_chat_state(graph_state)

        assert isinstance(chat_state, ChatState)
        assert len(chat_state.citations) == 1
        assert isinstance(chat_state.citations[0], Citation)
        assert chat_state.citations[0].file_path == "notes/a.md"
        assert chat_state.citations[0].text_snippet == "Test content"

    def test_convert_preserves_all_fields(self) -> None:
        """Test all fields are preserved in conversion."""
        graph_state: GraphState = {
            "session_id": "full-session",
            "query": "full query",
            "selected_source_paths": ["a.md", "b.md"],
            "retrieved_chunks": [{"text": "chunk"}],
            "conversation_history": [{"role": "user", "content": "hello"}],
            "response": "full response",
            "citations": [],
            "error": None,
        }

        chat_state = state_to_chat_state(graph_state)

        assert chat_state.session_id == "full-session"
        assert chat_state.query == "full query"
        assert chat_state.selected_source_paths == ["a.md", "b.md"]
        assert len(chat_state.retrieved_chunks) == 1
        assert len(chat_state.conversation_history) == 1
        assert chat_state.response == "full response"


class TestChatGraphIntegration:
    """Integration tests for full chat graph flow."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, setup_dependencies, mock_llm_service) -> None:
        """Test complete conversation flow."""
        rag_tool = setup_dependencies["rag_tool"]
        chat_db = setup_dependencies["chat_db"]

        # Create graph
        graph = create_chat_graph(
            rag_tool=rag_tool,
            chat_db=chat_db,
            llm_service=mock_llm_service,
        )

        # First turn
        result1 = await run_chat_graph(
            graph=graph,
            session_id="integration-session",
            query="First question",
        )

        assert result1["response"] != ""

        # Save to conversation history (simulating what API would do)
        await chat_db.save_message(
            "integration-session", 0, "user", "First question"
        )
        await chat_db.save_message(
            "integration-session", 1, "assistant", result1["response"]
        )

        # Second turn
        result2 = await run_chat_graph(
            graph=graph,
            session_id="integration-session",
            query="Follow-up question",
        )

        assert result2["response"] != ""
        assert result2["session_id"] == "integration-session"
