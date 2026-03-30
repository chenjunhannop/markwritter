# Changelog

All notable changes to this project will be documented in this file.

## [0.1.1.0] - 2026-03-30

### Added
- **Chat Session Database** (`storage/chat_db.py`): SQLite-backed session persistence with async support
- **RAG Search Tool** (`storage/rag_tool.py`): Source-scoped retrieval with vector search caching
- **Source Selection API** (`api/routes/chat.py`): POST/GET/DELETE `/api/v1/chat/sources` endpoints
- **LangGraph Chat Graph** (`agent/chat_graph.py`): StateGraph-based chat orchestration (retrieve -> generate -> respond)
- **Chat Models** (`api/models/chat.py`): ChatState, Citation, SourceSelectionRequest/Response models
- **Tests**: 39 new tests across 3 test files (test_chat_db, test_rag_tool, test_chat_graph, test_chat routes)

### Changed
- `pyproject.toml`: Added `rag` optional dependencies (langgraph, llama-index)
- `api/routes/chat.py`: Added source management endpoints alongside existing SSE streaming

### Test Coverage
- 1181 tests passing, 18 skipped
- New files with matching test files:
  - `storage/chat_db.py` -> `tests/storage/test_chat_db.py`
  - `storage/rag_tool.py` -> `tests/storage/test_rag_tool.py`
  - `agent/chat_graph.py` -> `tests/agent/test_chat_graph.py`
  - `api/routes/chat.py` -> `tests/api/routes/test_chat.py`

## [0.1.0.0] - 2026-03-29

### Added
- TODOS.md with engineering review action items (ENG-001 ~ ENG-006)
- Engineering review process completed via /plan-eng-review

### Notes
- Initial version for Chat with Sources feature branch
- Design document created at `~/.gstack/projects/chenjunhannop-markwritter/chenjunhan-main-design-20260329-185058.md`
