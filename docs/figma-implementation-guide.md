# Figma 设计实现指南

> 基于 Markwritter 现有前端代码的完整 Figma 设计实现指南

---

## 📋 文档索引

本项目包含以下设计文档：

| 文档 | 描述 | 路径 |
|------|------|------|
| **设计规范** | 完整的设计系统规范（颜色、字体、组件） | [`figma-design-spec.md`](./figma-design-spec.md) |
| **页面线框图** | 所有页面的详细线框图和布局规格 | [`figma-wireframes.md`](./figma-wireframes.md) |
| **实现指南** | 本文档，Figma 实现步骤和建议 |

---

## 🚀 开始 Figma 设计

### 方式 1：使用 Figma MCP（推荐）

如果已连接 Figma MCP，可以运行以下命令自动生成设计：

```bash
# 使用 figma-generate-design skill
/figma-generate-design
```

**前置条件：**
- Figma MCP 服务器已连接
- 目标 Figma 文件已创建
- 设计系统组件库已发布（或准备从零创建）

### 方式 2：手动创建

1. **创建新 Figma 文件**
   - 文件名：`Markwritter Design System`
   - 团队：选择你的团队

2. **设置 Pages 结构**
   ```
   🎨 Foundations
   ├── Colors
   ├── Typography
   ├── Spacing
   └── Shadows

   🧩 Components
   ├── Buttons
   ├── Cards
   ├── Inputs
   ├── Badges
   ├── Alerts
   ├── Navigation
   └── Overlays

   📄 Templates
   ├── Chat Page
   ├── Skills Page
   ├── Explore Page
   ├── Query Page
   ├── Record Page
   ├── Logs Page
   └── Settings Page

   🚀 Exports
   └── Design Specs
   ```

