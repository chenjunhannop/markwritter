# Task 02: Integrate LLM into LangGraph Generate Node

## Priority: P0 (blocking real chat functionality)

## Problem

The LangGraph `generate_response` node in `markwritter/agent/chat_graph.py` is a placeholder that builds a hardcoded template string instead of calling an LLM.

## Current Code (placeholder)

File: `markwritter/agent/chat_graph.py`, line 145-216

```python
def create_generate_node():
    """Create the response generation node."""

    async def generate(state: GraphState) -> GraphState:
        query = state["query"]
        chunks = state["retrieved_chunks"]
        history = state["conversation_history"]

        try:
            if not chunks:
                response = "I couldn't find relevant information..."
                citations = []
            else:
                context_parts = []
                citations = []

                for i, chunk in enumerate(chunks[:3]):
                    context_parts.append(f"[{chunk['file_path']}]: {chunk['text'][:200]}")
                    citations.append({
                        "file_path": chunk["file_path"],
                        "page_num": chunk["page_num"],
                        "paragraph_idx": chunk["paragraph_idx"],
                        "text_snippet": chunk["text"][:100],
                    })

                response = (
                    f"Based on your sources, here's what I found about '{query}':\n\n"
                    + "\n\n".join(context_parts)
                    + "\n\n"
                    + f"(This is a placeholder response. LLM integration coming soon.)"
                )

            return {
                **state,
                "response": response,
                "citations": citations,
            }
        except Exception as e:
            return {
                **state,
                "error": str(e),
                "response": f"Error generating response: {str(e)}",
                "citations": [],
            }

    return generate
```

## What To Build

Inject `LLMService` (or `LLMClient`) into the generate node and call `chat_complete()` with a properly structured prompt.

### New generate node implementation

```python
from markwritter.api.services.llm_service import LLMService
from markwritter.models import LLMConfig

def create_generate_node(llm_service: Optional[LLMService] = None):
    """Create the response generation node with LLM integration."""

    # Lazy init if not provided
    if llm_service is None:
        from markwritter.llm_client import LLMClient
        from markwritter.config import get_config
        config = get_config()
        llm_client = LLMClient(config.llm)
        llm_service = LLMService(llm_client)

    async def generate(state: GraphState) -> GraphState:
        query = state["query"]
        chunks = state["retrieved_chunks"]
        history = state["conversation_history"]

        try:
            if not chunks:
                # No context - let LLM answer from general knowledge
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": query},
                ]
                result = await llm_service.chat_complete(messages)
                response = result.output
                citations = []
            else:
                # Build context from chunks
                context_parts = []
                citations = []

                for i, chunk in enumerate(chunks[:5]):  # Use top 5 chunks
                    context_parts.append(f"[Source {i+1}: {chunk['file_path']}]: {chunk['text']}")
                    citations.append({
                        "file_path": chunk["file_path"],
                        "page_num": chunk["page_num"],
                        "paragraph_idx": chunk["paragraph_idx"],
                        "text_snippet": chunk["text"][:100],
                    })

                context = "\n\n".join(context_parts)

                # Build RAG prompt
                system_prompt = """You are a helpful assistant answering questions based on provided context.
- Use the context below to answer the user's question
- If the answer is not in the context, say so clearly
- Cite sources using [1], [2], etc. format
- Be concise but thorough"""

                user_prompt = f"""Context:
{context}

Question: {query}

Answer:"""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]

                result = await llm_service.chat_complete(messages)
                response = result.output

            return {
                **state,
                "response": response,
                "citations": citations,
            }
        except Exception as e:
            logger.error(f"Generate error: {e}")
            return {
                **state,
                "error": str(e),
                "response": f"Error generating response: {str(e)}",
                "citations": [],
            }

    return generate
```

### Update `create_chat_graph` to accept llm_service

```python
def create_chat_graph(
    rag_tool: RAGSearchTool,
    chat_db: ChatSessionDB,
    llm_service: Optional[LLMService] = None,
) -> StateGraph:
    """Create the chat conversation graph."""
    builder = StateGraph(GraphState)

    builder.add_node("retrieve_sources", create_retrieve_node(rag_tool, chat_db))
    builder.add_node("generate_response", create_generate_node(llm_service))

    builder.set_entry_point("retrieve_sources")
    builder.add_edge("retrieve_sources", "generate_response")
    builder.add_edge("generate_response", END)

    return builder
```

## Implementation Steps

1. **Import `LLMService`** in `chat_graph.py`
2. **Modify `create_generate_node`** to accept optional `llm_service` parameter
3. **Implement lazy init** if `llm_service` not provided
4. **Build proper RAG prompt** with context from chunks
5. **Call `llm_service.chat_complete()`** with messages array
6. **Update `create_chat_graph`** to accept and pass `llm_service`

## Files to Modify

- `markwritter/agent/chat_graph.py` - Main implementation

## Files to Read First

- `markwritter/agent/chat_graph.py` - Current generate node
- `markwritter/api/services/llm_service.py` - LLMService API
- `markwritter/llm_client.py` - Underlying LLMClient
- `markwritter/config.yaml` - LLM config (default model)

## Tests

Update `tests/agent/test_chat_graph.py`:
- Mock `LLMService.chat_complete()` and verify it's called with correct messages
- Test fallback when no chunks available
- Test error handling when LLM fails
- Test that citations are still generated
