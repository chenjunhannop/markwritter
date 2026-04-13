# Markwritter Figma MCP Handoff

基于仓库实际前端实现与现有设计文档整理的 Figma 交付说明。

## 当前 Figma MCP 状态

- Figma 账号已连接：`chenjunhanb@gmail.com` / `junhan`
- 当前团队：`junhan's team`
- 当前 seat：`View`
- 本次会话未暴露通用画布编辑工具，无法直接在 Figma 文件中创建 Variables、Components、Frames

结论：

- 当前可以完成代码对齐、设计规范整理、组件与页面结构定义
- 当前不能直接执行你要求的 `use_figma` 式画布编辑
- 若要真正落到 Figma，需要两个条件：
  1. Figma 团队权限至少为 `Edit`
  2. 会话里需要提供可创建/编辑 Figma 画布的 MCP 工具

## 设计文件结构

建议在 Figma 中创建文件：`Markwritter Design System`

Pages:

- `01 Foundations`
- `02 Components`
- `03 Templates`
- `04 Dark Mode`
- `05 Responsive`

在 `01 Foundations` 下创建：

- `Colors`
- `Typography`
- `Spacing`
- `Radius`
- `Elevation`
- `Icons`

在 `02 Components` 下创建：

- `Button`
- `Card`
- `Input`
- `Textarea`
- `Badge`
- `Alert`
- `Dialog`
- `Select`
- `Tabs`
- `Navigation`
- `Chat`
- `Data Display`

在 `03 Templates` 下创建：

- `Chat`
- `Skills`
- `Explore`
- `Query`
- `Record`
- `Logs`
- `Settings`

## Foundations

### 颜色 Tokens

来源：

- `web/app/globals.css`

#### Light

| Token | HSL | Hex |
| --- | --- | --- |
| `background` | `0 0% 100%` | `#FFFFFF` |
| `foreground` | `222.2 84% 4.9%` | `#0C1427` |
| `card` | `0 0% 100%` | `#FFFFFF` |
| `card-foreground` | `222.2 84% 4.9%` | `#0C1427` |
| `popover` | `0 0% 100%` | `#FFFFFF` |
| `popover-foreground` | `222.2 84% 4.9%` | `#0C1427` |
| `primary` | `222.2 47.4% 11.2%` | `#0F172A` |
| `primary-foreground` | `210 40% 98%` | `#F8FAFC` |
| `secondary` | `210 40% 96.1%` | `#F1F5F9` |
| `secondary-foreground` | `222.2 47.4% 11.2%` | `#0F172A` |
| `muted` | `210 40% 96.1%` | `#F1F5F9` |
| `muted-foreground` | `215.4 16.3% 46.9%` | `#64748B` |
| `accent` | `210 40% 96.1%` | `#F1F5F9` |
| `accent-foreground` | `222.2 47.4% 11.2%` | `#0F172A` |
| `destructive` | `0 84.2% 60.2%` | `#EF4444` |
| `destructive-foreground` | `210 40% 98%` | `#F8FAFC` |
| `border` | `214.3 31.8% 91.4%` | `#E2E8F0` |
| `input` | `214.3 31.8% 91.4%` | `#E2E8F0` |
| `ring` | `222.2 84% 4.9%` | `#0C1427` |

#### Dark

| Token | HSL | Hex |
| --- | --- | --- |
| `background` | `222.2 84% 4.9%` | `#0B1120` |
| `foreground` | `210 40% 98%` | `#F8FAFC` |
| `card` | `222.2 84% 4.9%` | `#0B1120` |
| `card-foreground` | `210 40% 98%` | `#F8FAFC` |
| `popover` | `222.2 84% 4.9%` | `#0B1120` |
| `popover-foreground` | `210 40% 98%` | `#F8FAFC` |
| `primary` | `210 40% 98%` | `#F8FAFC` |
| `primary-foreground` | `222.2 47.4% 11.2%` | `#0F172A` |
| `secondary` | `217.2 32.6% 17.5%` | `#1E293B` |
| `secondary-foreground` | `210 40% 98%` | `#F8FAFC` |
| `muted` | `217.2 32.6% 17.5%` | `#1E293B` |
| `muted-foreground` | `215 20.2% 65.1%` | `#94A3B8` |
| `accent` | `217.2 32.6% 17.5%` | `#1E293B` |
| `accent-foreground` | `210 40% 98%` | `#F8FAFC` |
| `destructive` | `0 62.8% 30.6%` | `#7F1D1D` |
| `destructive-foreground` | `210 40% 98%` | `#F8FAFC` |
| `border` | `217.2 32.6% 17.5%` | `#1E293B` |
| `input` | `217.2 32.6% 17.5%` | `#1E293B` |
| `ring` | `212.7 26.8% 83.9%` | `#CBD5E1` |

