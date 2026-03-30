# Codex Implementation Plans for Markwritter

These files contain detailed implementation instructions for OpenAI Codex.

## Context

Markwritter is a NotebookLM-style knowledge management app with Obsidian integration.
Stack: FastAPI (Python) backend + Next.js 15 frontend.

## Current State

- Backend: FastAPI with LangGraph, RAG tool, chat session DB, LiteLLM client all built
- Frontend: Chat UI with sources panel, file tree, SSE streaming all built
- **Critical gap**: The pieces are not connected end-to-end

## Files

| File | Priority | Description |
|------|----------|-------------|
| `01-wire-chat-endpoint.md` | P0 | Connect SSE chat endpoint to LangGraph (currently uses old Framework) |
| `02-integrate-llm-generate.md` | P0 | Replace placeholder generate node with real LLM calls |
| `03-update-chat-request.md` | P0 | Accept sources and history from frontend in chat request |
| `04-stream-llm-sse.md` | P0 | Stream LLM tokens through SSE in real-time |
| `05-citation-frontend.md` | P1 | Add citation event support and rendering |
| `06-source-selection-frontend.md` | P1 | Connect frontend source selection to backend API |

## Execution Order

Execute 01-04 in sequence (they depend on each other).
05-06 can be done in parallel after 01-04 are complete.

## Important Files to Read First

- `markwritter/api/routes/chat.py` - SSE endpoint (needs rewriting)
- `markwritter/agent/chat_graph.py` - LangGraph graph (generate node is placeholder)
- `markwritter/llm_client.py` - Working LLM client (already functional)
- `markwritter/api/services/llm_service.py` - LLM service wrapper
- `markwritter/storage/rag_tool.py` - RAG search tool
- `markwritter/storage/chat_db.py` - Session persistence
- `markwritter/api/models/chat.py` - API request/response models
- `web/lib/types.ts` - Frontend TypeScript types
- `web/hooks/use-chat.ts` - Frontend chat hook
- `web/lib/api.ts` - Frontend API client
- `config.yaml` - LLM configuration

## Testing

After each task, run: `uv run pytest tests/ -x -q`

All 1181 existing tests must continue to pass. Add new tests for new functionality.
