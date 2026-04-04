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
| **WRT-005-V1** | Diff 预览 (简化版) | 完成后显示 diff + Accept/Reject/Undo | 新增 | 🔴 P0 |
| **WRT-005-V2** | Diff 预览 (完整版) | 流式词级 diff + DiffDecorator | 延后至 V1 后 | ⚪ P1 |
| **WRT-006** | 错误分类 UX | 超时/模型/网络错误的清晰区分和提示 | 新增 | 🔴 P0 |
| **WRT-003** | 上下文菜单 | 选中文本右键 AI 选项 | 延后 | ⚪ P2 |
| **WRT-002** | SSE 流式端点 | 已完成 | ✅ Done | - |

**完成标准** (全部需要才是 100%):

**V1 完成标准**:
- [ ] 移除"保存笔记"限制 — 允许在草稿上使用 AI
- [ ] 用户选择文本 → 触发改写 → 等待完成 → 看到 diff 预览
- [ ] 用户可以 Accept（替换选区）/ Reject（关闭）
- [ ] Undo 支持（30 秒内）
- [ ] 埋点记录：操作类型、文本长度、时间、accept/reject

**V2 完成标准**:
- [ ] 流式词级 diff 渲染
- [ ] DiffDecorator 覆盖层与 textarea 同步
- [ ] 部分接受/拒绝单个建议
- [ ] 错误清晰区分：超时/模型/网络
- [ ] 真实 E2E 测试覆盖，或记录真实响应的回归测试

---

## WRT-005 设计规范 (Design Review + Codex Review Approved)

**设计策略**: V1 简化版 (1 个月交付) → V2 完整版 (差异化功能)

### Codex 评审结论 (2026-04-04)

> **Bottom line**: "Variant C is strong as a later differentiator. For this month's goal, I'd ship a simpler post-generation diff preview first."

**核心风险**:
1. 技术风险高 — `textarea` 需要镜像覆盖层，scroll sync/对齐/IME 都是坑
2. 流式词级 diff 闪烁风险 — 范围不稳定，计算开销大
3. 对 1 个月创业时间线过度工程化

**成功指标评估**:
- Accept 率 >50%：可能，但仅限于**小范围编辑**（段落/选中）
- 使用率提升：有帮助，但更大摩擦是"必须先保存笔记"

---

### WRT-005 V1 (简化版 - 本月交付) | Completeness: 7/10

**目标**: 快速交付，验证核心假设（diff 预览提升信任和接受率）

| 特性 | 实现方式 | 状态 |
|------|----------|------|
| 作用范围 | 选中文本 / 当前段落 | 新增 |
| 生成模式 | 等待完成，非流式 | ✅ 完成 |
| Diff 显示 | 完成后显示 inline 或 side panel diff | ✅ 完成 |
| 操作 | 一键 Accept / Reject / Undo | ✅ 完成 |
| 移除限制 | 不需要保存笔记即可使用 AI | ✅ 完成 |
| 埋点 | 操作类型、文本长度、时间、accept/reject | ✅ 完成 |

**架构实现 (V1 完成)**:
- [x] 后端：`DiffDelta` 和 `DiffResult` 数据类
- [x] 后端：`_compute_simple_diff` 方法（V1 简单全量替换 diff）
- [x] 后端：`rewrite_with_diff` 和 `polish_with_diff` 方法
- [x] 后端：`/ai-assist/rewrite/diff` 和 `/ai-assist/polish/diff` 端点
- [x] 后端：`/ai-assist/telemetry` 埋点端点
- [x] 前端：`DiffDelta` 和 `AIRewriteWithDiffResponse`/`AIPolishWithDiffResponse` 类型
- [x] 前端：`aiRewriteWithDiff` 和 `aiPolishWithDiff` API 函数
- [x] 前端：`trackAITelemetry` 遥测函数
- [x] 前端：`record-store.ts` diff 状态（`baseContent`, `generatedContent`, `showDiffPreview`, `diffResult`）
- [x] 前端：`record-store.ts` 遥测状态（`aiStartTime`, `aiActionType`）
- [x] 前端：`acceptDiff` 和 `rejectDiff` 动作（带遥测追踪）
- [x] 前端：`undoLastAccept` 动作（30 秒超时）
- [x] 前端：`DiffPreview` 组件（并排预览 + Accept/Reject 按钮）
- [x] 前端：`AIAssistPanel` 集成 diff 预览和 Undo 按钮
- [ ] 前端：支持选中文本操作（当前针对整个内容）

