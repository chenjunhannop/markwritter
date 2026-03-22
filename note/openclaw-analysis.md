# OpenClaw 架构分析 - 设计思路借鉴

## 项目概述

OpenClaw 是一个多平台 AI 助手框架，可以在多种设备上运行，支持多种通信渠道（Telegram、Discord、Slack、iMessage 等）。

---

## 核心架构设计

### 1. 分层架构

```
┌─────────────────────────────────────────┐
│           前端应用层 (Apps)              │
│  macOS App | iOS App | Android | Web   │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           网关层 (Gateway)               │
│     消息路由 | 会话管理 | 权限控制       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           核心服务层 (Core)              │
│  Agents | Channels | Commands | Config │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           扩展层 (Extensions)            │
│    Plugins | Skills | Tools | Memory   │
└─────────────────────────────────────────┘
```

### 2. 模块化设计原则

| 原则 | 实现方式 | 借鉴价值 |
|------|----------|----------|
| **Core 精简** | 核心只保留基础能力 | 我们的项目也应保持核心精简 |
| **插件化扩展** | 通过 Extensions 目录扩展 | 支持第三方工具集成（如 Obsidian）|
| **技能系统** | Skills 目录存放可复用能力 | AI 总结能力可作为 Skill |
| **多平台支持** | Apps 目录分离平台代码 | SwiftUI 前端独立开发 |

---

## 关键设计思路

### 1. CLI 优先 (Terminal-first)

- OpenClaw 采用**终端优先**的设计
- 所有功能都有 CLI 命令
- GUI 应用是对 CLI 的封装
- **借鉴**：我们的项目可以先开发 Python CLI，再用 SwiftUI 封装

### 2. 配置管理

```
配置文件: ~/.openclaw/config.json
凭证存储: ~/.openclaw/credentials/
会话数据: ~/.openclaw/sessions/
```

- 统一配置目录
- 敏感信息分离存储
- **借鉴**：我们的配置可以放在 `~/.note-agent/config.json`

### 3. 插件系统

OpenClaw 的插件支持两种形式：

1. **Native Plugin**: `openclaw.plugin.json` + 运行时模块
2. **Bundle**: `.claude-plugin/plugin.json` (兼容格式)

插件可以：
- 注册新的命令
- 绑定会话回调
- 访问 API

**借鉴**：我们可以设计插件系统支持不同的笔记工具（Obsidian、Notion、Bear 等）

### 4. 代理系统 (Agents)

OpenClaw 有专门的 `src/agents` 目录管理各种代理：
- 代理发现 (Agent Discovery)
- 代理注册 (Agent Registration)
- 代理工作流 (Agent Workflows)

**借鉴**：我们的 AI 内容提取可以设计为 Agent 模式

### 5. 技能系统 (Skills)

`skills/` 目录包含可复用的能力模块：
- 每个 Skill 有独立的目录和配置
- 可以在 ClawHub 发布分享
- 支持版本管理

**借鉴**：视频分析、AI 总结可以作为独立 Skill

---

## 技术实现亮点

### 1. 前端架构 (macOS App)

```
apps/macos/
├── Sources/OpenClaw/       # Swift 源代码
├── Resources/              # 资源文件
└── fastlane/               # 发布配置
```

- 使用 SwiftUI 开发
- 支持代码签名和沙盒
- 使用 Sparkle 自动更新

### 2. 后端架构 (Node.js/TypeScript)

```
src/
├── cli/           # 命令行接口
├── commands/      # 命令实现
├── gateway/       # 网关服务
├── agents/        # 代理管理
├── channels/      # 通信渠道
├── config/        # 配置管理
└── infra/         # 基础设施
```

- ESM 模块系统
- 严格的 TypeScript 类型
- Vitest 测试框架

### 3. 扩展架构 (Extensions)

```
extensions/
├── discord/       # Discord 集成
├── anthropic/     # Claude API 集成
├── notion/        # Notion 集成
└── ...
```

- 每个扩展是独立的 workspace package
- 通过 plugin-sdk 与核心交互
- 支持 npm 分发

---

## 对我们项目的借鉴

### 架构建议

```
note-agent/
├── apps/
│   └── macos/              # SwiftUI 前端
├── core/                   # Python 核心服务
│   ├── cli/               # 命令行工具
│   ├── agents/            # AI 处理代理
│   └── plugins/           # 笔记工具插件
├── plugins/               # 第三方集成
│   └── obsidian/         # Obsidian 插件
└── skills/               # 可复用能力
    └── video-summarize/  # 视频总结技能
```

### 关键借鉴点

1. **CLI + GUI 分离**
   - Python 提供 CLI 和 API 服务
   - SwiftUI 通过 API 与后端通信

2. **插件化设计**
   - 核心只处理视频链接和 AI 调用
   - 笔记存储通过插件实现（Obsidian、Notion 等）

3. **配置管理**
   - 统一配置目录 `~/.note-agent/`
   - 敏感信息（API Key）单独存储

4. **技能复用**
   - 视频下载、字幕提取、AI 总结作为独立技能
   - 支持技能配置和版本管理

5. **开发流程**
   - 先开发 CLI 版本验证核心流程
   - 再开发 SwiftUI 前端
   - 使用本地 API 通信（HTTP 或 Unix Socket）

---

## 文件组织最佳实践

从 OpenClaw 学到的文件组织原则：

1. **小文件原则**: 单个文件不超过 700 行
2. **测试相邻**: 测试文件与源文件同目录 (`*.test.ts`)
3. **文档内联**: 每个目录有 README.md 说明用途
4. **类型安全**: 严格的 TypeScript 类型（我们可用 Python type hints）
5. **统一命名**: 使用 kebab-case 文件名
