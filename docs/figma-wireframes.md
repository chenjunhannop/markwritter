# Markwritter 页面线框图规格

> 所有页面的详细线框图规格，用于 Figma 设计实现

---

## 1. Chat 页面 (/chat)

### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar │                    Chat Area                         │
│ (56px)  │ ┌──────────────────────────────────────────────────┐ │
│         │ │ Panel Header (h-14 / 56px)                       │ │
│  Nav    │ │ "Chat"  [2 sources]              [+] New Chat    │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │ Error Alert (conditional)                        │ │
│         │ │ ⚠️ Error message  [Retry] [Dismiss]              │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │                                                    │ │
│         │ │  Messages Area (flex-1, overflow-y-auto)          │ │
│         │ │                                                    │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ User Message                               │  │ │
│         │ │  │ How do I connect to the database?          │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ Assistant Message                          │  │ │
│         │ │  │ To connect to the database, you need to... │  │ │
│         │ │  │ [Source 1] [Source 2]                      │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ │  [Thinking...] (when isThinking)                  │ │
│         │ │                                                    │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │ Input Area (border-t, p-3)                       │ │
│         │ │ ┌────────────────────────────────────────────┐   │ │
│         │ │ │ Type your message...                       │   │ │
│         │ │ └────────────────────────────────────────────┘   │ │
│         │ │ [📄 2 sources selected] [Clear]                  │ │
│         │ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 组件规格

**Panel Header:**
- Height: `42px (h-[42px])`
- Background: `--background`
- Border-bottom: `1px solid --border`
- Padding: `px-3 (12px)`
- Elements:
  - Title: `font-semibold, text-[13px]`
  - Badge: `variant="secondary", text-[10px]`
  - New Chat Button: `variant="ghost", size="icon", h-7 w-7`

**Message Bubble (User):**
- Background: `--primary`
- Text: `--primary-foreground`
- Rounded: `rounded-lg`
- Padding: `px-4 py-2`
- Max-width: `max-w-[80%]`
- Self-align: `self-end`

**Message Bubble (Assistant):**
- Background: `--secondary`
- Text: `--foreground`
- Rounded: `rounded-lg`
- Padding: `px-4 py-2`
- Max-width: `max-w-[80%]`
- Self-align: `self-start`

**Empty State:**
```tsx
<div className="flex flex-col items-center justify-center h-full">
  <MessageSquare className="h-12 w-12 mb-4 opacity-30" />
  <h3 className="text-lg font-medium mb-1">Start a conversation</h3>
  <p className="text-sm text-center max-w-xs text-muted-foreground">
    Select a source from the left panel or type a message below.
  </p>
</div>
```

**Thinking Indicator:**
```tsx
<div className="flex items-center gap-2 px-4 py-2 text-muted-foreground">
  <Loader2 className="h-4 w-4 animate-spin" />
  <span className="text-sm">Thinking...</span>
</div>
```

---

## 2. Skills 页面 (/skills)

### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar │                    Skills Page                       │
│         │ ┌──────────────────────────────────────────────────┐ │
│         │ │ Header (h-14, border-b)                          │ │
│         │ │ Skills                          [+ New Skill]    │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │                                                    │ │
│         │ │  Skill Cards Grid (grid, gap-4)                  │ │
│         │ │  ┌──────────────┐ ┌──────────────┐               │ │
│         │ │  │ 🧩 Hello     │ │ 📝 Summarize │               │ │
│         │ │  │ Run a simple │ │ Summarize    │               │ │
│         │ │  │ skill        │ │ notes        │               │ │
│         │ │  │ [Run]        │ │ [Run]        │               │ │
│         │ │  └──────────────┘ └──────────────┘               │ │
│         │ │  ┌──────────────┐ ┌──────────────┐               │ │
│         │ │  │ 🔍 Search    │ │ 📊 Analyze   │               │ │
│         │ │  │ Search docs  │ │ data         │               │ │
│         │ │  │ [Run]        │ │ [Run]        │               │ │
│         │ │  └──────────────┘ └──────────────┘               │ │
│         │ │                                                    │ │
│         │ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Skill Card 规格

```tsx
<Card className="w-full">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <Icon className="w-5 h-5" />
      Skill Name
    </CardTitle>
    <CardDescription>Skill description</CardDescription>
  </CardHeader>
  <CardContent>
    <p className="text-sm text-muted-foreground">
      Detailed description of what this skill does.
    </p>
  </CardContent>
  <CardFooter>
    <Button>Run Skill</Button>
  </CardFooter>
</Card>
```

