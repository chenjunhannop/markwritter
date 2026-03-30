# Implementation Summary and Checklist

## Project: Markwritter Chat with Sources MVP

**Goal**: Connect all the pieces to make "Chat with Sources" work end-to-end.

---

## Current State

| Component | Status |
|-----------|--------|
| LangGraph chat graph | Built, but generate node is placeholder |
| RAG search tool | Built, keyword-based (vector search TODO) |
| Chat session DB | Built, SQLite with async support |
| Source selection API | Built, but frontend doesn't call it |
| SSE chat endpoint | Built, but uses old Framework path |
| LLM client | Built and functional |
| Frontend chat UI | Built with sources panel |
| Frontend SSE parsing | Built |
| Citation rendering | NOT built |

---

## Execution Order

### Phase 1: Backend Core (P0)

These tasks must be done in order:

1. **[01-wire-chat-endpoint.md](./01-wire-chat-endpoint.md)** - Connect SSE endpoint to LangGraph
2. **[02-integrate-llm-generate.md](./02-integrate-llm-generate.md)** - Add LLM calls to generate node
3. **[03-update-chat-request.md](./03-update-chat-request.md)** - Accept sources/history from frontend
4. **[04-stream-llm-sse.md](./04-stream-llm-sse.md)** - Stream LLM tokens in real-time

### Phase 2: Frontend Integration (P1)

These tasks can be done in parallel after Phase 1:

5. **[05-citation-frontend.md](./05-citation-frontend.md)** - Add citation rendering
6. **[06-source-selection-frontend.md](./06-source-selection-frontend.md)** - Connect source selection to backend

---

## Testing

After each task:

```bash
# Backend tests
cd /Users/chenjunhan/dev/github-project/markwrtier
uv run pytest tests/ -x -q

# Frontend tests
cd web
pnpm test
```

All 1181 existing tests must pass. Add new tests for new functionality.

---

## Success Criteria

When all tasks are complete:

- [ ] User can select 2+ files in the sources panel
- [ ] User can type a question and get a streamed response
- [ ] Response is based on selected sources (RAG retrieval)
- [ ] Citations appear as [1][2] badges in the response
- [ ] Clicking a citation shows source card with file path, page, snippet
- [ ] Refreshing the page keeps sources selected
- [ ] Multi-turn conversation works (history is preserved)

---

## Key Files Reference

| Purpose | File |
|---------|------|
| SSE endpoint | `markwritter/api/routes/chat.py` |
| LangGraph graph | `markwritter/agent/chat_graph.py` |
| RAG tool | `markwritter/storage/rag_tool.py` |
| Session DB | `markwritter/storage/chat_db.py` |
| LLM client | `markwritter/llm_client.py` |
| LLM service | `markwritter/api/services/llm_service.py` |
| API models | `markwritter/api/models/chat.py` |
| Frontend types | `web/lib/types.ts` |
| Frontend chat hook | `web/hooks/use-chat.ts` |
| Frontend API client | `web/lib/api.ts` |
| Sources panel | `web/components/chat/sources-panel.tsx` |
| Chat session | `web/components/chat/chat-session.tsx` |

---

## Notes for Codex

- Read the referenced files before implementing each task
- Follow existing code style and patterns
- Add tests for all new functionality
- Keep changes focused and incremental
- If you find issues not covered here, note them and continue

---

## After Implementation

Once all 6 tasks are complete, run `/codex review` to get an independent code review before merging.