#### 额外功能色

这些颜色来自实际页面实现，应作为 semantic variables 补充：

- `success`: `#22C55E`
- `info`: `#3B82F6`
- `warning`: `#F59E0B`
- `error`: `#EF4444`
- `neutral-400`: `#94A3B8`
- `neutral-500`: `#64748B`

### 字体系统

来源：

- `web/app/layout.tsx`

字体：

- Sans: `Geist`
- Mono: `Geist Mono`

建议在 Figma 中建立以下 Text Styles：

| Style | Size | Weight | Line Height | 使用场景 |
| --- | --- | --- | --- | --- |
| `display/lg` | 24 | 700 | 28 | 页面主标题 |
| `heading/md` | 20 | 600 | 28 | 卡片/分区标题 |
| `heading/sm` | 18 | 600 | 24 | 次级标题 |
| `body/md` | 16 | 400 | 24 | 正文 |
| `body/sm` | 14 | 400 | 20 | 表单、描述 |
| `label/md` | 14 | 500 | 20 | 按钮、控件 |
| `label/sm` | 12 | 500 | 16 | badge、辅助标签 |
| `mono/sm` | 13 | 400 | 20 | Logs、路径、代码 |
| `mono/xs` | 12 | 400 | 16 | 时间戳、状态 |

### 间距系统

按实际 Tailwind 使用频率创建：

- `space-1`: 4
- `space-1.5`: 6
- `space-2`: 8
- `space-2.5`: 10
- `space-3`: 12
- `space-4`: 16
- `space-5`: 20
- `space-6`: 24
- `space-8`: 32

### 圆角

来源：

- 全局 `--radius: 0.5rem`
- 组件中存在 `rounded-md`、`rounded-lg`、`rounded-xl`、`rounded-full`

建议 Variables：

- `radius-sm`: 4
- `radius-md`: 6
- `radius-lg`: 8
- `radius-xl`: 12
- `radius-pill`: 999

### 阴影

实际实现主要使用：

- `shadow-xs`
- `shadow-sm`
- `shadow-md`
- `shadow-lg`

建议在 Figma 中建为：

- `elevation-1`: 控件
- `elevation-2`: 卡片
- `elevation-3`: 下拉层
- `elevation-4`: 对话框

## 组件库

### Button

来源：

- `web/components/ui/button.tsx`

Variants:

- `default`
- `destructive`
- `outline`
- `secondary`
- `ghost`
- `link`

Sizes:

- `xs`
- `sm`
- `default`
- `lg`
- `icon`
- `icon-xs`
- `icon-sm`
- `icon-lg`

States:

- `default`
- `hover`
- `focus`
- `disabled`

关键规格：

- 默认高度 `36`
- `sm`: `32`
- `xs`: `24`
- `lg`: `40`
- 默认圆角 `6`
- icon gap 默认 `8`

### Card

来源：

- `web/components/ui/card.tsx`

结构：

- `Card`
- `CardHeader`
- `CardTitle`
- `CardDescription`
- `CardAction`
- `CardContent`
- `CardFooter`

关键规格：

- 圆角 `12`
- 边框 `1`
- 垂直内边距 `24`
- Header/Content/Footer 水平内边距 `24`
- 组件内部主间距 `24`

### Input

来源：

- `web/components/ui/input.tsx`

规格：

- 高度 `36`
- 圆角 `6`
- 左右内边距 `12`
- Focus ring `3`
- 支持状态：
  - `default`
  - `focus`
  - `disabled`
  - `error`

### Textarea

来源：

- `web/components/ui/textarea.tsx`
- `web/components/chat/message-input.tsx`
- `web/components/record/quick-record.tsx`

规格：

- 默认最小高度 `64`
- Quick Record 最小高度 `120`
- Chat 输入最小高度 `44`，最大高度 `200`
- 圆角 `6`
- Focus ring `3`

建议建三个变体：

- `default`
- `chat`
- `quick-record`

### Badge

来源：

- `web/components/ui/badge.tsx`
- `web/components/chat/chat-area.tsx`

Variants:

- `default`
- `secondary`
- `destructive`
- `outline`
- `ghost`
- `link`

规格：

