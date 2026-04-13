# Markwritter Figma 设计规范

> 基于现有 Next.js + Radix UI + Tailwind CSS 前端代码的完整设计规范

## 1. 设计系统基础

### 1.1 颜色变量 (Color Tokens)

**Light Mode:**
| Token | HSL Value | RGB Equivalent | Usage |
|-------|-----------|----------------|-------|
| `--background` | 0 0% 100% | #FFFFFF | 页面背景 |
| `--foreground` | 222.2 84% 4.9% | #0C1427 | 主要文字 |
| `--card` | 0 0% 100% | #FFFFFF | 卡片背景 |
| `--card-foreground` | 222.2 84% 4.9% | #0C1427 | 卡片文字 |
| `--primary` | 222.2 47.4% 11.2% | #0F172A | 主按钮、激活状态 |
| `--primary-foreground` | 210 40% 98% | #F8FAFC | 主按钮文字 |
| `--secondary` | 210 40% 96.1% | #F1F5F9 | 次级按钮背景 |
| `--secondary-foreground` | 222.2 47.4% 11.2% | #0F172A | 次级按钮文字 |
| `--muted` | 210 40% 96.1% | #F1F5F9 | 弱化背景 |
| `--muted-foreground` | 215.4 16.3% 46.9% | #64748B | 次要文字 |
| `--accent` | 210 40% 96.1% | #F1F5F9 | 悬停状态 |
| `--accent-foreground` | 222.2 47.4% 11.2% | #0F172A | 悬停文字 |
| `--destructive` | 0 84.2% 60.2% | #EF4444 | 错误/删除 |
| `--destructive-foreground` | 210 40% 98% | #F8FAFC | 错误文字 |
| `--border` | 214.3 31.8% 91.4% | #E2E8F0 | 边框 |
| `--input` | 214.3 31.8% 91.4% | #E2E8F0 | 输入框边框 |
| `--ring` | 222.2 84% 4.9% | #0F172A | 焦点环 |

**Dark Mode:**
| Token | HSL Value | RGB Equivalent |
|-------|-----------|----------------|
| `--background` | 222.2 84% 4.9% | #0B1120 |
| `--foreground` | 210 40% 98% | #F8FAFC |
| `--card` | 222.2 84% 4.9% | #0B1120 |
| `--primary` | 210 40% 98% | #F8FAFC |
| `--secondary` | 217.2 32.6% 17.5% | #1E293B |

### 1.2 间距系统 (Spacing Scale)

基于 Tailwind CSS 默认 scale:

| Token | Value | Usage |
|-------|-------|-------|
| `gap-1` | 0.25rem (4px) | 紧密间距 |
| `gap-1.5` | 0.375rem (6px) | 图标与文字 |
| `gap-2` | 0.5rem (8px) | 组件内间距 |
| `gap-3` | 0.75rem (12px) | 相关元素 |
| `gap-4` | 1rem (16px) | 标准间距 |
| `gap-6` | 1.5rem (24px) | 卡片内边距 |
| `px-2` | 0.5rem (8px) | 小内边距 |
| `px-3` | 0.75rem (12px) | 标准内边距 |
| `px-4` | 1rem (16px) | 大内边距 |
| `px-6` | 1.5rem (24px) | 卡片内边距 |

### 1.3 圆角 (Border Radius)

| Token | Value | Usage |
|-------|-------|-------|
| `rounded-md` | 0.375rem (6px) | 按钮、输入框 |
| `rounded-lg` | 0.5rem (8px) | 卡片 |
| `rounded-xl` | 0.75rem (12px) | 大卡片 |

### 1.4 字体排印 (Typography)

**Font Family:** 系统字体栈，带连字特性
```css
font-feature-settings: "rlig" 1, "calt" 1
```

**Type Scale:**
| Style | Size | Weight | Line Height | Usage |
|-------|------|--------|-------------|-------|
| `text-xs` | 0.75rem (12px) | 400 | 1.5 | 辅助文字、版本号 |
| `text-sm` | 0.875rem (14px) | 400 | 1.5 | 次要文字、描述 |
| `text-base` | 1rem (16px) | 400 | 1.5 | 正文 |
| `text-lg` | 1.125rem (18px) | 500 | 1.5 | 小标题 |
| `text-xl` | 1.25rem (20px) | 600 | 1.5 | 中标题 |
| `text-2xl` | 1.5rem (24px) | 700 | 1.2 | 大标题 |

### 1.5 阴影 (Shadows)

| Token | Usage |
|-------|-------|
| `shadow-xs` | 轻微浮起 |
| `shadow-sm` | 卡片阴影 |
| `shadow` | 标准阴影 |
| `shadow-md` | 中等阴影 |
| `shadow-lg` | 大阴影 (模态框) |

---

## 2. 核心组件规范

### 2.1 Button 按钮

**变体 (Variants):**

