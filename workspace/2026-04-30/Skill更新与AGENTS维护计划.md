# Skill 更新与 AGENTS.md 维护计划

> **项目**: Markwritter
> **日期**: 2026-04-30
> **状态**: 已完成

---

## 目标

审查当前全局工作流资产（skills、agents、commands、instructions）与 Markwritter 项目实际技术栈的适配程度，更新项目 `AGENTS.md` 使其包含项目特定约定，并识别需要新增、重构或废弃的工作流资产。

---

## 目录

1. 问题框定
2. 事实、推断与不确定性
3. 验收标准
4. 计划前工作流审计
5. 受影响层与文件清单
6. 实施计划
7. 风险与缓解
8. 验证清单
9. 计划后工作流维护

---

## 1. 问题框定

**一句话重述**: 项目 `AGENTS.md` 存在三层问题——12 条 skill routing 规则全部指向不存在的 skill、缺少项目特定约定、全局工作流资产中存在与 Vite SPA 技术栈不匹配的引用——需要清除失效内容、补充有效约定、并清理过时引用。

**角色**: 开发者
**触发条件**: 项目已从 Next.js 迁移到 Vite SPA，但项目 AGENTS.md 的 12 条路由规则全部失效（引用不存在的 skill），且缺少 build/test/lint 命令和架构约定。

**预期结果**:
- 项目 `AGENTS.md` 清除全部 12 条已失效路由，替换为指向实际存在 skill 的新路由
- 项目 `AGENTS.md` 补充项目特定约定（技术栈、命令、架构）
- 项目 `AGENTS.md` 包含独立"前端约定"章节，用强措辞覆盖 `nextjs-app-router` 的误导
- 删除废弃的 `skills/hello/` 并清理 README.md、CODEMAP.md 中的死引用
- 全局工作流资产不被动

**非目标**:
- 不改变全局 `AGENTS.md` 或全局工作流资产（这些服务所有项目）
- 不引入新的全局 agent、command 或 instruction
- 不改变项目业务代码
- 不全面重写 README.md 或 CODEMAP.md（仅清理 hello 相关死引用）

## 2. 事实、推断与不确定性

### 2.1 已确认事实

| # | 事实 | 来源 |
|---|------|------|
| F1 | 前端已从 Next.js 迁移到 Vite SPA + react-router-dom v7 | `web/package.json`、`workspace/2026-04-30/前端框架迁移计划.md` |
| F2 | 后端是 Python FastAPI，非 Node.js | `pyproject.toml`、`markwritter/api/` |
| F3 | 前端使用 biome（非 eslint）做 lint | `web/biome.json`、`web/package.json` |
| F4 | 前端使用 vitest（非 jest）做测试 | `web/package.json` |
| F5 | 后端使用 pytest + ruff + black | `pyproject.toml` |
| F6 | 全局有 29 个 skills、9 个 agents、9 个 commands、10 个 instructions | `~/.config/opencode/` 目录扫描（含 `acceptance-criteria`） |
| F7 | 项目 `AGENTS.md` 仅 21 行，12 条 routing 规则全部指向不存在的 skill | 文件内容确认 |
| F8 | 项目 `skills/` 目录只有示例 `hello` skill | 目录扫描 |
| F9 | 全局 `frontend-implementer` 的 `permission.skill` 硬编码了 `nextjs-app-router: allow` | `agents/frontend-implementer.md` 第 14 行 |
| F10 | 多个 agents/commands 引用 `chrome_devtools` 和 `playwright` MCP，但项目未配置 | `opencode.json` 无此 MCP 条目 |
| F11 | 全局 skill `nextjs-app-router` 仅适用于 Next.js 项目 | skill 名称和内容确认 |
| F12 | 后端 AI 层使用 LangGraph + LiteLLM | `config.yaml`、`pyproject.toml` rag extras |
| F13 | 项目 AGENTS.md 引用的 12 个 skill（office-hours, investigate, ship, qa, review, document-release, retro, design-consultation, design-review, plan-eng-review, checkpoint, health）在全局 skills 中全部不存在 | AGENTS.md 第 10-21 行 vs `~/.config/opencode/skills/` 目录 |
| F14 | README.md 第 56/126/130-131 行和 CODEMAP.md 第 83 行引用 `hello` skill | 文件内容确认 |
| F15 | CODEMAP.md 多处过时：第 13 行仍写 "Next.js"、第 73 行 `app/` 描述为 "Next.js pages"、第 121 行 config 示例用 `gpt-4o-mini`、端口仍为 :3000 | 文件内容确认 |
| F16 | OpenCode 无项目级 skill deny 配置；agent frontmatter 的 `permission.skill` 优先级高于项目 AGENTS.md 的 prompt 指令 | `opencode.json` 结构分析：skill 权限仅在 agent 级配置 |

