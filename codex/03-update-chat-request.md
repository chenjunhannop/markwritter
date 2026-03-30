# Task 03: Update ChatRequest Model to Accept Sources and History

## Priority: P0

## Problem

The frontend already sends `sources` and `conversation_history` in the chat request body, but the backend `ChatRequest` model ignores them.

## Current Code

File: `markwritter/api/models/chat.py`

```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
```

File: `web/lib/api.ts` (frontend)

```typescript
export interface ChatRequestBody {
  message: string;
  sources?: string[];  // <-- Already sent by frontend
  conversation_history?: ConversationMessage[];
}
```

## What To Build

Extend `ChatRequest` to accept the fields the frontend already sends.

### Updated model

```python
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    sources: Optional[list[str]] = None  # NEW: selected file paths
    conversation_history: Optional[list[dict]] = None  # NEW
```

## Implementation Steps

1. **Update `ChatRequest`** in `markwritter/api/models/chat.py`

2. **Pass sources to LangGraph** in `routes/chat.py`:
   ```python
   result = await run_chat_graph(
       graph=graph,
       session_id=request.session_id or "default",
       query=request.message,
       selected_source_paths=request.sources or [],  # NEW
       conversation_history=request.conversation_history or [],  # NEW
   )
   ```

3. **Update `run_chat_graph`** in `markwritter/agent/chat_graph.py` to accept these params:
   ```python
   async def run_chat_graph(
       graph: StateGraph,
       session_id: str,
       query: str,
       selected_source_paths: Optional[list[str]] = None,
       conversation_history: Optional[list[dict]] = None,
   ) -> dict:
       initial_state = {
           "session_id": session_id,
           "query": query,
           "selected_source_paths": selected_source_paths or [],
           "retrieved_chunks": [],
           "conversation_history": conversation_history or [],
           "response": "",
           "citations": [],
           "error": None,
       }
       # ... rest of function
   ```

4. **Update `retrieve_sources` node** to use sources from state instead of querying DB (or use DB as fallback)

## Files to Modify

- `markwritter/api/models/chat.py` - Add fields
- `markwritter/api/routes/chat.py` - Pass sources to graph
- `markwritter/agent/chat_graph.py` - Update `run_chat_graph` signature

## Files to Read First

- `markwritter/api/models/chat.py` - Current model
- `markwritter/agent/chat_graph.py` - `run_chat_graph` function
- `web/lib/api.ts` - Frontend request format

## Tests

- Test that sources are received and passed to graph
- Test that conversation_history is received
- Test backward compatibility (requests without these fields)
