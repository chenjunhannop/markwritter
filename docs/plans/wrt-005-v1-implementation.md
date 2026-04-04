# WRT-005-V1 实现总结

**日期**: 2026-04-04
**状态**: ✅ 核心功能完成
**完成度**: 90% (待选中文本支持)

---

## 实现概览

WRT-005-V1 是 AI Writing Assist 的简化版 Diff/预览功能，目标是在 1 个月内交付核心价值，验证用户对 AI 修改的信任度和接受率。

### 设计策略

- **V1 简化版**（本月交付）：完成后显示 diff，简单预览，低风险
- **V2 完整版**（后续差异化）：流式词级 diff，DiffDecorator 覆盖层，复杂

---

## 已完成功能

### 1. 后端 API (Python FastAPI)

#### 文件：`markwritter/record/assistant.py`

```python
@dataclass
class DiffDelta:
    """A single diff operation."""
    type: str  # 'add', 'remove', 'replace'
    text: str
    original: Optional[str] = None

@dataclass
class DiffResult:
    """Result of AI operation with diff information."""
    original: str
    modified: str
    diff: list[DiffDelta]
```

**新增方法**:
- `_compute_simple_diff()` - V1 简单全量替换 diff
- `rewrite_with_diff()` - 带 diff 的改写
- `polish_with_diff()` - 带 diff 的润色

#### 文件：`markwritter/api/routes/record.py`

**新增响应模型**:
- `RewriteWithDiffResponse` - 改写 diff 响应
- `PolishWithDiffResponse` - 润色 diff 响应
- `AITelemetryEvent` - 遥测事件
- `AITelemetryResponse` - 遥测响应

**新增端点**:
- `POST /ai-assist/rewrite/diff` - 带 diff 的改写
- `POST /ai-assist/polish/diff` - 带 diff 的润色
- `POST /ai-assist/telemetry` - 遥测追踪

---

### 2. 前端 API (TypeScript)

#### 文件：`web/lib/record-api.ts`

**新增类型**:
```typescript
interface DiffDelta {
  type: string;  // 'add', 'remove', 'replace', 'error'
  text: string;
  original?: string | null;
}

interface AIRewriteWithDiffResponse {
  original: string;
  modified: string;
  diff: DiffDelta[];
}

interface AITelemetryRequest {
  action: string;  // 'rewrite', 'polish', 'continue'
  text_length: number;
  time_to_result_ms?: number;
  accepted?: boolean;
  error?: string;
  metadata?: Record<string, unknown>;
}
```

**新增函数**:
- `aiRewriteWithDiff()` - 带 diff 的改写
- `aiPolishWithDiff()` - 带 diff 的润色
- `trackAITelemetry()` - 遥测追踪

---

### 3. 前端状态管理 (Zustand)

#### 文件：`web/lib/record-store.ts`

**新增状态**:
```typescript
// Diff state
baseContent: string | null;
generatedContent: string | null;
showDiffPreview: boolean;
diffResult: AIRewriteWithDiffResponse | AIPolishWithDiffResponse | null;
aiStartTime: number | null;
aiActionType: string | null;

// Undo state
lastAcceptedContent: string | null;
lastAcceptTimestamp: number | null;
canUndo: boolean;
```

**新增动作**:
- `aiRewriteWithDiff(style)` - 带 diff 的改写
- `aiPolishWithDiff()` - 带 diff 的润色
- `acceptDiff()` - 接受 diff（带遥测）
- `rejectDiff()` - 拒绝 diff（带遥测）
- `undoLastAccept()` - 撤销接受（30 秒超时）

---

### 4. 前端组件

#### 文件：`web/components/editor/diff-preview.tsx`

**新建组件**: `DiffPreview`
- 并排预览原文和修改后内容
- Accept/Reject 按钮
- 字符数变化显示

#### 文件：`web/components/editor/ai-assist-panel.tsx`

**更新内容**:
- 移除"保存笔记"限制
- 集成 DiffPreview 组件
- 显示 Undo 按钮（接受后 30 秒内）
- 使用 diff 版本 API

---

## 用户交互流程

### 1. 基本流程

```
用户输入内容
    ↓
点击 Rewrite/Polish 按钮
    ↓
AI 处理（非流式）
    ↓
显示 Diff 预览
    ↓
用户 Accept / Reject
    ↓
Accept: 应用修改，显示 Undo 按钮 (30s)
Reject: 恢复原文
```

### 2. Undo 流程

```
用户 Accept 修改
    ↓
记录时间戳和原始内容
    ↓
显示 Undo 按钮（黄色提示条）
    ↓
30 秒内点击 Undo → 恢复原始内容
30 秒后 → Undo 按钮自动隐藏
```

### 3. 遥测追踪

**追踪事件**:
- AI 操作开始（action, text_length, start_time）
- AI 操作完成（time_to_result）
- 用户 Accept/Reject（accepted）
- 错误（error）

**端点**: `POST /ai-assist/telemetry`

---

## 完成标准对比

| 标准 | 要求 | 状态 |
|------|------|------|
| 移除"保存笔记"限制 | 允许草稿使用 AI | ✅ |
| 用户选择文本 → 触发 AI | 点击按钮触发 | ✅ (整个内容) |
| 等待完成 → 看到 diff 预览 | 并排预览 | ✅ |
| Accept/Reject | 按钮操作 | ✅ |
| Undo (30 秒) | 超时撤销 | ✅ |
| 埋点记录 | 操作类型/长度/时间/accept | ✅ |
| 选中文本操作 | 仅处理选中部分 | ⏳ 待实现 |

---

## 待完成项目

### 1. 选中文本操作支持

当前实现针对整个笔记内容，需要扩展为：
- 支持编辑器中选中文本
- 仅改写/润色选中部分
- 正确合并回原文

### 2. 更智能的 Diff 算法

当前 V1 使用简单全量替换：
```python
if original == modified:
    return []
return [DiffDelta(type="replace", text=modified, original=original)]
```

V2 需要使用 `diff-match-patch` 进行词级 diff。

---

## 技术债务

1. **内存存储**: 遥测事件存储在内存列表 `_ai_telemetry_events`，生产环境需要数据库
2. **静默失败**: 遥测错误使用 `.catch(() => {})` 静默处理，可能需要日志记录
3. **类型安全**: 部分 TypeScript 测试文件存在类型错误（预先存在的问题）

---

## 下一步

### P0 (本周)
1. 实现选中文本操作支持
2. 添加 E2E 测试验证完整流程
3. 真实 LLM 模型测试

### P1 (下周)
1. 部署到生产环境
2. 收集用户遥测数据
3. 分析 Accept 率和使用率

### P2 (后续)
1. WRT-005-V2 流式词级 diff
2. DiffDecorator 覆盖层
3. 部分接受/拒绝

---

## 文件清单

### 后端
- `markwritter/record/assistant.py` - 修改
- `markwritter/api/routes/record.py` - 修改

### 前端
- `web/lib/record-api.ts` - 修改
- `web/lib/record-store.ts` - 修改
- `web/components/editor/diff-preview.tsx` - 新建
- `web/components/editor/ai-assist-panel.tsx` - 修改

---

## Codex 评审结论

> "Variant C is strong as a later differentiator. For this month's goal, I'd ship a simpler post-generation diff preview first."

V1 实现符合 Codex 建议的简化方案，先交付核心价值，后续再通过 V2 实现差异化功能。
