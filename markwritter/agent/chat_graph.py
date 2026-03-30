"""LangGraph-based chat agent for RAG-powered conversations.

This module implements the chat graph that orchestrates the RAG pipeline:
1. Retrieve: Fetch relevant chunks from selected sources
2. Synthesize: Generate response using LLM with retrieved context
3. Respond: Stream response with citations

The graph maintains conversation state across multi-turn dialogues.
"""

import logging
from typing import TypedDict

from langgraph.graph import StateGraph, END

from markwritter.api.models.chat import ChatState, Citation
from markwritter.api.services.llm_service import LLMService
from markwritter.storage.rag_tool import RAGSearchTool
from markwritter.storage.chat_db import ChatSessionDB

logger = logging.getLogger(__name__)


class GraphState(TypedDict):
    """LangGraph state for chat conversations.

    This is the internal state used during graph execution.
    Maps to ChatState for external API.
    """

    session_id: str
    query: str
    selected_source_paths: list[str]
    retrieved_chunks: list[dict]
    conversation_history: list[dict]
    response: str
    citations: list[dict]
    # Internal tracking
    error: str | None


def create_chat_graph(
    rag_tool: RAGSearchTool,
    chat_db: ChatSessionDB,
    llm_service: LLMService | None = None,
) -> StateGraph:
    """Create the chat conversation graph.

    Args:
        rag_tool: RAG search tool for retrieval
        chat_db: Chat session database for persistence

    Returns:
        Compiled LangGraph state graph

    Graph flow:
        start -> retrieve_sources -> generate_response -> end
                      |
                      v
                 (on error) -> end
    """
    # Create graph builder
    builder = StateGraph(GraphState)

    # Add nodes
    builder.add_node("retrieve_sources", create_retrieve_node(rag_tool, chat_db))
    builder.add_node("generate_response", create_generate_node(llm_service))

    # Set entry point
    builder.set_entry_point("retrieve_sources")

    # Add edges
    builder.add_edge("retrieve_sources", "generate_response")
    builder.add_edge("generate_response", END)

    return builder


def normalize_conversation_history(history: list[dict] | None) -> list[dict[str, str]]:
    """Normalize history entries to role/content dicts."""
    normalized: list[dict[str, str]] = []
    for item in history or []:
        role = str(item.get("role", "")).strip()
        content = str(item.get("content", "")).strip()
        if role in {"user", "assistant", "system"} and content:
            normalized.append({"role": role, "content": content})
    return normalized


def build_citations(chunks: list[dict], max_chunks: int = 5) -> list[dict]:
    """Build citation payloads from retrieved chunks."""
    citations: list[dict] = []
    for chunk in chunks[:max_chunks]:
        citations.append(
            {
                "file_path": chunk["file_path"],
                "page_num": chunk["page_num"],
                "paragraph_idx": chunk["paragraph_idx"],
                "text_snippet": chunk["text"][:200],
            }
        )
    return citations


def build_chat_messages(
    query: str,
    chunks: list[dict],
    history: list[dict] | None = None,
    max_chunks: int = 5,
) -> list[dict[str, str]]:
    """Build LLM messages for chat generation."""
    normalized_history = normalize_conversation_history(history)

    if not chunks:
        system_prompt = (
            "You are a helpful assistant. Answer clearly and concisely. "
            "If the user references prior context, use the conversation history when helpful."
        )
        return [
            {"role": "system", "content": system_prompt},
            *normalized_history,
            {"role": "user", "content": query},
        ]

    context_parts: list[str] = []
    for index, chunk in enumerate(chunks[:max_chunks], start=1):
        location = chunk["file_path"]
        if chunk.get("page_num", 0) > 0:
            location = f"{location}, page {chunk['page_num']}"
        context_parts.append(f"[{index}] {location}\n{chunk['text']}")

    system_prompt = (
        "You answer questions using the provided source context. "
        "Prefer the supplied context over prior assumptions. "
        "If the answer is not supported by the context, say that clearly. "
        "When you rely on a source, cite it inline as [1], [2], etc."
    )
    context = "\n\n".join(context_parts)
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )

    return [
        {"role": "system", "content": system_prompt},
        *normalized_history,
        {"role": "user", "content": user_prompt},
    ]