3. **创建 Color Styles**
   - 参考 [`figma-design-spec.md`](./figma-design-spec.md#11-颜色变量)
   - 为 Light 和 Dark 模式分别创建颜色变量

4. **创建 Text Styles**
   ```
   text-xs      12px  Regular
   text-sm      14px  Regular
   text-base    16px  Regular
   text-lg      18px  Medium (500)
   text-xl      20px  SemiBold (600)
   text-2xl     24px  Bold (700)
   ```

5. **创建组件库**
   - 按照 [`figma-design-spec.md`](./figma-design-spec.md#2-核心组件规范) 的规格
   - 为每个组件创建变体（Variants）

---

## 🎨 设计系统快速参考

### 颜色 (Colors)

**主色调：**
```
Primary:       #0F172A (深蓝)
Primary-FG:    #F8FAFC (白色)
Background:    #FFFFFF (白色) / #0B1120 (深色)
Foreground:    #0C1427 (深色) / #F8FAFC (浅色)
```

**功能色：**
```
Secondary:     #F1F5F9
Muted:         #F1F5F9
Destructive:   #EF4444
Border:        #E2E8F0
```

### 圆角 (Corner Radius)

```
Small:   6px  (buttons, inputs)
Medium:  8px  (cards)
Large:   12px (large cards)
```

### 间距 (Spacing)

```
1:   4px
2:   8px
3:   12px
4:   16px
6:   24px
```

### 按钮尺寸

| Size | Height | Padding |
|------|--------|---------|
| xs   | 24px   | 8px     |
| sm   | 32px   | 12px    |
| default | 36px | 16px  |
| lg   | 40px   | 24px    |

---

## 📱 页面设计清单

### Chat 页面
- [ ] Panel Header (42px, border-b)
- [ ] Empty State (centered, icon + text)
- [ ] Message Bubbles (user/assistant styles)
- [ ] Thinking Indicator (spinner)
- [ ] Input Area (textarea + source context)
- [ ] Error Alert (destructive variant)

### Skills 页面
- [ ] Page Header
- [ ] Skills Grid (3 columns)
- [ ] Skill Cards (Card component)
- [ ] Run Button

### Explore 页面
- [ ] Knowledge Graph container
- [ ] Node styles (5 connection levels)
- [ ] Edge styles (gray, 1px, arrow)
- [ ] Legend component
- [ ] MiniMap + Zoom Controls

### Query 页面
- [ ] Search Mode Selector (dropdown)
- [ ] Search Input (with icons)
- [ ] Suggestions Dropdown
- [ ] Results List
- [ ] Result Cards
- [ ] No Results State

### Record 页面
- [ ] Quick Record Form
- [ ] Textarea (min-height 120px)
- [ ] Action Bar (helper text + button)
- [ ] Template Selector

### Logs 页面
- [ ] Filter Bar
- [ ] Log Stream (mono font)
- [ ] Log Levels (color coded)
- [ ] Empty State

### Settings 页面
- [ ] Tabs (horizontal)
- [ ] Form Groups
- [ ] Radio Groups
- [ ] Sliders
- [ ] Save Button

---

## 🛠️ Figma 操作技巧

### 创建颜色变量

1. 打开 **Local Variables** 面板
2. 创建新集合 `Markwritter Colors`
3. 添加颜色变量：
   ```
   --background      #FFFFFF
   --foreground      #0C1427
   --primary         #0F172A
   --primary-foreground  #F8FAFC
   ...
   ```
4. 为 Dark 模式创建第二个 Mode

### 创建组件变体

**Button 组件：**
1. 创建一个 Frame，命名为 `Button`
2. 添加属性：
   - `Variant`: default, destructive, outline, secondary, ghost, link
   - `Size`: xs, sm, default, lg, icon
   - `State`: default, hover, active, disabled
3. 为每个组合创建变体

**Card 组件：**
1. 创建主组件 `Card`
2. 添加子组件：
   - `CardHeader`
   - `CardTitle`
   - `CardDescription`
   - `CardAction`
   - `CardContent`
   - `CardFooter`

### 使用 Auto Layout

所有组件都应该使用 Auto Layout：

```
Button (Horizontal, gap-2)
├── Icon (w-4 h-4)
└── Label (text-sm)

Card (Vertical, gap-6)
├── CardHeader (Vertical, gap-2)
├── CardContent (Vertical)
└── CardFooter (Horizontal)
```

### 响应式设计

为不同断点创建变体：

| Breakpoint | Width | Sidebar |
|------------|-------|---------|
| Mobile | 375px | Drawer |
| Tablet | 768px | Collapsed (56px) |
| Desktop | 1440px | Expanded (368px) |

---

## 📤 导出设计

### 导出为开发规格

1. 选择要导出的 Frame
2. 在 **Inspect** 面板中查看代码
3. 导出为 PDF 或共享原型链接

### 导出设计 Token

使用 Figma 插件导出设计 Token：
- **Tokens Studio** (推荐)
- **Style Dictionary**
- **Figma to React**

导出格式示例：
```json
{
  "colors": {
    "primary": { "value": "#0F172A", "type": "color" }
  },
  "spacing": {
    "4": { "value": "16px", "type": "spacing" }
  }
}
```

---

## ✅ 设计审查清单

在交付开发前检查：

### 基础规范
- [ ] 所有颜色使用设计 token 命名
- [ ] 间距符合 4px 网格系统
- [ ] 字体大小/行高符合类型比例
- [ ] 按钮/输入框高度符合规范 (36px default)

### 交互状态
- [ ] Hover 状态已定义
- [ ] Active 状态已定义
- [ ] Disabled 状态已定义
- [ ] Focus 状态已定义（可访问性）

### 主题支持
- [ ] Light 模式完整
- [ ] Dark 模式完整
- [ ] 颜色对比度符合 WCAG AA

### 响应式设计
- [ ] Mobile (< 768px) 布局
- [ ] Tablet (≥ 768px) 布局
- [ ] Desktop (≥ 1024px) 布局

### 组件完整性
- [ ] 所有变体已创建
- [ ] 所有尺寸已创建
- [ ] 图标已嵌入/链接

---

## 🔗 相关资源

### 前端代码参考
- **UI 组件库**: `web/components/ui/`
- **布局组件**: `web/components/layout/`
- **页面组件**: `web/app/`
- **样式定义**: `web/app/globals.css`

### 设计资源
- [Radix UI Primitives](https://www.radix-ui.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)

---

## 📞 获取帮助

如需进一步协助，请参考：
1. [`figma-design-spec.md`](./figma-design-spec.md) - 完整设计规范
2. [`figma-wireframes.md`](./figma-wireframes.md) - 页面线框图
3. 现有前端代码 - 最准确的设计参考

---

*文档版本：1.0*
*创建日期：2026-04-04*
*适用于 Markwritter v1.0.0*