### 2.2 推断

| # | 推断 | 依据 | 信心 |
|---|------|------|------|
| I1 | `nextjs-app-router` skill 对当前项目无用，但可能被其他 Next.js 项目复用 | F1、F11 | 高 |
| I2 | `frontend-implementer` 会加载 `nextjs-app-router` skill（permission 硬编码 allow），项目 AGENTS.md 无法从配置层面阻止加载，只能用 prompt 层强措辞覆盖其建议 | F9、F16 | 高 |
| I3 | `chrome_devtools`/`playwright` 引用不会报错，只是这些工具不可用 | F10 | 高 |
| I4 | `hello` skill 是脚手架示例，对实际开发无帮助 | F8、`skill.yaml` 内容 | 高 |
| I5 | AGENTS.md 的 12 条失效路由意味着 skill routing 对本项目从未生效过 | F13 | 高 |

### 2.3 不确定性

| # | 不确定项 | 影响 | 验证方式 |
|---|---------|------|---------|
| U1 | 用户是否计划配置 chrome_devtools/playwright MCP | 影响是否保留相关引用 | 直接询问 |
| U2 | 是否需要项目级 FastAPI 后端 skill | 影响项目 skills/ 目录内容 | 评估全局 `rest-api-design` 等是否足够 |

### 2.4 决策理由

- **清除失效路由再补充新内容（C1）**：12 条路由指向不存在的 skill，继续保留只会误导 agent。先清除再重建。
- **更新项目 AGENTS.md 而非全局资产**：项目特定约定应就近放置；全局资产服务所有项目，不应因单个项目变化而修改。
- **用独立"前端约定"章节强措辞覆盖而非依赖 skill deny（M2）**：OpenCode 不支持项目级 skill deny（F16），`frontend-implementer` 的 `permission.skill` 硬编码了 `nextjs-app-router: allow`。唯一可行方案是在 AGENTS.md 的 prompt 层用强措辞明确"本前端不使用 Next.js"。
- **保留 `chrome_devtools`/`playwright` 引用不动**：全局 agents/commands 中的通用能力引用，未来配置后即可生效；无需为单个项目清理。
- **仅清理 hello 死引用而非全面重写 README/CODEMAP（M1）**：全面重写超出本次范围；CODEMAP.md 的 Next.js/端口/配置过时问题记入未来关注。

## 3. 验收标准

| # | 标准 | 可观察方式 |
|---|------|-----------|
| AC1 | 项目 `AGENTS.md` 已清除全部 12 条失效路由，新路由仅指向实际存在的 skill | `grep -c 'invoke office-hours\|invoke investigate\|invoke ship\|invoke qa\|invoke review\|invoke document-release\|invoke retro\|invoke design-consultation\|invoke design-review\|invoke plan-eng-review\|invoke checkpoint\|invoke health' AGENTS.md` 返回 0 |
| AC2 | 项目 `AGENTS.md` 包含完整技术栈概述 | 读取文件，确认包含 Vite/React/FastAPI/LiteLLM 等信息 |
| AC3 | 项目 `AGENTS.md` 包含 build/dev/test/lint 命令 | 读取文件，确认包含 `pnpm dev`、`pytest`、`biome` 等命令 |
| AC4 | 项目 `AGENTS.md` 包含独立"前端约定"章节，用强措辞覆盖 Next.js 误导 | 读取文件，确认存在独立章节明确声明"不使用 Next.js" |
| AC5 | `skills/hello/` 目录已删除 | `ls skills/hello/` 返回错误 |
| AC6 | README.md 和 CODEMAP.md 无 `hello` 死引用 | `grep -n 'hello' README.md docs/CODEMAP.md` 仅返回无害匹配 |
| AC7 | 全局工作流资产未被修改 | `git -C ~/.config/opencode status --short` 返回空或无相关文件变更 |
| AC8 | 计划后工作流维护章节记录了所有决策 | 计划文档第 9 节完整 |
| AC9 | 项目 `AGENTS.md` 长度不超过 80 行 | `wc -l AGENTS.md` ≤ 80 |

