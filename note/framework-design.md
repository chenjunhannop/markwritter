# Markwritter 框架设计

## 设计哲学

**Markwritter 是一个轻量级的 Agent 编排框架**，而非特定功能的工具。

核心思想：
- **框架是主体**：负责理解用户意图、管理 Skills、调度执行
- **Skills 是扩展**：具体功能通过 Skills 实现，框架本身保持精简
- **对话式交互**：用户用自然语言表达需求，框架解析并执行
- **Subagent 执行**：框架不直接执行任务，而是通过 Subagent 代理执行

**与原有设计的根本区别**：
- 旧：视频笔记提取工具（具体功能）
- 新：Agent 编排框架（通用平台）

---

## 核心架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户输入层                          │
│              CLI 命令行 / GUI 图形界面                    │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    框架主体 (Core)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │   Parser    │  │  Registry   │  │    Executor     │  │
│  │  对话解析器  │  │ Skill 注册表 │  │  Subagent 执行器 │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ 创建 Subagent
┌─────────────────────────▼───────────────────────────────┐
│                     Skill 层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │  Skill A    │  │  Skill B    │  │    Skill C      │  │
│  │ (具体功能)   │  │ (具体功能)   │  │   (具体功能)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. Parser（对话解析器）

- 接收用户自然语言输入
- 识别用户意图（需要调用什么 Skill）
- 提取 Skill 所需参数
- 简单的关键词匹配 + 意图识别（MVP 阶段）

#### 2. Registry（Skill 注册表）

- 管理所有可用的 Skills
- 从本地目录加载 Skill 定义
- 支持运行时热加载
- 提供 Skill 查找和匹配

#### 3. Executor（Subagent 执行器）

- 根据 Skill 定义创建 Subagent
- 传递参数并执行 Skill
- 收集执行结果
- 错误处理和超时控制

---

## Skill 系统

Skill 是框架的扩展单元，每个 Skill 是一个独立的功能模块。

### Skill 定义格式 (YAML)

```yaml
# skills/hello/skill.yaml
name: hello
description: 简单的问候 Skill
version: 1.0.0

# 输入参数定义
inputs:
  - name: name
    type: string
    description: 要问候的名字
    required: true

# 输出格式定义
output:
  type: string
  description: 问候语

# 执行配置
execution:
  command: python
  script: run.py
```

### Skill 目录结构

```
skills/
├── hello/                    # Skill 名称
│   ├── skill.yaml           # Skill 定义
│   └── run.py               # 执行脚本
├── fetch-url/               # 另一个 Skill
│   ├── skill.yaml
│   └── run.py
└── ...
```

### Skill 执行流程

1. 框架根据意图找到匹配的 Skill
2. 从用户输入提取 Skill 所需参数
3. 创建 Subagent（子进程）执行 Skill 脚本
4. Skill 脚本接收参数，执行任务
5. 返回结构化结果给框架
6. 框架格式化输出给用户

---

## 目录结构

```
markwritter/
├── markwritter/              # 框架核心代码
│   ├── __init__.py
│   ├── cli.py               # CLI 入口
│   ├── core.py              # 框架主体（调度器）
│   ├── parser.py            # 对话解析
│   ├── registry.py          # Skill 注册表
│   └── executor.py          # Subagent 执行器
├── skills/                  # Skill 目录（用户可扩展）
│   └── example/
│       ├── skill.yaml
│       └── run.py
├── tests/                   # 测试
├── config.yaml             # 框架配置
├── pyproject.toml
└── README.md
```

---

## 核心流程

### 用户交互流程

```
用户: "帮我提取这个视频的信息 https://bilibili.com/xxx"
  │
  ▼
Parser: 识别意图 → 需要调用 "video-info" Skill
  │        提取参数 → url: "https://bilibili.com/xxx"
  ▼
Registry: 查找 "video-info" Skill 定义
  │
  ▼
Executor: 创建 Subagent，执行 video-info/run.py
  │        传递参数: {"url": "https://bilibili.com/xxx"}
  ▼
Skill: 执行具体任务（下载视频信息）
  │
  ▼
框架: 接收结果 → 格式化输出给用户
```

### CLI 使用示例

```bash
# 直接输入命令
markwritter "提取 https://bilibili.com/xxx 的信息"

# 或使用子命令
markwritter run hello --name=World

# 列出可用 Skills
markwritter list

# 交互模式
markwritter chat
> 提取 https://bilibili.com/xxx 的信息
```

---

## 技术选型

| 组件 | 技术 | 理由 |
|------|------|------|
| 语言 | Python 3.10+ | 生态丰富，适合框架开发 |
| CLI 框架 | Typer | 类型安全，自动生成帮助文档 |
| 配置 | Pydantic + YAML | 类型验证，易读易编辑 |
| 进程管理 | Asyncio + Subprocess | 异步执行，并发控制 |
| 日志 | Python logging | 标准库，无需额外依赖 |

---

## 扩展性设计

### 如何添加新 Skill

1. 在 `skills/` 目录创建新文件夹
2. 编写 `skill.yaml` 定义 Skill 元数据
3. 编写执行脚本（任何语言，通过 command 调用）
4. 框架自动识别并加载

### 框架与 Skill 的边界

| 框架负责 | Skill 负责 |
|----------|-----------|
| 解析用户输入 | 具体业务逻辑 |
| 管理 Skill 生命周期 | 参数处理和验证 |
| 创建 Subagent | 执行具体任务 |
| 结果格式化输出 | 返回结构化数据 |

---

## MVP 范围

### Phase 1: 最简核心 ✅

- [x] 项目骨架和 CLI 入口
- [x] Registry：加载本地 skills 目录
- [x] Executor：用 subprocess 运行脚本
- [x] 示例 Skill（hello）验证流程

### Phase 2: 对话解析

- [ ] Parser：关键词匹配 + 意图识别
- [ ] Skill 选择逻辑
- [ ] 参数提取

### Phase 3: 扩展机制

- [ ] 完整的 Skill YAML 规范
- [ ] Skill 热加载
- [ ] 结果格式化

### Phase 4: Polish

- [ ] 错误处理和日志
- [ ] 配置管理
- [ ] 文档

---

## 与原有代码的关系

**原有代码（视频笔记提取）**：
- 将作为框架的一个 Skill 实现
- `skills/video-note/` 包含原有核心逻辑
- 框架本身不依赖具体功能

**迁移计划**：
1. 先实现框架核心（markwritter/）
2. 将原有功能封装为 Skill
3. 逐步迁移其他功能