**Grid Layout:**
- Columns: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Gap: `gap-4`

---

## 3. Explore 页面 (/explore)

### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar │                    Explore Page                      │
│         │ ┌──────────────────────────────────────────────────┐ │
│         │ │ Header (h-14, border-b)                          │ │
│         │ │ Knowledge Graph                                  │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │                                                    │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │                                            │  │ │
│         │ │  │         🟢 Node A                          │  │ │
│         │ │  │           ╱ ╲                              │  │ │
│         │ │  │          ╱   ╲                             │  │ │
│         │ │  │        🔵     🔵                           │  │ │
│         │ │  │      Node B   Node C                       │  │ │
│         │ │  │         ╲     ╱                            │  │ │
│         │ │  │          ╲   ╱                             │  │ │
│         │ │  │           🟠                               │  │ │
│         │ │  │         Node D                             │  │ │
│         │ │  │                                            │  │ │
│         │ │  │  [Legend]                                  │  │ │
│         │ │  │  🟢 0      🟢 1-2   🔵 3-5                 │  │ │
│         │ │  │  🟠 6-10   🔴 10+                          │  │ │
│         │ │  │                                            │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │  [MiniMap] [+ Zoom Controls]                     │ │
│         │ │                                                    │ │
│         │ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Graph Node 规格

**节点样式:**
| Connections | Color | Size |
|-------------|-------|------|
| 0 | `#94a3b8` (gray-400) | 20px |
| 1-2 | `#22c55e` (green-500) | 22-28px |
| 3-5 | `#3b82f6` (blue-500) | 30-38px |
| 6-10 | `#f59e0b` (amber-500) | 40-45px |
| 10+ | `#ef4444` (red-500) | 46-50px |

**节点属性:**
- Shape: Circle
- Border: `2px solid #fff`
- Text: White, 12px, centered
- Font: System font

**Edge 样式:**
- Stroke: `#64748b` (slate-500)
- Stroke-width: `1px`
- Marker-end: Arrow (closed, same color)

**Legend 组件:**
```tsx
<div className="bg-white dark:bg-gray-800 border rounded-lg p-3 shadow-sm">
  <h3 className="text-xs font-medium mb-2">Connections</h3>
  {[
    { color: '#94a3b8', label: '0' },
    { color: '#22c55e', label: '1-2' },
    { color: '#3b82f6', label: '3-5' },
    { color: '#f59e0b', label: '6-10' },
    { color: '#ef4444', label: '10+' },
  ].map(({ color, label }) => (
    <div key={label} className="flex items-center gap-2">
      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
      <span className="text-xs text-gray-600">{label}</span>
    </div>
  ))}
</div>
```

---

## 4. Query 页面 (/query)

### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar │                    Query Page                        │
│         │ ┌──────────────────────────────────────────────────┐ │
│         │ │ Header (h-14, border-b)                          │ │
│         │ │ Search Notes                                     │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │                                                    │ │
│         │ │  Search Bar                                       │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ [Hybrid ▼] 🔍 Search your notes... [✕]    │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │  [🔍] (search button)                            │ │
│         │ │                                                    │ │
│         │ │  Suggestions (dropdown, conditional)              │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ suggestion 1                               │  │ │
│         │ │  │ suggestion 2 (hovered)                     │  │ │
│         │ │  │ suggestion 3                               │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │ Results Area                                     │ │
│         │ │                                                    │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ 📄 Note Title 1                            │  │ │
│         │ │  │ This is the excerpt from the note that...  │  │ │
│         │ │  │ Tags: [tag1] [tag2]  •  Score: 0.95       │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ 📄 Note Title 2                            │  │ │
│         │ │  │ Another excerpt from a different note...   │  │ │
│         │ │  │ Tags: [tag3]  •  Score: 0.87              │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ │  No Results State (conditional)                   │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │           🔍 No results found              │  │ │
│         │ │  │  Try adjusting your search terms           │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Search Input 规格

**Mode Selector:**
```tsx
<select className="h-10 px-3 rounded-lg border bg-white text-sm">
  <option value="hybrid">Hybrid</option>
  <option value="keyword">Keyword</option>
  <option value="semantic">Semantic</option>
</select>
```

**Input Field:**
- Height: `40px (h-10)`
- Width: `flex-1`
- Padding: `pl-10 pr-10`
- Border: `border rounded-lg`
- Focus: `ring-2 ring-blue-500`