## 4. 计划前工作流审计

### 4.1 全局 Skills（29 个）

| Skill | 与本项目相关度 | 建议 |
|-------|-------------|------|
| `main-agent-orchestration` | ✅ 核心 | 保持不变 |
| `delivery-planning` | ✅ 核心 | 保持不变 |
| `skill-authoring` | ✅ 维护用 | 保持不变 |
| `codex-second-review` | ✅ 审查用 | 保持不变 |
| `frontend-implementation-core` | ✅ 高 | 保持不变（通用前端指引） |
| `frontend-design` | ✅ 高 | 保持不变 |
| `ui-structure-review` | ✅ 高 | 保持不变 |
| `form-validation` | ✅ 高 | 保持不变 |
| `list-detail-crud` | ✅ 高 | 保持不变 |
| `frontend-backend-contract-sync` | ✅ 高 | 保持不变 |
| `rest-api-design` | ✅ 高 | 保持不变 |
| `controller-service-repository` | ✅ 高 | 保持不变 |
| `input-validation` | ✅ 高 | 保持不变 |
| `auth-permission-check` | 中 | 保持不变 |
| `db-schema-migration` | 中 | 保持不变（未来 Phase 用） |
| `debug-reproduction` | ✅ 高 | 保持不变 |
| `integration-test-writing` | ✅ 高 | 保持不变 |
| `acceptance-criteria` | 中 | 保持不变 |
| **`nextjs-app-router`** | ❌ 不适用 | 无法从项目层阻止加载，用 AGENTS.md prompt 强措辞覆盖 |
| `browser-research-workflow` | ✅ 研究 | 保持不变 |
| `browser-latest-research` | ✅ 研究 | 保持不变 |
| `dynamic-site-investigation` | 中 | 保持不变 |
| `react-component-build` | ✅ 高 | 保持不变 |
| `responsive-states` | 中 | 保持不变 |
| `safe-refactor` | 中 | 保持不变 |
| `source-attribution` | 中 | 保持不变 |
| `task-breakdown` | 中 | 保持不变 |
| `requirement-clarification` | 中 | 保持不变 |

### 4.2 全局 Agents（9 个）

| Agent | 与本项目相关度 | 问题 | 建议 |
|-------|-------------|------|------|
| `planner` | ✅ 核心 | 无 | 保持不变 |
| `frontend-implementer` | ✅ 核心 | 引用 `nextjs-app-router` skill | 项目 AGENTS.md 覆盖 |
| `backend-implementer` | ✅ 核心 | 无 | 保持不变 |
| `ui-designer` | ✅ 高 | 引用 `chrome_devtools`/`playwright`（未配置） | 保持不变，未来按需配置 |
| `bug-investigator` | ✅ 高 | 同上 | 保持不变 |
| `test-writer` | ✅ 高 | 同上 | 保持不变 |
| `browser-researcher` | ✅ 研究 | 无 | 保持不变 |
| `skill-author` | ✅ 维护 | 无 | 保持不变 |
| `codex-reviewer` | ✅ 审查 | 无 | 保持不变 |

### 4.3 全局 Commands（9 个）

