# 前端实现计划

**分支:** main
**创建日期:** 2026-04-04
**作者:** 前端开发团队

---

## 计划摘要

基于现有设计文档实现 Markwritter 7 个核心页面的完整前端。项目已有完整的设计规范 (`docs/figma-design-spec.md`)、页面线框图 (`docs/figma-wireframes.md`) 和实现指南 (`docs/figma-implementation-guide.md`)。

---

## 范围定义

### 包含内容

1. **Chat 页面** - 三栏布局，聊天区域，来源面板，工作室面板
2. **Skills 页面** - 技能列表，技能卡片，运行操作
3. **Explore 页面** - 知识图谱，节点样式，控制面板
4. **Query 页面** - 搜索输入，建议下拉，结果列表
5. **Record 页面** - 快速记录，完整编辑器，AI 辅助面板
6. **Logs 页面** - 日志流，级别过滤，连接状态
7. **Settings 页面** - 配置卡片，表单控件，主题切换

### 排除内容

- 后端 API 开发 (已完成)
- Figma 设计文件创建 (已有设计规范文档)
- 移动端原生应用 (计划中的 Tauri 桌面应用)

---

## 前提条件

### 已完成
- [x] Next.js 15 + React 19 基础架构
- [x] Radix UI + Tailwind CSS 4 组件库
- [x] Zustand 状态管理
- [x] Chat with Sources MVP
- [x] 设计系统文档

### 待完成
- [ ] AI Writing Assist (continue, rewrite, polish)
- [ ] Content Summarization
- [ ] Knowledge Graph 可视化

---

## 实施策略

采用增量方式完成 7 个页面的 UI 实现，复用现有组件库 (Button, Card, Input, Badge, Alert 等)。

### 阶段 1: Chat 页面增强
- 完善三栏布局响应式行为
- 实现 Sources Panel 和 Studio Panel
- 添加消息流式显示优化

### 阶段 2: 内容页面
- Skills 页面完整实现
- Query 页面搜索与 Q&A 双模式
- Record 页面快速记录与完整编辑器

### 阶段 3: 辅助页面
- Explore 页面知识图谱
- Logs 页面日志流
- Settings 页面配置管理

---

## 成本估算

### 人工开发估算

| 阶段 | 内容 | 估算时间 |
|------|------|----------|
| 阶段 1 | Chat 页面 | 2 天 |
| 阶段 2 | Skills + Query + Record | 4 天 |
| 阶段 3 | Explore + Logs + Settings | 3 天 |
| 测试 | 单元测试 + E2E | 2 天 |
| 审查 | 代码审查 + 优化 | 1 天 |
| **总计** | | **12 天** |

### CC+gstack 估算

| 阶段 | 内容 | 估算时间 |
|------|------|----------|
| 阶段 1 | Chat 页面 | 30 分钟 |
| 阶段 2 | Skills + Query + Record | 60 分钟 |
| 阶段 3 | Explore + Logs + Settings | 45 分钟 |
| 测试 | 生成测试用例 | 30 分钟 |
| 审查 | 自动代码审查 | 15 分钟 |
| **总计** | | **~3 小时** |

---

## 风险与假设

### 风险
1. 知识图谱可视化复杂度可能被低估
2. AI Writing Assist 需要额外的后端支持
3. 响应式布局在移动端可能需要额外调整

### 假设
1. 现有组件库满足 80% 以上的需求
2. 设计规范文档准确反映代码实现
3. 不需要重大架构调整

---

## 下一步行动

- [x] 1. 运行 CEO 审查 - 验证范围和策略
- [x] 2. 运行设计审查 - 验证 UI 规范完整性
- [x] 3. 运行工程审查 - 验证架构和测试计划
- [ ] 4. 运行 DX 审查 - 验证开发者体验
- [ ] 5. 最终成本确认

---

## 审查结果汇总

### CEO 审查 (2026-04-04)

**双声音共识**: 都质疑 7 页面策略和 AI 估算

| 维度 | Claude | Codex | 共识 |
|------|--------|-------|------|
| 前提验证 | 🔴 | 🔴 | DISAGREE |
| 问题正确性 | 🔴 | 🔴 | CONFIRMED |
| 6 个月遗憾 | 🔴 | 🔴 | CONFIRMED |
| 替代方案 | 🟡 | 🔴 | DISAGREE |
| 竞争风险 | 🟡 | 🔴 | CONFIRMED |

**用户挑战**: 两个模型都建议收缩到单一核心工作流，而非 7 页面并行

---

### 设计审查 (2026-04-04)

**整体评分**: 3/10 — 需要重大重构才能成为有效的实现指南

| 维度 | Claude | Codex | 共识 |
|------|--------|-------|------|
| 信息层级 | 🔴 | 🔴 | CONFIRMED |
| 缺失状态 | 🔴 | 🔴 | CONFIRMED |
| 用户旅程 | 🔴 | 🔴 | CONFIRMED |
| 具体性 | 🔴 | 🔴 | CONFIRMED |
| 困扰实现者 | 🔴 | 🔴 | CONFIRMED |

**关键发现**: 11 个含糊点，文档彼此冲突，状态矩阵缺失

---

### 工程审查 (2026-04-04)

**整体评分**: 2/10 — 当前基线 build 失败，有 9 个 blocking 问题

| 维度 | Claude | Codex | 共识 |
|------|--------|-------|------|
| 架构 | 🟡 | 🔴 | DISAGREE |
| 边缘情况 | 🔴 | 🔴 | CONFIRMED |
| 测试 | 🔴 | 🔴 | CONFIRMED |
| 安全 | 🔴 | 🔴 | CONFIRMED |
| 隐藏复杂度 | 🔴 | 🔴 | CONFIRMED |

**Blocking 问题**:
1. Record 语法错误 - `next build` 失败
2. Query 核心入口缺失 - SearchInput 未渲染
3. Settings 状态契约假 - 配置不持久化
4. 主题设置不生效 - 未应用到 html/body
5. Record 编辑流程缺失
6. Explore 竞态条件
7. Chat 会话污染
8. 测试假阳性
9. Skills 死链 `/skills/new` 404

---

## 设计文档引用

- [`docs/figma-design-spec.md`](../docs/figma-design-spec.md) - 完整设计规范
- [`docs/figma-wireframes.md`](../docs/figma-wireframes.md) - 页面线框图
- [`docs/figma-implementation-guide.md`](../docs/figma-implementation-guide.md) - 实现指南
- [`docs/ui-prototype.html`](../docs/ui-prototype.html) - HTML 原型