def create_retrieve_node(
    rag_tool: RAGSearchTool,
    chat_db: ChatSessionDB,
):
    """Create the retrieval node.

    Retrieves relevant chunks from selected sources.
    """

    async def retrieve(state: GraphState) -> GraphState:
        """Retrieve relevant chunks for the query.

        Args:
            state: Current graph state

        Returns:
            Updated state with retrieved chunks
        """
        session_id = state["session_id"]
        query = state["query"]
        source_paths = state["selected_source_paths"]

        try:
            # Get selected sources from DB if not in state
            if not source_paths:
                source_paths = await chat_db.get_sources(session_id)
                state["selected_source_paths"] = source_paths

            # Perform RAG search
            result = await rag_tool.search(
                query=query,
                source_paths=source_paths if source_paths else None,
                limit=5,
            )

            # Convert chunks to dict format
            chunks = [
                {
                    "text": chunk.text,
                    "file_path": chunk.file_path,
                    "page_num": chunk.page_num,
                    "paragraph_idx": chunk.paragraph_idx,
                    "score": chunk.score,
                    "content_id": chunk.content_id,
                }
                for chunk in result.chunks
            ]

            logger.info(
                f"Retrieved {len(chunks)} chunks for query: {query[:50]}..."
            )

            return {
                **state,
                "retrieved_chunks": chunks,
            }

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return {
                **state,
                "error": str(e),
                "retrieved_chunks": [],
            }

    return retrieve


async def retrieve_chat_context(
    rag_tool: RAGSearchTool,
    chat_db: ChatSessionDB,
    session_id: str,
    query: str,
    selected_source_paths: list[str] | None = None,
    conversation_history: list[dict] | None = None,
) -> GraphState:
    """Run only the retrieval portion of the chat workflow."""
    state: GraphState = {
        "session_id": session_id,
        "query": query,
        "selected_source_paths": selected_source_paths or [],
        "retrieved_chunks": [],
        "conversation_history": normalize_conversation_history(conversation_history),
        "response": "",
        "citations": [],
        "error": None,
    }
    retrieve = create_retrieve_node(rag_tool, chat_db)
    return await retrieve(state)


def create_generate_node(llm_service: LLMService | None = None):
    """Create the response generation node.

    Generates response using retrieved context.
    """

    if llm_service is None:
        from markwritter.llm_client import LLMClient

        llm_service = LLMService(LLMClient())

    async def generate(state: GraphState) -> GraphState:
        """Generate response from retrieved context.

        Args:
            state: Current graph state with retrieved chunks

        Returns:
            Updated state with generated response
        """
        query = state["query"]
        chunks = state["retrieved_chunks"]
        history = normalize_conversation_history(state["conversation_history"])

        try:
            citations = build_citations(chunks)
            messages = build_chat_messages(query=query, chunks=chunks, history=history)
            result = llm_service.chat_complete(messages=messages)

            if not result.success:
                raise RuntimeError(result.message or "LLM completion failed")

            response = result.content

            logger.info(f"Generated response with {len(citations)} citations")

            return {
                **state,
                "response": response,
                "citations": citations,
            }

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                **state,
                "error": str(e),
                "response": f"Error generating response: {str(e)}",
                "citations": [],
            }

    return generate


async def run_chat_graph(
    graph: StateGraph,
    session_id: str,
    query: str,
    selected_source_paths: list[str] | None = None,
    conversation_history: list[dict] | None = None,
) -> dict:
    """Run the chat graph for a single query.

    Args:
        graph: Compiled LangGraph state graph
        session_id: Session identifier
        query: User query

    Returns:
        Final state with response and citations
    """
    # Compile graph
    compiled = graph.compile()

    # Initial state
    initial_state = {
        "session_id": session_id,
        "query": query,
        "selected_source_paths": selected_source_paths or [],
        "retrieved_chunks": [],
        "conversation_history": normalize_conversation_history(conversation_history),
        "response": "",
        "citations": [],
        "error": None,
    }

    # Run graph
    result = await compiled.ainvoke(initial_state)

    return result


def state_to_chat_state(state: GraphState) -> ChatState:
    """Convert GraphState to ChatState.

    Args:
        state: GraphState from LangGraph

    Returns:
        ChatState for API response
    """
    citations = [
        Citation(
            file_path=c["file_path"],
            page_num=c["page_num"],
            paragraph_idx=c["paragraph_idx"],
            text_snippet=c["text_snippet"],
        )
        for c in state.get("citations", [])
    ]

    return ChatState(
        session_id=state["session_id"],
        query=state["query"],
        selected_source_paths=state["selected_source_paths"],
        retrieved_chunks=state["retrieved_chunks"],
        conversation_history=state["conversation_history"],
        response=state["response"],
        citations=citations,
    )


__all__ = [
    "create_chat_graph",
    "run_chat_graph",
    "state_to_chat_state",
    "build_chat_messages",
    "build_citations",
    "normalize_conversation_history",
    "retrieve_chat_context",
    "GraphState",
]