| Command | 与本项目相关度 | 建议 |
|---------|-------------|------|
| `feature-spec` | ✅ 核心 | 保持不变 |
| `frontend-feature` | ✅ 核心 | 保持不变 |
| `backend-feature` | ✅ 核心 | 保持不变 |
| `fullstack-feature` | ✅ 核心 | 保持不变 |
| `bug-fix` | ✅ 高 | 保持不变 |
| `ui-design` | ✅ 高 | 保持不变 |
| `test-gap` | ✅ 高 | 保持不变 |
| `codex-review` | ✅ 审查 | 保持不变 |
| `latest-research` | ✅ 研究 | 保持不变 |

### 4.4 全局 Instructions（10 个）

| Instruction | 与本项目相关度 | 建议 |
|-------------|-------------|------|
| `core-workflow` | ✅ 核心 | 保持不变 |
| `deliberate-reasoning` | ✅ 核心 | 保持不变 |
| `plan-artifacts` | ✅ 核心 | 保持不变 |
| `markdown-write-safety` | ✅ 核心 | 保持不变 |
| `orchestration-boundaries` | ✅ 核心 | 保持不变 |
| `product-delivery` | ✅ 核心 | 保持不变 |
| `frontend-quality` | ✅ 核心 | 保持不变 |
| `backend-quality` | ✅ 核心 | 保持不变 |
| `verification` | ✅ 核心 | 保持不变 |
| `source-governance` | ✅ 核心 | 保持不变 |

### 4.5 项目 Skills（1 个）

| Skill | 评估 | 建议 |
|-------|------|------|
| `hello` | 示例脚手架，无实际用途 | 废弃（删除） |

### 4.6 审计结论

- 全局资产质量高，无需因本项目修改全局文件。
- **关键发现（C1）**：项目 AGENTS.md 的 12 条 routing 规则全部指向不存在的 skill，必须先清除再重建。
- `nextjs-app-router` skill 被 `frontend-implementer` 硬编码 allow（F9），项目无法从配置层阻止加载（F16），只能用 prompt 层强措辞覆盖。
- `hello` skill 应废弃，README.md 和 CODEMAP.md 存在死引用需清理（M1）。
- 全局 agents/commands 对 `chrome_devtools`/`playwright` 的引用保留不动，未来配置后自动生效。

## 5. 受影响层与文件清单

### 5.1 受影响层

| 层 | 影响程度 | 说明 |
|----|---------|------|
| Docs | 主要 | 项目 AGENTS.md 是主要变更目标 |
| Config | 次要 | 废弃 `skills/hello/` 目录 |
| 全局工作流资产 | 无 | 不修改全局 `~/.config/opencode/` 下任何文件 |

### 5.2 受影响文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `AGENTS.md`（项目根目录） | **重写** | 清除 12 条失效路由，补充项目特定约定 |
| `skills/hello/` | **删除** | 废弃示例 skill（含 `run.py`、`skill.yaml`、`__pycache__/`） |
| `README.md` | **局部编辑** | 清理 hello 相关段落（第 56、126、130-131 行） |
| `docs/CODEMAP.md` | **局部编辑** | 清理 hello 相关行（第 83 行） |
| `~/.config/opencode/*` | **不变** | 全局资产保持原样 |

## 6. 实施计划

### Step 1a: 清除项目 AGENTS.md 失效路由（C1）

**目标**: 删除全部 12 条指向不存在 skill 的 routing 规则。

**操作**:
- 删除 AGENTS.md 第 9-21 行（`Key routing rules:` 及全部 12 条 `invoke` 规则）
- 保留 `# Markwritter` 标题和 `## Skill routing` 章节框架

**验证**: `grep -c 'invoke office-hours\|invoke investigate\|invoke ship\|invoke qa\|invoke review\|invoke document-release\|invoke retro\|invoke design-consultation\|invoke design-review\|invoke plan-eng-review\|invoke checkpoint\|invoke health' AGENTS.md` 返回 0。

### Step 1b: 补充项目 AGENTS.md 新内容

**目标**: 在清除后的 AGENTS.md 中补充项目特定约定。

