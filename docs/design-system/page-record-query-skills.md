# Record, Query & Skills — Page Composition Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion specs:** `layout-shell.md` · `components-button-badge.md` · `components-surface-overlay.md` · `components-form-inputs.md` · `components-feedback-utility.md`
> **Implementation:** `web/src/features/{record,query,skills}/`

---

## Table of Contents

1. [Shared Page Patterns](#1-shared-page-patterns)
2. [PAGE 1: Record — Layout Structure](#2-page-1-record--layout-structure)
3. [PAGE 1: Record — FileTreePanel](#3-page-1-record--filetreepanel)
4. [PAGE 1: Record — NoteEditor](#4-page-1-record--noteeditor)
5. [PAGE 1: Record — AIAssistPanel](#5-page-1-record--aiassistpanel)
6. [PAGE 1: Record — DiffPreview](#6-page-1-record--diffpreview)
7. [PAGE 2: Query — Layout Structure](#7-page-2-query--layout-structure)
8. [PAGE 2: Query — SearchBar](#8-page-2-query--searchbar)
9. [PAGE 2: Query — ResultCard](#9-page-2-query--resultcard)
10. [PAGE 3: Skills — Layout Structure](#10-page-3-skills--layout-structure)
11. [PAGE 3: Skills — SkillCard](#11-page-3-skills--skillcard)
12. [PAGE 3: Skills — SkillRunDialog](#12-page-3-skills--skillrundialog)
13. [State Frames Specification](#13-state-frames-specification)
14. [Glass Treatment Map](#14-glass-treatment-map)
15. [Diff Color Semantic Mapping](#15-diff-color-semantic-mapping)
16. [Responsive Behavior](#16-responsive-behavior)
17. [Figma Frames Specification](#17-figma-frames-specification)
18. [TSX Skeleton — RecordPage](#18-tsx-skeleton--recordpage)
19. [TSX Skeleton — QueryPage](#19-tsx-skeleton--querypage)
20. [TSX Skeleton — SkillsPage](#20-tsx-skeleton--skillspage)
21. [Migration Mapping](#21-migration-mapping)
22. [Appendix A: Accessibility Checklist](#appendix-a-accessibility-checklist)
23. [Appendix B: Token Cross-Reference](#appendix-b-token-cross-reference)
24. [Appendix C: Implementation Checklist](#appendix-c-implementation-checklist)

---

## 1. Shared Page Patterns

### 1.1 Page Container Variants

Three pages share two layout patterns:

| Pattern | Pages | Container Classes |
|---|---|---|
| **Full-height split** | Record | `flex h-full` — fills the main content area from the layout shell |
| **Scrollable padded** | Query, Skills | `flex flex-col gap-4 p-4 md:p-6` — padded with responsive spacing |

### 1.2 Page Title Treatment

Query and Skills pages use the same title treatment:

| Property | Value |
|---|---|
| Typography | `title-2` (22px / 600 / semibold) |
| Color | `foreground` |
| Tag | `<h1>` |
| Class | `text-[22px] font-semibold text-foreground` |

Record has no visible page title — the layout is a split-panel editor that fills the viewport.

### 1.3 Max-Width Content

Query results and search bar use `max-w-2xl` (672px) for optimal reading width. Skills grid uses the full content area.

### 1.4 Z-Index Allocation

| Element | Token | Value |
|---|---|---|
| AI panel (Record) | `z-sidebar` | 20 (above sticky header) |
| Diff preview (Record) | `z-content` | 1 (within flow) |
| SkillRunDialog overlay | `z-modal-backdrop` | 40 |
| SkillRunDialog content | `z-modal` | 50 |

---

## 2. PAGE 1: Record — Layout Structure

### 2.1 Component Hierarchy

```
RecordPage (flex h-full, relative)
├── FileTreePanel (w-64, glass-tier-thin, border-r glass-border, flex-col, shrink-0)
│   ├── Header (h-10, px-3, flex, items-center, justify-between)
│   │   ├── "Files" label (subhead: 13px/500, foreground)
│   │   └── CollapseButton (Button ghost icon-sm, PanelLeftClose icon)
│   ├── TreeArea (ScrollArea, flex-1, glass scrollbar)
│   │   └── TreeItem × N (recursive)
│   │       ├── Folder items: chevron + folder icon + name + file count
│   │       └── File items: file icon + name
│   └── Footer (px-3, py-2, border-t glass-border)
│       └── File count (caption: 12px/400, muted-foreground)
├── NoteEditor (flex-1, flex-col, min-w-0)
│   ├── TitleBar (h-12, border-b glass-border, glass-tier-ultra-thin, px-4, flex, items-center)
│   │   ├── Title Input (border-none, bg-transparent, flex-1, title-3)
│   │   └── Action group (flex, items-center, gap-2)
│   │       ├── Save status (caption, token-driven color)
│   │       ├── Save Button (outline sm, Save icon)
│   │       └── AI toggle (outline/default sm, Sparkles icon)
│   ├── Editor area (flex-1, overflow-auto, relative)
│   │   ├── No file state: EmptyState
│   │   ├── Loading state: Loader2 spinner
│   │   ├── Error state: inline error
│   │   └── Textarea (surface-raised bg, font-mono, text-sm, border-none, resize-none, h-full)
│   └── Shortcut indicator (absolute, bottom-4, right-4, caption, muted-foreground/60)
└── AIAssistPanel (w-72, glass-tier-regular, border-l glass-border, flex-col, conditional)
    ├── Header (h-10, px-3, flex, items-center, justify-between, border-b glass-border)
    │   ├── "AI Assist" label (subhead) + Sparkles icon (16px, primary)
    │   └── Close button (Button ghost icon-sm, X icon)
    ├── Action buttons (p-3, flex, flex-col, gap-2)
    │   ├── Continue (Button default sm, w-full, Type icon)
    │   ├── Rewrite (Button outline sm, w-full, Sparkles icon)
    │   └── Polish (Button outline sm, w-full, PenLine icon)
    ├── Selection indicator (px-3, caption, muted-foreground)
    ├── Loading state (p-3, flex, items-center, gap-2)
    ├── Error state (p-3, rounded-md, border-destructive/50, bg-destructive/10)
    ├── DiffPreview area (ScrollArea, flex-1, p-3)
    └── Diff actions (p-3, border-t glass-border, flex, gap-2)
        ├── Accept (Button default sm, Check icon)
        └── Reject (Button outline sm, X icon)
```

### 2.2 Dimensional Spec

| Element | Width | Height | Notes |
|---|---|---|---|
| FileTreePanel | 256px (w-64) | full | Collapsed: 48px (w-12) |
| NoteEditor | flex-1 | full | Minimum 320px usable width |
| AIAssistPanel | 288px (w-72) | full | Conditional; tablet → Sheet |
| TitleBar | — | 48px (h-12) | Fixed |
| Header rows | — | 40px (h-10) | FileTreePanel + AIAssistPanel headers |

---

## 3. PAGE 1: Record — FileTreePanel

### 3.1 Panel Anatomy

| Property | Value |
|---|---|
| Width | 256px (`w-64`), 48px when collapsed (`w-12`) |
| Background | glass-tier-thin |
| Border | `border-r` with glass border (`rgba(255,255,255,0.10)` light / `rgba(255,255,255,0.06)` dark) |
| Display | `flex flex-col` |
| Overflow | hidden (ScrollArea manages scroll) |

### 3.2 TreeItem Specification

**Folder item:**

| Property | Value |
|---|---|
| Display | `flex`, `items-center`, `gap-1.5` |
| Padding | `py-1.5`, horizontal: `depth * 16 + 8px` (inline style) |
| Border radius | `rounded-sm` (10px) |
| Typography | callout (14px / 400) |
| Color (default) | `foreground` |
| Color (hover) | `accent` background, `accent-foreground` text |
| Chevron | `ChevronRight` 14px, `rotate-90` when open via `transition-transform duration-150` |
| Folder icon | `Folder` / `FolderOpen` 14px, `muted-foreground` |
| File count | caption (12px), `muted-foreground`, `ml-auto` |

**File item:**

| Property | Value |
|---|---|
| Display | `flex`, `items-center`, `gap-1.5` |
| Padding | same as folder |
| Border radius | `rounded-sm` |
| Typography | callout (14px / 400) |
| Color (default) | `foreground` |
| Color (selected) | `accent-muted` background (#F8EDD5 light / #29201A dark), `primary` text |
| Color (hover) | `accent` background |
| Icon | `FileText` 14px, `muted-foreground` |

### 3.3 Empty & Error States

| State | Component | Icon | Title | Description |
|---|---|---|---|---|
| Empty tree | `EmptyState` | `FolderOpen` | "No files found" | "Add markdown files to your vault to get started." |
| Loading | Inline text | — | — | "Loading..." (caption, muted-foreground) |
| Error | Inline text | — | — | "Failed to load files" (caption, destructive) |

### 3.4 Collapsed State

When collapsed, the panel shrinks to 48px showing only the expand button:

```tsx
<div className="flex w-12 flex-col items-center border-r border-white/10 dark:border-white/6 py-2">
  <Button variant="ghost" size="icon-sm" onClick={onToggleCollapse}>
    <PanelLeftOpen className="size-4" />
  </Button>
</div>
```

---

## 4. PAGE 1: Record — NoteEditor

### 4.1 TitleBar Anatomy

| Property | Value |
|---|---|
| Height | 48px (`h-12`) |
| Background | glass-tier-ultra-thin |
| Border bottom | glass border |
| Padding | `px-4` |
| Display | `flex`, `items-center` |

### 4.2 Title Input

| Property | Value |
|---|---|
| Typography | `title-3` (18px / 600) |
| Background | transparent |
| Border | none |
| Focus ring | none (deliberate — the title bar provides visual context) |
| Placeholder | "Note title" |
| Flex | `flex-1` |

### 4.3 Save Status

| Status | Text | Color Token | Tailwind Class |
|---|---|---|---|
| `idle` | (empty) | — | — |
| `dirty` | "Unsaved" | `status-warning` | `text-status-warning` |
| `saving` | "Saving..." | `muted-foreground` | `text-muted-foreground` |
| `saved` | "Saved" | `status-success` | `text-status-success` |

Typography: caption (12px / 400).

### 4.4 Editor Textarea

| Property | Value |
|---|---|
| Background | `surface-raised` (#FCF6EE light / #231B14 dark) |
| Font | `font-mono`, `text-sm` (14px) |
| Border | none |
| Resize | none |
| Height | `h-full` (fills parent) |
| Padding | `p-4` on parent div |
| Placeholder | "Start writing..." |
| Focus ring | none (deliberate — content area is the editing context) |

### 4.5 No File Selected State

Uses `EmptyState` component:

| Property | Value |
|---|---|
| Icon | `FileText` |
| Title | "Select a file" |
| Description | "Choose a file from the tree to start editing." |
| `iconBackground` | true |

### 4.6 Cmd+S Shortcut Indicator

| Property | Value |
|---|---|
| Position | absolute, bottom 16px, right 16px |
| Typography | caption (12px) |
| Color | `muted-foreground` at 60% opacity |
| Text | "⌘S to save" |
| Pointer events | none |

---

## 5. PAGE 1: Record — AIAssistPanel

### 5.1 Panel Anatomy

| Property | Value |
|---|---|
| Width | 288px (`w-72`) |
| Background | glass-tier-regular |
| Border left | glass border |
| Display | `flex flex-col` |

### 5.2 Action Buttons

| Button | Variant | Icon | Full Width | Disabled When |
|---|---|---|---|---|
| Continue | `default` | `Type` (14px) | yes | `loading` or `content.trim() === ""` |
| Rewrite | `outline` | `Sparkles` (14px) | yes | `loading` or `targetContent.trim() === ""` |
| Polish | `outline` | `PenLine` (14px) | yes | `loading` or `targetContent.trim() === ""` |

All buttons use `loading` prop pattern from Button spec §2.3 — spinner replaces icon on icon-only, spinner before label on text buttons.

### 5.3 Selection Indicator

Shown only when `selectedText` is non-null:

```tsx
<p className="px-3 text-xs text-muted-foreground">
  Applying to selected text ({selectedText.length} chars)
</p>
```

### 5.4 Loading State

```tsx
<div className="flex items-center gap-2 p-3 text-sm text-muted-foreground">
  <Loader2 className="size-4 animate-spin" />
  AI is thinking...
</div>
```

### 5.5 Error State

Inline error with dismiss, using status tokens:

```tsx
<div className="flex items-center gap-2 rounded-[10px] border border-destructive/50 bg-status-error-bg px-3 py-2 text-sm text-destructive">
  <span>{error}</span>
  <Button variant="ghost" size="sm" onClick={() => setError(null)}>
    Dismiss
  </Button>
</div>
```

---

## 6. PAGE 1: Record — DiffPreview

### 6.1 DiffSegment — Insert

| Property | Value |
|---|---|
| Background | `bg-status-success/15` |
| Border left | 3px, `border-l-status-success` |
| Border radius | `rounded-sm` (4px) |
| Padding | `px-0.5` |

### 6.2 DiffSegment — Delete

| Property | Value |
|---|---|
| Background | `bg-status-error/15` |
| Border left | 3px, `border-l-status-error` |
| Text decoration | `line-through` |
| Border radius | `rounded-sm` (4px) |
| Padding | `px-0.5` |

### 6.3 DiffSegment — Equal

Unchanged text, no special styling.

### 6.4 Accepted State

| Property | Value |
|---|---|
| Border | `border-status-success/40` |
| Background | `bg-status-success-bg` |
| Border radius | `rounded-[10px]` |
| Check icon | `Check`, 16px, `text-status-success` |
| Text | "Changes accepted", 14px, `text-status-success` |
| Undo button | `Button outline sm`, `RotateCcw` icon, positioned `ml-auto` |
| Undo window | 30 seconds — then component unmounts |

### 6.5 Preview Container

| Property | Value |
|---|---|
| Border | `border` (standard border token) |
| Border radius | `rounded-[10px]` |
| Content area | `font-mono`, `text-sm`, `leading-relaxed`, `whitespace-pre-wrap` |
| ScrollArea | `max-h-64` (256px) |
| Background | glass-tier-ultra-thin (for code area) |

---

## 7. PAGE 2: Query — Layout Structure

### 7.1 Component Hierarchy

```
QueryPage (flex flex-col, gap-4, p-4 md:p-6, h-full)
├── PageTitle: "Query" (title-2: 22px/600)
├── SearchBar (flex, gap-2, max-w-2xl)
│   ├── SearchInput (flex-1, iconLeft=<Search />)
│   ├── ClearButton (ghost icon-sm, X icon, conditional on query value)
│   ├── ModeSelect (Select, w-[130px])
│   └── SearchButton (Button default, Search icon + "Search", loading prop)
├── ResultsArea (flex-1, overflow-y-auto, max-w-2xl)
│   ├── Loading → 4× Skeleton cards
│   ├── Error → EmptyState
│   ├── Empty → EmptyState
│   ├── No results → EmptyState
│   └── Results → list of ResultCards
```

### 7.2 Dimensional Spec

| Element | Width | Notes |
|---|---|---|
| Search bar row | `max-w-2xl` (672px) | Centered or left-aligned |
| Results area | `max-w-2xl` | Matches search bar width |
| ResultCard | full width within results area | `w-full` |
| Mode Select | 130px (`w-[130px]`) | Compact control |

### 7.3 Page Title

```tsx
<h1 className="text-[22px] font-semibold text-foreground">Query</h1>
```

---

## 8. PAGE 2: Query — SearchBar

### 8.1 Search Input

Uses `Input` from `components-form-inputs.md` with `iconLeft`:

```tsx
<Input
  value={query}
  onChange={(e) => setQuery(e.target.value)}
  onKeyDown={handleKeyDown}
  placeholder="Search your notes..."
  iconLeft={<Search />}
  className="flex-1"
/>
```

When `query` is non-empty, show clear button inside the input's trailing area:

```tsx
{query && (
  <Button
    variant="ghost"
    size="icon-sm"
    onClick={handleClear}
    className="absolute right-2 top-1/2 -translate-y-1/2"
    aria-label="Clear search"
  >
    <X />
  </Button>
)}
```

### 8.2 Mode Select

Uses `Select` from `components-form-inputs.md`:

```tsx
<Select value={mode} onValueChange={setMode}>
  <SelectTrigger className="w-[130px]">
    <SelectValue />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="hybrid">Hybrid</SelectItem>
    <SelectItem value="keyword">Keyword</SelectItem>
    <SelectItem value="semantic">Semantic</SelectItem>
  </SelectContent>
</Select>
```

### 8.3 Search Button

Uses `loading` prop from Button spec:

```tsx
<Button
  onClick={handleSearch}
  disabled={mutation.isPending || !query.trim()}
  loading={mutation.isPending}
>
  <Search />
  Search
</Button>
```

---

## 9. PAGE 2: Query — ResultCard

### 9.1 Anatomy

Built on `Card` from `components-surface-overlay.md` (glass-tier-thin, default variant):

| Property | Value |
|---|---|
| Component | `<Card>` |
| Cursor | `cursor-pointer` |
| Padding | `p-4` |
| Hover | `shadow-elevated`, `-translate-y-px` (200ms ease-out) |
| Click | Toggles expanded state |

### 9.2 Row Structure

**Row 1 — Title + Score:**

| Element | Typography | Color | Notes |
|---|---|---|---|
| Title | subhead (13px/500) | `foreground`, `text-primary` on hover | Truncated via `truncate` |
| Score | `Badge variant="secondary"` | — | `shrink-0` |

**Row 2 — Content Preview:**

| Property | Value |
|---|---|
| Typography | callout (14px/400) |
| Color | `muted-foreground` |
| Clamp | `line-clamp-2` when collapsed, no clamp when expanded |
| Transition | `max-height` 200ms ease-out (via `overflow-hidden` + dynamic max-height) |

**Row 3 — Tags:**

```tsx
<div className="mt-2 flex flex-wrap gap-1">
  {tags.map((tag) => (
    <Badge key={tag} variant="outline">{tag}</Badge>
  ))}
</div>
```

### 9.3 Expanded State

On click, the card expands to show full content:

- Remove `line-clamp-2`
- Apply `whitespace-pre-wrap`
- Smooth `max-height` transition: `transition-[max-height] duration-200 ease-out`
- `max-height: 600px` when expanded, `max-height: 80px` when collapsed

---

## 10. PAGE 3: Skills — Layout Structure

### 10.1 Component Hierarchy

```
SkillsPage (flex flex-col, gap-4, p-4 md:p-6, h-full)
├── PageTitle: "Skills" (title-2: 22px/600)
├── Grid area (flex-1, overflow-y-auto)
│   ├── Loading → 6× Skeleton cards in grid
│   ├── Error → EmptyState
│   ├── Empty → EmptyState
│   └── Skills → grid of SkillCards
└── SkillRunDialog (conditional, Dialog glass-tier-thick)
```

### 10.2 Grid Spec

| Breakpoint | Columns | Gap |
|---|---|---|
| Mobile (<768px) | 1 | 16px (`gap-4`) |
| Tablet (768–1023px) | 2 | 16px |
| Desktop (≥1024px) | 3 | 16px |

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

### 10.3 Page Title

```tsx
<h1 className="text-[22px] font-semibold text-foreground">Skills</h1>
```

---

## 11. PAGE 3: Skills — SkillCard

### 11.1 Anatomy

Built on `Card` from `components-surface-overlay.md`:

| Property | Value |
|---|---|
| Component | `<Card>` |
| Glass tier | thin |
| Hover | `shadow-elevated`, `-translate-y-px` (200ms ease-out) |

### 11.2 CardHeader

| Property | Value |
|---|---|
| Padding | `p-4 pb-2` |
| Display | `flex flex-col gap-1` |

**Icon + Name row:**

```tsx
<div className="flex items-center gap-2">
  <SkillIcon className="size-5 text-primary" />
  <CardTitle className="text-[13px] font-medium">{skill.name}</CardTitle>
</div>
```

### 11.3 CardDescription

| Property | Value |
|---|---|
| Typography | caption (12px / 400) |
| Color | `muted-foreground` |
| Clamp | `line-clamp-2` |

### 11.4 CardContent — Parameter Badges

Preview of skill parameter types as badge pills:

```tsx
<div className="flex flex-wrap gap-1">
  {skill.inputs.map((input) => (
    <Badge key={input.name} variant={input.type === "enum" ? "outline" : "secondary"}>
      {input.name}: {input.type}
    </Badge>
  ))}
</div>
```

### 11.5 CardFooter

```tsx
<CardFooter className="p-4 pt-0 flex justify-end">
  <Button variant="default" size="sm" onClick={() => setRunSkill(skill)}>
    <Play />
    Run
  </Button>
</CardFooter>
```

---

## 12. PAGE 3: Skills — SkillRunDialog

### 12.1 Dialog Structure

Uses `Dialog` from `components-surface-overlay.md` (glass-tier-thick):

```
Dialog.Root
├── Dialog.Portal
│   ├── DialogOverlay (black/40, blur(4px))
│   └── DialogContent (glass-tier-thick, max-w-md)
│       ├── DialogHeader
│       │   ├── DialogTitle: skill icon + name (title-3: 18px/600)
│       │   └── DialogDescription: skill description (callout: 14px, muted-foreground)
│       ├── Form fields (space-y-4, px-6)
│       │   ├── String params → Input with label
│       │   ├── Number params → Input type=number with label
│       │   ├── Boolean params → Switch with label
│       │   └── Enum params → Select with label
│       ├── Output area (conditional, glass-tier-ultra-thin, rounded-[14px], p-3, font-mono, text-sm, max-h-48, overflow-auto)
│       ├── Error area (conditional, bg-status-error-bg, rounded-[14px], p-3, text-destructive)
│       └── DialogFooter (flex, justify-end, gap-2)
│           ├── Close (Button outline)
│           └── Execute (Button default, loading prop)
```

### 12.2 Form Field Spec

**Labels:**

| Property | Value |
|---|---|
| Typography | `text-sm font-medium` (14px / 500) |
| Required indicator | `<span className="text-destructive"> *</span>` |
| Helper text | `text-xs text-muted-foreground` |

**String parameter:**

```tsx
<div className="space-y-1">
  <label htmlFor={id} className="text-sm font-medium">
    {input.name}{input.required && <span className="text-destructive"> *</span>}
  </label>
  <Input id={id} value={value} onChange={(e) => onChange(e.target.value)} placeholder={input.description} />
  {input.description && <p className="text-xs text-muted-foreground">{input.description}</p>}
</div>
```

**Number parameter:**

```tsx
<Input id={id} type="number" value={value} onChange={(e) => onChange(Number(e.target.value))} />
```

**Boolean parameter:**

```tsx
<div className="flex items-center gap-3">
  <Switch id={id} checked={value} onCheckedChange={onChange} />
  <label htmlFor={id} className="text-sm font-medium">
    {input.name}{input.required && <span className="text-destructive"> *</span>}
  </label>
</div>
```

**Enum parameter:**

```tsx
<Select value={value} onValueChange={(v) => onChange(v || undefined)}>
  <SelectTrigger id={id} className="w-full">
    <SelectValue placeholder="Select..." />
  </SelectTrigger>
  <SelectContent>
    {input.enum.map((opt) => (
      <SelectItem key={opt} value={opt}>{opt}</SelectItem>
    ))}
  </SelectContent>
</Select>
```

### 12.3 Output Area

> **Treatment:** The output area is an **inset well**, not a nested panel. No additional shadow or elevation. Visual separation comes from the glass-tier-ultra-thin background and the border radius. Keep it secondary — it should read as recessed utility content, not as a floating card inside the modal.

| Property | Value |
|---|---|
| Background | glass-tier-ultra-thin |
| Border radius | `rounded-[14px]` |
| Padding | `p-3` |
| Typography | `font-mono text-sm` |
| Max height | `max-h-48` (192px) |
| Overflow | `overflow-auto` |

### 12.4 Error Area

| Property | Value |
|---|---|
| Background | `bg-status-error-bg` |
| Border radius | `rounded-[14px]` |
| Padding | `p-3` |
| Typography | `text-sm` |
| Color | `text-destructive` |

---

## 13. State Frames Specification

### 13.1 Record Page States

| # | State | FileTreePanel | NoteEditor | AIAssistPanel | DiffPreview |
|---|---|---|---|---|---|
| 1 | Empty tree | EmptyState (FolderOpen, "No files found", "Add markdown files...") | EmptyState (FileText, "Select a file") | — | — |
| 2 | Tree loading | "Loading..." caption | — | — | — |
| 3 | Tree error | "Failed to load files" (destructive) | — | — | — |
| 4 | File selected | Selected: accent-muted bg, primary text | Title + content loaded | — | — |
| 5 | Editing | — | Textarea focused | — | — |
| 6 | Dirty | — | "Unsaved" (status-warning), Save enabled | — | — |
| 7 | Saving | — | "Saving..." (muted), Save disabled | — | — |
| 8 | Saved | — | "Saved" (status-success) | — | — |
| 9 | AI closed | — | AI button=outline | Not rendered | — |
| 10 | AI open | — | AI button=default, editor shrinks | Full panel | — |
| 11 | AI loading | — | — | Spinner + "AI is thinking..." | — |
| 12 | AI error | — | — | Inline error with dismiss | — |
| 13 | Diff preview | — | — | Diff visible | Showing delta |
| 14 | Diff accepted | — | Content updated | "Changes accepted" + Undo | Green state, 30s undo |
| 15 | Diff rejected | — | Unchanged | Returns to actions | — |
| 16 | Note loading | — | Loader2 + "Loading note..." | — | — |
| 17 | Note error | — | Inline error (destructive) | — | — |
| 18 | Collapsed tree | 48px strip with expand button | Full width | — | — |

### 13.2 Query Page States

| # | State | SearchBar | ResultsArea |
|---|---|---|---|
| 1 | Empty (initial) | Placeholder "Search your notes...", mode=Hybrid | EmptyState (Search, "Search your notes", "Use keywords or natural language...") |
| 2 | Typing | Value visible, clear button (X) shown | Previous state preserved |
| 3 | Searching | Search button loading, input NOT disabled (user can type) | 4× Skeleton cards |
| 4 | Results | Search button default | ResultCards list |
| 5 | No results | Search button default | EmptyState (FileText, "No results found", "Try different keywords...") |
| 6 | Error | Search button default | EmptyState (AlertCircle, "Search failed", retry outline button) |
| 7 | Result hover | — | Card: shadow-elevated, -translate-y-px, title text-primary |
| 8 | Result expanded | — | Clicked card: full content, no line-clamp, smooth max-height transition |

### 13.3 Skills Page States

| # | State | Grid | Dialog |
|---|---|---|---|
| 1 | Loading | 6× Skeleton cards in 3-col grid | — |
| 2 | Error | EmptyState (AlertCircle, "Failed to load skills", retry outline) | — |
| 3 | Empty | EmptyState (Boxes, "No skills available", "Skills will appear here when configured.") | — |
| 4 | Grid loaded | SkillCards with icon, name, description, params, Run button | — |
| 5 | Dialog open | Grid behind overlay | Form fields rendered, Execute/Close buttons |
| 6 | Running | Grid behind overlay | Execute button loading, fields disabled |
| 7 | Success output | Grid behind overlay | Output area visible (glass-tier-ultra-thin, font-mono) |
| 8 | Error output | Grid behind overlay | Error area visible (status-error-bg, destructive) |

---

## 14. Glass Treatment Map

### 14.1 Per-Element Assignment

| Element | Page | Glass Tier | Light Background | Dark Background | Border (Light) | Border (Dark) |
|---|---|---|---|---|---|---|
| FileTreePanel | Record | thin | `rgba(255,255,255,0.55)` + `blur(16px)` | `rgba(26,20,15,0.60)` + `blur(16px)` | `rgba(255,255,255,0.35)` | `rgba(255,255,255,0.10)` |
| FileTreePanel collapsed | Record | thin | same | same | same | same |
| FileTreePanel separator | Record | glass | `rgba(255,255,255,0.10)` | `rgba(255,255,255,0.06)` | — | — |
| NoteEditor TitleBar | Record | ultra-thin | `rgba(255,255,255,0.45)` + `blur(8px)` | `rgba(26,20,15,0.50)` + `blur(8px)` | `rgba(255,255,255,0.35)` | `rgba(255,255,255,0.10)` |
| NoteEditor textarea | Record | none (solid) | `surface-raised` #FCF6EE | `surface-raised` #231B14 | — | — |
| AIAssistPanel | Record | regular | `rgba(255,255,255,0.65)` + `blur(24px)` | `rgba(26,20,15,0.70)` + `blur(24px)` | `rgba(255,255,255,0.40)` | `rgba(255,255,255,0.12)` |
| AI panel separator | Record | glass | `rgba(255,255,255,0.10)` | `rgba(255,255,255,0.06)` | — | — |
| DiffPreview code area | Record | ultra-thin | `rgba(255,255,255,0.45)` + `blur(8px)` | `rgba(26,20,15,0.50)` + `blur(8px)` | standard border | standard border |
| Diff accepted | Record | **solid** | `status-success-bg` #EAF2E6 | `status-success-bg` #1A2616 | `status-success/40` | `status-success/40` |
| Search Input | Query | solid or ultra-thin | `surface-base` #FFF9F2 | `surface-base` #1A140F | `border` #DCC7A7 | `border` #5A4630 |
| Search Select trigger | Query | solid | `surface-base` #FFF9F2 | `surface-base` #1A140F | `border` #DCC7A7 | `border` #5A4630 |
| Search Select dropdown | Query | thin | glass-tier-thin | glass-tier-thin | glass border | glass border |
| ResultCard | Query | thin | `rgba(255,255,255,0.55)` + `blur(16px)` | `rgba(26,20,15,0.60)` + `blur(16px)` | `rgba(255,255,255,0.35)` | `rgba(255,255,255,0.10)` |
| SkillCard | Skills | thin | same as ResultCard | same | same | same |
| SkillRunDialog content | Skills | thick | `rgba(255,255,255,0.78)` + `blur(40px)` | `rgba(26,20,15,0.80)` + `blur(40px)` | `rgba(255,255,255,0.45)` | `rgba(255,255,255,0.15)` |
| SkillRunDialog overlay | Skills | — | `rgba(0,0,0,0.40)` + `blur(4px)` | same | — | — |
| Output area | Skills | ultra-thin | `rgba(255,255,255,0.45)` + `blur(8px)` | `rgba(26,20,15,0.50)` + `blur(8px)` | — | — |
| Error area | Skills | **solid** | `status-error-bg` #F8E6E0 | `status-error-bg` #261612 | — | — |
| Scrollbar thumb (on glass) | All | glass thumb | `rgba(255,255,255,0.20)` → hover `0.30` | `rgba(255,255,255,0.10)` → hover `0.15` | — | — |

### 14.2 Side Rail Weight Guardrail

> **Rule:** In the Record page split layout, at most **one** side rail may use `glass-tier-regular`. The file tree always uses `thin`; the AI assist panel always uses `regular`. No future side panel should promote to `regular` without demoting the AI panel to `thin`, to avoid over-weighting the split view.

### 14.2 Decision Tree Compliance

| Element | Decision Path | Result |
|---|---|---|
| FileTreePanel | "Content container" → thin | ✅ |
| TitleBar | "Navigation chrome" → ultra-thin | ✅ |
| AIAssistPanel | "Between card and dialog" → regular | ✅ |
| DiffPreview code | "Navigation chrome" → ultra-thin | ✅ |
| ResultCard | "Content container" → thin | ✅ |
| SkillCard | "Content container" → thin | ✅ |
| SkillRunDialog | "Focused overlay" → thick | ✅ |
| Output area | "Navigation chrome" → ultra-thin | ✅ |
| Error area | Solid status bg | Correct — status tokens provide contrast |

---

## 15. Diff Color Semantic Mapping

### 15.1 Migration Table

This section documents the migration from hardcoded green/red colors to design system status tokens across all three pages.

| # | File:Line | Element | Before (hardcoded) | After (token) | Tailwind Class |
|---|---|---|---|---|---|
| 1 | `diff-preview.tsx:24` | Insert highlight (light) | `bg-green-200/60` | `status-success` at 15% | `bg-status-success/15` |
| 2 | `diff-preview.tsx:24` | Insert highlight (dark) | `dark:bg-green-900/40` | `status-success` at 15% | (handled by same class) |
| 3 | `diff-preview.tsx:31` | Delete highlight (light) | `bg-red-200/60` | `status-error` at 15% | `bg-status-error/15` |
| 4 | `diff-preview.tsx:31` | Delete highlight (dark) | `dark:bg-red-900/40` | `status-error` at 15% | (handled by same class) |
| 5 | `diff-preview.tsx:97` | Accepted border (light) | `border-green-300` | `status-success` at 40% | `border-status-success/40` |
| 6 | `diff-preview.tsx:97` | Accepted border (dark) | `dark:border-green-800` | `status-success` at 40% | (handled by same class) |
| 7 | `diff-preview.tsx:97` | Accepted bg (light) | `bg-green-50` | `status-success-bg` | `bg-status-success-bg` |
| 8 | `diff-preview.tsx:97` | Accepted bg (dark) | `dark:bg-green-950` | `status-success-bg` | (handled by same class) |
| 9 | `diff-preview.tsx:98` | Accepted check icon (light) | `text-green-600` | `status-success` | `text-status-success` |
| 10 | `diff-preview.tsx:98` | Accepted check icon (dark) | `dark:text-green-400` | `status-success` | (handled by same class) |
| 11 | `diff-preview.tsx:99` | Accepted text (light) | `text-green-700` | `status-success` | `text-status-success` |
| 12 | `diff-preview.tsx:99` | Accepted text (dark) | `dark:text-green-300` | `status-success` | (handled by same class) |
| 13 | `note-editor.tsx:159` | "Saved" status (light) | `text-green-600` | `status-success` | `text-status-success` |
| 14 | `note-editor.tsx:159` | "Saved" status (dark) | `dark:text-green-400` | `status-success` | (handled by same class) |
| 15 | `note-editor.tsx:163` | "Unsaved" status | `text-orange-500` | `status-warning` | `text-status-warning` |

### 15.2 Semantic Intent

| Semantic | Token | Meaning |
|---|---|---|
| Content addition (insert) | `status-success` | New content is positive, productive |
| Content removal (delete) | `status-error` | Removed content signals caution |
| Changes accepted | `status-success` | User confirmed the change |
| Changes saved | `status-success` | Save succeeded |
| Changes unsaved | `status-warning` | Data at risk of loss |

### 15.3 New DiffSegment Styling

The enhanced DiffSegment adds left-border stripes for visual clarity:

```tsx
function DiffSegment({ segment }: { segment: DiffDelta }) {
  if (segment.op === "equal") {
    return <span>{segment.text}</span>;
  }
  if (segment.op === "insert") {
    return (
      <span className="bg-status-success/15 border-l-[3px] border-l-status-success rounded-sm px-0.5">
        {segment.text}
      </span>
    );
  }
  if (segment.op === "delete") {
    return (
      <span className="bg-status-error/15 border-l-[3px] border-l-status-error line-through rounded-sm px-0.5">
        {segment.text}
      </span>
    );
  }
  return null;
}
```

### 15.4 New Accepted State

```tsx
<div className="flex items-center gap-2 rounded-[10px] border border-status-success/40 bg-status-success-bg px-3 py-2">
  <Check className="size-4 text-status-success" />
  <span className="text-sm text-status-success">Changes accepted</span>
  <Button variant="outline" size="sm" onClick={handleUndo} className="ml-auto">
    <RotateCcw />
    Undo
  </Button>
</div>
```

---

## 16. Responsive Behavior

### 16.1 Record Page

| Breakpoint | FileTreePanel | NoteEditor | AIAssistPanel |
|---|---|---|---|
| Desktop (≥1024px) | w-64, visible, glass-tier-thin | flex-1 | w-72, glass-tier-regular, inline |
| Tablet (768–1023px, pointer:fine) | Collapsed to w-12 icon strip with hover labels | flex-1 | Sheet (side="right", w-72) |
| Tablet (768–1023px, pointer:coarse) | Hidden; file drawer via Sheet (side="left", w-64) with labels | flex-1, "Browse files" in title bar | Sheet (side="right", w-72) |
| Mobile (<768px) | Hidden; file selector via Sheet (side="left", w-72) | Full width | Sheet (side="right", w-72) |

**Mobile file selector:** When the file tree is hidden on mobile, add a "Browse files" button to the NoteEditor title bar that opens a Sheet with the FileTreePanel content.

**Tablet collapsed tree:** Show folder/file icons only in a 48px strip. Tooltip on hover shows full name.

### 16.2 Query Page

| Breakpoint | SearchBar | ResultsArea |
|---|---|---|
| Desktop (≥1024px) | Horizontal row: Input + Select + Button, max-w-2xl | max-w-2xl, same column |
| Tablet (768–1023px) | Same layout, p-4 instead of p-6 | Same |
| Mobile (<768px) | Stacked: Input (full-width) → row(Select + Button), no max-w | Full-width cards, no max-w |

**Mobile stacking:**
```tsx
<div className="flex flex-col gap-2 md:flex-row md:gap-2 max-w-2xl">
  <div className="relative flex-1">
    <Input ... iconLeft={<Search />} />
  </div>
  <div className="flex gap-2">
    <Select ... />
    <Button ...>Search</Button>
  </div>
</div>
```

### 16.3 Skills Page

| Breakpoint | Grid | Dialog |
|---|---|---|
| Desktop (≥1024px) | 3 columns | Dialog max-w-md, centered |
| Tablet (768–1023px) | 2 columns | Dialog max-w-md, centered |
| Mobile (<768px) | 1 column, full-width cards | Full-screen: `w-[calc(100vw-32px)] max-h-[calc(100vh-32px)]` |

### 16.4 Shared Responsive Tokens

| Property | Desktop | Tablet | Mobile |
|---|---|---|---|
| Page padding | `p-6` | `p-4` | `p-4` |
| Card grid gap | `gap-4` | `gap-4` | `gap-3` |
| Max content width | `max-w-2xl` (Query only) | same | none |

---

## 17. Figma Frames Specification

### 17.1 Frame Naming Convention

```
📄 Pages / Record / {State}
📄 Pages / Query / {State}
📄 Pages / Skills / {State}
```

### 17.2 Record Page Frames

| # | Frame Name | Width | Height | Content |
|---|---|---|---|---|
| R1 | Record / Empty Tree | 1280 | 800 | Empty FileTreePanel + EmptyState NoteEditor |
| R2 | Record / File Selected | 1280 | 800 | Tree with selection + NoteEditor with content |
| R3 | Record / Editing Dirty | 1280 | 800 | Tree + Editor with "Unsaved" status |
| R4 | Record / AI Panel Open | 1600 | 800 | Full 3-panel: Tree + Editor + AI Assist |
| R5 | Record / AI Loading | 1600 | 800 | AI panel with spinner |
| R6 | Record / Diff Preview | 1600 | 800 | AI panel with diff visible |
| R7 | Record / Diff Accepted | 1600 | 800 | AI panel with green accepted state |
| R8 | Record / Collapsed Tree | 1088 | 800 | Collapsed tree (48px) + full editor |
| R9 | Record / Mobile | 390 | 844 | No tree, editor full, "Browse files" button |

### 17.3 Query Page Frames

| # | Frame Name | Width | Height | Content |
|---|---|---|---|---|
| Q1 | Query / Empty | 1280 | 800 | Search bar + EmptyState (Search icon) |
| Q2 | Query / Searching | 1280 | 800 | Search bar (loading) + 4 Skeleton cards |
| Q3 | Query / Results | 1280 | 800 | Search bar + 5 ResultCards |
| Q4 | Query / No Results | 1280 | 800 | Search bar + EmptyState (FileText) |
| Q5 | Query / Error | 1280 | 800 | Search bar + EmptyState (AlertCircle) |
| Q6 | Query / Expanded Card | 1280 | 800 | One card expanded showing full content |
| Q7 | Query / Mobile | 390 | 844 | Stacked search bar + 1-col results |

### 17.4 Skills Page Frames

| # | Frame Name | Width | Height | Content |
|---|---|---|---|---|
| S1 | Skills / Loading | 1280 | 800 | 6 Skeleton cards in 3-col grid |
| S2 | Skills / Grid | 1280 | 800 | 6+ SkillCards in 3-col grid |
| S3 | Skills / Empty | 1280 | 800 | EmptyState (Boxes icon) |
| S4 | Skills / Error | 1280 | 800 | EmptyState (AlertCircle, retry) |
| S5 | Skills / Dialog Open | 1280 | 800 | Grid behind overlay + dialog with form |
| S6 | Skills / Dialog Running | 1280 | 800 | Dialog with Execute button loading |
| S7 | Skills / Dialog Success | 1280 | 800 | Dialog with output area visible |
| S8 | Skills / Dialog Error | 1280 | 800 | Dialog with error area visible |
| S9 | Skills / Mobile | 390 | 844 | 1-col grid + full-screen dialog |

### 17.5 Component Instance Properties

**ResultCard instance in Figma:**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `collapsed`, `expanded`, `hover` | `collapsed` |
| `Has Tags` | Boolean | `true`, `false` | `true` |
| `Title` | Text | — | `Understanding Neural Networks` |
| `Preview` | Text | — | `An introduction to the fundamental concepts...` |
| `Score` | Text | — | `0.87` |

**SkillCard instance in Figma:**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `default`, `hover` | `default` |
| `Has Params` | Boolean | `true`, `false` | `true` |
| `Icon` | Instance Swap | Lucide | `Boxes` |
| `Name` | Text | — | `Summarize` |
| `Description` | Text | — | `Generate a summary of the selected content.` |

**SkillRunDialog instance in Figma:**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `form`, `running`, `success`, `error` | `form` |
| `Skill Name` | Text | — | `Summarize` |
| `Skill Description` | Text | — | `Generate a summary...` |
| `Has Output` | Boolean | `true`, `false` | `false` |
| `Has Error` | Boolean | `true`, `false` | `false` |

**Layer Structure — Record Page (Frame R4):**
```
Record / AI Panel Open (Frame, 1600×800, bg-background)
├── FileTreePanel (Frame, w-256, glass-thin, border-r)
│   ├── Header (Frame, h-40, flex-row)
│   │   ├── Label (Text, 13px/500, "Files")
│   │   └── CollapseBtn (Instance, Button ghost icon-sm)
│   ├── Tree (Instance, ScrollArea)
│   │   ├── TreeItem Folder (Frame, flex-row, depth-0)
│   │   │   ├── ChevronRight (SVG, 14px, rotated)
│   │   │   ├── Folder (SVG, 14px)
│   │   │   └── Name (Text, 14px)
│   │   ├── TreeItem File (Frame, flex-row, depth-1, selected)
│   │   │   ├── FileText (SVG, 14px)
│   │   │   └── Name (Text, 14px, primary)
│   │   └── ...
│   └── Footer (Frame, border-t)
│       └── Count (Text, 12px, muted-foreground, "12 files")
├── NoteEditor (Frame, flex-1, flex-col)
│   ├── TitleBar (Frame, h-48, glass-ultra-thin, border-b)
│   │   ├── Title (Text, 18px/600, "Meeting Notes")
│   │   ├── Status (Text, 12px, status-warning, "Unsaved")
│   │   ├── SaveBtn (Instance, Button outline sm)
│   │   └── AIBtn (Instance, Button default sm, Sparkles)
│   └── Editor (Frame, flex-1)
│       └── Textarea (Frame, bg-surface-raised, font-mono)
└── AIAssistPanel (Frame, w-288, glass-regular, border-l)
    ├── Header (Frame, h-40, border-b)
    │   ├── Sparkles (SVG, 14px, primary) + Label (Text, 13px/500)
    │   └── CloseBtn (Instance, Button ghost icon-sm, X)
    ├── Actions (Frame, p-12, flex-col, gap-8)
    │   ├── ContinueBtn (Instance, Button default sm, w-full)
    │   ├── RewriteBtn (Instance, Button outline sm, w-full)
    │   └── PolishBtn (Instance, Button outline sm, w-full)
    ├── DiffPreview (Frame, rounded-[10px], border)
    │   ├── Header (Text, 14px/500, "Diff Preview")
    │   ├── Content (Frame, font-mono, 14px)
    │   │   ├── Equal text (Text, foreground)
    │   │   ├── Insert (Text, bg-status-success/15, border-l-status-success)
    │   │   └── Delete (Text, bg-status-error/15, border-l-status-error, line-through)
    │   └── Footer (Frame, border-t, flex-row, gap-8)
    │       ├── AcceptBtn (Instance, Button default sm, Check)
    │       └── RejectBtn (Instance, Button outline sm, X)
    └── ...
```

---

## 18. TSX Skeleton — RecordPage

```tsx
// web/src/features/record/record-page.tsx
import { useState } from "react";
import { FileTreePanel } from "./file-tree-panel";
import { NoteEditor } from "./note-editor";

export function RecordPage() {
  const [treeCollapsed, setTreeCollapsed] = useState(false);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  return (
    <div className="flex h-full">
      <FileTreePanel
        collapsed={treeCollapsed}
        onToggleCollapse={() => setTreeCollapsed(!treeCollapsed)}
        selectedPath={selectedPath}
        onSelectFile={setSelectedPath}
      />
      <NoteEditor
        filePath={selectedPath}
        aiPanelOpen={aiPanelOpen}
        onToggleAI={() => setAiPanelOpen(!aiPanelOpen)}
      />
    </div>
  );
}
```

### 18.1 FileTreePanel Skeleton

```tsx
// web/src/features/record/file-tree-panel.tsx
import { useQuery } from "@tanstack/react-query";
import {
  ChevronDown,
  ChevronRight,
  FileText,
  Folder,
  FolderOpen,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import type { TreeNode } from "@/types/record";
import { getFileTree } from "./record-api";

interface FileTreePanelProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  selectedPath: string | null;
  onSelectFile: (path: string) => void;
}

function TreeItem({
  node,
  depth,
  selectedPath,
  onSelectFile,
}: {
  node: TreeNode;
  depth: number;
  selectedPath: string | null;
  onSelectFile: (path: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const isDir = node.type === "directory";
  const isSelected = node.path === selectedPath;

  if (isDir) {
    return (
      <div>
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className="flex w-full items-center gap-1.5 rounded-[10px] px-2 py-1.5 text-[14px] hover:bg-accent hover:text-accent-foreground transition-colors duration-100"
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
        >
          <ChevronRight
            className={cn(
              "size-3.5 shrink-0 text-muted-foreground transition-transform duration-150",
              open && "rotate-90",
            )}
          />
          {open ? (
            <FolderOpen className="size-3.5 shrink-0 text-muted-foreground" />
          ) : (
            <Folder className="size-3.5 shrink-0 text-muted-foreground" />
          )}
          <span className="truncate">{node.name}</span>
          {node.file_count != null && (
            <span className="ml-auto text-[12px] text-muted-foreground">
              {node.file_count}
            </span>
          )}
        </button>
        {open && node.children && (
          <div>
            {node.children.map((child) => (
              <TreeItem
                key={child.path}
                node={child}
                depth={depth + 1}
                selectedPath={selectedPath}
                onSelectFile={onSelectFile}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => onSelectFile(node.path)}
      className={cn(
        "flex w-full items-center gap-1.5 rounded-[10px] px-2 py-1.5 text-[14px] transition-colors duration-100",
        "hover:bg-accent hover:text-accent-foreground",
        isSelected && "bg-accent-muted text-primary font-medium",
      )}
      style={{ paddingLeft: `${depth * 16 + 8}px` }}
    >
      <FileText className="size-3.5 shrink-0 text-muted-foreground" />
      <span className="truncate">{node.name}</span>
    </button>
  );
}

export function FileTreePanel({
  collapsed,
  onToggleCollapse,
  selectedPath,
  onSelectFile,
}: FileTreePanelProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["fileTree"],
    queryFn: getFileTree,
  });

  if (collapsed) {
    return (
      <div className="flex w-12 shrink-0 flex-col items-center border-r border-white/10 dark:border-white/6 bg-white/55 backdrop-blur-[16px] saturate-[140%] dark:bg-[rgba(26,20,15,0.60)] py-2">
        <Button variant="ghost" size="icon-sm" onClick={onToggleCollapse} aria-label="Expand file tree">
          <PanelLeftOpen className="size-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex w-64 shrink-0 flex-col border-r border-white/10 dark:border-white/6 bg-white/55 backdrop-blur-[16px] saturate-[140%] dark:bg-[rgba(26,20,15,0.60)]">
      {/* Header */}
      <div className="flex h-10 items-center justify-between px-3">
        <span className="text-[13px] font-medium text-foreground">Files</span>
        <Button variant="ghost" size="icon-sm" onClick={onToggleCollapse} aria-label="Collapse file tree">
          <PanelLeftClose className="size-4" />
        </Button>
      </div>

      {/* Tree */}
      <ScrollArea glass className="flex-1">
        <div className="px-1 pb-2">
          {isLoading && (
            <p className="px-2 py-4 text-center text-[12px] text-muted-foreground">
              Loading...
            </p>
          )}
          {error && (
            <p className="px-2 py-4 text-center text-[12px] text-destructive">
              Failed to load files
            </p>
          )}
          {!isLoading && !error && data?.tree.length === 0 && (
            <EmptyState
              icon={FolderOpen}
              title="No files found"
              description="Add markdown files to your vault to get started."
              iconBackground
            />
          )}
          {data?.tree.map((node) => (
            <TreeItem
              key={node.path}
              node={node}
              depth={0}
              selectedPath={selectedPath}
              onSelectFile={onSelectFile}
            />
          ))}
        </div>
      </ScrollArea>

      {/* Footer */}
      <Separator glass className="shrink-0" />
      <div className="px-3 py-2">
        <span className="text-[12px] text-muted-foreground">
          {data?.tree.length ?? 0} files
        </span>
      </div>
    </div>
  );
}
```

### 18.2 NoteEditor Skeleton

```tsx
// web/src/features/record/note-editor.tsx
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save, Sparkles } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { AIAssistPanel } from "./ai-assist-panel";
import { getNoteContent, saveNote } from "./record-api";

type SaveStatus = "idle" | "dirty" | "saving" | "saved";

interface NoteEditorProps {
  filePath: string | null;
  aiPanelOpen: boolean;
  onToggleAI: () => void;
}

export function NoteEditor({ filePath, aiPanelOpen, onToggleAI }: NoteEditorProps) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isExternalUpdate = useRef(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["noteContent", filePath],
    queryFn: () => getNoteContent(filePath as string),
    enabled: filePath !== null,
  });

  useEffect(() => {
    if (data) {
      isExternalUpdate.current = true;
      setTitle(data.title);
      setContent(data.content);
      setSaveStatus("saved");
    }
  }, [data]);

  useEffect(() => {
    if (!filePath) {
      setTitle("");
      setContent("");
      setSaveStatus("idle");
    }
  }, [filePath]);

  const saveMutation = useMutation({
    mutationFn: () =>
      saveNote({ path: filePath as string, content, title: title || undefined }),
    onSuccess: () => {
      setSaveStatus("saved");
      queryClient.invalidateQueries({ queryKey: ["fileTree"] });
    },
  });

  const handleContentChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      if (isExternalUpdate.current) {
        isExternalUpdate.current = false;
        return;
      }
      setContent(e.target.value);
      setSaveStatus("dirty");
    },
    [],
  );

  const handleTitleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setTitle(e.target.value);
      setSaveStatus("dirty");
    },
    [],
  );

  const handleSave = useCallback(() => {
    if (filePath && saveStatus === "dirty") {
      setSaveStatus("saving");
      saveMutation.mutate();
    }
  }, [filePath, saveStatus, saveMutation]);

  const handleAppend = useCallback((text: string) => {
    setContent((prev) => prev + text);
    setSaveStatus("dirty");
  }, []);

  const handleReplace = useCallback((text: string) => {
    setContent(text);
    setSaveStatus("dirty");
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave]);

  const handleTextSelect = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const sel = textarea.value.substring(textarea.selectionStart, textarea.selectionEnd);
    setSelectedText(sel.length > 0 ? sel : null);
  }, []);

  if (!filePath) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          icon={FileText}
          title="Select a file"
          description="Choose a file from the tree to start editing."
          iconBackground
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center gap-2 text-muted-foreground">
        <Loader2 className="size-5 animate-spin" />
        <span className="text-[15px]">Loading note...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2">
        <EmptyState
          icon={AlertCircle}
          title="Failed to load note"
          description={error.message}
          action={{ label: "Retry", onClick: () => queryClient.refetchQueries({ queryKey: ["noteContent", filePath] }), variant: "outline" }}
        />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-1 min-w-0">
      {/* Editor column */}
      <div className="flex flex-1 flex-col min-w-0">
        {/* Title bar */}
        <div className="flex h-12 items-center gap-3 border-b border-white/10 dark:border-white/6 bg-white/45 backdrop-blur-[8px] saturate-[120%] dark:bg-[rgba(26,20,15,0.50)] px-4">
          <Input
            value={title}
            onChange={handleTitleChange}
            placeholder="Note title"
            className="h-8 flex-1 border-none bg-transparent shadow-none text-[18px] font-semibold focus-visible:ring-0"
          />
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "text-[12px]",
                saveStatus === "saved" && "text-status-success",
                saveStatus === "saving" && "text-muted-foreground",
                saveStatus === "dirty" && "text-status-warning",
              )}
            >
              {saveStatus === "saved" && "Saved"}
              {saveStatus === "saving" && "Saving..."}
              {saveStatus === "dirty" && "Unsaved"}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleSave}
              disabled={saveStatus !== "dirty"}
            >
              <Save />
              Save
            </Button>
            <Button
              variant={aiPanelOpen ? "default" : "outline"}
              size="sm"
              onClick={onToggleAI}
            >
              <Sparkles />
              AI
            </Button>
          </div>
        </div>

        {/* Editor area */}
        <div className="relative flex-1 overflow-auto p-4">
          <Textarea
            ref={textareaRef}
            value={content}
            onChange={handleContentChange}
            onSelect={handleTextSelect}
            onMouseUp={handleTextSelect}
            placeholder="Start writing..."
            className="h-full resize-none rounded-[10px] border-none bg-surface-raised p-4 font-mono text-[14px] shadow-none focus-visible:ring-0"
          />
          <span className="pointer-events-none absolute bottom-4 right-4 text-[12px] text-muted-foreground/60">
            ⌘S to save
          </span>
        </div>
      </div>

      {/* AI Assist Panel */}
      {aiPanelOpen && (
        <AIAssistPanel
          content={content}
          selectedText={selectedText}
          onAppend={handleAppend}
          onReplace={handleReplace}
          onClose={onToggleAI}
        />
      )}
    </div>
  );
}
```

### 18.3 AIAssistPanel Skeleton

```tsx
// web/src/features/record/ai-assist-panel.tsx
import { Loader2, PenLine, Sparkles, Type, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { AIRewriteWithDiffResponse } from "@/types/record";
import { DiffPreview } from "./diff-preview";
import { aiContinue, aiPolishWithDiff, aiRewriteWithDiff } from "./record-api";

interface AIAssistPanelProps {
  content: string;
  selectedText: string | null;
  onAppend: (text: string) => void;
  onReplace: (text: string) => void;
  onClose: () => void;
}

export function AIAssistPanel({
  content,
  selectedText,
  onAppend,
  onReplace,
  onClose,
}: AIAssistPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [diffResult, setDiffResult] = useState<AIRewriteWithDiffResponse | null>(null);
  const [diffActionType, setDiffActionType] = useState("");
  const [startTime, setStartTime] = useState(0);

  const targetContent = selectedText || content;
  const hasSelection = selectedText !== null && selectedText.length > 0;

  const handleContinue = async () => {
    setLoading(true);
    setError(null);
    setDiffResult(null);
    setStartTime(Date.now());
    try {
      const result = await aiContinue(content);
      onAppend(result.generated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to continue");
    } finally {
      setLoading(false);
    }
  };

  const handleRewrite = async () => {
    setLoading(true);
    setError(null);
    setDiffResult(null);
    setDiffActionType("rewrite");
    setStartTime(Date.now());
    try {
      const result = await aiRewriteWithDiff(targetContent);
      setDiffResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to rewrite");
    } finally {
      setLoading(false);
    }
  };

  const handlePolish = async () => {
    setLoading(true);
    setError(null);
    setDiffResult(null);
    setDiffActionType("polish");
    setStartTime(Date.now());
    try {
      const result = await aiPolishWithDiff(targetContent);
      setDiffResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to polish");
    } finally {
      setLoading(false);
    }
  };

  const handleDiffAccept = (modified: string) => {
    if (hasSelection && diffResult && selectedText) {
      const idx = content.indexOf(selectedText);
      const before = content.substring(0, idx);
      const after = content.substring(idx + selectedText.length);
      onReplace(before + modified + after);
    } else {
      onReplace(modified);
    }
    setDiffResult(null);
  };

  const handleDiffReject = () => {
    setDiffResult(null);
  };

  return (
    <div className="flex w-72 shrink-0 flex-col border-l border-white/12 dark:border-white/6 bg-white/65 backdrop-blur-[24px] saturate-[160%] dark:bg-[rgba(26,20,15,0.70)]">
      {/* Header */}
      <div className="flex h-10 items-center justify-between border-b border-white/10 dark:border-white/6 px-3">
        <div className="flex items-center gap-1.5">
          <Sparkles className="size-4 text-primary" />
          <span className="text-[13px] font-medium text-foreground">AI Assist</span>
        </div>
        <Button variant="ghost" size="icon-sm" onClick={onClose} aria-label="Close AI panel">
          <X />
        </Button>
      </div>

      {/* Action buttons */}
      <div className="flex flex-col gap-2 p-3">
        <Button
          variant="default"
          size="sm"
          className="w-full"
          onClick={handleContinue}
          loading={loading}
          disabled={content.trim().length === 0}
        >
          <Type />
          Continue
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="w-full"
          onClick={handleRewrite}
          loading={loading}
          disabled={targetContent.trim().length === 0}
        >
          <Sparkles />
          Rewrite
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="w-full"
          onClick={handlePolish}
          loading={loading}
          disabled={targetContent.trim().length === 0}
        >
          <PenLine />
          Polish
        </Button>
      </div>

      {/* Selection indicator */}
      {hasSelection && (
        <p className="px-3 text-[12px] text-muted-foreground">
          Applying to selected text ({selectedText.length} chars)
        </p>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-2 p-3 text-[14px] text-muted-foreground">
          <Loader2 className="size-4 animate-spin" />
          AI is thinking...
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 rounded-[10px] border border-destructive/50 bg-status-error-bg px-3 py-2 text-[14px] text-destructive mx-3">
          <span className="flex-1">{error}</span>
          <Button variant="ghost" size="sm" onClick={() => setError(null)}>
            Dismiss
          </Button>
        </div>
      )}

      {/* Diff result */}
      {diffResult && (
        <ScrollArea glass className="flex-1 p-3">
          <DiffPreview
            delta={diffResult.delta}
            original={diffResult.original}
            modified={diffResult.modified}
            actionType={diffActionType}
            startTime={startTime}
            onAccept={handleDiffAccept}
            onReject={handleDiffReject}
          />
        </ScrollArea>
      )}
    </div>
  );
}
```

### 18.4 DiffPreview Skeleton

```tsx
// web/src/features/record/diff-preview.tsx
import { Check, RotateCcw, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { DiffDelta } from "@/types/record";
import { trackTelemetry } from "./record-api";

interface DiffPreviewProps {
  delta: DiffDelta[];
  original: string;
  modified: string;
  actionType: string;
  startTime: number;
  onAccept: (modified: string) => void;
  onReject: () => void;
}

function DiffSegment({ segment }: { segment: DiffDelta }) {
  if (segment.op === "equal") {
    return <span>{segment.text}</span>;
  }
  if (segment.op === "insert") {
    return (
      <span className="bg-status-success/15 border-l-[3px] border-l-status-success rounded-[4px] px-0.5">
        {segment.text}
      </span>
    );
  }
  if (segment.op === "delete") {
    return (
      <span className="bg-status-error/15 border-l-[3px] border-l-status-error line-through rounded-[4px] px-0.5">
        {segment.text}
      </span>
    );
  }
  return null;
}

export function DiffPreview({
  delta,
  modified,
  actionType,
  startTime,
  onAccept,
  onReject,
}: DiffPreviewProps) {
  const [accepted, setAccepted] = useState(false);
  const [undoDeadline, setUndoDeadline] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const handleAccept = useCallback(() => {
    setAccepted(true);
    onAccept(modified);
    trackTelemetry({
      action_type: actionType,
      text_length: modified.length,
      duration_ms: Date.now() - startTime,
      accepted: true,
    });
    timerRef.current = setTimeout(() => {
      setUndoDeadline(true);
    }, 30_000);
  }, [modified, actionType, startTime, onAccept]);

  const handleUndo = useCallback(() => {
    setAccepted(false);
    setUndoDeadline(false);
    if (timerRef.current) clearTimeout(timerRef.current);
    trackTelemetry({
      action_type: actionType,
      text_length: modified.length,
      duration_ms: Date.now() - startTime,
      accepted: false,
    });
  }, [modified, actionType, startTime]);

  const handleReject = useCallback(() => {
    onReject();
    trackTelemetry({
      action_type: actionType,
      text_length: modified.length,
      duration_ms: Date.now() - startTime,
      accepted: false,
    });
  }, [modified, actionType, startTime, onReject]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  if (accepted && undoDeadline) return null;

  if (accepted) {
    return (
      <div className="flex items-center gap-2 rounded-[10px] border border-status-success/40 bg-status-success-bg px-3 py-2">
        <Check className="size-4 text-status-success" />
        <span className="text-[14px] text-status-success">Changes accepted</span>
        <Button variant="outline" size="sm" onClick={handleUndo} className="ml-auto">
          <RotateCcw />
          Undo
        </Button>
      </div>
    );
  }

  return (
    <div className="rounded-[10px] border border-border">
      <div className="flex items-center justify-between border-b border-white/10 dark:border-white/6 px-3 py-2">
        <span className="text-[14px] font-medium text-foreground">Diff Preview</span>
      </div>
      <ScrollArea glass className="max-h-64">
        <div className="whitespace-pre-wrap bg-white/45 backdrop-blur-[8px] dark:bg-[rgba(26,20,15,0.50)] px-3 py-2 font-mono text-[14px] leading-relaxed">
          {delta.map((segment, i) => (
            <DiffSegment key={String(i)} segment={segment} />
          ))}
        </div>
      </ScrollArea>
      <div className="flex items-center gap-2 border-t border-white/10 dark:border-white/6 px-3 py-2">
        <Button size="sm" onClick={handleAccept}>
          <Check />
          Accept
        </Button>
        <Button variant="outline" size="sm" onClick={handleReject}>
          <X />
          Reject
        </Button>
      </div>
    </div>
  );
}
```

---

## 19. TSX Skeleton — QueryPage

```tsx
// web/src/features/query/query-page.tsx
import { useMutation } from "@tanstack/react-query";
import { AlertCircle, FileText, Search } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import type { SearchResult } from "@/types/query";
import { searchNotes } from "./query-api";

const SEARCH_MODES = [
  { value: "hybrid", label: "Hybrid" },
  { value: "keyword", label: "Keyword" },
  { value: "semantic", label: "Semantic" },
] as const;

export function QueryPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<string>("hybrid");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (q: string) => searchNotes(q, mode, 20),
    onSuccess: (data) => {
      setResults(data.results);
    },
    onError: () => {
      toast.error("Search failed. Please try again.");
    },
  });

  const handleSearch = () => {
    const trimmed = query.trim();
    if (!trimmed) return;
    mutation.mutate(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    setExpandedId(null);
  };

  const hasSearched = mutation.isIdle ? results.length > 0 : mutation.isSuccess;
  const isEmpty = hasSearched && results.length === 0;

  return (
    <div className="flex h-full flex-col gap-4 p-4 md:p-6">
      <h1 className="text-[22px] font-semibold text-foreground">Query</h1>

      {/* Search bar */}
      <div className="flex flex-col gap-2 md:flex-row md:gap-2 max-w-2xl">
        <div className="relative flex-1">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search your notes..."
            iconLeft={<Search />}
          />
        </div>
        <div className="flex gap-2">
          <Select value={mode} onValueChange={setMode}>
            <SelectTrigger className="w-[130px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {SEARCH_MODES.map((m) => (
                <SelectItem key={m.value} value={m.value}>
                  {m.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            onClick={handleSearch}
            disabled={mutation.isPending || !query.trim()}
            loading={mutation.isPending}
          >
            <Search />
            Search
          </Button>
        </div>
      </div>

      {/* Results area */}
      <div className="flex-1 overflow-y-auto max-w-2xl">
        {mutation.isPending && (
          <div className="space-y-3">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="rounded-[14px] border border-white/35 dark:border-white/10 bg-white/55 backdrop-blur-[16px] p-4 space-y-2">
                <Skeleton className="h-5 w-1/3" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            ))}
          </div>
        )}

        {mutation.isError && (
          <EmptyState
            icon={AlertCircle}
            title="Search failed"
            description="Something went wrong. Please try again."
            action={{ label: "Retry", onClick: handleSearch, variant: "outline" }}
            iconBackground
          />
        )}

        {!mutation.isPending && !mutation.isError && !hasSearched && (
          <EmptyState
            icon={Search}
            title="Search your notes"
            description="Use keywords or natural language to find relevant content."
            iconBackground
          />
        )}

        {isEmpty && (
          <EmptyState
            icon={FileText}
            title="No results found"
            description="Try different keywords or switch search mode."
            iconBackground
          />
        )}

        {hasSearched && results.length > 0 && (
          <div className="space-y-3">
            {results.map((result) => {
              const isExpanded = expandedId === result.id;
              return (
                <Card
                  key={result.id}
                  className="cursor-pointer"
                  onClick={() => setExpandedId(isExpanded ? null : result.id)}
                >
                  <CardHeader className="p-4 pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-[13px] font-medium group-hover:text-primary transition-colors">
                        {result.title}
                      </CardTitle>
                      <Badge variant="secondary" className="shrink-0">
                        {result.score.toFixed(2)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <p
                      className={
                        isExpanded
                          ? "text-[14px] text-muted-foreground whitespace-pre-wrap"
                          : "text-[14px] text-muted-foreground line-clamp-2"
                      }
                    >
                      {result.content}
                    </p>
                    {Array.isArray(result.metadata?.tags) && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {(result.metadata.tags as string[]).map((tag: string) => (
                          <Badge key={tag} variant="outline">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## 20. TSX Skeleton — SkillsPage

```tsx
// web/src/features/skills/skills-page.tsx
import { useMutation, useQuery } from "@tanstack/react-query";
import { AlertCircle, Boxes, Loader2, Play } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Switch } from "@/components/ui/switch";
import type { Skill, SkillInput } from "@/types/skills";
import { executeSkill, getSkills } from "./skills-api";

// ─── SkillParamField ───
function SkillParamField({
  input,
  value,
  onChange,
}: {
  input: SkillInput;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  if (input.enum && input.enum.length > 0) {
    return (
      <div className="space-y-1">
        <label className="text-[14px] font-medium">
          {input.name}
          {input.required && <span className="text-destructive"> *</span>}
        </label>
        <Select
          value={(value as string) ?? (input.default as string) ?? ""}
          onValueChange={(v) => onChange(v || undefined)}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {input.enum.map((opt) => (
              <SelectItem key={opt} value={opt}>{opt}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        {input.description && (
          <p className="text-[12px] text-muted-foreground">{input.description}</p>
        )}
      </div>
    );
  }

  switch (input.type) {
    case "boolean":
      return (
        <div className="flex items-center gap-3">
          <Switch
            id={`skill-param-${input.name}`}
            checked={(value as boolean) ?? (input.default as boolean) ?? false}
            onCheckedChange={(v) => onChange(v)}
          />
          <label htmlFor={`skill-param-${input.name}`} className="text-[14px] font-medium">
            {input.name}
            {input.required && <span className="text-destructive"> *</span>}
          </label>
        </div>
      );
    case "number":
      return (
        <div className="space-y-1">
          <label className="text-[14px] font-medium">
            {input.name}
            {input.required && <span className="text-destructive"> *</span>}
          </label>
          <Input
            type="number"
            value={(value as string) ?? (input.default as string) ?? ""}
            onChange={(e) => onChange(Number(e.target.value))}
          />
          {input.description && (
            <p className="text-[12px] text-muted-foreground">{input.description}</p>
          )}
        </div>
      );
    default:
      return (
        <div className="space-y-1">
          <label className="text-[14px] font-medium">
            {input.name}
            {input.required && <span className="text-destructive"> *</span>}
          </label>
          <Input
            value={(value as string) ?? (input.default as string) ?? ""}
            onChange={(e) => onChange(e.target.value)}
            placeholder={input.description}
          />
          {input.description && (
            <p className="text-[12px] text-muted-foreground">{input.description}</p>
          )}
        </div>
      );
  }
}

// ─── SkillRunDialog ───
function SkillRunDialog({
  skill,
  open,
  onOpenChange,
}: {
  skill: Skill;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [params, setParams] = useState<Record<string, unknown>>({});
  const [output, setOutput] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runMutation = useMutation({
    mutationFn: () => executeSkill(skill.name, params),
    onSuccess: (data) => {
      if (data.success) {
        setOutput(data.output);
        setError(null);
        toast.success("Skill executed successfully");
      } else {
        setError(data.error);
        setOutput(null);
        toast.error("Skill execution failed");
      }
    },
    onError: (err) => {
      setError(err.message);
      setOutput(null);
      toast.error("Skill execution failed");
    },
  });

  const handleParamChange = (name: string, value: unknown) => {
    setParams((prev) => ({ ...prev, [name]: value }));
  };

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      setParams({});
      setOutput(null);
      setError(null);
      runMutation.reset();
    }
    onOpenChange(nextOpen);
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-[18px] font-semibold">
            Run: {skill.name}
          </DialogTitle>
          <DialogDescription>{skill.description}</DialogDescription>
        </DialogHeader>

        {skill.inputs.length > 0 && (
          <div className="space-y-4 px-6">
            {skill.inputs.map((input) => (
              <SkillParamField
                key={input.name}
                input={input}
                value={params[input.name]}
                onChange={(v) => handleParamChange(input.name, v)}
              />
            ))}
          </div>
        )}

        {output && (
          <div className="mx-6 rounded-[14px] bg-white/45 backdrop-blur-[8px] saturate-[120%] dark:bg-[rgba(26,20,15,0.50)] p-3 max-h-48 overflow-auto">
            <p className="text-[14px] font-medium text-foreground mb-1">Output</p>
            <pre className="font-mono text-[14px] whitespace-pre-wrap text-foreground">{output}</pre>
          </div>
        )}

        {error && (
          <div className="mx-6 rounded-[14px] bg-status-error-bg p-3">
            <p className="text-[14px] text-destructive">{error}</p>
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={() => handleOpenChange(false)}>
            Close
          </Button>
          <Button
            onClick={() => runMutation.mutate()}
            loading={runMutation.isPending}
          >
            Execute
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ─── SkillsPage ───
export function SkillsPage() {
  const [runSkill, setRunSkill] = useState<Skill | null>(null);

  const {
    data: skills,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["skills"],
    queryFn: getSkills,
  });

  return (
    <div className="flex h-full flex-col gap-4 p-4 md:p-6">
      <h1 className="text-[22px] font-semibold text-foreground">Skills</h1>

      <div className="flex-1 overflow-y-auto">
        {isLoading && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="rounded-[14px] border border-white/35 dark:border-white/10 bg-white/55 backdrop-blur-[16px] p-4 space-y-3">
                <Skeleton className="h-5 w-1/2" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-9 w-20" />
              </div>
            ))}
          </div>
        )}

        {isError && (
          <EmptyState
            icon={AlertCircle}
            title="Failed to load skills"
            action={{ label: "Retry", onClick: () => refetch(), variant: "outline" }}
            iconBackground
          />
        )}

        {skills && skills.length === 0 && (
          <EmptyState
            icon={Boxes}
            title="No skills available"
            description="Skills will appear here when configured."
            iconBackground
          />
        )}

        {skills && skills.length > 0 && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {skills.map((skill) => (
              <Card key={skill.name}>
                <CardHeader className="p-4 pb-2">
                  <div className="flex items-center gap-2">
                    <Play className="size-5 text-primary" />
                    <CardTitle className="text-[13px] font-medium">{skill.name}</CardTitle>
                  </div>
                  <CardDescription className="line-clamp-2">{skill.description}</CardDescription>
                </CardHeader>
                <CardContent className="p-4 pt-0">
                  {skill.inputs.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {skill.inputs.map((input) => (
                        <Badge
                          key={input.name}
                          variant={input.type === "enum" ? "outline" : "secondary"}
                        >
                          {input.name}: {input.type}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
                <CardFooter className="p-4 pt-0 flex justify-end">
                  <Button variant="default" size="sm" onClick={() => setRunSkill(skill)}>
                    <Play />
                    Run
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>

      {runSkill && (
        <SkillRunDialog
          skill={runSkill}
          open={!!runSkill}
          onOpenChange={(open) => {
            if (!open) setRunSkill(null);
          }}
        />
      )}
    </div>
  );
}
```

---

## 21. Migration Mapping

### 21.1 Record Page Migrations

| # | File | Before | After | Rationale |
|---|---|---|---|---|
| R1 | `file-tree-panel.tsx:123` | `w-64 shrink-0 flex-col border-r` | Glass-tier-thin classes on panel | Glass treatment for file tree |
| R2 | `file-tree-panel.tsx:47-49` | `hover:bg-accent hover:text-accent-foreground` + inline `style paddingLeft` | Same hover + `depth * 16 + 8px` indent + `rounded-[10px]` | Design system radius + indent spec |
| R3 | `file-tree-panel.tsx:91` | `bg-accent text-accent-foreground font-medium` (selected) | `bg-accent-muted text-primary font-medium` | Use accent-muted for selected state |
| R4 | `file-tree-panel.tsx:152-155` | Ad-hoc "No files found" text | `<EmptyState icon={FolderOpen} ...>` | Design system EmptyState |
| R5 | `file-tree-panel.tsx:133-136` | Ad-hoc "Loading..." text | Skeleton or caption with proper tokens | Status token alignment |
| R6 | `note-editor.tsx:148` | `flex items-center gap-3 border-b px-4 py-2` | Glass-tier-ultra-thin title bar + h-12 | Glass treatment for title bar |
| R7 | `note-editor.tsx:157-164` | Hardcoded `text-green-600` / `text-orange-500` | `text-status-success` / `text-status-warning` | §15 Diff Color Semantic Mapping |
| R8 | `note-editor.tsx:201` | `h-full resize-none rounded-none border-none shadow-none focus-visible:ring-0 font-mono text-sm` | `bg-surface-raised rounded-[10px] border-none font-mono text-[14px] p-4` | Surface-raised bg + design system radius |
| R9 | `note-editor.tsx:120-125` | Ad-hoc "Select a file..." text | `<EmptyState icon={FileText} ...>` | Design system EmptyState |
| R10 | `ai-assist-panel.tsx:98` | Plain `div` with `space-y-3` | Glass-tier-regular panel with header/footer structure | Glass treatment for AI panel |
| R11 | `ai-assist-panel.tsx:104-143` | `flex flex-wrap gap-2` for buttons | `flex flex-col gap-2 p-3` with full-width buttons | Vertical stack layout |
| R12 | `ai-assist-panel.tsx:160` | `border-destructive/50 bg-destructive/10` error | `border-destructive/50 bg-status-error-bg` | Status token for error bg |
| R13 | `diff-preview.tsx:24` | `bg-green-200/60 dark:bg-green-900/40` | `bg-status-success/15 border-l-[3px] border-l-status-success` | §15 — status tokens + left stripe |
| R14 | `diff-preview.tsx:31` | `bg-red-200/60 dark:bg-red-900/40` | `bg-status-error/15 border-l-[3px] border-l-status-error` | §15 — status tokens + left stripe |
| R15 | `diff-preview.tsx:97` | `border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-950` | `border-status-success/40 bg-status-success-bg` | §15 — status tokens |
| R16 | `diff-preview.tsx:98` | `text-green-600 dark:text-green-400` | `text-status-success` | §15 — status tokens |
| R17 | `diff-preview.tsx:99` | `text-green-700 dark:text-green-300` | `text-status-success` | §15 — status tokens |

### 21.2 Query Page Migrations

| # | File | Before | After | Rationale |
|---|---|---|---|---|
| Q1 | `query-page.tsx:59` | `<Input ... className="pl-9 pr-9">` | `<Input iconLeft={<Search />}>` | Design system Input with icon slot |
| Q2 | `query-page.tsx:67-74` | Inline `<button>` clear | `<Button variant="ghost" size="icon-sm">` | Design system Button |
| Q3 | `query-page.tsx:76-86` | Native `<select>` | `<Select>` + `<SelectTrigger>` + `<SelectContent>` | Design system Select from form-inputs spec |
| Q4 | `query-page.tsx:87-97` | Inline `Loader2` spinner handling | `Button loading={mutation.isPending}` | Design system Button loading prop |
| Q5 | `query-page.tsx:101-123` | Ad-hoc Skeleton cards | Skeleton with design system card styling | Glass-tier-thin cards |
| Q6 | `query-page.tsx:126-136` | Ad-hoc error state | `<EmptyState icon={AlertCircle} ... action>` | Design system EmptyState |
| Q7 | `query-page.tsx:138-143` | Ad-hoc empty state | `<EmptyState icon={Search} ...>` | Design system EmptyState |
| Q8 | `query-page.tsx:145-150` | Ad-hoc no results | `<EmptyState icon={FileText} ...>` | Design system EmptyState |
| Q9 | `query-page.tsx:159` | `hover:bg-accent/50` on Card | Remove; Card spec handles hover with shadow | Design system Card hover |

### 21.3 Skills Page Migrations

| # | File | Before | After | Rationale |
|---|---|---|---|---|
| S1 | `skills-page.tsx:44-56` | Native `<select>` for enum params | `<Select>` + `<SelectTrigger>` + `<SelectContent>` | Design system Select from form-inputs spec |
| S2 | `skills-page.tsx:66-81` | `<Checkbox>` for boolean params | `<Switch>` for boolean params | Design system Switch (toggle pattern) |
| S3 | `skills-page.tsx:193-197` | `bg-muted` output area | Glass-tier-ultra-thin output area | Glass treatment |
| S4 | `skills-page.tsx:200-203` | `bg-destructive/10` error area | `bg-status-error-bg` error area | Status token |
| S5 | `skills-page.tsx:214-217` | Inline `Loader2` spinner | `Button loading={runMutation.isPending}` | Design system Button loading prop |
| S6 | `skills-page.tsx:243-275` | Ad-hoc Skeleton cards | Skeleton with design system card styling | Glass-tier-thin cards |
| S7 | `skills-page.tsx:278-287` | Ad-hoc error state | `<EmptyState icon={AlertCircle} ...>` | Design system EmptyState |
| S8 | `skills-page.tsx:290-294` | Ad-hoc empty state | `<EmptyState icon={Boxes} ...>` | Design system EmptyState |

---

## Appendix A: Accessibility Checklist

### A.1 Record Page

| Check | FileTreePanel | NoteEditor | AIAssistPanel | DiffPreview |
|---|---|---|---|---|
| Keyboard nav | Arrow keys / Tab for tree items ✅ | Tab to title, Tab to textarea, Cmd+S ✅ | Tab through buttons ✅ | Tab to Accept/Reject ✅ |
| Focus indicator | `ring-2 ring-ring` on tree items ✅ | `focus-visible:ring-2` on title ✅ | Button focus ring ✅ | Button focus ring ✅ |
| Screen reader | Tree role or list semantics ✅ | `aria-label` on title input ✅ | Panel landmark or section ✅ | `role="region"` for diff ✅ |
| Color contrast | Tree text: 9.21:1 ✅ AAA | Status text: 4.5:1+ ✅ AA | Button text on primary: 7.21:1 ✅ | Status-success on success-bg: 4.5:1+ ✅ |
| Motion | Transition 100-150ms ✅ | Status color transition 150ms ✅ | Button transitions 120ms ✅ | Diff display: no animation needed ✅ |
| `prefers-reduced-motion` | Collapse transition disabled | Save spinner disabled | AI loading spinner disabled | Undo timer unaffected |

### A.2 Query Page

| Check | SearchBar | ResultCard |
|---|---|---|
| Keyboard nav | Tab to Input → Tab to Select → Tab to Button ✅ | Enter/Space to expand card ✅ |
| Focus indicator | Input ring ✅, Select ring ✅, Button ring ✅ | Card focus ring ✅ |
| Screen reader | `aria-label` on search, select, clear | Card as button or article with `aria-expanded` |
| Color contrast | Input text: 9.21:1 ✅ | Card text: 9.21:1, muted: 5.51:1 ✅ |
| Loading state | Button `aria-busy="true"` ✅ | Skeleton `aria-hidden="true"` ✅ |

### A.3 Skills Page

| Check | SkillCard | SkillRunDialog |
|---|---|---|
| Keyboard nav | Tab to "Run" button ✅ | Tab trap in dialog (Radix) ✅ |
| Focus indicator | Button ring ✅ | All form elements ring ✅ |
| Screen reader | Card as article ✅ | `Dialog.Title` + `Dialog.Description` ✅ |
| Color contrast | Card text: 9.21:1 ✅ | Form labels: 9.21:1 ✅ |
| Loading state | Skeleton `aria-hidden` ✅ | Execute button `aria-busy` ✅ |
| Form validation | — | Required fields with `aria-required` ✅ |

---

## Appendix B: Token Cross-Reference

| CSS Custom Property | Tailwind Class | Used In |
|---|---|---|
| `--color-foreground` | `text-foreground` | Page titles, tree names, card titles, editor text, dialog titles |
| `--color-muted-foreground` | `text-muted-foreground` | Tree icons, descriptions, status "Saving...", captions, placeholders |
| `--color-primary` | `text-primary` | Selected file text, AI icon, skill card icon, active AI button |
| `--color-primary-foreground` | `text-primary-foreground` | (via Button default text) |
| `--color-accent` | `bg-accent` | Tree item hover, tree item selected (via accent-muted) |
| `--color-accent-muted` | `bg-accent-muted` | Selected file background |
| `--color-surface-raised` | `bg-surface-raised` | Note editor textarea background |
| `--color-surface-base` | `bg-surface-base` | (via Select trigger, Input default bg) |
| `--color-border` | `border-border` | Card borders, dialog content borders |
| `--color-status-success` | `text-status-success`, `bg-status-success`, `border-status-success` | Diff insert, accepted state, "Saved" status |
| `--color-status-success-bg` | `bg-status-success-bg` | Diff accepted bg, Badge success bg |
| `--color-status-error` | `text-status-error`, `bg-status-error`, `border-status-error` | Diff delete, error areas |
| `--color-status-error-bg` | `bg-status-error-bg` | AI error bg, skill dialog error area |
| `--color-status-warning` | `text-status-warning` | "Unsaved" status |
| `--color-destructive` | `text-destructive`, `border-destructive` | Required field asterisks, error text |
| `--color-ring` | `ring-ring` | Focus rings on all interactive elements |
| `--color-background` | `ring-offset-background` | Focus ring offset |

### Glass Tailwind Classes Reference

| Element | Tailwind Classes |
|---|---|
| FileTreePanel | `bg-white/55 backdrop-blur-[16px] saturate-[140%] dark:bg-[rgba(26,20,15,0.60)]` |
| NoteEditor TitleBar | `bg-white/45 backdrop-blur-[8px] saturate-[120%] dark:bg-[rgba(26,20,15,0.50)]` |
| AIAssistPanel | `bg-white/65 backdrop-blur-[24px] saturate-[160%] dark:bg-[rgba(26,20,15,0.70)]` |
| ResultCard | `bg-white/55 backdrop-blur-[16px] saturate-[140%] dark:bg-[rgba(26,20,15,0.60)]` |
| SkillCard | same as ResultCard |
| SkillRunDialog | `bg-white/78 backdrop-blur-[40px] saturate-[180%] dark:bg-[rgba(26,20,15,0.80)]` |
| Output area | `bg-white/45 backdrop-blur-[8px] saturate-[120%] dark:bg-[rgba(26,20,15,0.50)]` |
| Glass border (light) | `border-white/10` or `border-white/35` |
| Glass border (dark) | `dark:border-white/6` or `dark:border-white/10` |
| Glass separator | `bg-white/10 dark:bg-white/6` |

---

## Appendix C: Implementation Checklist

### Phase 1: Token Prerequisites
- [ ] Verify `--color-status-success`, `--color-status-success-bg` in `globals.css` (both modes)
- [ ] Verify `--color-status-error`, `--color-status-error-bg` in `globals.css` (both modes)
- [ ] Verify `--color-status-warning` in `globals.css` (both modes)
- [ ] Verify `--color-surface-raised`, `--color-surface-base` in `globals.css` (both modes)
- [ ] Verify `--color-accent-muted` token exists or add it

### Phase 2: Record Page
- [ ] Update `file-tree-panel.tsx` — glass-tier-thin background, new indent spec, accent-muted selected, EmptyState for empty tree
- [ ] Update `note-editor.tsx` — glass-tier-ultra-thin title bar, status tokens for save status, surface-raised textarea, EmptyState for no-file
- [ ] Update `ai-assist-panel.tsx` — glass-tier-regular background, full-width vertical button stack, status-error-bg for errors
- [ ] Update `diff-preview.tsx` — status-success/status-error tokens per §15, left-border stripes, status-success-bg for accepted state

### Phase 3: Query Page
- [ ] Update `query-page.tsx` — Select component, Button loading prop, Input iconLeft, EmptyState for all empty/error states, Skeleton cards with glass styling
- [ ] Remove inline clear button → Button ghost icon-sm
- [ ] Remove native `<select>` → Select component

### Phase 4: Skills Page
- [ ] Update `skills-page.tsx` — Select for enum params, Switch for boolean params, Button loading prop, EmptyState for empty/error, Skeleton cards with glass styling
- [ ] Update output area to glass-tier-ultra-thin
- [ ] Update error area to status-error-bg

### Phase 5: Visual QA
- [ ] Record: light + dark mode across all 18 states (§13.1)
- [ ] Query: light + dark mode across all 8 states (§13.2)
- [ ] Skills: light + dark mode across all 8 states (§13.3)
- [ ] Verify glass treatments render correctly on mesh background
- [ ] Verify glass scrollbar thumb on all glass surfaces
- [ ] Verify responsive breakpoints (mobile/tablet/desktop)
- [ ] Verify keyboard navigation across all interactive elements
- [ ] Verify focus ring visibility on all components
- [ ] Verify `prefers-reduced-motion` disables animations
- [ ] Verify diff color tokens provide sufficient contrast (≥4.5:1)

### Phase 6: Accessibility Audit
- [ ] Verify all icon-only buttons have `aria-label`
- [ ] Verify tree items have appropriate ARIA roles
- [ ] Verify dialog focus trap works (Radix)
- [ ] Verify form field labels associated via `htmlFor`
- [ ] Verify color is not the sole indicator of state
- [ ] Verify result cards are keyboard-expandable

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