**Search Button:**
- Height: `40px (h-10)`
- Padding: `px-4`
- Background: `bg-blue-600`
- Text: White
- Disabled: `opacity-50 cursor-not-allowed`

**Suggestions Dropdown:**
- Z-index: `10`
- Background: `bg-white dark:bg-gray-800`
- Border: `border rounded-lg shadow-lg`
- Max-height: `200px`
- Item: `px-4 py-2 hover:bg-gray-100`

**Result Card:**
```tsx
<Card className="cursor-pointer hover:bg-muted/50">
  <CardContent className="py-4">
    <div className="flex items-start justify-between">
      <div>
        <h3 className="font-medium">Note Title</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">
          Excerpt from the note...
        </p>
        <div className="flex items-center gap-2 mt-2">
          <Badge>tag1</Badge>
          <Badge>tag2</Badge>
        </div>
      </div>
      <span className="text-xs text-muted-foreground">
        Score: 0.95
      </span>
    </div>
  </CardContent>
</Card>
```

---

## 5. Record 页面 (/record)

### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar │                    Record Page                       │
│         │ ┌──────────────────────────────────────────────────┐ │
│         │ │ Header (h-14, border-b)                          │ │
│         │ │ Quick Note                        [Template ▼]   │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │                                                    │ │
│         │ │  Quick Record Form                                │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │                                            │  │ │
│         │ │  │  Type your quick note here...              │  │ │
│         │ │  │                                            │  │ │
│         │ │  │                                            │  │ │
│         │ │  │                                            │  │ │
│         │ │  │                                            │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │  Press Ctrl+Enter to save                        │ │
│         │ │                              [📤 Save]           │ │
│         │ │                                                    │ │
│         │ │  Error State (conditional)                        │ │
│         │ │  ⚠️ Failed to save. Please try again.             │ │
│         │ │                                                    │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │ Recent Notes (optional)                          │ │
│         │ │ ┌────────────┐ ┌────────────┐ ┌────────────┐    │ │
│         │ │ │ Note 1     │ │ Note 2     │ │ Note 3     │    │ │
│         │ │ │ 2024-01-01 │ │ 2024-01-02 │ │ 2024-01-03 │    │ │
│         │ │ └────────────┘ └────────────┘ └────────────┘    │ │
│         │ │                                                    │ │
│         │ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Record Form 规格

**Textarea:**
- Min-height: `120px`
- Resize: `resize-none`
- Border: `border rounded-lg`
- Padding: `p-3`
- Focus: `ring-2 ring-blue-500`

**Action Bar:**
- Display: `flex items-center justify-between`
- Gap: `gap-2`
- Helper text: `text-xs text-muted-foreground`

**Save Button:**
```tsx
<Button type="submit" disabled={!hasContent || isSaving}>
  {isSaving ? (
    <>
      <Loader2 className="h-4 w-4 animate-spin" />
      Saving...
    </>
  ) : (
    <>
      <Send className="h-4 w-4" />
      Save
    </>
  )}
</Button>
```

---

## 6. Logs 页面 (/logs)

### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar │                    Logs Page                         │
│         │ ┌──────────────────────────────────────────────────┐ │
│         │ │ Header (h-14, border-b)                          │ │
│         │ │ System Logs     [🔄 Refresh] [🗑️ Clear]         │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │ Filter Bar                                       │ │
│         │ │ [All ▼] [Error ▼] [Search logs...]              │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │                                                    │ │
│         │ │  Log Stream (scrollable)                          │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ [INFO]  10:23:45  Application started     │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ [WARN]  10:24:12  High memory usage       │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ [ERROR] 10:25:00  Failed to connect      │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │ [DEBUG] 10:25:30  Processing request     │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ │  Empty State (conditional)                        │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │        📋 No logs available                │  │ │
│         │ │  │  Logs will appear here in real-time        │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Log Entry 规格

**Log Levels:**
| Level | Color | Icon |
|-------|-------|------|
| INFO | `text-blue-500` | ℹ️ |
| WARN | `text-amber-500` | ⚠️ |
| ERROR | `text-red-500` | ❌ |
| DEBUG | `text-gray-500` | 🔍 |

**Log Entry Component:**
```tsx
<div className="font-mono text-sm border-b py-2 px-4 hover:bg-muted/50">
  <span className="text-blue-500">[INFO]</span>
  <span className="text-muted-foreground ml-2">10:23:45</span>
  <span className="ml-2">Application started</span>
</div>
```