- 高度约 `20`
- 圆角 `999`
- 水平 padding `8`
- 聊天页头部 source badge 使用更紧凑规格：`text 10`, `px 6`

### Alert

来源：

- `web/components/ui/alert.tsx`

Variants:

- `default`
- `destructive`

结构：

- Leading Icon
- Title
- Description
- Optional Actions

### Dialog

来源：

- `web/components/ui/dialog.tsx`

结构：

- Overlay
- DialogContent
- DialogHeader
- DialogTitle
- DialogDescription
- DialogFooter
- Optional Close Button

规格：

- 内容区最大宽度：`sm:max-w-lg`
- 内边距：`24`
- 圆角：`8`
- 阴影：大层级

### Select

来源：

- `web/components/ui/select.tsx`
- `web/components/settings/settings-panel.tsx`

结构：

- Trigger
- Content
- Item
- Label
- Separator

规格：

- Trigger 默认高度 `36`
- `sm` 高度 `32`
- Dropdown 使用 `popover` 语义颜色

### Tabs

来源：

- `web/components/ui/tabs.tsx`
- `web/app/record/page.tsx`
- `web/components/record/note-form.tsx`

Variants:

- `default`
- `line`

方向：

- `horizontal`
- `vertical`

状态：

- `default`
- `active`
- `hover`
- `disabled`

### Navigation

来源：

- `web/components/layout/sidebar.tsx`
- `web/components/layout/header.tsx`
- `web/components/layout/top-bar.tsx`
- `web/components/layout/drawer-nav.tsx`

需要建立三套导航模式：

1. `App Sidebar`
2. `Chat Top Bar`
3. `Mobile Drawer`

关键规格：

- Main header 高度 `56`
- Chat top bar 高度 `52`
- Chat panel header 高度 `42`
- Collapsed sidebar 宽度 `64`
- Expanded sidebar 宽度 `224`
- Chat left panel 宽度 `240`
- Chat right panel 宽度 `320`
- Mobile drawer 宽度 `240`

## 7 个核心页面模板

### 1. Chat

来源：

- `web/components/chat/chat-layout.tsx`
- `web/components/chat/chat-area.tsx`
- `web/components/chat/sources-panel.tsx`
- `web/components/chat/studio-panel.tsx`

这是项目最重要的页面，应该设计为三栏工作台而不是普通内容页。

Desktop:

- 顶部 `TopBar`，高度 `52`
- 左侧 `SourcesPanel`，宽 `240`
- 中间 `ChatArea` 自适应
- 右侧 `StudioPanel`，宽 `320`
- 左右折叠后显示 `24` 宽展开条

Tablet:

- 左右面板默认折叠
- 通过侧边 `expand strip` 或顶部按钮拉出 Sheet

Mobile:

- 仅保留 Chat 主区
- Sources / Studio 通过 Sheet 打开
- Navigation 通过 Drawer 打开

中心区需要包含：

- `Panel Header`
- `Empty State`
- `Error Alert`
- `Message Bubbles`
- `Thinking Indicator`
- `MessageInput`
- `Selected Sources Indicator`

建议创建以下子模板：

- `Chat / Empty`
- `Chat / Active Conversation`
- `Chat / Error`
- `Chat / Streaming`
- `Chat / Mobile`

### 2. Skills

来源：

- `web/app/skills/page.tsx`
- `web/components/skills/skill-list.tsx`
- `web/components/skills/skill-card.tsx`

页面结构：

- Standard header inside content
- 页面标题 + `New Skill` CTA
- Search bar
- Skill count
- 3 列响应式卡片栅格

卡片内容：

- Skill name
- Version badge
- Description
- Inputs / required count / output meta
- `Run` / `Edit` / optional `Delete`

建议模板：

- `Skills / Grid`
- `Skills / Empty`
- `Skills / Loading`
- `Skills / Error`

### 3. Explore

来源：

- `web/app/explore/page.tsx`
- `web/components/explore/knowledge-graph.tsx`

页面结构：

- 主图谱画布
- Controls
- MiniMap
- Legend
- 可选右侧 `Node Details` 面板
- 顶部错误 banner

图谱语义：

- 0 connections: gray
- 1-2: green
- 3-5: blue
- 6-10: amber
- 10+: red

建议模板：

- `Explore / Graph Only`
- `Explore / Graph + Details`
- `Explore / Loading`
- `Explore / Empty`
- `Explore / Error`

### 4. Query

来源：

- `web/app/query/page.tsx`
- `web/components/query/search-input.tsx`
- `web/components/query/results-list.tsx`
- `web/components/query/query-chat-area.tsx`

