# TODOS - Markwritter

> **Last Updated:** 2026-04-04 (基于 Codex 评审重新设计)
> **Version:** 0.2.1.0

---

## Completed (Chat with Sources MVP)

All ENG-001 ~ ENG-006 items have been completed as part of the Chat with Sources MVP:

- [x] **ENG-001:** LlamaIndex integration dependencies
- [x] **ENG-002:** SSE Citation protocol extension
- [x] **ENG-003:** Path -> ContentID mapping layer
- [x] **ENG-004:** LRI cache design
- [x] **ENG-005:** Watchdog integration
- [x] **ENG-006:** Conversation History consistency

### MVP Features Delivered

| Feature | Status | Files |
|---------|--------|-------|
| Chat Session DB | Done | `storage/chat_db.py` |
| RAG Search Tool | Done | `storage/rag_tool.py` |
| Source Selection API | Done | `api/routes/chat.py` |
| LangGraph Chat Graph | Done | `agent/chat_graph.py` |
| SSE Streaming + Citations | Done | Frontend + Backend |
| Vector Search Cache | Done | `storage/cache.py` |
| Path Resolver | Done | `storage/path_resolver.py` |

**Test Coverage:** 1910 tests passing (1187 backend + 723 frontend)

> **Codex 评审警示**: "1910 个测试是弱证据，核心风险表面（LLM 集成）仍是 mock 的"

---

## Phase 1: Core AI Loop (当前唯一优先级)

**Codex 建议**: "Build one complete, real-model writing-assist slice. Not the context menu."

### P0 - AI Writing Assist 完整闭环 (~60% → 需完成至 100%)

| ID | Task | Description | Status | 优先级 |
|----|------|-------------|--------|--------|
| **WRT-001** | 真实模型 E2E | 前端→后端→真实 LLM→SSE 流式→应用结果全链路 | ~60% → 需完成 | 🔴 P0 |
| **WRT-004** | 错误恢复完善 | 重试 + 错误详情 + Record 模块支持 | ~90% → 需完成 | 🔴 P0 |
| **WRT-005** | Diff/预览 UX | 用户看到 AI 编辑的 diff，可接受/拒绝/撤销 | 新增 | 🔴 P0 |
| **WRT-006** | 错误分类 UX | 超时/模型/网络错误的清晰区分和提示 | 新增 | 🔴 P0 |
| **WRT-003** | 上下文菜单 | 选中文本右键 AI 选项 | 延后 | ⚪ P2 |
| **WRT-002** | SSE 流式端点 | 已完成 | ✅ Done | - |

**完成标准** (全部需要才是 100%):
- [ ] 用户选择文本 → 触发改写 → 请求 hits 真实模型 (非 mock)
- [ ] 响应通过 SSE 流式返回到编辑器
- [ ] 用户看到 diff 或预览
- [ ] 用户可以接受、拒绝、重试、撤销
- [ ] 错误清晰区分：超时/模型/网络
- [ ] 真实 E2E 测试覆盖，或记录真实响应的回归测试

---

## Phase 2: Summarization (在知识图谱之前)

**Codex 建议**: "SUM-003 should come before SUM-002. Single-note extraction is a simpler proving ground."

| ID | Task | Description | Status | 优先级 |
|----|------|-------------|--------|--------|
| **SUM-003** | 关键点提取 | 单笔记关键洞察提取 | 新增 | 🟡 P1 |
| **SUM-001** | 单笔记摘要 | 为单个笔记生成简洁摘要 | 新增 | 🟡 P1 |
| **SUM-002** | 多笔记摘要 | 跨文档智能摘要 | 新增 | 🟢 P2 |

---

## Phase 3: Infrastructure & Polish (Phase 1&2 完成后)

### 知识图谱 (60% 完成，但 Codex 警示"无可信的边生成=装饰")

| ID | Task | Description | Status | 优先级 |
|----|------|-------------|--------|--------|
| **GRP-001** | Graph Data API | REST API with node/edge relationships | ✅ Done | - |
| **GRP-002** | Graph Visualization | React Flow 交互式图 | ~80% | 🟢 P3 |
| **GRP-003** | Link Suggestions | AI 驱动的关系发现 | 未开始 | 🟢 P3 |

### 性能优化 (Codex: "太早了，除非已有测量的延迟/检索失败")

| ID | Task | Description | 优先级 |
|----|------|-------------|--------|
| **PERF-001** | Vector Search | 替换关键词搜索为 pgvector/FAISS | 🟢 P3 |
| **PERF-002** | Incremental Indexing | Watchdog 实时索引更新 | 🟢 P3 |
| **PERF-003** | Query Optimization | 数据库查询优化和索引 | 🟢 P3 |

### Web Clipping

| ID | Task | Description | 优先级 |
|----|------|-------------|--------|
| **CLIP-001** | URL Content Extraction | 集成 defuddle 或类似服务 | 🟢 P3 |
| **CLIP-002** | Read Mode Processing | 从网页提取主要内容 | 🟢 P3 |
| **CLIP-003** | Auto-Tagging | AI 生成标签 | 🟢 P3 |

---

## Phase 4: Long-term (当前不做)

**Codex 警示**: "Plugin system, API SDK, collaboration, cloud sync, desktop, and voice in a 0.2-stage product."

| ID | Task | Description | 状态 |
|----|------|-------------|------|
| **VOC-001** | Voice Recording | ASR 集成语音转文字 | ⛔ 冻结 |
| **DTP-001** | Tauri Desktop App | 跨平台桌面应用 | ⛔ 冻结 |
| **DTP-002** | Local-First Sync | 离线支持 + 云同步 | ⛔ 冻结 |
| **EXT-001** | Plugin System | 第三方扩展框架 | ⛔ 冻结 |
| **EXT-002** | Cloud Sync Service | 多设备同步 | ⛔ 冻结 |
| **EXT-003** | Team Collaboration | 共享 vaults 和实时编辑 | ⛔ 冻结 |
| **EXT-004** | API SDK | 开发者 SDK | ⛔ 冻结 |

---

## Notes

- **Current Branch:** `main`
- **Blockers:** WRT-001 - 核心 LLM 路径未用真实模型验证
- **Dependencies:** LlamaIndex, LangGraph, LiteLLM all integrated
- **Next Action:** WRT-001 真实模型 E2E + WRT-005 Diff/预览 UX

---

## Codex 评审问题追踪

| 问题 | Codex 发现 | 应对 |
|------|-----------|------|
| 优先级错位 | WRT-001 应是真 P0 | 已调整 |
| 过度工程化 | 知识图谱/插件/桌面太早 | 降级到 P3/P4 |
| 测试幻觉 | 1910 测试但核心路径 mock | WRT-001 真实 E2E |
| 内部矛盾 | Watchdog done vs PERF-002 未来 | 需澄清 |
| 缺失：AI 质量标准 | "Works" 未定义 | WRT-001 完成标准 |
| 缺失：真实模型 eval | Mock 测试不降险 | 需真实响应回归测试 |
| 缺失：可观测性 | AI 调用和 SSE 失败无追踪 | 需添加 |
| 缺失：隐私/安全 | 发送笔记内容到外部模型 | 需评估 |