**新增内容**:
1. **技术栈概述**: Vite SPA + React + react-router-dom / FastAPI + LangGraph + LiteLLM / Zustand + Radix UI + Tailwind
2. **开发环境命令**: `pnpm dev`、`uvicorn`、`pytest`、`vitest`、`biome check`、`ruff check`
3. **项目架构关键路径**: `markwritter/`（后端）、`web/src/`（前端）、`skills/`（agent skills）
4. **Skill routing（新规则）**: 仅映射实际存在的全局 skills（`delivery-planning`、`codex-second-review` 等），不映射不存在的 skill
5. **前端约定（独立章节）**: 用强措辞声明"本前端是 Vite SPA + react-router-dom，不使用 Next.js。忽略任何 App Router、Server Components、Server Actions 或 `'use client'` 指令的建议。前端路由使用 `react-router-dom` 的 `BrowserRouter` + `Routes`，不是 Next.js 文件系统路由。"
6. **后端约定**: FastAPI + LangGraph + LiteLLM 模式

**长度约束**: 不超过 80 行（AC9）。

**验证**: 读取更新后的文件，确认 AC1-AC4、AC9 满足。

### Step 2a: 废弃 hello skill

**目标**: 删除无用的示例 skill。

**操作**:
- 删除 `skills/hello/` 目录（含 `run.py`、`skill.yaml`、`__pycache__/`）

**验证**: `ls skills/hello/` 返回错误。

### Step 2b: 清理 README.md 和 CODEMAP.md 死引用（M1）

**目标**: 消除删除 hello 后的死引用。

**操作**:
- `README.md` 第 56 行: 将 `│   └── hello/            # Example skill` 改为适当描述（如删除该行或改为通用说明）
- `README.md` 第 126 行: 将 `markwritter run hello name=World` 移除或替换为有效示例
- `README.md` 第 130-131 行: 将 `> hello` / `> hello --name Alice` 移除或替换
- `docs/CODEMAP.md` 第 83 行: 将 `| hello | Example skill |` 行移除

**验证**: `grep -n 'hello' README.md docs/CODEMAP.md` 无匹配或仅剩无害上下文引用。

### Step 3: 评估是否需要新增项目级 skill

**评估条件**:
- 如果全局 `rest-api-design` + `controller-service-repository` 足以覆盖 FastAPI 开发 → 不新增
- 如果全局 `frontend-implementation-core` 足以覆盖 Vite+React 开发 → 不新增
- 如果 AI/LangGraph agent 开发有独特模式需要固化 → 考虑新增

**当前判断**: 全局 skills 已足够通用，暂不新增项目级 skill。如果后续开发中发现重复模式，再按需创建。

### Step 4: 验证全局资产未被动

**操作**: 确认 `~/.config/opencode/` 下文件未发生修改。

**验证**: `git -C ~/.config/opencode status --short` 返回空或无相关文件变更。

### Step 5: 最终验收

**操作**: 按第 3 节验收标准逐项检查。

**验证**: 全部 AC1-AC9 通过。

## 7. 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|------|------|------|
| R1 | 项目 AGENTS.md 更新后内容过长，导致 agent 上下文膨胀 | 低 | 中 | 硬约束 ≤80 行（AC9），只记录最常用约定；细节放在全局 `instructions/` 或 `skills/` |
| R2 | `frontend-implementer` 加载 `nextjs-app-router` skill 后产生误导性建议 | 中 | 中 | 在 AGENTS.md 中用独立"前端约定"章节强措辞声明"不使用 Next.js"；这是 prompt 层唯一可行的覆盖方式 |
| R3 | 删除 `hello` 后 README.md / CODEMAP.md 残留死引用 | 低 | 低 | Step 2b 显式清理；用 `grep` 验证 |
| R4 | CODEMAP.md 全面过时（Next.js 描述、旧端口、旧配置示例）误导新读者 | 中 | 低 | 本次仅清理 hello 引用；过时技术栈描述记入未来关注 |
| R5 | README.md CLI 示例段删除 hello 后可能需要替换为有效示例 | 低 | 低 | 如果 `markwritter list-skills` 等命令仍有效则替换；否则注释掉整个 CLI 示例段 |

**正向说明**: `chrome_devtools`/`playwright` MCP 未来配置后，现有 agents/commands 中的引用会自动生效，无需额外操作。

## 8. 验证清单

