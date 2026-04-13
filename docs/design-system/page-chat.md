# Chat Page — Full Composition Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion specs:** `layout-shell.md` · `components-button-badge.md` · `components-surface-overlay.md` · `components-form-inputs.md` · `components-feedback-utility.md`
> **Implementation:** `web/src/features/chat/`

---

## Table of Contents

1. [Page Layout Structure](#1-page-layout-structure)
2. [SessionList Sub-Component](#2-sessionlist-sub-component)
3. [ChatArea Sub-Component](#3-chatarea-sub-component)
4. [PanelHeader Sub-Component](#4-panelheader-sub-component)
5. [MessageBubble Sub-Component](#5-messagebubble-sub-component)
6. [MessageInput Sub-Component](#6-messageinput-sub-component)
7. [SourcesPanel Sub-Component](#7-sourcespanel-sub-component)
8. [CitationBadge Sub-Component](#8-citationbadge-sub-component)
9. [Streaming Indicator](#9-streaming-indicator)
10. [State Frames Specification](#10-state-frames-specification)
11. [Glass Treatment Map](#11-glass-treatment-map)
12. [Markdown Prose Overrides](#12-markdown-prose-overrides)
13. [Responsive Behavior](#13-responsive-behavior)
14. [Figma Frames Specification](#14-figma-frames-specification)
15. [TSX Skeleton](#15-tsx-skeleton)
16. [Migration Mapping](#16-migration-mapping)
17. [Appendix A: Accessibility Checklist](#appendix-a-accessibility-checklist)
18. [Appendix B: Token Cross-Reference](#appendix-b-token-cross-reference)
19. [Appendix C: Implementation Checklist](#appendix-c-implementation-checklist)

---

## 1. Page Layout Structure

### 1.1 Component Hierarchy

```
ChatPage (flex h-full, relative)
├── SessionList (w-52, glass-tier-thin, border-r glass-border)
│   ├── Header (h-12, flex, items-center, justify-between, px-3)
│   │   ├── Label: "Chats" (subhead: 13px/500, muted-foreground)
│   │   └── Button variant="ghost" size="icon-sm" (Plus icon)
│   ├── Session items (ScrollArea, flex-1, gap-1, px-2, py-1)
│   │   └── SessionItem (rounded-sm, px-3, py-2, group)
│   │       ├── Title (truncate, callout: 14px/400)
│   │       ├── Active indicator: left 2px primary stripe
│   │       └── Delete: Button ghost icon-sm data-destructive
│   │           (opacity-0 group-hover:opacity-100)
│   └── Footer (px-3, py-2, muted-foreground)
│       └── Caption: "N conversation(s)"
├── ChatArea (flex-1, flex-col, min-w-0, relative)
│   ├── PanelHeader (h-12, glass-tier-ultra-thin, border-b glass-border)
│   │   ├── Left: session title (subhead, truncate) + source count Badge
│   │   └── Right: Sources toggle (Button ghost sm) + New (Button ghost sm)
│   ├── MessagesArea (flex-1, overflow-hidden, relative)
│   │   ├── Empty state: EmptyState component
│   │   └── Message list (ScrollArea, max-w-3xl, mx-auto, gap-4, p-4)
│   │       ├── UserMessage: solid primary bg, radius-md, max-w-[80%], ml-auto
│   │       ├── AIMessage: glass-tier-ultra-thin, radius-md, max-w-[85%]
│   │       │   └── Markdown prose with warm overrides
│   │       ├── CitationBadges (flex-wrap, gap-1, mt-2)
│   │       └── StreamingIndicator: three pulsing dots
│   └── MessageInput (border-t glass-border, glass-tier-ultra-thin, p-3)
│       ├── Textarea (flex-1, auto-resize, max 6 rows, radius-sm)
│       ├── Send: Button variant="default" size="icon"
│       ├── Stop: Button variant="destructive" size="icon" (streaming only)
│       └── Source context caption (muted-foreground, mt-1)
└── SourcesPanel (w-64, glass-tier-regular, border-l glass-border, conditional)
    ├── Header (h-12, flex, items-center, justify-between, px-3)
    │   ├── "Sources" label + count Badge
    │   └── Close: Button ghost icon-sm (X icon)
    ├── File tree (ScrollArea, flex-1)
    │   └── TreeItem: recursive, indent depth×16px, Checkbox + icon + name
    └── Footer (border-t, px-3, py-2, flex, justify-between)
        ├── Selection count (caption, muted-foreground)
        ├── Clear: Button ghost xs "Clear"
        └── Done: Button default xs "Done"
```

### 1.2 ASCII Layout — Desktop (1440×900)

```
┌───────────┬─────────────────────────────────────────────┬──────────┐
│           │ ▼ PanelHeader (48px, glass-ultra-thin)      │          │
│  Session  │ [Title...]  [1 src]     [Sources] [New]     │ Sources  │
│  List     ├─────────────────────────────────────────────│  Panel   │
│  (208px)  │                                             │ (256px)  │
│           │                                             │          │
│  Chats ⊕  │    ┌──────────────────────────┐             │ Sources  │
│ ───────── │    │  User message             │             │ [Close]  │
│ ● Chat 1  │    │  (solid primary amber)    │             │ ──────── │
│   Chat 2  │    └──────────────────────────┘             │ ☑ notes  │
│   Chat 3  │                                             │   ☑ ch-1 │
│   Chat 4  │  ┌──────────────────────────────┐           │   ☐ ch-2 │
│ ───────── │  │  AI message (glass-ultra-thin)│           │   ☐ ideas│
│  5 chats  │  │  with markdown content...     │           │ ──────── │
│           │  │                               │           │ 2 select│
│           │  │  ┌────┐ ┌────┐ ┌────┐        │           │ [Clear] │
│           │  │  │ [1]│ │ [2]│ │ [3]│        │           │ [Done]  │
│           │  │  └────┘ └────┘ └────┘        │           │          │
│           │  └──────────────────────────────┘           │          │
│           │                                             │          │
│           ├─────────────────────────────────────────────│          │
│           │ [Type a message...              ] [Send]    │          │
│           │ 2 sources selected                          │          │
└───────────┴─────────────────────────────────────────────┴──────────┘
```

### 1.3 Z-Index Layering

| Layer | Token | Value | Element |
|---|---|---|---|
| Background mesh | `z-base` | 0 | Mesh gradient (inherited from layout shell) |
| Panel surfaces | — | 1 | SessionList, ChatArea, SourcesPanel |
| Panel headers | `z-sticky` | 10 | PanelHeader (sticky within ChatArea) |
| Citation popovers | `z-dropdown` | 30 | CitationBadge popover content |
| Sources sheet (mobile) | `z-modal-backdrop` | 40 | Sheet overlay |
| Sources sheet content | `z-modal` | 50 | Sheet panel |

### 1.4 Dimensional Summary

| Element | Width | Height | Notes |
|---|---|---|---|
| SessionList | 208px (`w-52`) | 100% | Fixed, collapsible on mobile |
| ChatArea | flex-1 | 100% | Flexible center |
| SourcesPanel | 256px (`w-64`) | 100% | Conditional, slide-on |
| PanelHeader | auto | 48px (`h-12`) | Sticky top within ChatArea |
| MessageInput | auto | auto (min ~52px) | Sticky bottom within ChatArea |
| Message list max-width | 768px (`max-w-3xl`) | — | Centered with mx-auto |
| User bubble max-width | 80% | auto | Right-aligned |
| AI bubble max-width | 85% | auto | Left-aligned |

---

## 2. SessionList Sub-Component

### 2.1 Glass Treatment

| Property | Light | Dark |
|---|---|---|
| Glass tier | **thin** (`blur(16px) saturate(140%)`) | Same |
| Background | `rgba(255,255,255,0.55)` | `rgba(26,20,15,0.60)` |
| Border-right | `1px solid rgba(255,255,255,0.35)` | `1px solid rgba(255,255,255,0.10)` |

### 2.2 Header

| Property | Value |
|---|---|
| Height | 48px (`h-12`) |
| Layout | `flex`, `items-center`, `justify-between`, `px-3` |
| Label | "Chats" — 13px/500 (`subhead`), `text-muted-foreground` |
| New button | `Button variant="ghost" size="icon-sm"` (28px), `MessageSquarePlus` icon 14px |

### 2.3 Session Items

**Container:** `ScrollArea` with `flex-1`, `gap-1`, `px-2`, `py-1`

**SessionItem anatomy:**

| Property | Value |
|---|---|
| Height | Auto (min 36px) |
| Padding | `px-3 py-2` |
| Border radius | 10px (`rounded-[10px]`) |
| Layout | `flex`, `items-center`, `group` |
| Transition | `transition-[background-color,color] duration-150 ease-out` |

**SessionItem states:**

| State | Background | Text | Border | Extra |
|---|---|---|---|---|
| Default | transparent | `text-foreground` | none | — |
| Hover | `bg-accent` | `text-accent-foreground` | none | — |
| Active | `bg-accent-muted` | `text-primary` | left 2px `primary` stripe | `::before` pseudo-element |
| Focus-visible | same as hover | same | 2px `ring` | Focus ring |

**Active stripe:** 2px-wide `primary`-colored bar on the left edge. Implementation: `::before` pseudo-element, `absolute left-0 top-1.5 bottom-1.5 w-[2px] rounded-full bg-primary`.

**Delete button:** `Button variant="ghost" size="icon-sm" data-destructive` with `Trash2` icon (14px). `opacity-0 group-hover:opacity-100`. Transition: `transition-opacity duration-150 ease-out`.

### 2.4 Empty State (no sessions)

| Property | Value |
|---|---|
| Text | "No conversations yet" |
| Typography | `caption` (12px/400), `text-muted-foreground`, `text-center` |
| Padding | `px-2 py-4` |

### 2.5 Footer

| Property | Value |
|---|---|
| Padding | `px-3 py-2` |
| Border-top | `glass-border` (`white/10` light, `white/6` dark) |
| Text | "N conversation(s)" — `caption` (12px/400), `text-muted-foreground` |
| Visibility | Hidden when `sessions.length === 0` |

### 2.6 Tailwind Classes

```tsx
// SessionList root
const sessionListClasses = cn(
  "flex h-full w-52 flex-col",
  // Glass-tier-thin
  "bg-white/55 backdrop-blur-[16px] saturate-[140%]",
  "border-r border-white/35",
  "dark:bg-[rgba(26,20,15,0.60)] dark:border-white/10",
);

// SessionItem
const itemClasses = cn(
  "group flex w-full items-center rounded-[10px] px-3 py-2",
  "text-[14px] text-foreground truncate",
  "transition-[background-color,color] duration-150 ease-out",
  "cursor-pointer outline-none",
  // Hover
  "hover:bg-accent hover:text-accent-foreground",
  // Active
  isActive && "bg-accent-muted text-primary relative",
  // Focus
  "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
);
```

---

## 3. ChatArea Sub-Component

### 3.1 Architecture

```
ChatArea (flex-1, flex-col, min-w-0, h-full, relative)
├── PanelHeader (h-12, sticky top-0)
├── MessagesArea (flex-1, overflow-hidden)
│   └── ScrollArea (h-full)
│       └── Message list (max-w-3xl, mx-auto, p-4, gap-4)
└── MessageInput (border-t, sticky bottom-0)
```

### 3.2 Glass Treatment

The ChatArea itself has **no glass treatment** — it is transparent, letting the background mesh gradient show through. Individual sub-components (PanelHeader, MessageInput, AI bubbles) apply their own glass tiers.

| Element | Glass Tier |
|---|---|
| ChatArea root | **transparent** (mesh visible) |
| PanelHeader | ultra-thin |
| MessagesArea | transparent |
| User message | **solid primary** (no glass) |
| AI message | ultra-thin |
| MessageInput bar | ultra-thin |

### 3.3 Empty State — No Session Selected

Uses the `EmptyState` component from `components-feedback-utility.md`:

| Property | Value |
|---|---|
| Icon | `MessageSquarePlus` |
| Icon background | `true` (glass circle) |
| Title | "No conversation selected" |
| Description | "Create a new chat to get started" |
| Action | `{ label: "New Chat", onClick: onNewChat, variant: "default" }` |

### 3.4 Empty State — No Messages (active session, empty)

| Property | Value |
|---|---|
| Icon | `MessageSquarePlus` |
| Icon background | `true` |
| Title | "Start a conversation" |
| Description | "Ask questions about your notes, get summaries, or brainstorm ideas." |
| Action | none |

### 3.5 Auto-Scroll Behavior

On new message or streaming start, `bottomRef.current?.scrollIntoView({ behavior: "smooth" })` scrolls the ScrollArea to the bottom.

---

## 4. PanelHeader Sub-Component

### 4.1 Glass Treatment

| Property | Light | Dark |
|---|---|---|
| Glass tier | **ultra-thin** (`blur(8px) saturate(120%)`) | Same |
| Background | `rgba(255,255,255,0.45)` | `rgba(26,20,15,0.50)` |
| Border-bottom | `1px solid rgba(255,255,255,0.35)` | `1px solid rgba(255,255,255,0.10)` |

### 4.2 Anatomy

| Property | Value |
|---|---|
| Height | 48px (`h-12`) |
| Layout | `flex`, `items-center`, `justify-between`, `px-4` |
| Position | `sticky top-0 z-10` within ChatArea |

### 4.3 Left Group

| Element | Spec |
|---|---|
| Session title | `text-[13px] font-medium truncate text-foreground` |
| Source count Badge | `Badge variant="secondary"` with `FileText` icon (12px) + "N source(s)" |
| Badge click | Triggers `onToggleSources` |
| Layout | `flex items-center gap-2 min-w-0` |

### 4.4 Right Group

| Element | Spec |
|---|---|
| Sources toggle | `Button variant="ghost" size="sm"` — `FileText` icon (14px) + "Sources" |
| New button | `Button variant="ghost" size="sm"` — `MessageSquarePlus` icon (14px) + "New" |
| Sources toggle visibility | Hidden when `sourcesOpen === true` |
| Layout | `flex items-center gap-1` |

---

## 5. MessageBubble Sub-Component

### 5.1 User Message

| Property | Value |
|---|---|
| Background | `bg-primary` — **solid amber, no glass** |
| Text | `text-primary-foreground` (#2B2116 in both modes) |
| Border radius | 14px top-left, 14px top-right, 14px bottom-right, 4px bottom-left |
| Max width | 80% (`max-w-[80%]`) |
| Alignment | `ml-auto` (right-aligned) |
| Padding | `px-4 py-3` |
| Typography | `text-[15px] leading-relaxed` (body-lg / 1.6) |
| Content | Plain text, `whitespace-pre-wrap` |
| Shadow | `shadow-md` (from tokens) |

### 5.2 AI Message

| Property | Light | Dark |
|---|---|---|
| Glass tier | **ultra-thin** (`blur(8px) saturate(120%)`) | Same |
| Background | `rgba(255,249,242,0.45)` | `rgba(26,20,15,0.40)` |
| Border | `1px solid rgba(220,199,167,0.10)` | `1px solid rgba(90,70,48,0.12)` |
| Text | `text-foreground` | Same |
| Border radius | 14px top-left, 14px top-right, 14px bottom-left, 4px bottom-right |
| Max width | 85% (`max-w-[85%]`) |
| Alignment | `mr-auto` (left-aligned) |
| Padding | `px-4 py-3` |
| Typography | `text-[15px] leading-relaxed` (body-lg / 1.6) |
| Content | Markdown via `react-markdown` + `remark-gfm` |
| Shadow | `shadow-sm` (from tokens) |

### 5.3 Bubble Radius Pattern

User and AI bubbles use asymmetric corner radii to create visual direction:

```
User bubble:                    AI bubble:
  ┌──────────────┐              ┌──────────────┐
  │ 14px    14px  │              │ 14px    14px  │
  │               │              │               │
  │ 14px     4px  │              │  4px     14px │
  └──────────────┘              └──────────────┘
  (flat tail → right)           (flat tail → left)
```

CSS: `rounded-[14px_14px_4px_14px]` for user, `rounded-[14px_14px_14px_4px]` for AI.

### 5.4 Streaming State

When `isStreaming && role === "assistant"`:

| Property | Value |
|---|---|
| Bubble content | Current markdown content + streaming indicator (§9) |
| Animation | Subtle — **no `animate-pulse` on the bubble itself** |
| Opacity | Full — content remains at 100% opacity |
| Cursor | Default — no visual change |

> **Critical:** The current codebase applies `animate-pulse` to the entire AI bubble during streaming, which makes content flicker. The new spec **removes** this and uses only the dedicated streaming indicator dots (§9).

### 5.5 Tailwind Classes

```tsx
// User message
const userBubbleClasses = cn(
  "max-w-[80%] ml-auto px-4 py-3",
  "rounded-[14px_14px_4px_14px]",
  "bg-primary text-primary-foreground shadow-md",
  "text-[15px] leading-[1.6] whitespace-pre-wrap",
);

// AI message
const aiBubbleClasses = cn(
  "max-w-[85%] mr-auto px-4 py-3",
  "rounded-[14px_14px_14px_4px]",
  // Glass-tier-ultra-thin
  "bg-white/45 backdrop-blur-[8px] saturate-[120%]",
  "border border-[rgba(220,199,167,0.10)]",
  "dark:bg-[rgba(26,20,15,0.40)] dark:border-[rgba(90,70,48,0.12)]",
  "text-foreground shadow-sm",
  "text-[15px] leading-[1.6]",
);
```

---

## 6. MessageInput Sub-Component

### 6.1 Glass Treatment

| Property | Light | Dark |
|---|---|---|
| Glass tier | **ultra-thin** (`blur(8px) saturate(120%)`) | Same |
| Background | `rgba(255,249,242,0.45)` | `rgba(26,20,15,0.50)` |
| Border-top | `1px solid rgba(255,255,255,0.35)` | `1px solid rgba(255,255,255,0.10)` |

### 6.2 Anatomy

| Element | Spec |
|---|---|
| Container | `flex items-end gap-2 p-3` |
| Textarea | `flex-1`, auto-resize, min 1 row, max 6 rows (144px), `rounded-[10px]` |
| Textarea border | `border-border bg-surface-base text-foreground` |
| Send button | `Button variant="default" size="icon"` — `SendHorizonal` icon (16px) |
| Stop button | `Button variant="destructive" size="icon"` — `Square` icon (16px), shown when streaming |
| Source context | `text-[12px] text-muted-foreground`, shown below input when sources selected |

### 6.3 Textarea Behavior

| Property | Value |
|---|---|
| Auto-resize | JS-driven: `el.style.height = 'auto'; el.style.height = Math.min(el.scrollHeight, 144) + 'px'` |
| Submit | Enter to send, Shift+Enter for newline |
| Disabled | When `isStreaming` or `disabled` prop is true |
| Focus | Standard focus ring (`ring-2 ring-ring`) |

### 6.4 Source Context Indicator

```
 ┌──────────────────────────────────────────────────────┐
 │ [Type a message...                          ] [▶ Send]│
 │ 📄 2 sources selected                                │
 └──────────────────────────────────────────────────────┘
```

Shown only when `sourceCount > 0`. Icon: inline SVG `FileText` (12px). Text: "N source(s) selected".

---

## 7. SourcesPanel Sub-Component

### 7.1 Glass Treatment

| Property | Light | Dark |
|---|---|---|
| Glass tier | **regular** (`blur(24px) saturate(160%)`) | Same |
| Background | `rgba(255,255,255,0.65)` | `rgba(26,20,15,0.70)` |
| Border-left | `1px solid rgba(255,255,255,0.40)` | `1px solid rgba(255,255,255,0.12)` |

### 7.2 Header

| Property | Value |
|---|---|
| Height | 48px (`h-12`) |
| Layout | `flex`, `items-center`, `justify-between`, `px-3` |
| Left | "Sources" label (13px/500) + source count `Badge variant="secondary"` |
| Right | Close button: `Button variant="ghost" size="icon-sm"` — `X` icon (14px) |

### 7.3 File Tree

**TreeItem anatomy:**

| Property | Value |
|---|---|
| Indentation | `depth × 16px` (`ml-[${depth * 16}px]`) |
| Height | ~32px per row |
| Layout | `flex items-center gap-1.5 px-2 py-1` |
| Hover | `hover:bg-accent/50` |
| Chevron | `ChevronRight` 12px, `rotate-90` when expanded |
| Checkbox | 18×18px, from `components-form-inputs.md` — supports indeterminate |
| Folder icon | `Folder` / `FolderOpen` 16px, `text-muted-foreground` |
| File icon | `FileText` 16px, `text-muted-foreground` |
| Name | `truncate text-[12px]` |

### 7.4 Footer

| Property | Value |
|---|---|
| Border-top | `glass-border` |
| Layout | `flex items-center justify-between px-3 py-2` |
| Left | Selection count: "N selected" — `caption`, `text-muted-foreground` |
| Right | `Button variant="ghost" size="xs"` "Clear" + `Button variant="default" size="xs"` "Done" |

### 7.5 Tailwind Classes

```tsx
const sourcesPanelClasses = cn(
  "flex h-full w-64 flex-col",
  // Glass-tier-regular
  "bg-white/65 backdrop-blur-[24px] saturate-[160%]",
  "border-l border-white/40",
  "dark:bg-[rgba(26,20,15,0.70)] dark:border-white/12",
);
```

---

## 8. CitationBadge Sub-Component

### 8.1 Anatomy

| Property | Value |
|---|---|
| Min-height | 22px |
| Padding | `0 6px` (`px-1.5 py-0.5`) |
| Border radius | 6px (`rounded-sm`) |
| Border | `1px solid border` |
| Background | `bg-accent/40` |
| Text | `text-[11px] font-medium text-muted-foreground` |
| Layout | `inline-flex items-center gap-1` |
| Icon | `FileText` 12px |
| Content | Filename + "p.N" (if page) + superscript index |
| Hover | `hover:bg-accent hover:text-foreground` |
| Transition | `transition-[background-color,color] duration-150 ease-out` |

### 8.2 Popover Content

Uses the `Popover` component from `components-surface-overlay.md` (glass-tier-thin):

| Property | Value |
|---|---|
| Width | 320px (`w-80`) |
| Side | `top` (default) |
| Side offset | 8px |
| Content padding | 12px (`p-3`) |

**Popover content sections:**

| Section | Spec |
|---|---|
| File path | `text-[12px] font-medium text-foreground` |
| Location | "Page N, Paragraph M" — `text-[12px] text-muted-foreground` |
| Snippet | `rounded-[10px] bg-accent/30 p-2 text-[12px] leading-relaxed text-foreground mt-2` |

### 8.3 Positioning

Citations render **inside** the AI bubble, below the markdown content:

```
┌──────────────────────────────┐
│  AI message markdown content  │
│  ...                          │
│                               │
│  ┌────┐ ┌────┐ ┌────┐       │
│  │[1] │ │[2] │ │[3] │       │
│  └────┘ └────┘ └────┘       │
└──────────────────────────────┘
```

Layout: `flex flex-wrap gap-1 mt-2`.

---

## 9. Streaming Indicator

### 9.1 Three-Dot Pulse

Replaces the current `Loader2` spinner with a subtle, warm amber pulse pattern:

```
  ● · ·     →   · ● ·     →   · · ●     →   ● · ·
  (600ms)       (600ms)       (600ms)
```

### 9.2 Anatomy

| Property | Value |
|---|---|
| Container | `flex items-center gap-1 mt-2` |
| Dot size | 6px (`w-1.5 h-1.5`) |
| Dot shape | `rounded-full` |
| Dot color | `bg-primary` (amber) |
| Animation | Staggered pulse with 200ms delay between dots |
| Opacity range | 0.3 (rest) → 1.0 (pulse) |
| Cycle | 1.4s total (`animation: citation-pulse 1.4s ease-in-out infinite`) |

### 9.3 Keyframe Animation

```css
@keyframes dot-pulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(1); }
  40% { opacity: 1; transform: scale(1.15); }
}
```

Each dot gets: `animation: dot-pulse 1.4s ease-in-out infinite`, with `animation-delay: 0s`, `0.2s`, `0.4s` for the three dots respectively.

### 9.4 Thinking State

When the AI is "thinking" (no content yet):

```
  Thinking ● · ·
```

Layout: `flex items-center gap-2 text-[14px] text-muted-foreground`. Text "Thinking..." + three-dot indicator.

### 9.5 Reduced Motion

Under `prefers-reduced-motion: reduce`: dots render at full opacity without animation. Single static dot: `opacity: 1, no transform`.

---

## 10. State Frames Specification

### Frame 1: Empty — No Session Selected

```
┌───────────┬─────────────────────────────────────────────┐
│           │                                             │
│  Chats ⊕  │         ┌──────────────────┐               │
│ ───────── │         │   💬 (40px icon)  │               │
│           │         │                  │               │
│  No       │         │  No conversation │               │
│  convers- │         │    selected      │               │
│  ations   │         │                  │               │
│  yet      │         │ Create a new chat│               │
│           │         │   to get started │               │
│           │         │                  │               │
│           │         │   [New Chat]     │               │
│           │         └──────────────────┘               │
│           │                                             │
└───────────┴─────────────────────────────────────────────┘
```

**Components:** SessionList (thin glass) + ChatArea with EmptyState (transparent bg, MessageSquarePlus icon, glass circle bg, title, description, action button).

### Frame 2: Empty — No Messages

```
┌───────────┬─────────────────────────────────────────────┐
│           │ ▼ New Chat                    [Sources][New]│
│  Chats ⊕  ├─────────────────────────────────────────────│
│ ───────── │                                             │
│ ● New Chat│         ┌──────────────────┐               │
│           │         │   💬 (40px icon)  │               │
│           │         │                  │               │
│           │         │ Start a          │               │
│           │         │  conversation    │               │
│           │         │                  │               │
│           │         │ Ask questions    │               │
│           │         │ about your notes │               │
│           │         └──────────────────┘               │
│           │                                             │
│           ├─────────────────────────────────────────────│
│           │ [Type a message...                    ] [▶] │
└───────────┴─────────────────────────────────────────────┘
```

**Components:** PanelHeader (ultra-thin glass) + EmptyState (no action button) + MessageInput (ultra-thin glass).

### Frame 3: Active Conversation

```
┌───────────┬─────────────────────────────────────────────┐
│           │ ▼ Markdown Notes             [Sources][New]│
│  Chats ⊕  ├─────────────────────────────────────────────│
│ ───────── │                                             │
│ ● Md Notes│   ┌──────────────────────────────┐          │
│  Research │   │ What are the key themes in    │ (user)  │
│  Ideas    │   │ my research notes?            │          │
│           │   └──────────────────────────────┘          │
│           │                                             │
│           │ ┌──────────────────────────────┐            │
│           │ │ Based on your notes, here    │ (AI,      │
│           │ │ are the main themes:         │  glass)    │
│           │ │                              │            │
│           │ │ 1. **Knowledge management**  │            │
│           │ │ 2. Information architecture  │            │
│           │ │ 3. Personal productivity     │            │
│           │ │                              │            │
│           │ │ ┌────┐ ┌────┐               │            │
│           │ │ │ [1]│ │ [2]│               │            │
│           │ │ └────┘ └────┘               │            │
│           │ └──────────────────────────────┘            │
│           │                                             │
│           ├─────────────────────────────────────────────│
│           │ [Type a message...                    ] [▶] │
└───────────┴─────────────────────────────────────────────┘
```

### Frame 4: Streaming

```
│           │ ┌──────────────────────────────┐            │
│           │ │ Based on the analysis, the   │            │
│           │ │ primary themes emerging from │            │
│           │ │ your research notes are:     │            │
│           │ │                              │            │
│           │ │ 1. **Knowledge management**  │            │
│           │ │ — organizing and connecting  │            │
│           │ │ information across domains   │            │
│           │ │                              │            │
│           │ │ 2. **Information architecture│            │
│           │ │ — structuring complex systems│            │
│           │ │                              │            │
│           │ │   ● · ·                      │            │
│           │ └──────────────────────────────┘            │
│           ├─────────────────────────────────────────────│
│           │ [Type a message...                 ] [■ Stop]│
```

Send button replaced by Stop button (destructive variant). Three-dot indicator pulses at bottom of AI bubble.

### Frame 5: Sources Panel Open

Three-column layout with SessionList + ChatArea + SourcesPanel visible.

### Frame 6: Long Message with Code Block

```
│           │ ┌──────────────────────────────┐            │
│           │ │ Here's a code example:       │            │
│           │ │                              │            │
│           │ │ ┌──────────────────────────┐ │            │
│           │ │ │ function greet(name) {   │ │ (code     │
│           │ │ │   return `Hello, ${n}!`; │ │  block)   │
│           │ │ │ }                        │ │            │
│           │ │ └──────────────────────────┘ │            │
│           │ │                              │            │
│           │ │ ## Summary                   │            │
│           │ │                              │            │
│           │ │ | Metric | Value |          │            │
│           │ │ |--------|-------|          │            │
│           │ │ | Lines  | 42    |          │            │
│           │ │                              │            │
│           │ │ > Note: This is a blockquote │            │
│           │ └──────────────────────────────┘            │
```

### Frame 7: Multiple Citations with Popover

```
│           │ │  ┌────┐ ┌────┐ ┌────┐ ┌────┐            │
│           │ │  │[1] │ │[2] │ │[3] │ │[4] │            │
│           │ │  └────┘ └─┬──┘ └────┘ └────┘            │
│           │ │      ┌────┴─────────────────┐            │
│           │ │      │ notes/research.md     │            │
│           │ │      │ Page 12, Paragraph 3  │            │
│           │ │      │ "The primary finding  │            │
│           │ │      │  suggests that..."     │            │
│           │ │      └───────────────────────┘            │
```

One badge has its Popover open. Popover uses glass-tier-thin, positioned above the badge row.

### Frame 8: Error State

```
│           │ ┌──────────────────────────────────────────┐ │
│           │ │ ▌⚠  Connection lost                      │ │
│           │ │    Check your network and retry. [Retry]  │ │
│           │ └──────────────────────────────────────────┘ │
│           │                                             │
│           │   ┌──────────────────────────────┐          │
│           │   │ Previous user message         │          │
│           │   └──────────────────────────────┘          │
```

AlertBanner (variant="error", dismissible, with "Retry" action) above the message list.

### Frame 9: Session List with Hover

```
│  Chats ⊕  │
│ ───────── │
│ ● Md Notes│  ← active (accent-muted bg, primary text, 2px stripe)
│  Research │  ← hover (accent bg, accent-foreground text)
│  Ideas 🗑│  ← hover shows delete button
│  Project X│  ← default (transparent bg, foreground text)
│  Archive  │  ← default
│ ───────── │
│  5 chats  │
```

---

## 11. Glass Treatment Map

| Element | Glass Tier | Backdrop-Filter | Light BG | Dark BG | Border (Light) | Border (Dark) | Notes |
|---|---|---|---|---|---|---|---|
| SessionList panel | thin | `blur(16px) saturate(140%)` | `white/55` | `[26,20,15]/60` | `white/35` | `white/10` | Static sidebar — moderate blur for item readability |
| PanelHeader | ultra-thin | `blur(8px) saturate(120%)` | `white/45` | `[26,20,15]/50` | `white/35` | `white/10` | Subtle — lets messages show through |
| MessagesArea | **transparent** | — | — | — | — | — | Mesh gradient visible for depth |
| User message bubble | **solid primary** | — | `primary` #E6A23C | `primary` #F0B04A | — | — | No glass — solid amber |
| AI message bubble | ultra-thin | `blur(8px) saturate(120%)` | `[255,249,242]/45` | `[26,20,15]/40` | `[220,199,167]/10` | `[90,70,48]/12` | Subtle frosted glass |
| MessageInput bar | ultra-thin | `blur(8px) saturate(120%)` | `white/45` | `[26,20,15]/50` | `white/35` | `white/10` | Floating above mesh |
| SourcesPanel | regular | `blur(24px) saturate(160%)` | `white/65` | `[26,20,15]/70` | `white/40` | `white/12` | More opaque for file tree readability |
| Citation popover | thin | `blur(16px) saturate(140%)` | `white/55` | `[26,20,15]/60` | `white/35` | `white/10` | Floating overlay — uses Popover spec |

### Glass Border Utility

Panel borders between glass surfaces use the glass separator token:

```css
.glass-border {
  border-color: rgba(255, 255, 255, 0.10);
}
.dark .glass-border {
  border-color: rgba(255, 255, 255, 0.06);
}
```

---

## 12. Markdown Prose Overrides

### 12.1 Prose Container Class

```css
.prose-warm {
  /* Base typography */
  --tw-prose-body: var(--color-foreground);
  --tw-prose-headings: var(--color-foreground);
  --tw-prose-lead: var(--color-muted-foreground);
  --tw-prose-links: var(--color-primary);
  --tw-prose-bold: var(--color-foreground);
  --tw-prose-counters: var(--color-muted-foreground);
  --tw-prose-bullets: var(--color-primary);
  --tw-prose-hr: var(--color-border);
  --tw-prose-quotes: var(--color-muted-foreground);
  --tw-prose-quote-borders: color-mix(in oklch, var(--color-primary) 30%, transparent);
  --tw-prose-captions: var(--color-muted-foreground);
  --tw-prose-code: var(--color-foreground);
  --tw-prose-pre-code: var(--color-foreground);
  --tw-prose-pre-bg: var(--color-surface-sunken);
  --tw-prose-th-borders: var(--color-border);
  --tw-prose-td-borders: var(--color-border);
}
```

### 12.2 Per-Element Styling

**Headings:**

```css
.prose-warm h1 { font-size: 24px; font-weight: 600; margin-top: 24px; margin-bottom: 8px; }
.prose-warm h2 { font-size: 20px; font-weight: 600; margin-top: 20px; margin-bottom: 8px; }
.prose-warm h3 { font-size: 18px; font-weight: 600; margin-top: 16px; margin-bottom: 6px; }
.prose-warm h4 { font-size: 16px; font-weight: 600; margin-top: 12px; margin-bottom: 4px; }
```

**Code blocks:**

```css
.prose-warm pre {
  background: var(--color-surface-sunken); /* #F6E6CA light, #0F0B08 dark */
  border-radius: 10px;
  padding: 12px 16px;
  margin: 12px 0;
  overflow-x: auto;
  font-family: var(--font-mono);
  font-size: 14px;
  line-height: 1.6;
  border: 1px solid rgba(255, 255, 255, 0.06);
}
```

**Inline code:**

```css
.prose-warm :not(pre) > code {
  background: var(--color-surface-sunken);
  border-radius: 4px;
  padding: 2px 6px;
  font-size: 13px;
  font-weight: 500;
}
```

**Links:**

```css
.prose-warm a {
  color: var(--color-primary);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 150ms ease-out;
}
.prose-warm a:hover {
  border-bottom-color: var(--color-primary);
}
```

**Tables:**

```css
.prose-warm table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 14px;
}
.prose-warm th {
  background: var(--color-accent); /* #F6E6CA light, #31261C dark */
  text-align: left;
  padding: 8px 12px;
  font-weight: 500;
  border-bottom: 1px solid var(--color-border);
}
.prose-warm td {
  padding: 6px 12px;
  border-bottom: 1px solid var(--color-border);
}
```

**Blockquotes:**

```css
.prose-warm blockquote {
  border-left: 4px solid color-mix(in oklch, var(--color-primary) 30%, transparent);
  padding-left: 16px;
  color: var(--color-muted-foreground);
  margin: 12px 0;
  font-style: normal;
}
```

**Lists:**

```css
.prose-warm ul {
  list-style-type: disc;
  margin: 8px 0;
  padding-left: 24px;
}
.prose-warm ol {
  list-style-type: decimal;
  margin: 8px 0;
  padding-left: 24px;
}
.prose-warm li {
  margin: 4px 0;
  line-height: 1.6;
}
.prose-warm li::marker {
  color: var(--color-primary);
}
```

**Horizontal rule:**

```css
.prose-warm hr {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 16px 0;
}
```

### 12.3 Tailwind Class Composition

```tsx
<div className={cn(
  "prose prose-warm max-w-none",
  // Paragraph spacing
  "prose-p:my-1.5 prose-p:leading-[1.6]",
  // Heading spacing
  "prose-headings:my-3",
  // Pre (code block) styling
  "prose-pre:my-3 prose-pre:rounded-[10px]",
  "prose-pre:bg-surface-sunken",
  // Inline code
  "prose-code:text-[13px] prose-code:font-medium",
  // List spacing
  "prose-li:my-0.5",
)}>
  <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
</div>
```

---

## 13. Responsive Behavior

### 13.1 Breakpoint Matrix

| Breakpoint | Viewport | SessionList | ChatArea | SourcesPanel |
|---|---|---|---|---|
| **< md** (< 768px) | Mobile | Hidden → Sheet (left) | Full-width | Hidden → Sheet (right) |
| **md – lg** (768–1023px) | Tablet | Collapsible (inline) | Full-width minus sidebar | Overlay (Sheet) |
| **≥ lg** (≥ 1024px) | Desktop | Fixed w-52 | flex-1 | Fixed w-64 (conditional) |

### 13.2 Mobile (< 768px)

**SessionList:**
- Hidden inline; accessible via hamburger button in PanelHeader
- Opens as `Sheet` (side="left", w-64, glass-tier-regular)
- Sheet uses `Dialog` from Radix for focus trapping
- Closes on: overlay click, Escape, session select

**ChatArea:**
- Full-width, no side panels
- PanelHeader shows hamburger on left: `Button variant="ghost" size="icon-sm"` — `Menu` icon
- Messages render at full width with `max-w-full` override (no centering constraint)

**SourcesPanel:**
- Not shown inline; opens as `Sheet` (side="right", w-64, glass-tier-regular)
- Triggered by Sources button in PanelHeader
- Closes on: overlay click, Escape, Done/Clear button

**MessageInput:**
- Full-width, same glass treatment
- Textarea expands vertically as normal

### 13.3 Tablet (768–1023px)

**SessionList:**
- Visible as collapsed w-14 by default (icons only, no text labels)
- Expandable to w-52 via toggle button
- When collapsed, session title shown via Tooltip `side="right"`

**ChatArea:**
- Takes remaining width after SessionList
- SourcesPanel not shown inline; opens as overlay Sheet

**SourcesPanel:**
- Opens as Sheet (side="right", w-64)
- Overlay backdrop dims ChatArea

### 13.4 Desktop (≥ 1024px)

All three panels visible. SourcesPanel is conditional (shown only when toggled and a session is active).

### 13.5 Responsive Tailwind Patterns

```tsx
// SessionList
<aside className={cn(
  // Hidden on mobile, visible on tablet+
  "hidden md:flex flex-col h-full",
  // Glass-tier-thin
  "bg-white/55 backdrop-blur-[16px] saturate-[140%]",
  "border-r border-white/35",
  "dark:bg-[rgba(26,20,15,0.60)] dark:border-white/10",
  // Width: collapsed on tablet, full on desktop
  collapsed ? "md:w-14 lg:w-52" : "w-52",
  "transition-[width] duration-300 ease-in-out",
)} />

// SourcesPanel
{sourcesOpen && (
  <aside className={cn(
    // Hidden on mobile (uses Sheet instead), visible on desktop
    "hidden lg:flex flex-col h-full w-64",
    "bg-white/65 backdrop-blur-[24px] saturate-[160%]",
    "border-l border-white/40",
    "dark:bg-[rgba(26,20,15,0.70)] dark:border-white/12",
  )} />
)}

// Mobile Sources Sheet (rendered at page level)
{isMobile && sourcesOpen && (
  <SheetRoot modal open={sourcesOpen} onOpenChange={setSourcesOpen}>
    <SheetContent side="right" className="w-64">
      <SourcesPanelContent />
    </SheetContent>
  </SheetRoot>
)}
```

---

## 14. Figma Frames Specification

### 14.1 Frame Inventory

16 frames total — 8 states × 2 themes:

| # | Frame Name | Size | Theme | State |
|---|---|---|---|---|
| 1 | `Desktop / Empty No Session / Light` | 1440 × 900 | Light | No session selected |
| 2 | `Desktop / Empty No Messages / Light` | 1440 × 900 | Light | Active session, no messages |
| 3 | `Desktop / Active Conversation / Light` | 1440 × 900 | Light | Mixed messages + citations |
| 4 | `Desktop / Streaming / Light` | 1440 × 900 | Light | AI streaming with dots |
| 5 | `Desktop / Sources Open / Light` | 1440 × 900 | Light | Three-panel layout |
| 6 | `Desktop / Error State / Light` | 1440 × 900 | Light | AlertBanner + messages |
| 7 | `Desktop / Long Message / Light` | 1440 × 900 | Light | Code blocks, tables, lists |
| 8 | `Desktop / Session Hover / Light` | 1440 × 900 | Light | Delete button visible |
| 9–16 | Same 8 frames | 1440 × 900 | Dark | Mirror of frames 1–8 |

Additional mobile frames:

| # | Frame Name | Size | Theme | State |
|---|---|---|---|---|
| 17 | `Mobile / Active / Light` | 375 × 812 | Light | Full-width chat |
| 18 | `Mobile / Drawer Open / Light` | 375 × 812 | Light | SessionList sheet |
| 19 | `Mobile / Sources Sheet / Light` | 375 × 812 | Light | SourcesPanel sheet |
| 20–22 | Same 3 frames | 375 × 812 | Dark | Mirror of 17–19 |

### 14.2 Frame Layout — Desktop Active Conversation (1440 × 900)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Background Mesh (warm amber radials over warm parchment)                │
│ ┌──────────┬──────────────────────────────────────┬──────────┐          │
│ │ 208px    │ PanelHeader 48px                      │ 256px    │          │
│ │          │ [Md Notes] [1 src]    [Sources] [New] │          │          │
│ │ glass-   ├──────────────────────────────────────│ glass-   │          │
│ │ thin     │                                      │ regular  │          │
│ │          │  ┌─────────────────────────────┐     │          │          │
│ │ Chats ⊕  │  │ What are the key themes?    │ (u) │ Sources  │          │
│ │ ──────── │  └─────────────────────────────┘     │ [Close]  │          │
│ │ ● Md Not │                                      │ ──────── │          │
│ │  Researc │  ┌─────────────────────────────┐     │ ☑ notes  │          │
│ │  Ideas   │  │ Based on your notes...      │ (a) │   ☑ ch-1 │          │
│ │  Project │  │                              │     │   ☐ ch-2 │          │
│ │  Archive │  │ 1. Knowledge management     │     │   ☐ ideas│          │
│ │ ──────── │  │ 2. Information architecture │     │ ──────── │          │
│ │ 5 chats  │  │                              │     │ 2 select│          │
│ │          │  │ ┌────┐ ┌────┐              │     │ [Clear] │          │
│ │          │  │ │[1] │ │[2] │              │     │ [Done]  │          │
│ │          │  │ └────┘ └────┘              │     │          │          │
│ │          │  └─────────────────────────────┘     │          │          │
│ │          │                                      │          │          │
│ │          ├──────────────────────────────────────│          │          │
│ │          │ [Type a message...            ] [▶]  │          │          │
│ │          │ 2 sources selected                   │          │          │
│ └──────────┴──────────────────────────────────────┴──────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Annotation key:**
- `(u)` = User message (solid primary, right-aligned, asymmetric radius)
- `(a)` = AI message (ultra-thin glass, left-aligned, asymmetric radius)

### 14.3 Figma Component Instances Per Frame

Each desktop frame uses these component instances:

| Component | Instance | Source Spec |
|---|---|---|
| Button | Header new, Sources toggle, New, Send, Stop, Close, Clear, Done | `components-button-badge.md` |
| Badge | Source count, selection count | `components-button-badge.md` |
| ScrollArea | Session list, message list, file tree | `components-feedback-utility.md` |
| Popover | Citation badge popover | `components-surface-overlay.md` |
| Checkbox | File tree items | `components-form-inputs.md` |
| Textarea | Message input | `components-form-inputs.md` |
| Separator | Panel dividers, list separators | `components-surface-overlay.md` |
| EmptyState | No session, no messages | `components-feedback-utility.md` |
| AlertBanner | Error state | `components-feedback-utility.md` |
| Sheet | Mobile SessionList, mobile SourcesPanel | `components-surface-overlay.md` |

---

## 15. TSX Skeleton

### 15.1 ChatPage

```tsx
// web/src/features/chat/chat-page.tsx
import { useState } from "react";
import { useIsMobile } from "@/hooks/use-mobile";
import { useChatStore } from "./chat-store";
import { ChatArea } from "./chat-area";
import { SessionList } from "./session-list";
import { SourcesPanel } from "./sources-panel";

export function ChatPage() {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const isMobile = useIsMobile();
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const createSession = useChatStore((s) => s.createSession);

  const handleNewChat = () => {
    createSession();
    setSourcesOpen(false);
  };

  return (
    <div className="flex h-full">
      {/* SessionList — hidden on mobile (Sheet handles it) */}
      <SessionList />

      {/* Main chat area */}
      <div className="flex flex-1 min-w-0">
        <ChatArea
          onToggleSources={() => setSourcesOpen(!sourcesOpen)}
          sourcesOpen={sourcesOpen}
          onNewChat={handleNewChat}
        />

        {/* SourcesPanel — inline on desktop, sheet on mobile */}
        {activeSessionId && !isMobile && (
          <SourcesPanel
            open={sourcesOpen}
            onClose={() => setSourcesOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
```

### 15.2 SessionList (migrated)

```tsx
// web/src/features/chat/session-list.tsx
import { MessageSquarePlus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useChatStore } from "./chat-store";

export function SessionList() {
  const sessions = useChatStore((s) => s.sessions);
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const createSession = useChatStore((s) => s.createSession);
  const setActiveSession = useChatStore((s) => s.setActiveSession);
  const deleteSession = useChatStore((s) => s.deleteSession);

  return (
    <div
      className={cn(
        "flex h-full w-52 flex-col",
        "bg-white/55 backdrop-blur-[16px] saturate-[140%]",
        "border-r border-white/35",
        "dark:bg-[rgba(26,20,15,0.60)] dark:border-white/10",
      )}
    >
      {/* Header */}
      <div className="flex h-12 items-center justify-between px-3">
        <span className="text-[13px] font-medium text-muted-foreground">
          Chats
        </span>
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={() => createSession()}
          aria-label="New chat"
        >
          <MessageSquarePlus />
        </Button>
      </div>

      {/* Session list */}
      <ScrollArea className="flex-1 px-2 py-1">
        {sessions.length === 0 && (
          <p className="px-2 py-4 text-center text-xs text-muted-foreground">
            No conversations yet
          </p>
        )}
        <div className="flex flex-col gap-1">
          {sessions.map((session) => {
            const isActive = session.id === activeSessionId;
            return (
              <button
                key={session.id}
                className={cn(
                  "group relative flex w-full items-center rounded-[10px] px-3 py-2",
                  "text-[14px] cursor-pointer outline-none",
                  "transition-[background-color,color] duration-150 ease-out",
                  isActive
                    ? "bg-accent-muted text-primary"
                    : "text-foreground hover:bg-accent hover:text-accent-foreground",
                  "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
                )}
                onClick={() => setActiveSession(session.id)}
              >
                {/* Active stripe */}
                {isActive && (
                  <span
                    className="absolute left-0 top-1.5 bottom-1.5 w-[2px] rounded-full bg-primary"
                    aria-hidden="true"
                  />
                )}
                <span className="flex-1 truncate text-left">{session.title}</span>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  data-destructive
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteSession(session.id);
                  }}
                  className="opacity-0 group-hover:opacity-100"
                  aria-label="Delete chat"
                >
                  <Trash2 />
                </Button>
              </button>
            );
          })}
        </div>
      </ScrollArea>

      {/* Footer */}
      {sessions.length > 0 && (
        <div className="border-t border-white/10 dark:border-white/6 px-3 py-2">
          <p className="text-[12px] text-muted-foreground">
            {sessions.length} conversation{sessions.length !== 1 ? "s" : ""}
          </p>
        </div>
      )}
    </div>
  );
}
```

### 15.3 MessageBubble (migrated)

```tsx
// web/src/features/chat/message-bubble.tsx
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import type { Message } from "@/types/chat";
import { CitationBadge } from "./citation-badge";

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      <div
        className={cn(
          "px-4 py-3 text-[15px] leading-[1.6]",
          isUser
            ? cn(
                "max-w-[80%] rounded-[14px_14px_4px_14px]",
                "bg-primary text-primary-foreground shadow-md",
                "whitespace-pre-wrap",
              )
            : cn(
                "max-w-[85%] rounded-[14px_14px_14px_4px]",
                "bg-white/45 backdrop-blur-[8px] saturate-[120%]",
                "border border-[rgba(220,199,167,0.10)]",
                "dark:bg-[rgba(26,20,15,0.40)] dark:border-[rgba(90,70,48,0.12)]",
                "text-foreground shadow-sm",
              ),
        )}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="prose prose-warm max-w-none prose-p:my-1.5 prose-p:leading-[1.6] prose-headings:my-3 prose-pre:my-3 prose-pre:rounded-[10px] prose-pre:bg-surface-sunken prose-code:text-[13px] prose-code:font-medium prose-li:my-0.5">
            {message.content ? (
              <Markdown remarkPlugins={[remarkGfm]}>{message.content}</Markdown>
            ) : (
              <span className="text-muted-foreground">...</span>
            )}
          </div>
        )}
      </div>

      {/* Citations below AI message */}
      {!isUser && message.citations && message.citations.length > 0 && (
        <div className="flex max-w-[85%] flex-wrap gap-1 mt-2">
          {message.citations.map((citation, i) => (
            <CitationBadge
              key={`${citation.file_path}-${citation.page_num}-${citation.paragraph_idx}`}
              citation={citation}
              index={i}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

### 15.4 Streaming Indicator

```tsx
// web/src/features/chat/streaming-indicator.tsx
export function StreamingIndicator() {
  return (
    <div className="flex items-center gap-1 mt-2" aria-label="Generating response">
      <span className="h-1.5 w-1.5 rounded-full bg-primary animate-[dot-pulse_1.4s_ease-in-out_infinite]" />
      <span className="h-1.5 w-1.5 rounded-full bg-primary animate-[dot-pulse_1.4s_ease-in-out_0.2s_infinite]" />
      <span className="h-1.5 w-1.5 rounded-full bg-primary animate-[dot-pulse_1.4s_ease-in-out_0.4s_infinite]" />
    </div>
  );
}
```

### 15.5 CitationBadge (migrated)

```tsx
// web/src/features/chat/citation-badge.tsx
import { FileText } from "lucide-react";
import { useState } from "react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import type { Citation } from "@/types/chat";

function getFileName(path: string): string {
  return path.split("/").pop() ?? path;
}

interface CitationBadgeProps {
  citation: Citation;
  index: number;
}

export function CitationBadge({ citation, index }: CitationBadgeProps) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          type="button"
          className={cn(
            "inline-flex items-center gap-1 rounded-sm border px-1.5 py-0.5",
            "text-[11px] font-medium text-muted-foreground",
            "bg-accent/40 border-border",
            "transition-[background-color,color] duration-150 ease-out",
            "hover:bg-accent hover:text-foreground",
            "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
            "outline-none",
          )}
        >
          <FileText className="h-3 w-3" />
          <span>{getFileName(citation.file_path)}</span>
          {citation.page_num > 0 && (
            <span className="text-muted-foreground">p.{citation.page_num}</span>
          )}
          <sup>{index + 1}</sup>
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-80" side="top">
        <div className="space-y-2 p-3">
          <p className="text-[12px] font-medium text-foreground">
            {citation.file_path}
          </p>
          {citation.page_num > 0 && (
            <p className="text-[12px] text-muted-foreground">
              Page {citation.page_num}, Paragraph {citation.paragraph_idx}
            </p>
          )}
          {citation.text_snippet && (
            <p className="rounded-[10px] bg-accent/30 p-2 text-[12px] leading-relaxed text-foreground">
              {citation.text_snippet}
            </p>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
```

---

## 16. Migration Mapping

### 16.1 Component Replacements

| # | Current File | Current Pattern | Target Component | Size/Variant |
|---|---|---|---|---|
| 1 | `session-list.tsx:15-21` | Inline ghost button (new chat) | `Button ghost icon-sm` | icon-sm |
| 2 | `session-list.tsx:42-50` | Inline destructive ghost button (delete) | `Button ghost icon-sm data-destructive` | icon-sm |
| 3 | `chat-area.tsx:47-53` | Inline primary button (New Chat) | `Button default default` | default |
| 4 | `chat-area.tsx:76-84` | Inline ghost button (Sources toggle) | `Button ghost sm` | sm |
| 5 | `chat-area.tsx:85-93` | Inline ghost button (New) | `Button ghost sm` | sm |
| 6 | `message-input.tsx:77-84` | Inline primary icon button (Send) | `Button default icon` | icon |
| 7 | `message-input.tsx:69-75` | Inline destructive icon button (Stop) | `Button destructive icon` | icon |
| 8 | `sources-panel.tsx:161-167` | Inline ghost button (Close) | `Button ghost icon-sm` | icon-sm |
| 9 | `sources-panel.tsx:180-185` | Inline ghost text button (Clear) | `Button ghost xs` | xs |
| 10 | `sources-panel.tsx:187-193` | Inline primary text button (Done) | `Button default xs` | xs |
| 11 | `chat-area.tsx:39-55` | Custom empty state (no session) | `EmptyState` | iconBackground, action |
| 12 | `chat-area.tsx:98-111` | Custom empty state (no messages) | `EmptyState` | iconBackground |
| 13 | `chat-area.tsx:126-129` | `Loader2` spinner (thinking) | `StreamingIndicator` | — |
| 14 | `message-bubble.tsx:29` | `animate-pulse` on AI bubble | Remove (use StreamingIndicator only) | — |

### 16.2 Glass Treatment Additions

| # | Current | Target |
|---|---|---|
| 1 | `bg-muted/30` (SessionList) | Glass-tier-thin classes |
| 2 | `border-r` (SessionList) | Glass border token |
| 3 | `border-b` (PanelHeader) | Glass border + ultra-thin glass |
| 4 | `bg-muted` (AI message) | Glass-tier-ultra-thin classes |
| 5 | `border-t bg-background` (MessageInput) | Glass border + ultra-thin glass |
| 6 | `border-l bg-background` (SourcesPanel) | Glass border + regular glass |

### 16.3 Style Changes

| # | Element | Current | Target |
|---|---|---|---|
| 1 | SessionItem radius | `rounded-md` (6px) | `rounded-[10px]` |
| 2 | SessionItem text | `text-sm` (14px) | `text-[14px]` (same, explicit) |
| 3 | User bubble radius | `rounded-lg` (8px) | `rounded-[14px_14px_4px_14px]` (asymmetric) |
| 4 | AI bubble radius | `rounded-lg` (8px) | `rounded-[14px_14px_14px_4px]` (asymmetric) |
| 5 | User bubble padding | `px-4 py-2.5` | `px-4 py-3` |
| 6 | AI bubble padding | `px-4 py-2.5` | `px-4 py-3` |
| 7 | PanelHeader height | `py-3` (~42px) | `h-12` (48px) |
| 8 | SessionList width | `w-52` | `w-52` (unchanged) |
| 9 | SourcesPanel width | `w-64` | `w-64` (unchanged) |
| 10 | Textarea in input | `rounded-md` (6px) | `rounded-[10px]` |
| 11 | Footer text | `text-[10px]` | `text-[12px]` (caption) |
| 12 | Active session | `bg-accent` | `bg-accent-muted` + left stripe |
| 13 | Citation badge text | `text-[10px]` | `text-[11px]` |

---

## Appendix A: Accessibility Checklist

| Check | SessionList | ChatArea | MessageBubble | MessageInput | SourcesPanel | CitationBadge |
|---|---|---|---|---|---|---|
| Landmark | `<aside aria-label="Chat sessions">` | `<main>` | — | — | `<aside aria-label="Sources">` | — |
| Keyboard nav | Tab through sessions, Enter to select | Tab through header buttons | — | Tab to textarea, Enter to send | Tab through tree items | Tab through badges, Enter opens popover |
| Focus indicator | `ring-2 ring-ring` on session items | `ring-2 ring-ring` on buttons | — | `ring-2 ring-ring` on textarea | `ring-2 ring-ring` on checkboxes | `ring-2 ring-ring` on badge trigger |
| Screen reader | Active session `aria-current="true"` | Empty state title/description | User/AI role context via `aria-label` | `aria-label="Message input"` | Checkbox state announced | Popover content announced |
| Color contrast | #2B2116 on glass-bg ≥AA | #2B2116 on amber ≥AAA | #2B2116 on primary ≥AAA, #F8F1E7 on glass ≥AA | #2B2116 on surface-base ≥AAA | #2B2116 on glass ≥AA | #78624B on glass-bg ≥AA |
| Reduced motion | Session hover: instant | Streaming dots: static | No pulse animation | — | — | Popover: fade only |
| Touch targets | Session items: ≥36px height | Header buttons: ≥32px | — | Send/Stop: 36px | Tree items: ≥32px, checkboxes 18px | Badge: ≥22px height |

---

## Appendix B: Token Cross-Reference

### Color Tokens

| Token | Tailwind Class | Used In |
|---|---|---|
| `--color-primary` | `bg-primary`, `text-primary` | User bubble bg, active stripe, streaming dots, send button |
| `--color-primary-foreground` | `text-primary-foreground` | User bubble text, send button text |
| `--color-primary-hover` | `bg-primary-hover` | Send button hover |
| `--color-foreground` | `text-foreground` | AI bubble text, session items, panel header title |
| `--color-muted-foreground` | `text-muted-foreground` | Session item default, footer, source context, streaming "Thinking" |
| `--color-accent` | `bg-accent` | Session item hover, citation badge hover, tree item hover |
| `--color-accent-muted` | `bg-accent-muted` | Active session item background |
| `--color-accent-foreground` | `text-accent-foreground` | Session item hover text |
| `--color-destructive` | `bg-destructive` | Stop button |
| `--color-destructive-foreground` | `text-destructive-foreground` | Stop button text |
| `--color-surface-base` | `bg-surface-base` | Textarea background |
| `--color-surface-sunken` | `bg-surface-sunken` | Code block background |
| `--color-border` | `border-border` | Textarea border, citation badge border |
| `--color-ring` | `ring-ring` | Focus rings |
| `--color-status-error` | `text-status-error` | AlertBanner error stripe/icon |
| `--color-status-error-bg` | `bg-status-error-bg` | AlertBanner error background |

### Glass Tier References

| Element | Tier | Light BG | Dark BG | Light Border | Dark Border |
|---|---|---|---|---|---|
| SessionList | thin | `white/55` | `[26,20,15]/60` | `white/35` | `white/10` |
| PanelHeader | ultra-thin | `white/45` | `[26,20,15]/50` | `white/35` | `white/10` |
| AI message | ultra-thin | `[255,249,242]/45` | `[26,20,15]/40` | `[220,199,167]/10` | `[90,70,48]/12` |
| MessageInput | ultra-thin | `white/45` | `[26,20,15]/50` | `white/35` | `white/10` |
| SourcesPanel | regular | `white/65` | `[26,20,15]/70` | `white/40` | `white/12` |
| Citation popover | thin | `white/55` | `[26,20,15]/60` | `white/35` | `white/10` |

---

## Appendix C: Implementation Checklist

### Phase 1: Token Infrastructure
- [ ] Add `.prose-warm` CSS custom properties to `globals.css`
- [ ] Add `@keyframes dot-pulse` to `globals.css`
- [ ] Verify glass tier CSS utilities are in place
- [ ] Add `.glass-border` utility class

### Phase 2: Component Migration — SessionList
- [ ] Replace inline new-chat button → `Button ghost icon-sm`
- [ ] Replace inline delete button → `Button ghost icon-sm data-destructive`
- [ ] Apply glass-tier-thin to SessionList root
- [ ] Add active session stripe (`::before` pseudo-element)
- [ ] Update session item radius to `rounded-[10px]`
- [ ] Update footer text size to 12px (caption)
- [ ] Wrap session items in `ScrollArea` component

### Phase 3: Component Migration — ChatArea
- [ ] Apply glass-tier-ultra-thin to PanelHeader
- [ ] Replace inline header buttons → `Button ghost sm`
- [ ] Replace custom empty states → `EmptyState` component
- [ ] Replace `Loader2` spinner → `StreamingIndicator` component
- [ ] Remove `animate-pulse` from AI message bubble during streaming
- [ ] Update PanelHeader height to `h-12`

### Phase 4: Component Migration — MessageBubble
- [ ] Apply glass-tier-ultra-thin to AI bubble (replace `bg-muted`)
- [ ] Apply asymmetric corner radii to both bubble types
- [ ] Replace `prose prose-sm` → `prose prose-warm` with warm token overrides
- [ ] Move citations inside AI bubble container

### Phase 5: Component Migration — MessageInput
- [ ] Apply glass-tier-ultra-thin to input bar
- [ ] Replace inline send button → `Button default icon`
- [ ] Replace inline stop button → `Button destructive icon`
- [ ] Update textarea radius to `rounded-[10px]`
- [ ] Style source context indicator with caption typography

### Phase 6: Component Migration — SourcesPanel
- [ ] Apply glass-tier-regular to SourcesPanel root
- [ ] Replace inline close button → `Button ghost icon-sm`
- [ ] Replace inline Clear button → `Button ghost xs`
- [ ] Replace inline Done button → `Button default xs`
- [ ] Update tree item indentation to `depth × 16px`

### Phase 7: Component Migration — CitationBadge
- [ ] Update badge styling: `text-[11px]`, `bg-accent/40`, `border-border`
- [ ] Update popover content with warm surface styling
- [ ] Ensure Popover uses glass-tier-thin from spec

### Phase 8: Responsive Behavior
- [ ] Add mobile SessionList → Sheet (left side)
- [ ] Add mobile SourcesPanel → Sheet (right side)
- [ ] Add tablet SessionList collapsed state (w-14)
- [ ] Add responsive PanelHeader (hamburger on mobile)

### Phase 9: Visual QA
- [ ] Light mode: warm mesh visible through glass surfaces
- [ ] Dark mode: candlelight glow visible through glass
- [ ] User bubbles: solid amber, high contrast in both modes
- [ ] AI bubbles: readable prose on glass in both modes
- [ ] Code blocks: readable on surface-sunken in both modes
- [ ] Streaming indicator: visible, warm amber, not distracting
- [ ] Citation badges: readable, popover content clear
- [ ] Session active state: stripe + background clearly visible
- [ ] Empty states: centered, properly spaced
- [ ] Mobile: full-width chat, sheets work correctly
- [ ] All focus rings visible
- [ ] `prefers-reduced-motion` tested

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