**完成标准**:
- [x] 后端 API 端点 `/ai-assist/rewrite/diff` 和 `/ai-assist/polish/diff`
- [x] 后端 `WritingAssistant` 添加 `rewrite_with_diff` 和 `polish_with_diff` 方法
- [x] 前端 API 客户端添加 `aiRewriteWithDiff` 和 `aiPolishWithDiff` 函数
- [x] 前端 `record-store.ts` 添加 diff 状态管理（`baseContent`, `generatedContent`, `showDiffPreview`, `acceptDiff`, `rejectDiff`）
- [x] 前端 `DiffPreview` 组件实现
- [x] 前端 `AIAssistPanel` 集成 diff 预览
- [ ] 移除"保存笔记"限制 — 允许在草稿上使用 AI
- [ ] 用户选择文本 → 触发改写 → 等待完成 → 看到 diff 预览
- [ ] 用户可以 Accept（替换选区）/ Reject（关闭）
- [ ] Undo 支持（30 秒内）
- [ ] 埋点记录：操作类型、文本长度、时间、accept/reject

---

### WRT-005 V2 (完整版 - 后续差异化) | Completeness: 10/10

**目标**: 流式词级 diff，最佳用户体验，竞争差异化

| 特性 | 实现方式 | 状态 |
|------|----------|------|
| 流式 diff | SSE 实时推送 diff 增量 | 延后 |
| 词级高亮 | 绿色新增，红色删除线 | 延后 |
| 覆盖层 | `DiffDecorator` 镜像 `textarea` | 延后 |
| 部分接受 | 逐个建议 Accept/Reject | 延后 |
| 段落级 | 自动检测当前段落 | 延后 |

**架构影响 (V2)**:
- 前端需要新增 `DiffDecorator` 组件层，覆盖在 `textarea` 之上
- `record-store.ts` 需要扩展：`pendingDiff`, `acceptDiff()`, `rejectDiff()`, `undoDiff()`
- 后端 SSE 需要支持 diff 格式：`{ type: 'diff_delta', additions: [...], deletions: [...] }`
- 需要新的 `useDiffStream` hook 处理流式 diff 合并
- 后端需要 diff 计算服务（词级/句子级）

**交互状态表 (V2)**:

| 状态 | 用户看到 | 用户操作 |
|------|----------|----------|
| **Idle** | 正常编辑器，AI 按钮可用 | 点击 Continue/Rewrite/Polish |
| **Streaming** | 行内高亮显示 AI 生成内容，绿色背景 = 新增，红色删除线 = 删除 | 点击 Cancel 停止生成 |
| **Complete** | 底部浮动条：显示更改数量，Accept All / Reject All 按钮 | 接受或拒绝 |
| **Accepted** | 更改应用到编辑器，Toolbar 显示 Undo 按钮 (30 秒) | 点击 Undo 撤销 |
| **Rejected** | 恢复原文，浮动条关闭 | — |
| **Error** | 底部浮动条显示错误消息 + Retry 按钮 | 点击 Retry 重试 |

**视觉规范 (V2)**:

- **新增内容**: 背景色 `#dcfce7` (green-100)，文字 `#14532d` (green-900)
- **删除内容**: 删除线，背景色 `#fee2e2` (red-100)，文字 `#450a0a` (red-900)，透明度 0.7
- **替换内容**: 行内 badge 样式 `[原文 → 新文]`
- **浮动条**: 固定在编辑器底部，白色背景，阴影，圆角 8px
- **按钮**: Accept (primary, blue-500), Reject (outline, gray), Undo (ghost, 仅 accepted 后可用)

### 设计 artifacts

- 比较板：`~/.gstack/projects/chenjunhannop-markwritter/designs/ai-writing-diff-20260404/comparison-board.html`
- 变体文档：`variant-A.txt`, `variant-B.txt`, `variant-C.txt`
- Codex Review: `/Users/chenjunhan/.claude/projects/-Users-chenjunhan-dev-github-project-markwritter/dcda5049-ad81-4c27-bd8f-c9808e3c74a2/tool-results/bi6vumesj.txt`

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