---

## 7. Settings 页面 (/settings)

### 页面结构

```
┌─────────────────────────────────────────────────────────────────┐
│ Sidebar │                   Settings Page                      │
│         │ ┌──────────────────────────────────────────────────┐ │
│         │ │ Header (h-14, border-b)                          │ │
│         │ │ Settings                                         │ │
│         │ ├──────────────────────────────────────────────────┤ │
│         │ │                                                    │ │
│         │ │  Tabs (horizontal)                                │ │
│         │ │  [General] [LLM] [Vault] [Advanced]              │ │
│         │ │                                                    │ │
│         │ │  Tab Content                                      │ │
│         │ │  ┌────────────────────────────────────────────┐  │ │
│         │ │  │                                            │  │ │
│         │ │  │  General Settings                          │  │ │
│         │ │  │                                            │  │ │
│         │ │  │  Theme                                     │  │ │
│         │ │  │  ○ Light  ● Dark  ○ System                │  │ │
│         │ │  │                                            │  │ │
│         │ │  │  Sidebar Width                             │  │ │
│         │ │  │  [─────●─────] 56px                        │  │ │
│         │ │  │                                            │  │ │
│         │ │  │  Language                                  │  │ │
│         │ │  │  [English ▼]                               │  │ │
│         │ │  │                                            │  │ │
│         │ │  │  [Save Changes]                            │  │ │
│         │ │  │                                            │  │ │
│         │ │  └────────────────────────────────────────────┘  │ │
│         │ │                                                    │ │
│         │ └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Settings Form 规格

**Form Group:**
```tsx
<div className="space-y-4">
  <div>
    <label className="text-sm font-medium">Label</label>
    <p className="text-xs text-muted-foreground">Description</p>
  </div>
  <Input defaultValue="value" />
</div>
```

**Radio Group:**
```tsx
<div className="flex items-center gap-4">
  <label className="flex items-center gap-2">
    <input type="radio" name="theme" value="light" />
    Light
  </label>
  <label className="flex items-center gap-2">
    <input type="radio" name="theme" value="dark" />
    Dark
  </label>
</div>
```

**Slider:**
```tsx
<input
  type="range"
  min="16"
  max="320"
  defaultValue="56"
  className="w-full"
/>
```

---

## 8. 响应式布局规格

### 断点定义

| Breakpoint | Min Width | Sidebar Behavior |
|------------|-----------|------------------|
| Mobile | < 768px | Drawer (hidden by default) |
| Tablet | ≥ 768px | Collapsible (56px/368px) |
| Desktop | ≥ 1024px | Collapsible (56px/368px) |

### Mobile 布局

```
┌──────────────────────────────────┐
│ ☰ Header (h-14)                 │
├──────────────────────────────────┤
│                                  │
│         Main Content             │
│                                  │
├──────────────────────────────────┤
│ Bottom Nav (mobile only)         │
│ [🏠] [🔍] [➕] [⚙️]              │
└──────────────────────────────────┘
```

### Drawer 组件 (Mobile)

```tsx
<Sheet open={isOpen} onOpenChange={setIsOpen}>
  <SheetContent side="left" className="w-64">
    <div className="py-4">
      <div className="h-14 border-b px-4 flex items-center">
        <span className="font-bold text-lg">Markwritter</span>
      </div>
      <nav className="py-4">
        {/* Nav items */}
      </nav>
    </div>
  </SheetContent>
</Sheet>
```

---

## 9. 暗色模式规格

### 颜色映射

| Token | Light | Dark |
|-------|-------|------|
| `--background` | `#FFFFFF` | `#0B1120` |
| `--foreground` | `#0C1427` | `#F8FAFC` |
| `--card` | `#FFFFFF` | `#0B1120` |
| `--primary` | `#0F172A` | `#F8FAFC` |
| `--secondary` | `#F1F5F9` | `#1E293B` |
| `--muted` | `#F1F5F9` | `#1E293B` |
| `--border` | `#E2E8F0` | `#1E293B` |

### 暗色模式切换

```tsx
<html className={dark ? 'dark' : ''}>
  <body className="bg-background text-foreground">
    {/* Content */}
  </body>
</html>
```

---

*文档版本：1.0*
*最后更新：2026-04-04*
*适用于 Figma 设计实现*
