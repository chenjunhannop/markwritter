# Task 04: Stream LLM Response Through SSE in Real-Time

## Priority: P0

## Problem

The current SSE endpoint iterates character-by-character over a complete string. But LLMs produce tokens incrementally. We need to stream LLM tokens as they're generated, not wait for the full response.

## Current Code (synchronous, not streaming)

File: `markwritter/api/routes/chat.py`

```python
# After getting result from LangGraph
response_text = result.get("response", "")
for char in response_text:  # <-- Iterates complete string, not streaming
    event = ChatEvent(type="text_delta", content=char)
    yield f"data: {event.model_dump_json()}\n\n"
```

## What To Build

The LLM client needs to support streaming, and the SSE endpoint needs to yield tokens as they arrive.

### Step 1: Add streaming to LLMClient

File: `markwritter/llm_client.py` - Add `stream_complete()` method:

```python
async def stream_complete(
    self,
    messages: list[dict],
    model: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Stream LLM response token by token."""
    import litellm

    model_name = model or self.config.default_model

    # litellm supports streaming via completion() with stream=True
    response = await litellm.acompletion(
        model=model_name,
        messages=messages,
        stream=True,
    )

    async for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
```

### Step 2: Update LLMService with streaming

File: `markwritter/api/services/llm_service.py`:

```python
async def stream_complete(
    self,
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    """Stream LLM response."""
    async for token in self.client.stream_complete(messages):
        yield token
```

### Step 3: Update generate node to support streaming

The generate node currently returns a complete response. We need it to either:
- Option A: Return an async generator for tokens
- Option B: Store tokens in state incrementally

**Option A is cleaner** but requires changing the graph architecture.

**Simpler approach for MVP**: Keep the generate node synchronous but make the SSE endpoint call LLM directly after retrieval.

### MVP Implementation (hybrid approach)

Modify `routes/chat.py` to:
1. Run LangGraph for retrieval only (get chunks)
2. Call LLM directly with streaming for response

```python
@router.post("/")
async def chat(request: ChatRequest):
    async def event_generator():
        yield f"data: {json.dumps({'type': 'thinking'})}\n\n"

        try:
            chat_db = await get_chat_db()
            rag_tool = get_rag_tool()

            # Step 1: Retrieve chunks via LangGraph (or directly)
            result = await rag_tool.search(
                query=request.message,
                source_paths=request.sources,
                limit=5,
            )

            chunks = result.chunks

            # Send sources event if chunks found
            if chunks:
                sources_event = ChatEvent(
                    type="sources",
                    content=json.dumps([
                        {"file_path": c.file_path, "score": c.score}
                        for c in chunks[:5]
                    ])
                )
                yield f"data: {sources_event.model_dump_json()}\n\n"

            # Step 2: Build prompt with context
            if chunks:
                context_parts = [
                    f"[Source {i+1}: {c.file_path}]: {c.text}"
                    for i, c in enumerate(chunks[:5])
                ]
                context = "\n\n".join(context_parts)
                user_prompt = f"Context:\n{context}\n\nQuestion: {request.message}\n\nAnswer:"
            else:
                user_prompt = request.message

            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_prompt},
            ]

            # Step 3: Stream LLM response
            llm_service = get_llm_service()
            citations = []  # Track citations for later

            async for token in llm_service.stream_complete(messages):
                event = ChatEvent(type="text_delta", content=token)
                yield f"data: {event.model_dump_json()}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Chat error: {e}")
            event = ChatEvent(type="error", content=str(e))
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

## Implementation Steps

1. **Add `stream_complete()` to `LLMClient`** in `llm_client.py`
2. **Add `stream_complete()` to `LLMService`** in `llm_service.py`
3. **Create `get_llm_service()` singleton** in `routes/chat.py`
4. **Rewrite SSE endpoint** to stream LLM tokens directly
5. **Keep LangGraph for retrieval** but don't wait for full response

## Files to Modify

- `markwritter/llm_client.py` - Add streaming method
- `markwritter/api/services/llm_service.py` - Add streaming method
- `markwritter/api/routes/chat.py` - Main rewrite for streaming

## Files to Read First

- `markwritter/llm_client.py` - Current LLM client
- `markwritter/api/services/llm_service.py` - Current service
- `markwritter/api/routes/chat.py` - Current endpoint
- `litellm` documentation for streaming API

## Tests

- Test SSE stream produces tokens incrementally
- Test streaming completes without errors
- Test error handling during stream
- Verify token format is valid SSE
