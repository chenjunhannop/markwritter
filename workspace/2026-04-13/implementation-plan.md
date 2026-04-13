# Liquid Crystal — Warm Amber · 前端实施计划

> **项目**: Markwritter Web UI
> **设计系统**: Liquid Crystal — Warm Amber v1.0-draft
> **日期**: 2026-04-13
> **状态**: 待实施

---

## 目录

1. [代码库现状](#1-代码库现状)
2. [实施总览](#2-实施总览)
3. [Phase 1 — Token 基础设施](#3-phase-1--token-基础设施)
4. [Phase 2 — UI 原语改造 + 新建](#4-phase-2--ui-原语改造--新建)
5. [Phase 3 — 布局壳改造](#5-phase-3--布局壳改造)
6. [Phase 4 — 页面逐页迁移](#6-phase-4--页面逐页迁移)
7. [风险与依赖](#7-风险与依赖)
8. [验证检查清单](#8-验证检查清单)

---

## 1. 代码库现状

### 1.1 技术栈

- React 19, React Router 7, TanStack Query 5, Zustand 5
- Tailwind CSS v4, Radix UI, Lucide icons, CVA
- @xyflow/react 12 (Explore 知识图谱)
- Vite 8, Biome (lint), Vitest

### 1.2 文件统计

| 类别 | 文件数 | 说明 |
|---|---|---|
| UI 原语 | 15 | button/badge/input/card/dialog/sheet 等，标准 shadcn/ui |
| 缺失组件 | 0 | 缺 Select/Switch/SegmentedControl/Progress/AlertBanner/EmptyState |
| 布局 | 4 | app-layout/sidebar/header/mobile-drawer |
| 页面 | 7 | chat/explore/query/record/skills/settings/logs |
| 共享组件 | 0 | `components/shared/` 为空，但 logs-page 已引用（**编译中断**） |

### 1.3 关键问题

#### 编译中断

`logs-page.tsx` 导入 `EmptyState`、`ErrorState`、`LoadingState` 从 `@/components/shared/*`，但该目录为空。

#### 原生 HTML 替代品

| 元素 | 使用位置 |
|---|---|
| `<select>` | `query-page.tsx` (search mode)、`skills-page.tsx` (enum params)、`settings-page.tsx` (language, log-level) |
| `<input type="radio">` | `settings-page.tsx` (theme) |

#### 内联按钮（~20 处）

以下文件使用原生 `<button>` 而非 `<Button>` 组件：
- `chat-area.tsx` ×3、`message-input.tsx` ×2、`session-list.tsx` ×3
- `sources-panel.tsx` ×5、`citation-badge.tsx` ×2
- `explore-page.tsx` ×1、`node-detail-panel.tsx` ×2

#### 硬编码颜色

| 文件 | 硬编码内容 |
|---|---|
| `explore-page.tsx` / `graph-node.tsx` / `node-detail-panel.tsx` | `NODE_COLORS` hex map (#3b82f6, #22c55e, #a855f7, #f59e0b) 重复 3 次 |
| `note-editor.tsx` | `text-green-600`, `text-orange-500` |
| `diff-preview.tsx` | `bg-green-200/60`, `bg-red-200/60` + dark 变体 |
| `settings-page.tsx` | `bg-green-100/bg-red-100`, `bg-green-500/bg-red-500` |
| `logs-page.tsx` | `text-blue-500`, `text-amber-500`, `text-red-500` |

### 1.4 当前 Token 状态

`globals.css` (92 行) 使用标准 shadcn 冷蓝色 oklch 色板：
- Primary: `oklch(13% 0.028 261.692)` — 冷深蓝
- Background: `oklch(100% 0 0)` — 纯白
- 无 glass tier、无 surface token、无 mesh 背景、无 motion token

---

## 2. 实施总览

```
Phase 1 — Token 基础设施        ← 影响全局，必须先行
Phase 2 — UI 原语改造 + 新建    ← 组件层，被所有页面依赖
Phase 3 — 布局壳改造            ← Sidebar/Header/BackgroundMesh
Phase 4 — 页面逐页迁移          ← Chat → Settings → Record/Query/Skills → Explore/Logs
```

### 前置条件

1. Phase 1 必须先完成（所有组件和页面依赖新 token）
2. Phase 2 中 `EmptyState` 组件需优先创建（修复 logs-page 编译中断）
3. Phase 2 中 `Select` 组件需在 Phase 4 Settings/Query/Skills 之前完成

### 设计文档索引

| 文档 | 路径 | Phase 引用 |
|---|---|---|
| Token 全量 | `docs/design-system/tokens.md` | Phase 1 |
| Button/Badge | `docs/design-system/components-button-badge.md` | Phase 2 |
| Form Inputs | `docs/design-system/components-form-inputs.md` | Phase 2 |
| Surface/Overlay | `docs/design-system/components-surface-overlay.md` | Phase 2 |
| Feedback/Utility | `docs/design-system/components-feedback-utility.md` | Phase 2 |
| Layout Shell | `docs/design-system/layout-shell.md` | Phase 3 |
| Chat 页面 | `docs/design-system/page-chat.md` | Phase 4 |
| Explore 页面 | `docs/design-system/page-explore.md` | Phase 4 |
| Settings 页面 | `docs/design-system/page-settings.md` | Phase 4 |
| Record/Query/Skills | `docs/design-system/page-record-query-skills.md` | Phase 4 |
| Handoff/Audit | `docs/design-system/HANDOFF.md` | 全局 |

---

## 3. Phase 1 — Token 基础设施

### 3.1 `globals.css` 重写

**文件**: `web/src/globals.css`

**当前**: 92 行标准 shadcn
**目标**: ~200 行 Liquid Crystal Warm Amber

#### `@theme` 块

```css
@theme {
  /* ─── Color: Core ─── */
  --color-background: oklch(0.99 0.005 85);
  --color-foreground: oklch(0.22 0.02 60);
  --color-muted: oklch(0.965 0.006 85);
  --color-muted-foreground: oklch(0.45 0.02 60);

  /* ─── Color: Accent (琥珀金) ─── */
  --color-primary: #E6A23C;
  --color-primary-foreground: #2B2116;
  --color-accent: oklch(0.965 0.006 85);
  --color-accent-foreground: oklch(0.22 0.02 60);

  /* ─── Color: Surface ─── */
  --color-surface-base: rgba(255, 255, 255, 0.72);
  --color-surface-raised: rgba(255, 255, 255, 0.82);
  --color-surface-sunken: rgba(0, 0, 0, 0.03);

  /* ─── Color: Border ─── */
  --color-border: rgba(0, 0, 0, 0.08);
  --color-border-strong: rgba(0, 0, 0, 0.15);
  --color-border-subtle: rgba(0, 0, 0, 0.04);
  --color-input: rgba(0, 0, 0, 0.08);
  --color-ring: #E6A23C;

  /* ─── Color: Card/Popover ─── */
  --color-card: rgba(255, 255, 255, 0.55);
  --color-card-foreground: oklch(0.22 0.02 60);
  --color-popover: rgba(255, 255, 255, 0.55);
  --color-popover-foreground: oklch(0.22 0.02 60);

  /* ─── Color: Sidebar ─── */
  --color-sidebar-background: rgba(255, 255, 255, 0.65);
  --color-sidebar-foreground: oklch(0.22 0.02 60);
  --color-sidebar-primary: #E6A23C;
  --color-sidebar-primary-foreground: #2B2116;
  --color-sidebar-accent: rgba(230, 162, 60, 0.12);
  --color-sidebar-accent-foreground: oklch(0.22 0.02 60);
  --color-sidebar-border: rgba(255, 255, 255, 0.40);
  --color-sidebar-ring: #E6A23C;

  /* ─── Color: Destructive ─── */
  --color-destructive: #C75050;
  --color-destructive-foreground: oklch(0.98 0.005 85);

  /* ─── Color: Semantic/Status ─── */
  --color-success: #6B9B5E;
  --color-success-bg: rgba(107, 155, 94, 0.10);
  --color-warning: #D4915C;
  --color-warning-bg: rgba(212, 145, 92, 0.10);
  --color-error: #C75050;
  --color-error-bg: rgba(199, 80, 80, 0.10);
  --color-info: #5B8DB5;
  --color-info-bg: rgba(91, 141, 181, 0.10);

  /* ─── Color: Chart/Node ─── */
  --color-chart-1: #6B8DB5;   /* node-person */
  --color-chart-2: #6D9B5E;   /* node-topic */
  --color-chart-3: #9B7B8E;   /* node-concept */
  --color-chart-4: #E6A23C;   /* node-note */
  --color-chart-5: #C75050;   /* fallback */

  /* ─── Radius (authoritative: surface-overlay §1.7) ─── */
  --radius-xs: 0.25rem;    /* 4px */
  --radius-sm: 0.625rem;   /* 10px */
  --radius-md: 0.875rem;   /* 14px */
  --radius-lg: 1.125rem;   /* 18px */
  --radius-xl: 1.375rem;   /* 22px */
  --radius-2xl: 1.75rem;   /* 28px */
  --radius-full: 9999px;

  /* ─── Shadow ─── */
  --shadow-resting: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-elevated: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-dragging: 0 12px 40px rgba(0, 0, 0, 0.12);

  /* ─── Z-Index ─── */
  --z-base: 0;
  --z-content: 1;
  --z-sticky: 10;
  --z-sidebar: 20;
  --z-dropdown: 30;
  --z-modal-backdrop: 40;
  --z-modal: 50;
  --z-tooltip: 60;
  --z-toast: 70;

  /* ─── Typography ─── */
  --font-sans: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
}
```

#### Dark Mode (`.dark` 块)

暖棕/espresso 色调，保持 sidebar-primary 为 `#F0B04A`（明亮琥珀）。

#### Glass Utility Classes

```css
@layer utilities {
  .glass-ultra-thin {
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(8px) saturate(120%);
  }
  .glass-thin {
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(16px) saturate(140%);
  }
  .glass-regular {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(24px) saturate(160%);
  }
  .glass-thick {
    background: rgba(255, 255, 255, 0.78);
    backdrop-filter: blur(40px) saturate(180%);
  }
  .dark .glass-ultra-thin {
    background: rgba(26, 20, 15, 0.50);
  }
  .dark .glass-thin {
    background: rgba(26, 20, 15, 0.60);
  }
  .dark .glass-regular {
    background: rgba(26, 20, 15, 0.70);
  }
  .dark .glass-thick {
    background: rgba(26, 20, 15, 0.80);
  }
}
```

#### Mesh Background Classes

```css
.mesh-light {
  background:
    radial-gradient(ellipse 80% 60% at 15% 20%, rgba(230, 162, 60, 0.40), transparent 50%),
    radial-gradient(ellipse 70% 50% at 85% 10%, rgba(212, 145, 92, 0.35), transparent 45%),
    radial-gradient(ellipse 90% 70% at 65% 75%, rgba(240, 200, 140, 0.25), transparent 55%),
    var(--color-background);
}
.mesh-dark {
  background:
    radial-gradient(ellipse 80% 60% at 18% 18%, rgba(60, 35, 15, 0.50), transparent 45%),
    radial-gradient(ellipse 70% 50% at 82% 12%, rgba(45, 25, 10, 0.40), transparent 40%),
    radial-gradient(ellipse 90% 70% at 72% 78%, rgba(55, 40, 20, 0.30), transparent 50%),
    var(--color-background);
}
```

#### Animation Keyframes

```css
@keyframes enter {
  from {
    opacity: var(--tw-enter-opacity, 0);
    transform: translate3d(var(--tw-enter-translate-x, 0), var(--tw-enter-translate-y, 0), 0)
      scale3d(var(--tw-enter-scale, 1), var(--tw-enter-scale, 1), var(--tw-enter-scale, 1));
  }
}
@keyframes exit {
  to {
    opacity: var(--tw-exit-opacity, 0);
    transform: translate3d(var(--tw-exit-translate-x, 0), var(--tw-exit-translate-y, 0), 0)
      scale3d(var(--tw-exit-scale, 1), var(--tw-exit-scale, 1), var(--tw-exit-scale, 1));
  }
}
```

### 3.2 新增 BackgroundMesh 组件

**文件**: `web/src/components/shared/background-mesh.tsx`

```tsx
export function BackgroundMesh() {
  return (
    <div
      aria-hidden="true"
      className="fixed inset-0 -z-0 pointer-events-none mesh-light dark:mesh-dark"
    />
  );
}
```

### 3.3 Phase 1 验证

- [ ] `npm run dev` 启动，无白屏/报错
- [ ] Light mode: 暖色调背景，琥珀色 primary
- [ ] Dark mode: 暖棕/espresso 背景，明亮琥珀 primary
- [ ] Glass class 渲染正确（backdrop-filter 生效）
- [ ] Mesh 背景显示渐变光晕
- [ ] 所有页面基本可访问（不崩）
- [ ] `npm run lint && npm run typecheck` 通过

---

## 4. Phase 2 — UI 原语改造 + 新建

### 4.1 改造现有组件

#### `button.tsx`

**当前变体**: default/destructive/outline/secondary/ghost/link × default/sm/lg/icon
**目标变体**: default/destructive/outline/secondary/ghost/link/accent × default/sm/lg/icon/icon-sm/icon-lg

关键改动:
- `default`: `bg-primary text-primary-foreground` (琥珀金)
- `accent`: `bg-accent-muted text-accent-text` (浅琥珀)
- `ghost`: `hover:bg-accent/10` (暖色 hover)
- `outline`: `border-border hover:bg-accent/10`
- 新增 `icon-sm` (28px), `icon-lg` (40px)
- focus ring 改为 `ring-ring` (琥珀色)

#### `badge.tsx`

**当前变体**: default/secondary/destructive/outline
**目标变体**: default/secondary/destructive/outline/warning/success/info/glass

关键改动:
- 新增 `warning` (`bg-warning-bg text-warning`)
- 新增 `success` (`bg-success-bg text-success`)
- 新增 `info` (`bg-info-bg text-info`)
- 新增 `glass` (`glass-ultra-thin border border-white/30`)

#### `card.tsx`

关键改动:
- 默认: `glass-thin border border-white/35 shadow-resting rounded-[14px]`
- CardHeader/CardFooter 保持结构不变

#### `dialog.tsx`

关键改动:
- DialogOverlay: `bg-black/40 backdrop-blur-[4px]`
- DialogContent: `glass-thick border border-white/45 rounded-[22px] shadow-dragging`
- Animation: `animate-in fade-in-0 zoom-in-95`

#### `sheet.tsx`

关键改动:
- SheetOverlay: `bg-black/40 backdrop-blur-[4px]`
- SheetContent: `glass-regular border border-white/40`
- left side: `rounded-r-[18px]`
- right side: `rounded-l-[18px]`
- top side: `rounded-b-[18px]`
- bottom side: `rounded-t-[18px]`

#### `popover.tsx`

关键改动:
- PopoverContent: `glass-thin border border-white/35 rounded-[14px] shadow-elevated`

#### `tooltip.tsx`

关键改动:
- Light: `bg-[#2B2116] text-[#F8F1E7] rounded-[4px]` (反色实心)
- Dark: `bg-[#F8F1E7] text-[#2B2116] rounded-[4px]` (反色实心)

#### `tabs.tsx`

关键改动:
- TabsList: `glass-ultra-thin rounded-[10px] p-[3px]`
- TabsTrigger active: `bg-surface-base shadow-resting rounded-[4px]`
- 滑动指示器 pill (通过 CSS 或 React state 实现)

#### `separator.tsx`

关键改动:
- 默认: `bg-border`
- 新增 `on-glass` prop: `bg-white/10 dark:bg-white/6`

#### `input.tsx`

关键改动:
- `glass-thin border border-white/35 rounded-[10px] focus:ring-2 focus:ring-ring`

#### `textarea.tsx`

关键改动:
- 同 input，`glass-thin border border-white/35 rounded-[10px]`

#### `checkbox.tsx`

关键改动:
- Checked: `bg-primary border-primary` (琥珀色)
- 新增 indeterminate 视觉 (dash icon)

#### `avatar.tsx`

关键改动:
- Fallback: `bg-primary text-primary-foreground` (琥珀色首字母)
- 新增 `data-loading` skeleton 状态

#### `scroll-area.tsx`

关键改动:
- 自定义 thumb 颜色：`bg-border hover:bg-border-strong`

#### `skeleton.tsx`

关键改动:
- `bg-muted` 而非 `bg-primary/10`

### 4.2 新建组件

#### `select.tsx`

**文件**: `web/src/components/ui/select.tsx`
**基于**: Radix Select
**参考**: `components-form-inputs.md` §4

结构:
```
Select → SelectTrigger → SelectValue
                      → SelectIcon (ChevronDown)
       → SelectContent (glass-thin)
         → SelectViewport
           → SelectItem × N
             → SelectItemText
             → SelectItemIndicator (Check icon)
```

Props:
- 与 Radix Select API 兼容
- SelectTrigger: `glass-thin border border-white/35 rounded-[10px] h-9 px-3`
- SelectContent: `glass-thin rounded-[14px] shadow-elevated`
- SelectItem: `rounded-[8px] px-2 py-1.5 hover:bg-accent/10`

#### `switch.tsx`

**文件**: `web/src/components/ui/switch.tsx`
**基于**: Radix Switch
**参考**: `components-form-inputs.md` §6

- Track: `w-11 h-6 rounded-full bg-muted data-[state=checked]:bg-primary`
- Thumb: `w-5 h-5 rounded-full bg-white shadow-resting translate-x-0.5 data-[state=checked]:translate-x-[22px]`

#### `segmented-control.tsx`

**文件**: `web/src/components/ui/segmented-control.tsx`
**基于**: Radix ToggleGroup
**参考**: `components-form-inputs.md` §5

- Container: `glass-ultra-thin rounded-[10px] p-[3px] inline-flex`
- Active item: `bg-surface-base shadow-resting rounded-[4px]`
- Items: `px-3 py-1.5 text-sm font-medium`

#### `progress.tsx`

**文件**: `web/src/components/ui/progress.tsx`
**基于**: Radix Progress
**参考**: `components-feedback-utility.md` §4

- Track: `h-2 rounded-full bg-border`
- Fill: `rounded-full bg-primary` (default/success/warning/destructive 变体)
- Indeterminate: sliding animation

#### `alert-banner.tsx`

**文件**: `web/src/components/ui/alert-banner.tsx`
**参考**: `components-feedback-utility.md` §5

结构:
```
AlertBanner → Stripe (3px left, status color)
            → Icon (status icon)
            → Content (Title + Description)
            → Dismiss (✕ button)
```

变体: info/success/warning/error
- `info`: `bg-info-bg` + `border-l-info`
- `success`: `bg-success-bg` + `border-l-success`
- `warning`: `bg-warning-bg` + `border-l-warning`
- `error`: `bg-error-bg` + `border-l-error`

#### `empty-state.tsx`

**文件**: `web/src/components/shared/empty-state.tsx`
**参考**: `components-feedback-utility.md` §6

Props: `icon`, `title`, `description`, `action` (optional ReactNode)
- Icon container: `w-14 h-14 rounded-full glass-thin flex items-center justify-center`
- Title: `text-lg font-semibold text-foreground`
- Description: `text-muted-foreground`
- Action slot: children 或 action prop

同时创建:
- `web/src/components/shared/loading-state.tsx` — `<Skeleton>` 组合
- `web/src/components/shared/error-state.tsx` — 错误 icon + message + retry button

### 4.3 Phase 2 验证

- [ ] 所有 21 个 UI 组件 (15 改造 + 6 新建) 存在且无 TS 错误
- [ ] `npm run lint && npm run typecheck` 通过
- [ ] logs-page 编译通过（EmptyState/ErrorState/LoadingState 已创建）
- [ ] Button 6 变体在 Light/Dark 下正确渲染
- [ ] Select 下拉菜单正常工作
- [ ] Dialog/Sheet glass 效果正常
- [ ] Tooltip 反色实心对比度 ≥ 15:1

---

## 5. Phase 3 — 布局壳改造

### 5.1 `app-layout.tsx`

**改动**:
- 外层 div: `relative h-screen w-screen overflow-hidden`
- 添加 `<BackgroundMesh />`（在 content layer 之前）
- Content layer div: `relative z-content flex h-full`

### 5.2 `sidebar.tsx`

**改动**:
- `<aside>` className 改为 glass-regular:
  ```
  glass-regular border-r border-white/40 dark:border-white/12
  ```
- Nav item active state: 加 3px 左侧 primary 竖条（`::before` 伪元素或 absolute div）
- Nav item rounded: `rounded-[10px]`
- Collapse toggle button: 使用 `<Button variant="ghost" size="icon-sm">`

### 5.3 `header.tsx`

**改动**:
- `<header>` className 改为 glass-thick:
  ```
  glass-thick border-b border-white/45 dark:border-white/15 sticky top-0 z-sticky
  ```
- Theme toggle / Sidebar toggle: 使用 `<Button variant="ghost" size="icon-sm">`

### 5.4 `mobile-drawer.tsx`

**改动**:
- SheetContent: 覆盖 glass tier 为 regular，`rounded-r-[18px]`
- Nav item 样式同 sidebar expanded 状态

### 5.5 Phase 3 验证

- [ ] Desktop expanded × Light: glass sidebar + glass header + mesh 背景
- [ ] Desktop collapsed × Light: 图标 sidebar + tooltip 正常
- [ ] Desktop expanded × Dark: dark glass + dark mesh
- [ ] Desktop collapsed × Dark: 正常
- [ ] Mobile × Light: 无 sidebar，hamburger 打开 drawer
- [ ] Mobile × Dark: drawer glass 正常
- [ ] Sidebar 折叠/展开动画流畅 (300ms)
- [ ] Header sticky 行为正常
- [ ] `prefers-reduced-motion` 禁用动画

---

## 6. Phase 4 — 页面逐页迁移

### 执行顺序

```
4.1 Chat     ← 主页面，最复杂
4.2 Settings ← 表单密集，验证新组件
4.3 Query    ← 简单页面
4.4 Skills   ← Dialog 密集
4.5 Record   ← 复杂三栏布局
4.6 Explore  ← ReactFlow 特殊处理
4.7 Logs     ← 修复编译 + 简单
```

### 6.1 Chat 页面

**文件**: `features/chat/`

| 文件 | 改动 | 优先级 |
|---|---|---|
| `chat-area.tsx` | 3 个内联 `<button>` → `<Button>` | 高 |
| `chat-area.tsx` | Empty state → `<EmptyState>` | 高 |
| `message-input.tsx` | 2 个内联 `<button>` → `<Button>` | 高 |
| `message-input.tsx` | 原生 textarea → `<Textarea>` | 中 |
| `session-list.tsx` | 3 个内联 `<button>` → `<Button>` | 高 |
| `session-list.tsx` | 固定 `w-52` → glass panel | 中 |
| `sources-panel.tsx` | 5 个内联 `<button>` → `<Button>` | 高 |
| `sources-panel.tsx` | 移除硬编码静态文件树数据 | 低 |
| `citation-badge.tsx` | 2 个内联 `<button>` → `<Button>` | 中 |
| `message-bubble.tsx` | prose 样式适配暖色调 | 低 |

**参考**: `page-chat.md`

### 6.2 Settings 页面

**文件**: `features/settings/settings-page.tsx`

| 改动 | 详情 |
|---|---|
| `<input type="radio">` ×3 (theme) → `<SegmentedControl>` | 3 选项: Light/Dark/System |
| `<select>` (language) → `<Select>` | 替换原生 select |
| `<select>` (log-level) → `<Select>` | 替换原生 select |
| 硬编码 `bg-green-100/text-green-700` → `<Badge variant="success">` | API key 状态 |
| 硬编码 `bg-green-500/bg-red-500` → `<Badge variant="success/destructive">` | Vault 连接状态 |
| Tab 间距和圆角适配新 radius token | |

**参考**: `page-settings.md`

### 6.3 Query 页面

**文件**: `features/query/query-page.tsx`

| 改动 | 详情 |
|---|---|
| `<select>` (search mode) → `<Select>` 或 `<SegmentedControl>` | 3 选项: semantic/keyword/fuzzy |
| Card 组件适配新 glass 样式 | 自动跟随 Phase 2 Card 改造 |

**参考**: `page-record-query-skills.md` §Query

### 6.4 Skills 页面

**文件**: `features/skills/skills-page.tsx`

| 改动 | 详情 |
|---|---|
| `<select>` (enum params) → `<Select>` | SkillParamField 组件内 |
| Dialog 内容适配 glass-thick | 自动跟随 Phase 2 Dialog 改造 |
| `<pre>` output 添加 glass 背景 | `glass-ultra-thin rounded-[10px]` |

**参考**: `page-record-query-skills.md` §Skills

### 6.5 Record 页面

**文件**: `features/record/`

| 文件 | 改动 |
|---|---|
| `note-editor.tsx` | `text-green-600` → `text-success`；`text-orange-500` → `text-warning` |
| `diff-preview.tsx` | `bg-green-200/60` → `bg-success-bg`；`bg-red-200/60` → `bg-error-bg` |
| `diff-preview.tsx` | accepted 状态颜色 → success token |
| `file-tree-panel.tsx` | 无硬编码颜色，仅需确认 glass 效果 |

**参考**: `page-record-query-skills.md` §Record

### 6.6 Explore 页面

**文件**: `features/explore/`

| 文件 | 改动 |
|---|---|
| `explore-page.tsx` | `NODE_COLORS` → 使用 `--color-chart-1..5` CSS 变量 |
| `graph-node.tsx` | inline `style={}` → CSS 变量引用 |
| `node-detail-panel.tsx` | `NODE_COLORS` → CSS 变量引用 |
| 所有 | 合并重复的 NODE_COLORS 为单一常量或 CSS 变量 |

**特殊处理**: ReactFlow 的 inline style 无法完全用 Tailwind 替代，保留 inline style 但改用 CSS 变量:
```tsx
style={{ backgroundColor: `var(--color-chart-${nodeTypeIndex})` }}
```

**参考**: `page-explore.md`

### 6.7 Logs 页面

**文件**: `features/logs/logs-page.tsx`

| 改动 | 详情 |
|---|---|
| 导入修复 | `EmptyState`/`ErrorState`/`LoadingState` → 已在 Phase 2 创建 |
| `LEVEL_COLORS` | `text-blue-500` → `text-info`；`text-amber-500` → `text-warning`；`text-red-500` → `text-error` |
| Log rows | 添加 `glass-ultra-thin rounded-[8px]` 背景 |

### 6.8 Phase 4 验证（每页完成后）

- [ ] `npm run lint && npm run typecheck` 通过
- [ ] 无原生 `<select>` / `<input type="radio">` 残留
- [ ] 无内联 `<button>` 残留（全部使用 `<Button>`）
- [ ] 无硬编码颜色残留（grep `bg-green-`, `bg-red-`, `text-blue-`, `text-amber-`）
- [ ] Light/Dark 双模式正确
- [ ] 页面功能不受影响（路由、API 调用、状态管理）

---

## 7. 风险与依赖

| 风险 | 影响 | 概率 | 缓解 |
|---|---|---|---|
| Phase 1 token 变更导致全局样式错乱 | 高 | 中 | Phase 1 后立即全站页面验证 |
| Radix Select/Switch 与现有表单状态兼容性 | 中 | 低 | 保持 value/onChange API 一致 |
| Glass backdrop-filter 浏览器兼容性 | 低 | 低 | CSS fallback: solid surface-base 背景 |
| ReactFlow inline style 限制 | 低 | 中 | 保留 inline style，使用 CSS 变量 |
| tailwindcss-animate 插件缺失 | 中 | 低 | 检查 package.json，必要时安装 |
| 大量文件同时改动导致 merge 冲突 | 中 | 中 | 按 Phase 顺序提交，每 Phase 一个 commit |

---

## 8. 验证检查清单

### Phase 1 完成标准

- [ ] `globals.css` 包含全部 ~140 token
- [ ] Light mode: 暖琥珀色 primary + 暖白背景
- [ ] Dark mode: 暖棕 background + 明亮琥珀 primary
- [ ] `.glass-*` classes 正确渲染 backdrop-filter
- [ ] `.mesh-light` / `.mesh-dark` 显示渐变光晕
- [ ] `npm run lint && npm run typecheck && npm run dev` 全部通过

### Phase 2 完成标准

- [ ] 15 个改造组件无 TS 错误
- [ ] 6 个新组件存在且可用
- [ ] `logs-page.tsx` 编译通过
- [ ] Button 6 变体 × 6 尺寸正确渲染
- [ ] Select 下拉工作正常
- [ ] Dialog glass 效果 + 动画正常
- [ ] Tooltip 对比度 ≥ 15:1

### Phase 3 完成标准

- [ ] BackgroundMesh 渲染在所有页面下层
- [ ] Sidebar glass-regular + 暖色 border
- [ ] Header glass-thick + sticky
- [ ] Mobile drawer glass-regular + rounded corners
- [ ] 折叠/展开动画 300ms
- [ ] Desktop + Mobile × Light + Dark = 8 种组合正确

### Phase 4 完成标准

- [ ] 0 个原生 `<select>` 残留
- [ ] 0 个原生 `<input type="radio">` 残留
- [ ] 0 个内联 `<button>` 残留
- [ ] 0 个硬编码颜色残留 (`bg-green-*`, `bg-red-*`, `text-blue-*`, `#3b82f6` 等)
- [ ] 全部 7 个页面功能正常
- [ ] `npm run lint && npm run typecheck && npm run build` 通过

---

*Generated: 2026-04-13 · Source: 10 design documents (13,687 lines) + full codebase analysis*
