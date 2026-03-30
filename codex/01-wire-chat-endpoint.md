# Task 01: Wire SSE Chat Endpoint Through LangGraph

## Priority: P0 (blocking everything else)

## Problem

The SSE chat endpoint at `POST /api/v1/chat/` currently uses the legacy `Framework.process_input()` which dispatches to skills. It should use the LangGraph chat graph for RAG-powered conversations with sources.

## Current Code (broken path)

File: `markwritter/api/routes/chat.py`, line 152-182

```python
@router.post("/")
async def chat(request: ChatRequest):
    async def event_generator():
        framework = get_framework()  # <-- OLD PATH, bypasses LangGraph
        yield f"data: {json.dumps({'type': 'thinking'})}\n\n"
        try:
            result = framework.process_input(request.message)
            for char in result:
                event = ChatEvent(type="text_delta", content=char)
                yield f"data: {event.model_dump_json()}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            event = ChatEvent(type="error", content=str(e))
            yield f"data: {event.model_dump_json()}\n\n"
```

## What To Build

Replace the event_generator to:

1. Initialize `RAGSearchTool` and `ChatSessionDB` (or get singletons)
2. Create the LangGraph chat graph via `create_chat_graph(rag_tool, chat_db)`
3. Run the graph with `run_chat_graph(graph, session_id, query)`
4. Stream the graph result as SSE events

### New endpoint implementation

```python
@router.post("/")
async def chat(request: ChatRequest):
    """Handle chat message with RAG pipeline, return SSE stream."""

    async def event_generator():
        yield f"data: {json.dumps({'type': 'thinking'})}\n\n"

        try:
            # Get dependencies
            chat_db = await get_chat_db()
            # TODO: get rag_tool singleton (create one if needed)
            rag_tool = get_rag_tool()

            # Build and run LangGraph
            graph = create_chat_graph(rag_tool=rag_tool, chat_db=chat_db)

            result = await run_chat_graph(
                graph=graph,
                session_id=request.session_id or "default",
                query=request.message,
            )

            # Check for errors
            if result.get("error"):
                event = ChatEvent(type="error", content=result["error"])
                yield f"data: {event.model_dump_json()}\n\n"
                return

            # Stream response text
            response_text = result.get("response", "")
            for char in response_text:
                event = ChatEvent(type="text_delta", content=char)
                yield f"data: {event.model_dump_json()}\n\n"

            # Send citations if any
            citations = result.get("citations", [])
            if citations:
                event = ChatEvent(
                    type="citation",
                    content=json.dumps(citations)
                )
                yield f"data: {event.model_dump_json()}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Chat error: {e}")
            event = ChatEvent(type="error", content=str(e))
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

## Implementation Steps

1. **Create `get_rag_tool()` singleton** in `routes/chat.py` (similar pattern to `get_chat_db()`)
   - Needs `ContentService`, `PathResolver`, `VectorSearchCache` dependencies
   - Use the same async lock + double-check pattern

2. **Import `create_chat_graph` and `run_chat_graph`** from `markwritter.agent.chat_graph`

3. **Replace the `event_generator`** in the `chat` endpoint

4. **Keep the old `Framework`-based endpoint** available at a different path (e.g., `/api/v1/chat/skill`) for backward compatibility

5. **Update `ChatRequest` model** in `api/models/chat.py` to include:
   ```python
   class ChatRequest(BaseModel):
       message: str
       session_id: Optional[str] = None
       sources: Optional[list[str]] = None  # NEW: frontend sends these
       conversation_history: Optional[list[dict]] = None  # NEW
   ```

6. **Pass sources and history** into the LangGraph initial state in `run_chat_graph`

## Files to Modify

- `markwritter/api/routes/chat.py` - Main rewrite
- `markwritter/api/models/chat.py` - Add fields to ChatRequest
- `markwritter/agent/chat_graph.py` - Update `run_chat_graph` to accept sources/history params

## Files to Read First

- `markwritter/api/routes/chat.py` - Current endpoint
- `markwritter/agent/chat_graph.py` - Graph definition
- `markwritter/storage/rag_tool.py` - RAG tool constructor
- `markwritter/storage/registry.py` - StorageRegistry for ContentService
- `markwritter/api/models/chat.py` - Current models

## Tests

Add test in `tests/api/routes/test_chat.py` or update existing:
- Test that chat endpoint calls LangGraph (mock the graph)
- Test that sources are passed through
- Test error handling when graph fails
- Test SSE format is preserved