- [x] 项目 `AGENTS.md` 已清除全部 12 条失效路由（AC1 grep 验证）✅ 0 条匹配
- [x] 项目 `AGENTS.md` 包含技术栈概述（AC2）✅ 7 处覆盖
- [x] 项目 `AGENTS.md` 包含 build/dev/test/lint 命令（AC3）✅ 5 处覆盖
- [x] 项目 `AGENTS.md` 包含独立"前端约定"章节，强措辞覆盖 Next.js 误导（AC4）✅ 存在
- [x] `skills/hello/` 目录已删除（AC5）✅
- [x] README.md 和 CODEMAP.md 无 `hello` 死引用（AC6 grep 验证）✅ 无匹配
- [x] 全局 `~/.config/opencode/` 文件未修改（AC7）✅
- [x] 计划后工作流维护章节记录了所有决策（AC8）✅
- [x] 项目 `AGENTS.md` 长度 ≤80 行（AC9）✅ 68 行

## 9. 计划后工作流维护

### 资产决策汇总

| 资产 | 决策 | 理由 |
|------|------|------|
| 项目 `AGENTS.md` | **重写** | 清除 12 条失效路由（C1），补充项目特定约定 |
| 项目 `skills/hello/` | **废弃** | 示例脚手架，无实际开发价值 |
| `README.md` | **局部编辑** | 清理 hello 死引用（第 56/126/130-131 行） |
| `docs/CODEMAP.md` | **局部编辑** | 清理 hello 死引用（第 83 行） |
| 全局 `skills/nextjs-app-router` | **保持不变** | 可能被其他 Next.js 项目使用；本项目用 prompt 强措辞覆盖 |
| 全局 `skills/*`（其余 28 个） | **保持不变** | 通用指引，适用于本项目 |
| 全局 `agents/*`（9 个） | **保持不变** | 无法从项目层修改 agent permission |
| 全局 `commands/*`（9 个） | **保持不变** | 通用入口，适用于本项目 |
| 全局 `instructions/*`（10 个） | **保持不变** | 核心工作流指引 |
| 项目级新 skill | **暂不新增** | 全局 skills 已足够覆盖当前需求 |

### AGENTS.md 长度约束

- 硬上限：80 行。
- 目标：60-70 行（保持上下文效率）。
- 如果内容膨胀，优先移除详细命令说明到项目 `docs/` 或全局 `instructions/`，AGENTS.md 只保留最关键的约定和路由。
- 每次更新后用 `wc -l` 验证。

### 回滚方案

| 步骤 | 回滚方式 |
|------|---------|
| Step 1a/1b | `git checkout AGENTS.md` 恢复原文件 |
| Step 2a | `git checkout skills/hello/` 恢复目录 |
| Step 2b | `git checkout README.md docs/CODEMAP.md` 恢复文件 |
| 全局资产 | 无需回滚（未修改） |

### 需要委托的工作

| 工作 | 委托目标 | 条件 |
|------|---------|------|
| 更新项目 AGENTS.md | 主 agent 直接执行 | 权限允许 |
| 废弃 hello skill + 清理死引用 | 主 agent 直接执行 | bash 删除 + 编辑 |
| 全局工作流资产维护 | 无需委托 | 不修改全局资产 |

### 未来关注

- **CODEMAP.md 全面过时**: 多处仍描述 Next.js（第 13 行 "Next.js"、第 73 行 "Next.js pages"）、端口 :3000（实际 Vite 端口）、config 示例用 `gpt-4o-mini`（实际用 `qwen/qwen3.5-plus`）。应在独立任务中全面更新。
- **README.md 技术栈过时**: 架构图仍包含 "Next.js" 描述（第 46-59 行）、Tech Stack 表仍列 "Next.js 15.x"。应在独立任务中更新为 Vite SPA 技术栈。
- 如果项目频繁出现 AI/LangGraph agent 开发模式，考虑创建项目级 `ai-agent-dev` skill
- 如果配置了 chrome_devtools/playwright MCP，验证现有 agent/command 引用自动生效
- 如果项目迁移回 Next.js 或换用其他框架，重新评估前端约定章节和 skill 路由