这是双模式页面，不是单一搜索列表。

页面结构：

- 上方 view toggle：`Search Results` / `Q&A Chat`
- 中部主卡片容器，圆角 `12`
- Search 模式包含：
  - Search mode selector
  - Search input
  - Search button
  - Suggestions dropdown
  - Results list
- Chat 模式包含：
  - Question bubble
  - Answer bubble
  - Sources cards
  - Error bubble
  - New question action
  - Bottom composer

建议模板：

- `Query / Search Empty`
- `Query / Search Results`
- `Query / Suggestions Open`
- `Query / QA Answer`
- `Query / QA Streaming`
- `Query / QA Error`

### 5. Record

来源：

- `web/app/record/page.tsx`
- `web/components/record/quick-record.tsx`
- `web/components/record/note-form.tsx`

页面结构：

- 顶部 tabs: `Quick Record` / `Full Editor`

Quick Record:

- 居中卡片
- 标题 `Quick Record`
- 大 textarea
- helper 文案
- Save CTA
- 错误提示

Full Editor:

- 顶部编辑器 header
- 左侧主编辑区
- Tabs: `Editor` / `Metadata`
- 右侧 AI 辅助面板，宽 `320`

建议模板：

- `Record / Quick`
- `Record / Quick Error`
- `Record / Full Editor`
- `Record / Metadata`

### 6. Logs

来源：

- `web/app/logs/page.tsx`
- `web/components/logs/LogStream.tsx`

页面结构：

- 顶部过滤条
- Connection status
- Level filter chips
- 底部日志流区域

关键设计点：

- 日志区使用 `Geist Mono`
- 背景比主界面略弱化
- level 颜色：
  - `DEBUG`: gray
  - `INFO`: blue
  - `WARNING`: yellow
  - `ERROR`: red

建议模板：

- `Logs / Connected`
- `Logs / Disconnected`
- `Logs / Filtered`
- `Logs / Empty`

### 7. Settings

来源：

- `web/app/settings/page.tsx`
- `web/components/settings/settings-panel.tsx`

页面结构：

- 页面标题
- Loading skeleton
- Error banner
- 三张设置卡片

卡片分组：

1. `Vault Path`
2. `LLM Configuration`
3. `General Settings`

交互控件：

- Input
- Select
- Theme segmented buttons
- Dialog confirm
- Icon action buttons

建议模板：

- `Settings / Default`
- `Settings / Loading`
- `Settings / Error`
- `Settings / Reset Dialog`

## 响应式策略

根据代码实现，应在 Figma 里明确做三个断点：

- `Mobile`: `375`
- `Tablet`: `768`
- `Desktop`: `1440`

关键差异：

- 普通页面使用 sidebar + header 布局
- Chat 页面使用独立三栏布局
- 小屏下 Sidebar 退化为 Drawer
- Chat 左右面板退化为 Sheets

## 建议的 Figma Variables 组织

Collections:

- `Core / Color`
- `Core / Typography`
- `Core / Spacing`
- `Core / Radius`
- `Core / Elevation`

Modes:

- `Light`
- `Dark`

建议命名：

- `color/background/default`
- `color/text/default`
- `color/text/muted`
- `color/action/primary`
- `color/action/secondary`
- `color/status/success`
- `color/status/warning`
- `color/status/error`
- `space/1`
- `space/2`
- `radius/md`
- `elevation/2`

## 建议的组件属性

Button:

- `variant`
- `size`
- `state`
- `icon-leading`
- `icon-trailing`

Badge:

- `variant`
- `size`

Card:

- `has-header`
- `has-footer`
- `has-action`

Input:

- `state`
- `has-leading-icon`
- `has-trailing-action`

Alert:

- `variant`
- `has-actions`

NavigationItem:

- `active`
- `collapsed`
- `has-tooltip`

## 直接在 Figma 执行所需条件

要继续完成你原始要求中的“实际创建 Figma 设计”，需要你先满足以下任一条件：

1. 重新连接一个带编辑能力的 Figma MCP 会话，并暴露画布创建/编辑工具
2. 将当前 Figma seat 从 `View` 提升为 `Edit`
3. 提供一个已存在且可编辑的 Figma 文件 URL，并确保该会话支持对该文件进行写入

满足后，我就可以按本文件的结构继续执行：

1. 建 Foundations Variables
2. 建组件主组件与 variants
3. 建 7 个页面模板
4. 补全 Dark mode 页面