| Variant | Background | Text | Hover | Usage |
|---------|------------|------|-------|-------|
| `default` | `--primary` | `--primary-foreground` | 90% opacity | 主要操作 |
| `destructive` | `--destructive` | white | 90% opacity | 删除/危险操作 |
| `outline` | `--background` | `--foreground` | `--accent` | 次要操作 |
| `secondary` | `--secondary` | `--secondary-foreground` | 80% opacity | 次级操作 |
| `ghost` | transparent | `--foreground` | `--accent` | 导航、工具栏 |
| `link` | transparent | `--primary` | underline | 文本链接 |

**尺寸 (Sizes):**

| Size | Height | Padding | Font | Icon Size |
|------|--------|---------|------|-----------|
| `xs` | 24px | 8px | 12px | 12px |
| `sm` | 32px | 12px | 14px | 16px |
| `default` | 36px | 16px | 14px | 20px |
| `lg` | 40px | 24px | 16px | 20px |
| `icon` | 36px | - | - | 20px |

**示例:**
```tsx
<Button variant="default" size="default">
  <Icon className="w-5 h-5" />
  Button Text
</Button>
```

---

### 2.2 Card 卡片

**结构:**
```
Card (rounded-xl, border, bg-card, py-6)
├── CardHeader (px-6, gap-2)
│   ├── CardTitle (font-semibold, leading-none)
│   ├── CardDescription (text-sm, text-muted-foreground)
│   └── CardAction (col-start-2, self-start)
├── CardContent (px-6, gap-6)
└── CardFooter (px-6, flex, items-center, [.border-t]:pt-6)
```

**属性:**
- 圆角：`0.75rem (12px)`
- 边框：`1px solid var(--border)`
- 内边距：`24px (py-6)`
- 阴影：`shadow-sm`

---

### 2.3 Input 输入框

**样式:**
```css
input {
  height: 36px;
  padding: 8px 12px;
  border: 1px solid var(--input);
  border-radius: 6px;
  font-size: 14px;
  background: var(--background);
}

input:focus {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.1);
}
```

---

### 2.4 Badge 标签

**变体:**
| Variant | Background | Text | Usage |
|---------|------------|------|-------|
| `default` | `--primary` | `--primary-foreground` | 默认状态 |
| `secondary` | `--secondary` | `--secondary-foreground` | 次级状态 |
| `destructive` | `--destructive` | white | 错误状态 |
| `outline` | transparent | `--foreground` | 边框样式 |

**尺寸:**
- 默认：`h-5 px-2.5 py-0.5 text-xs`
- 小：`h-4 px-2 py-0 text-[10px]`

---

### 2.5 Alert 警告框

**结构:**
```tsx
<Alert variant="default|destructive">
  <Icon className="h-4 w-4" />
  <AlertTitle>标题</AlertTitle>
  <AlertDescription>
    描述内容
  </AlertDescription>
</Alert>
```

**样式:**
- 内边距：`16px`
- 圆角：`6px`
- 边框：`1px solid`
- `destructive`: 红色边框和背景

---

### 2.6 Separator 分隔线

```css
.separator {
  background-color: var(--border);
  height: 1px; /* horizontal */
  width: 1px;  /* vertical */
}
```

---

### 2.7 Tooltip 工具提示

```tsx
<Tooltip delayDuration={0}>
  <TooltipTrigger asChild>
    {/* 触发元素 */}
  </TooltipTrigger>
  <TooltipContent side="right">
    提示文字
  </TooltipContent>
</Tooltip>
```

**样式:**
- 背景：`--popover`
- 文字：`--popover-foreground`
- 圆角：`6px`
- 阴影：`shadow-md`
- 内边距：`8px 12px`
- 字体：`text-sm`

---

## 3. 页面布局规范

### 3.1 整体布局结构

```
App (h-full, w-full)
├── Sidebar (w-16/w-56, h-full, border-r, bg-muted/30)
│   ├── Logo (h-14, border-b, px-4)
│   │   └── "Markwritter" (font-bold, text-lg)
│   ├── NavItems (flex-1, py-4)
│   │   └── NavButton (w-full, mb-1, mx-2)
│   └── Footer (border-t, p-4)
│       └── Version (text-xs, text-muted-foreground)
└── MainContent (flex-1, h-full)
    └── Page Content
```

### 3.2 Sidebar 侧边栏

**状态:**
| State | Width | Behavior |
|-------|-------|----------|
| Expanded | `w-56 (368px)` | 显示图标 + 文字 |
| Collapsed | `w-16 (64px)` | 仅显示图标 + Tooltip |

**导航项:**
```tsx
NavButton {
  variant: "ghost"
  size: "sm"
  className: "w-full justify-start gap-3 px-3 mx-2 mb-1"

  // Active state
  active: "bg-primary/10 text-primary hover:bg-primary/15"

  // Inactive state
  inactive: "hover:bg-muted"
}
```

**导航菜单:**
| Icon | Label | Path |
|------|-------|------|
| MessageSquare | Chat | /chat |
| Boxes | Skills | /skills |
| GitGraph | Explore | /explore |
| Search | Query | /query |
| FileEdit | Record | /record |
| FileText | Logs | /logs |
| Settings | Settings | /settings |

