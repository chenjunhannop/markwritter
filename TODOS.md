# TODOS - Markwritter

> **Last Updated:** 2026-03-30
> **Version:** 0.2.0.0

---

## ✅ Completed (Chat with Sources MVP)

All ENG-001 ~ ENG-006 items have been completed as part of the Chat with Sources MVP:

- [x] **ENG-001:** LlamaIndex 集成依赖 — Added to `pyproject.toml` rag dependencies
- [x] **ENG-002:** SSE Citation 协议扩展 — Added `citation` event type to `ChatEvent`
- [x] **ENG-003:** Path → ContentID 映射层 — Created `PathResolver` class
- [x] **ENG-004:** LRI 缓存设计 — Created `VectorSearchCache` class
- [x] **ENG-005:** Watchdog 集成 — Created `VaultWatcher` class with watchdog
- [x] **ENG-006:** Conversation History 一致性 — Implemented in `chat_db.py` with session persistence

### MVP Features Delivered

| Feature | Status | Files |
|---------|--------|-------|
| Chat Session DB | ✅ | `storage/chat_db.py` |
| RAG Search Tool | ✅ | `storage/rag_tool.py` |
| Source Selection API | ✅ | `api/routes/chat.py` |
| LangGraph Chat Graph | ✅ | `agent/chat_graph.py` |
| SSE Streaming + Citations | ✅ | Frontend + Backend |
| Vector Search Cache | ✅ | `storage/cache.py` |
| Path Resolver | ✅ | `storage/path_resolver.py` |

**Test Coverage:** 1910 tests passing (1187 backend + 723 frontend)

---

## 🎯 Phase 2: Core Experience (Current Priority)

### P0 - AI Writing Assist (已有 90% 完成)

**状态：** 核心功能已实现，需要验证和收尾

| ID | Task | Description | Status |
|----|------|-------------|--------|
| **WRT-001** | 端到端验证 | 验证前端→后端→LLM 完整链路 | ⏳ 待执行 |
| **WRT-002** | 添加流式端点 | rewrite/polish 流式支持 | ⏳ 待实现 |
| **WRT-003** | 右键菜单 | 选中文字后右键弹出 AI 选项 | ⏳ 待实现 |
| **WRT-004** | 错误恢复 | 重试按钮和错误详情 | ⏳ 待实现 |

**关键发现：** `markwritter/record/assistant.py` 已包含完整的 WritingAssistant 类，支持续写、改写、润色功能，API 路由已存在于 `api/routes/record.py`。

### P0 - Summarization

| ID | Task | Description |
|----|------|-------------|
| **SUM-001** | Single Note Summary | Generate concise summary for single note |
| **SUM-002** | Multi-Note Summary | Cross-document intelligent summarization |
| **SUM-003** | Key Points Extraction | Extract key insights from content |

### P1 - Knowledge Graph Basic

| ID | Task | Description |
|----|------|-------------|
| **GRP-001** | Graph Data API | Build graph data endpoint with node/edge relationships |
| **GRP-002** | Force-Directed Visualization | D3.js or React Flow based graph viz |
| **GRP-003** | Link Suggestions | AI-powered relationship discovery |

---

## 📋 Phase 3: Enhanced Features (Future)

### P1 - Web Clipping

| ID | Task | Description |
|----|------|-------------|
| **CLIP-001** | URL Content Extraction | Integrate defuddle or similar service |
| **CLIP-002** | Read Mode Processing | Extract main content from web pages |
| **CLIP-003** | Auto-Tagging | AI-generated tags for clipped content |

### P1 - Performance Optimization

| ID | Task | Description |
|----|------|-------------|
| **PERF-001** | Vector Search | Replace keyword search with pgvector/FAISS |
| **PERF-002** | Incremental Indexing | Watchdog-based real-time index updates |
| **PERF-003** | Query Optimization | Database query optimization and indexing |

### P2 - Voice & Desktop

| ID | Task | Description |
|----|------|-------------|
| **VOC-001** | Voice Recording | ASR integration for voice-to-text |
| **DTP-001** | Tauri Desktop App | Cross-platform desktop application |
| **DTP-002** | Local-First Sync | Offline support with cloud sync |

---

## 🚀 Phase 4: Ecosystem (Long-term)

| ID | Task | Description |
|----|------|-------------|
| **EXT-001** | Plugin System | Third-party extension framework |
| **EXT-002** | Cloud Sync Service | Multi-device synchronization |
| **EXT-003** | Team Collaboration | Shared vaults and real-time editing |
| **EXT-004** | API SDK | Developer SDK for integrations |

---

## 📝 Notes

- **Current Branch:** `main` (Chat with Sources MVP merged)
- **Next Recommended Branch:** `feature/ai-writing-assist`
- **Blockers:** None
- **Dependencies:** LlamaIndex, LangGraph, LiteLLM all integrated

---

**Maintainer:** Markwritter Team