---

### 3.3 Chat 页面

**结构:**
```
ChatPage (h-full, flex)
├── ChatLayout
│   └── ChatArea (flex h-full flex-col)
│       ├── PanelHeader (h-[42px], border-b, px-3)
│       │   ├── Title ("Chat", font-semibold)
│       │   ├── Badge (variant="secondary", source count)
│       │   └── NewChatButton (ghost, icon)
│       ├── ErrorAlert (mx-4, variant="destructive")
│       ├── MessagesArea (flex-1, overflow-hidden)
│       │   ├── EmptyState (items-center, text-muted-foreground)
│       │   ├── ChatSession (messages list)
│       │   └── ThinkingIndicator (animate-spin)
│       └── InputArea (border-t, p-3)
│           ├── MessageInput
│           └── SourceContext (text-xs, text-muted-foreground)
```

**Empty State:**
```tsx
<div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8">
  <MessageSquare className="h-12 w-12 mb-4 opacity-30" />
  <h3 className="text-lg font-medium mb-1">Start a conversation</h3>
  <p className="text-sm text-center max-w-xs">
    Select a source or type a message.
  </p>
</div>
```

---

### 3.4 Header 顶部栏

**结构:**
```tsx
<header className="h-14 border-b px-4 flex items-center justify-between">
  <PageTitle />
  <Actions />
</header>
```

---

## 4. Figma 文件结构建议

### 4.1 Pages 组织

```
Markwritter Design System
├── 🎨 Foundations
│   ├── Colors (Light/Dark tokens)
│   ├── Typography
│   ├── Spacing
│   └── Shadows
├── 🧩 Components
│   ├── Buttons
│   ├── Cards
│   ├── Inputs
│   ├── Badges
│   ├── Alerts
│   ├── Navigation
│   └── Overlays
├── 📄 Templates
│   ├── Chat Page
│   ├── Skills Page
│   ├── Explore Page
│   ├── Query Page
│   ├── Record Page
│   └── Settings Page
└── 🚀 Exports
    └── Design Specs
```

### 4.2 Component Properties

**Button 组件属性:**
- `Variant`: default | destructive | outline | secondary | ghost | link
- `Size`: xs | sm | default | lg | icon
- `State`: default | hover | active | disabled
- `Has Icon`: boolean
- `Label`: text

**Card 组件属性:**
- `Has Header`: boolean
- `Has Footer`: boolean
- `Has Action`: boolean

---

## 5. 响应式断点

| Breakpoint | Min Width | Usage |
|------------|-----------|-------|
| `sm` | 640px | 手机横屏 |
| `md` | 768px | 平板竖屏 |
| `lg` | 1024px | 平板横屏 |
| `xl` | 1280px | 桌面 |
| `2xl` | 1536px | 大桌面 |

**Sidebar 响应式行为:**
- `< 768px`: 抽屉式，可隐藏
- `≥ 768px`: 固定显示，可折叠

---

## 6. 交互动效

### 6.1 过渡效果

```css
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.duration-200 {
  transition-duration: 200ms;
}

.duration-300 {
  transition-duration: 300ms;
}
```

### 6.2 悬停状态

| Element | Hover Effect |
|---------|--------------|
| Button (default) | opacity: 90% |
| Button (ghost) | background: --accent |
| NavItem | background: --muted |

### 6.3 焦点状态

```css
focus-visible {
  outline: none;
  border-color: var(--ring);
  box-shadow: 0 0 0 3px rgba(15, 23, 42, 0.1);
}
```

---

## 7. 设计审查清单

在将设计交付开发前，检查以下项目：

- [ ] 所有颜色使用设计 token 命名
- [ ] 间距符合 4px 网格系统
- [ ] 字体大小/行高符合类型比例
- [ ] 按钮/输入框高度符合规范 (36px default)
- [ ] 交互状态完整 (hover, active, disabled, focus)
- [ ] 暗色模式已定义
- [ ] 响应式断点已标注
- [ ] 组件变体完整
- [ ] 可访问性对比度达标 (WCAG AA)

---

## 8. 导出规格

### 8.1 设计 Token 导出格式

```json
{
  "colors": {
    "primary": { "value": "#0F172A", "type": "color" },
    "background": { "value": "#FFFFFF", "type": "color" }
  },
  "spacing": {
    "1": { "value": "4px", "type": "spacing" },
    "2": { "value": "8px", "type": "spacing" }
  },
  "borderRadius": {
    "md": { "value": "6px", "type": "borderRadius" },
    "lg": { "value": "8px", "type": "borderRadius" }
  }
}
```

### 8.2 组件标注

每个组件需标注:
- 尺寸 (宽高、内边距、间距)
- 颜色 (使用 token 名称)
- 字体 (大小、字重、行高)
- 交互状态
- 响应式行为

---

*文档版本：1.0*
*最后更新：2026-04-04*
*基于代码版本：v1.0.0*
