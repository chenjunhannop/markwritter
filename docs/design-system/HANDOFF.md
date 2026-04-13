# Liquid Crystal — Warm Amber · Design System Handoff

> **Single source of truth for implementation.** Every token, component, surface, and migration item consolidated from 10 design documents (13 687 lines).

---

## 1 · Executive Summary

| Field | Value |
|---|---|
| **System name** | Liquid Crystal — Warm Amber |
| **Version** | 1.0-draft |
| **Scope** | Full desktop + responsive web app (chat, explore, record, query, skills, settings) |
| **Components** | 22 fully specified (Button, Badge, Input, Textarea, Checkbox, Select, SegmentedControl, Switch, Card, Dialog, Sheet, Popover, Tooltip, Tabs, Separator, Avatar, ScrollArea, Skeleton, Progress, AlertBanner, EmptyState, BackgroundMesh) |
| **Pages** | 5 (Chat, Explore, Settings, Record, Query+Skills) |
| **Layout primitives** | 4 (AppLayout, Sidebar, Header, MobileDrawer) |
| **Source documents** | 10 |
| **Total source lines** | 13 687 |
| **Foundation tokens** | ~140 (colors, radius, shadow, glass, spacing, motion, z-index, breakpoints, typography) |

### Document Map

| # | Document | Lines | Purpose |
|---|---|---|---|
| 1 | `tokens.md` | 713 | Foundation tokens — colors, typography, radius, shadows, glass tiers, spacing, motion, z-index, breakpoints |
| 2 | `components-button-badge.md` | 855 | Button (6 variants × 6 sizes + loading) and Badge (8 variants) |
| 3 | `components-form-inputs.md` | 1 478 | Input, Textarea, Checkbox, Select, SegmentedControl, Switch; native element migration |
| 4 | `components-surface-overlay.md` | 1 763 | Card, Dialog, Sheet, Popover, Tooltip, Tabs, Separator; **authoritative** radius / glass / shadow updates |
| 5 | `components-feedback-utility.md` | 1 319 | Avatar, ScrollArea, Skeleton, Progress, AlertBanner, EmptyState; hardcoded color audit |
| 6 | `layout-shell.md` | 948 | BackgroundMesh, Sidebar, Header, MobileDrawer, AppLayout, responsive breakpoints |
| 7 | `page-chat.md` | 1 643 | Chat — SessionList, ChatArea, MessageBubble, MessageInput, SourcesPanel, Citation, StreamingIndicator |
| 8 | `page-explore.md` | 781 | Explore — SearchBar, StatsPill, LegendPanel, GraphNode, NodeDetailPanel, MiniMap, ControlsShell |
| 9 | `page-settings.md` | 1 612 | Settings — General, LLM, Vault, Advanced tabs; form patterns; native element migrations |
| 10 | `page-record-query-skills.md` | 2 575 | Record (FileTree, NoteEditor, AIAssist, DiffPreview), Query (Search, ResultCard), Skills (SkillCard, SkillRunDialog) |

---

## 2 · Token Registry

### 2.1 Color Tokens (Light / Dark)

> **Authoritative source**: `tokens.md §1` + overrides from `components-surface-overlay.md §1.7`.
> Any token listed below that also appears in `components-surface-overlay.md` with updated values uses the **updated** value.

#### Core

| Token | Light | Dark | Source |
|---|---|---|---|
| `--color-bg` | `oklch(0.99 0.005 85)` | `oklch(0.145 0.008 85)` | tokens.md §1.1 |
| `--color-bg-subtle` | `oklch(0.965 0.006 85)` | `oklch(0.185 0.01 85)` | tokens.md §1.1 |
| `--color-surface-base` | `rgba(255,255,255,0.72)` | `rgba(20,18,16,0.72)` | tokens.md §1.2 |
| `--color-surface-raised` | `rgba(255,255,255,0.82)` | `rgba(28,26,24,0.82)` | tokens.md §1.2 |
| `--color-surface-sunken` | `rgba(0,0,0,0.03)` | `rgba(0,0,0,0.2)` | tokens.md §1.2 |
| `--color-border` | `rgba(0,0,0,0.08)` | `rgba(255,255,255,0.08)` | tokens.md §1.3 |
| `--color-border-strong` | `rgba(0,0,0,0.15)` | `rgba(255,255,255,0.15)` | tokens.md §1.3 |
| `--color-border-subtle` | `rgba(0,0,0,0.04)` | `rgba(255,255,255,0.04)` | tokens.md §1.3 |
| `--color-text` | `oklch(0.22 0.02 60)` | `oklch(0.92 0.01 85)` | tokens.md §1.4 |
| `--color-text-secondary` | `oklch(0.45 0.02 60)` | `oklch(0.68 0.02 85)` | tokens.md §1.4 |
| `--color-text-tertiary` | `oklch(0.62 0.015 60)` | `oklch(0.52 0.015 85)` | tokens.md §1.4 |
| `--color-text-inverse` | `oklch(0.98 0.005 85)` | `oklch(0.12 0.01 85)` | tokens.md §1.4 |

#### Accent

| Token | Light | Dark | Source |
|---|---|---|---|
| `--color-accent` | `#C67B4A` | `#D4915C` | tokens.md §1.1 |
| `--color-accent-hover` | `#B56A3B` | `#E0A06E` | tokens.md §1.1 |
| `--color-accent-muted` | `rgba(198,123,74,0.12)` | `rgba(212,145,92,0.15)` | ⚠️ implied by surface-overlay & page docs — **not in tokens.md color table** |
| `--color-accent-subtle` | `rgba(198,123,74,0.08)` | `rgba(212,145,92,0.10)` | tokens.md §1.1 |
| `--color-accent-text` | `#9B5E35` | `#E8B088` | tokens.md §1.1 |

#### Semantic / Status

| Token | Light | Dark | Source |
|---|---|---|---|
| `--color-success` | `#6B9B5E` | `#7DAF6E` | tokens.md §1.5 |
| `--color-success-bg` | `rgba(107,155,94,0.10)` | `rgba(125,175,110,0.12)` | tokens.md §1.5 |
| `--color-warning` | `#D4915C` | `#E6A23C` | tokens.md §1.5 |
| `--color-warning-bg` | `rgba(212,145,92,0.10)` | `rgba(230,162,60,0.12)` | tokens.md §1.5 |
| `--color-error` | `#C75050` | `#D96060` | tokens.md §1.5 |
| `--color-error-bg` | `rgba(199,80,80,0.10)` | `rgba(217,96,96,0.12)` | tokens.md §1.5 |
| `--color-info` | `#5B8DB5` | `#6B9EC7` | tokens.md §1.5 |
| `--color-info-bg` | `rgba(91,141,181,0.10)` | `rgba(107,158,199,0.12)` | tokens.md §1.5 |

#### Chart / Node

| Token | Light | Dark | Source |
|---|---|---|---|
| `--color-chart-node-person` | `#6B8DB5` | `#5B7DA5` | feedback-utility §6 (proposed) |
| `--color-chart-node-topic` | `#6D9B5E` | `#5D8B4E` | feedback-utility §6 (proposed) |
| `--color-chart-node-concept` | `#9B7B8E` | `#8B6B7E` | feedback-utility §6 (proposed) |
| `--color-chart-node-note` | `#E6A23C` | `#D4922C` | feedback-utility §6 (proposed) |

### 2.2 Radius Tokens

> ⚠️ **CONTRADICTION**: `tokens.md §3` defines smaller values; `components-surface-overlay.md §1.7` defines **updated** larger values and marks them **authoritative**. All component/page specs reference the **updated** values. Use the **updated** values.

| Token | Updated Value (authoritative) | Original Value (tokens.md) | Source |
|---|---|---|---|
| `--radius-sm` | `10px` | `6px` | surface-overlay §1.7 ✅ |
| `--radius-md` | `14px` | `8px` | surface-overlay §1.7 ✅ |
| `--radius-lg` | `18px` | `12px` | surface-overlay §1.7 ✅ |
| `--radius-xl` | `22px` | `16px` | surface-overlay §1.7 ✅ |
| `--radius-2xl` | `28px` | `—` | surface-overlay §1.7 (new) |
| `--radius-full` | `9999px` | `9999px` | tokens.md §3 |

### 2.3 Shadow Tokens

> ⚠️ **DUAL SYSTEM**: `tokens.md §5` defines `shadow-sm/md/lg/xl`. `components-surface-overlay.md §1.7` introduces semantic tokens `shadow-resting/elevated/dragging`. Both are used. Implement both.

| Token | Value | Source |
|---|---|---|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.04)` | tokens.md §5 |
| `--shadow-md` | `0 4px 12px rgba(0,0,0,0.06)` | tokens.md §5 |
| `--shadow-lg` | `0 8px 24px rgba(0,0,0,0.08)` | tokens.md §5 |
| `--shadow-xl` | `0 16px 48px rgba(0,0,0,0.12)` | tokens.md §5 |
| `--shadow-resting` | `0 2px 8px rgba(0,0,0,0.04), 0 0 1px rgba(0,0,0,0.06)` | surface-overlay §1.7 |
| `--shadow-elevated` | `0 12px 32px rgba(0,0,0,0.10), 0 0 1px rgba(0,0,0,0.08)` | surface-overlay §1.7 |
| `--shadow-dragging` | `0 20px 52px rgba(0,0,0,0.16), 0 0 1px rgba(0,0,0,0.10)` | surface-overlay §1.7 |

### 2.4 Glass Tier Tokens

> ⚠️ **CONTRADICTION**: `tokens.md §6.1` defines original 4-tier values. `components-surface-overlay.md §1.7` defines **updated** values. All component/page specs use the **updated** values. Use the **updated** values.

| Tier | Updated Blur | Updated Light Alpha | Updated Dark Alpha | Original Blur (tokens.md) | Original Alpha |
|---|---|---|---|---|---|
| `glass-ultra-thin` | `blur(8px)` | `0.45` / `0.40` | `0.45` / `0.40` | blur(8px) | same |
| `glass-thin` | `blur(16px)` | `0.55` / `0.60` | `0.55` / `0.60` | blur(12px) | 0.58 / 0.52 |
| `glass-regular` | `blur(24px)` | `0.65` / `0.70` | `0.65` / `0.70` | blur(20px) | 0.72 / 0.64 |
| `glass-thick` | `blur(40px)` | `0.78` / `0.80` | `0.78` / `0.80` | blur(28px) | 0.84 / 0.78 |

### 2.5 Spacing Scale

| Token | Value | Source |
|---|---|---|
| `--space-0` | `0px` | tokens.md §7 |
| `--space-1` | `4px` | tokens.md §7 |
| `--space-2` | `8px` | tokens.md §7 |
| `--space-3` | `12px` | tokens.md §7 |
| `--space-4` | `16px` | tokens.md §7 |
| `--space-5` | `20px` | tokens.md §7 |
| `--space-6` | `24px` | tokens.md §7 |
| `--space-8` | `32px` | tokens.md §7 |
| `--space-10` | `40px` | tokens.md §7 |
| `--space-12` | `48px` | tokens.md §7 |
| `--space-16` | `64px` | tokens.md §7 |
| `--space-20` | `80px` | tokens.md §7 |

### 2.6 Typography Scale

| Token | Size | Weight | Line Height | Source |
|---|---|---|---|---|
| `--text-xs` | `11px` | 500 | 16px | tokens.md §4 |
| `--text-sm` | `13px` | 400 | 18px | tokens.md §4 |
| `--text-base` | `15px` | 400 | 22px | tokens.md §4 |
| `--text-lg` | `17px` | 500 | 24px | tokens.md §4 |
| `--text-xl` | `20px` | 600 | 28px | tokens.md §4 |
| `--text-2xl` | `24px` | 600 | 32px | tokens.md §4 |
| `--text-3xl` | `30px` | 700 | 36px | tokens.md §4 |
| `--text-4xl` | `36px` | 700 | 40px | tokens.md §4 |

### 2.7 Motion Tokens

| Token | Value | Source |
|---|---|---|
| `--duration-instant` | `100ms` | tokens.md §8 |
| `--duration-fast` | `180ms` | tokens.md §8 |
| `--duration-normal` | `280ms` | tokens.md §8 |
| `--duration-slow` | `420ms` | tokens.md §8 |
| `--duration-gentle` | `600ms` | tokens.md §8 |
| `--ease-default` | `cubic-bezier(0.25, 0.1, 0.25, 1)` | tokens.md §8 |
| `--ease-spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | tokens.md §8 |
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | tokens.md §8 |

### 2.8 Z-Index Scale

| Token | Value | Source |
|---|---|---|
| `--z-base` | `0` | tokens.md §9 |
| `--z-dropdown` | `100` | tokens.md §9 |
| `--z-sticky` | `200` | tokens.md §9 |
| `--z-overlay` | `300` | tokens.md §9 |
| `--z-modal` | `400` | tokens.md §9 |
| `--z-popover` | `500` | tokens.md §9 |
| `--z-toast` | `600` | tokens.md §9 |
| `--z-tooltip` | `700` | tokens.md §9 |
| `--z-max` | `9999` | tokens.md §9 |
| `--z-content` | `⚠️ used but not defined` | page-explore §2.4, page-record §1.4 |

### 2.9 Breakpoints

| Token | Value | Source |
|---|---|---|
| `--bp-sm` | `640px` | tokens.md §10 |
| `--bp-md` | `768px` | tokens.md §10 |
| `--bp-lg` | `1024px` | tokens.md §10 |
| `--bp-xl` | `1280px` | tokens.md §10 |
| `--bp-2xl` | `1536px` | tokens.md §10 |

### Token Count Summary

| Category | Count |
|---|---|
| Color tokens (core + accent + status + chart) | ~38 |
| Radius tokens | 6 |
| Shadow tokens | 7 |
| Glass tier tokens | 4 |
| Spacing tokens | 12 |
| Typography tokens | 8 |
| Motion tokens | 8 |
| Z-index tokens | 9 (+ 1 undefined) |
| Breakpoint tokens | 5 |
| **Total unique tokens** | **~98** |

---

## 3 · Component Inventory

| Component | Document Location | Variant Count | State Coverage | New / Existing |
|---|---|---|---|---|
| **Button** | components-button-badge.md | 6 variants (default, accent, ghost, subtle, destructive, link) × 6 sizes (xs–2xl) + loading state | default, hover, active, disabled, focus, loading | New |
| **Badge** | components-button-badge.md | 8 variants (default, accent, outline, ghost, success, warning, error, info) | default, with-icon | New |
| **Input** | components-form-inputs.md | default, with-prefix, with-suffix, with-both, textarea-mode | default, hover, focus, disabled, error, filled | New |
| **Textarea** | components-form-inputs.md | default, auto-resize | default, hover, focus, disabled, error | New |
| **Checkbox** | components-form-inputs.md | default, with-description | unchecked, checked, indeterminate, disabled, focus | New |
| **Select** | components-form-inputs.md | default, with-search | default, hover, focus, disabled, error, open | New |
| **SegmentedControl** | components-form-inputs.md | default, on-glass | default, selected, hover, focus | New |
| **Switch** | components-form-inputs.md | default, with-label, with-description | off, on, disabled, focus | New |
| **Card** | components-surface-overlay.md | default, elevated, interactive, on-glass, static | default, hover, active, focus | New |
| **Dialog** | components-surface-overlay.md | default, confirmation, form, side-panel | default, open-transition, close-transition | New |
| **Sheet** | components-surface-overlay.md | right (default), left, bottom | default, open, close, drag | New |
| **Popover** | components-surface-overlay.md | default, with-actions, form | default, hover-trigger, click-trigger | New |
| **Tooltip** | components-surface-overlay.md | default, inverted, rich | default, visible | New |
| **Tabs** | components-surface-overlay.md | default, pill, on-glass | default, selected, hover, disabled | New |
| **Separator** | components-surface-overlay.md | horizontal, vertical | default | New |
| **Avatar** | components-feedback-utility.md | default, with-status, group | default | New |
| **ScrollArea** | components-feedback-utility.md | default, thin | default, hover, scrolling | New |
| **Skeleton** | components-feedback-utility.md | text, circular, rectangular, card | default, pulse-animation | New |
| **Progress** | components-feedback-utility.md | linear, circular | default, indeterminate, success, error | New |
| **AlertBanner** | components-feedback-utility.md | info, success, warning, error | default, dismiss | New |
| **EmptyState** | components-feedback-utility.md | default, with-action, compact | default | New |
| **BackgroundMesh** | layout-shell.md | default (warm amber gradient) | animated | New |

**Total: 22 components, all new.**

---

## 4 · Glass Tier Master Map

| Surface | Glass Tier | Usage Context | Source |
|---|---|---|---|
| TabsList | ultra-thin | Chat input tabs, Explore filter tabs | surface-overlay §4, page-chat §3.4 |
| PanelHeader (Chat) | ultra-thin | SourcesPanel header, ChatArea header | page-chat §2.2, §3.2 |
| TitleBar (Record) | ultra-thin | NoteEditor top bar | page-record §1.3 |
| MessageInput bar | ultra-thin | Chat message compose area | page-chat §3.5 |
| AI message bubbles | ultra-thin | Bot responses in chat | page-chat §3.3 |
| Tooltip | ultra-thin (exception: solid inverted) | All tooltip surfaces | surface-overlay §5 |
| EmptyState icon bg | ultra-thin | All empty state illustrations | feedback-utility §6 |
| LegendPanel (Explore) | ultra-thin | Graph legend overlay | page-explore §2.4 |
| StatsPill (Explore) | ultra-thin | Graph statistics pills | page-explore §2.2 |
| SegmentedControl (on glass) | ultra-thin | Explore filter controls | form-inputs §5, page-explore §2.1 |
| Input (on glass) | ultra-thin | Explore search bar on glass | form-inputs §1, page-explore §2.1 |
| DiffPreview code area | ultra-thin | Record page diff viewer | page-record §1.5 |
| Output area (Skills) | ultra-thin | Skill execution output | page-skills §3 |
| AlertBanner | ultra-thin | All alert banner surfaces | feedback-utility §5 |
| **Card (default)** | **thin** | All default card surfaces | surface-overlay §1 |
| SessionList | thin | Chat session list container | page-chat §2.1 |
| FileTreePanel | thin | Record file tree sidebar | page-record §1.1 |
| Popover | thin | All popover surfaces | surface-overlay §3 |
| Select dropdown | thin | Select open state dropdown | form-inputs §4 |
| SearchBar (Explore) | thin | Graph search container | page-explore §2.1 |
| MiniMapShell (Explore) | thin | Graph minimap container | page-explore §2.6 |
| ControlsShell (Explore) | thin | Graph zoom/controls container | page-explore §2.7 |
| ResultCard (Query) | thin | Search result cards | page-query §2 |
| SkillCard | thin | Skill listing cards | page-skills §1 |
| Citation popover | thin | Chat citation popover | page-chat §3.6 |
| **Card (elevated)** | **regular** | Elevated card hover state | surface-overlay §1 |
| SourcesPanel | regular | Chat sources sidebar | page-chat §4 |
| AIAssistPanel | regular | Record AI assist panel | page-record §1.4 |
| NodeDetailPanel (Explore) | regular | Graph node detail sidebar | page-explore §2.5 |
| MobileDrawer | regular | Mobile navigation drawer | layout-shell §5 |
| Sidebar | regular | Main navigation sidebar | layout-shell §3 |
| **Dialog** | **thick** | All modal dialogs | surface-overlay §2 |
| **Sheet** | **regular** ⚠️ | Side sheets — see note below | surface-overlay §2 |
| SkillRunDialog | thick | Skill execution dialog | page-skills §3 |
| Header | thick | App header bar | layout-shell §4 |

### ⚠️ Contradiction: Sheet Glass Tier

- `components-surface-overlay.md §2` specs Sheet as **regular** glass.
- Sidebar interaction patterns in `layout-shell.md §3` reference Sheet behavior with **regular** glass.
- `page-settings.md` and `page-chat.md` reference Sheet overlays for mobile — consistent with regular.
- **Resolution**: Sheet = **regular**. No actual contradiction in usage; the spec is consistent.

---

## 5 · Hardcoded Color Master Migration

### 5.1 From Feedback-Utility Audit (feedback-utility §6)

| Current File:Line Pattern | Current Value | Replacement Token | Document Source |
|---|---|---|---|
| Avatar fallback bg | `hsl(var(--muted))` | `--color-surface-raised` | feedback-utility §6 |
| Avatar status online | `bg-green-500` | `--color-success` | feedback-utility §6 |
| Avatar status busy | `bg-red-500` | `--color-error` | feedback-utility §6 |
| Avatar status offline | `bg-gray-400` | `--color-text-tertiary` | feedback-utility §6 |
| Skeleton base | `bg-muted animate-pulse` | `--color-surface-base` + custom pulse keyframe | feedback-utility §6 |
| Skeleton shimmer | `bg-gradient-to-r from-transparent via-white/20 to-transparent` | `--color-surface-raised` with alpha mask | feedback-utility §6 |
| Progress track | `bg-secondary` | `--color-surface-sunken` | feedback-utility §6 |
| Progress fill default | `bg-primary` | `--color-accent` | feedback-utility §6 |
| Progress fill success | `bg-green-500` | `--color-success` | feedback-utility §6 |
| Progress fill error | `bg-red-500` | `--color-error` | feedback-utility §6 |
| Alert info bg | `bg-blue-50 dark:bg-blue-950` | `--color-info-bg` | feedback-utility §6 |
| Alert success bg | `bg-green-50 dark:bg-green-950` | `--color-success-bg` | feedback-utility §6 |
| Alert warning bg | `bg-amber-50 dark:bg-amber-950` | `--color-warning-bg` | feedback-utility §6 |
| Alert error bg | `bg-red-50 dark:bg-red-950` | `--color-error-bg` | feedback-utility §6 |
| Alert info icon | `text-blue-600` | `--color-info` | feedback-utility §6 |
| Alert success icon | `text-green-600` | `--color-success` | feedback-utility §6 |
| Alert warning icon | `text-amber-600` | `--color-warning` | feedback-utility §6 |
| Alert error icon | `text-red-600` | `--color-error` | feedback-utility §6 |

### 5.2 From Button-Badge Audit (button-badge §7)

| Element | Current Pattern | Replacement |
|---|---|---|
| Inline action buttons (14 identified) | Raw `<button>` with Tailwind utility classes | `<Button variant="ghost" size="xs">` or appropriate variant |
| Icon-only actions | `<button className="...">` | `<Button variant="ghost" size="icon-sm">` |

### 5.3 Explore Node Colors

| Node Type | Current Hardcoded | Proposed Token | Source |
|---|---|---|---|
| Person | `#3b82f6` (blue-500) | `--color-chart-node-person` → `#6B8DB5` | page-explore §3, feedback-utility §6 |
| Topic | `#22c55e` (green-500) | `--color-chart-node-topic` → `#6D9B5E` | page-explore §3, feedback-utility §6 |
| Concept | `#a855f7` (purple-500) | `--color-chart-node-concept` → `#9B7B8E` | page-explore §3, feedback-utility §6 |
| Note | `#f59e0b` (amber-500) | `--color-chart-node-note` → `#E6A23C` | page-explore §3, feedback-utility §6 |

### 5.4 Settings Page Hardcoded

| Element | Current Pattern | Replacement |
|---|---|---|
| Settings status dot (online) | `bg-green-500` | `--color-success` |
| Settings status dot (error) | `bg-red-500` | `--color-error` |
| Settings badge (vault count) | `bg-primary/10 text-primary` | `--color-accent-subtle` + `--color-accent-text` |
| Settings badge (model) | `bg-muted text-muted-foreground` | `--color-surface-raised` + `--color-text-secondary` |

### 5.5 Mesh Gradient Format

| Location | Current Format | Recommended |
|---|---|---|
| tokens.md §2 | `rgba()` values | Keep for CSS compatibility |
| layout-shell.md §2.2 | `oklch()` values | Standardize to `rgba()` for widest browser support |
| **Decision** | Use `rgba()` everywhere; oklch is visually equivalent but less supported | |

**Total hardcoded items to migrate: ~40**

---

## 6 · Native Element Replacement Master List

### 6.1 `<select>` → Select Component

| Location | Current Element | Replacement | Source |
|---|---|---|---|
| Settings → General → Theme selector | `<select>` | `<Select>` with search disabled | page-settings §2.2 |
| Settings → General → Language selector | `<select>` | `<Select>` with search disabled | page-settings §2.2 |
| Settings → LLM → Model selector | `<select>` | `<Select>` with search enabled | page-settings §3.2 |
| Settings → LLM → Temperature preset selector | `<select>` | `<Select>` with search disabled | page-settings §3.3 |

### 6.2 `<input type="radio">` → SegmentedControl

| Location | Current Element | Replacement | Source |
|---|---|---|---|
| Settings → LLM → Context scope | `<input type="radio">` group | `<SegmentedControl>` | page-settings §3.2 |

### 6.3 Checkbox → Switch

| Location | Current Element | Replacement | Source |
|---|---|---|---|
| Settings → Advanced → Hardware acceleration | `<Checkbox>` | `<Switch>` with description | page-settings §5.2 |
| Settings → Advanced → Auto-update | `<Checkbox>` | `<Switch>` with description | page-settings §5.2 |

### 6.4 Inline `<button>` → Button Component

| Location | Count | Replacement Variant | Source |
|---|---|---|---|
| Chat → Message actions (copy, regen, etc.) | 4 | `<Button variant="ghost" size="xs">` | page-chat §3.3 |
| Chat → Panel header actions | 2 | `<Button variant="ghost" size="xs">` | page-chat §2.2 |
| Record → Note editor toolbar | 3 | `<Button variant="ghost" size="xs">` | page-record §1.3 |
| Query → Result card actions | 2 | `<Button variant="ghost" size="xs">` | page-query §2 |
| Skills → Skill card actions | 2 | `<Button variant="ghost" size="xs">` | page-skills §1 |
| Explore → Node detail actions | 1 | `<Button variant="ghost" size="xs">` | page-explore §2.5 |

**Total native replacements: 4 selects + 1 radio group + 2 checkbox→switch + 14 inline buttons = 21 items**

---

## 7 · Implementation Priority Guide

### Phase 0 — Token Foundation (Est: 2–3 days)

**Goal**: All tokens in CSS, no hardcoded values in globals.

| Task | Effort | Depends On |
|---|---|---|
| Add all token CSS custom properties to `globals.css` `@theme` block | 1 day | — |
| Resolve radius contradiction → use updated (surface-overlay) values | 0.5 hr | Decision |
| Resolve glass tier contradiction → use updated (surface-overlay) values | 0.5 hr | Decision |
| Add `shadow-resting`, `shadow-elevated`, `shadow-dragging` tokens | 0.5 hr | — |
| Define missing tokens: `--color-accent-muted`, `--z-content`, `--color-status-*-bg`, `--color-surface-base/raised/sunken` | 1 hr | — |
| Add `--radius-2xl` token | 15 min | — |
| Verify mesh gradient uses `rgba()` consistently | 1 hr | — |

### Phase 1 — Layout Shell (Est: 3–4 days)

**Goal**: App chrome renders with glass surfaces and BackgroundMesh.

| Task | Effort | Depends On |
|---|---|---|
| Implement BackgroundMesh component with animated gradient | 1 day | Phase 0 tokens |
| Implement AppLayout (Sidebar + Header + content area) | 1 day | BackgroundMesh |
| Implement Sidebar with glass-regular surface | 0.5 day | AppLayout |
| Implement Header with glass-thick surface | 0.5 day | AppLayout |
| Implement MobileDrawer with glass-regular surface | 0.5 day | Sidebar |
| Responsive breakpoints (desktop/tablet/mobile) | 0.5 day | AppLayout |

### Phase 2 — Core Components (Est: 5–7 days)

**Goal**: All 22 components implemented with full variant/state/dark-mode support.

| Priority | Component | Est. | Depends On |
|---|---|---|---|
| 🔴 | Button | 1 day | Phase 0 tokens |
| 🔴 | Badge | 0.5 day | — |
| 🔴 | Input | 1 day | — |
| 🔴 | Textarea | 0.5 day | Input |
| 🔴 | Card | 0.5 day | Glass tokens |
| 🔴 | Separator | 0.5 hr | — |
| 🟡 | Select | 1 day | Input, Popover |
| 🟡 | Checkbox | 0.5 day | — |
| 🟡 | Switch | 0.5 day | — |
| 🟡 | SegmentedControl | 0.5 day | — |
| 🟡 | Tabs | 0.5 day | — |
| 🟡 | Tooltip | 0.5 day | — |
| 🟡 | Popover | 1 day | Card |
| 🟡 | ScrollArea | 0.5 day | — |
| 🟢 | Dialog | 1 day | Card, Button |
| 🟢 | Sheet | 0.5 day | Dialog |
| 🟢 | Avatar | 0.5 day | — |
| 🟢 | Skeleton | 0.5 day | — |
| 🟢 | Progress | 0.5 day | — |
| 🟢 | AlertBanner | 0.5 day | — |
| 🟢 | EmptyState | 0.5 day | — |

### Phase 3 — Page Assembly (Est: 6–8 days)

| Page | Est. | Depends On |
|---|---|---|
| Chat (SessionList, ChatArea, MessageBubble, MessageInput, SourcesPanel, Citation, StreamingIndicator) | 2 days | Phase 1 + 2 |
| Settings (General, LLM, Vault, Advanced tabs + native replacements) | 1.5 days | Phase 1 + 2 |
| Record (FileTreePanel, NoteEditor, AIAssistPanel, DiffPreview) | 1.5 days | Phase 1 + 2 |
| Query (SearchBar, ResultCard) | 1 day | Phase 1 + 2 |
| Skills (SkillCard, SkillRunDialog) | 1 day | Phase 1 + 2 |
| Explore (SearchBar, StatsPill, LegendPanel, GraphNode, NodeDetailPanel, MiniMap, ControlsShell, ReactFlow theming) | 2 days | Phase 1 + 2 |

### Phase 4 — Hardcoded Color Migration (Est: 2–3 days)

**Goal**: Zero hardcoded Tailwind color classes; all colors via tokens.

| Task | Effort | Source |
|---|---|---|
| Replace 18 feedback-utility hardcoded colors | 1 day | §5.1 above |
| Replace 14 inline buttons with Button component | 0.5 day | §5.2 above |
| Replace 4 explore node colors with chart tokens | 0.5 day | §5.3 above |
| Replace settings hardcoded badges/dots | 0.5 day | §5.4 above |
| Standardize mesh gradients to rgba() | 0.5 day | §5.5 above |

### Phase 5 — Native Element Migration (Est: 1–2 days)

| Task | Effort | Source |
|---|---|---|
| Replace 4 `<select>` → `<Select>` | 0.5 day | §6.1 above |
| Replace 1 radio group → `<SegmentedControl>` | 2 hr | §6.2 above |
| Replace 2 checkbox → `<Switch>` | 1 hr | §6.3 above |
| Replace 14 inline `<button>` → `<Button>` | 0.5 day | §6.4 above |

### Phase 6 — Polish & QA (Est: 2–3 days)

| Task | Effort |
|---|---|
| WCAG contrast audit across all pages | 1 day |
| Responsive testing (desktop, tablet, mobile) | 0.5 day |
| Dark mode visual QA | 0.5 day |
| Animation / motion QA | 0.5 day |
| Cross-browser testing (Chrome, Firefox, Safari) | 0.5 day |

### Total Estimated Timeline: 21–30 days (single developer)

---

## 8 · WCAG Contrast Report

### 8.1 Text on Background — Consolidated Matrix

| Text Token | On `--color-bg` (light) | On `--color-bg` (dark) | On Glass Ultra-Thin (light) | On Glass Ultra-Thin (dark) | Status |
|---|---|---|---|---|---|
| `--color-text` | ✅ ~14.5:1 | ✅ ~13.8:1 | ✅ | ✅ | PASS |
| `--color-text-secondary` | ✅ ~6.2:1 | ✅ ~5.8:1 | ✅ | ✅ | PASS |
| `--color-text-tertiary` | ⚠️ ~3.8:1 | ⚠️ ~3.5:1 | ⚠️ | ⚠️ | FAIL for small text (needs ≥4.5:1) |
| `--color-text-inverse` | ✅ (on accent bg) | ✅ (on accent bg) | ✅ | ✅ | PASS |
| `--color-accent-text` | ✅ ~5.5:1 | ✅ ~6.2:1 | ✅ | ✅ | PASS |

### 8.2 Status Colors on White/Dark Background

| Token | On White (light) | On Dark BG (dark) | WCAG AA Normal | WCAG AA Large |
|---|---|---|---|---|
| `--color-success` | ~3.8:1 | ~4.2:1 | ⚠️ FAIL | ✅ PASS |
| `--color-warning` | ~3.2:1 | ~3.8:1 | ⚠️ FAIL | ⚠️ FAIL |
| `--color-error` | ~5.0:1 | ~4.8:1 | ✅ PASS | ✅ PASS |
| `--color-info` | ~4.5:1 | ~4.2:1 | ✅ PASS | ✅ PASS |

### 8.3 Interactive States

| Element | State | Contrast Ratio | Status |
|---|---|---|---|
| Button default text on accent bg | default | ~4.8:1 | ✅ PASS |
| Button hover text on accent-hover bg | hover | ~5.2:1 | ✅ PASS |
| Ghost button text on bg | default | ~6.2:1 | ✅ PASS |
| Ghost button text on bg | hover (accent-muted bg) | ~5.8:1 | ✅ PASS |
| Badge text on badge bg | default | varies by variant | ⚠️ Audit per variant |
| Link text (`--color-accent-text`) | default | ~5.5:1 | ✅ PASS |

### 8.4 Known Failures & Remediation

| Issue | Current | Fix | Priority |
|---|---|---|---|
| `--color-text-tertiary` too low contrast | oklch(0.62) light / oklch(0.52) dark | Darken light to oklch(0.55), lighten dark to oklch(0.58) | 🔴 High |
| `--color-success` fails AA normal text | ~3.8:1 | Darken to `#5A8A4E` (~4.6:1) or only use with `--color-success-bg` for non-text | 🟡 Medium |
| `--color-warning` fails AA | ~3.2:1 | Darken to `#B87A40` (~4.5:1) for text; keep for icons/badges only | 🟡 Medium |
| Badge variant contrast | Not fully calculated | Per-variant audit needed before implementation | 🟡 Medium |

---

## 9 · Cross-Document Consistency Report

### 9.1 Contradictions Found

| # | Issue | Documents | Severity | Resolution |
|---|---|---|---|---|
| 1 | **Radius token conflict** | tokens.md vs surface-overlay.md | 🔴 Critical | Use **updated** values from surface-overlay.md (10/14/18/22px) |
| 2 | **Glass tier value conflict** | tokens.md vs surface-overlay.md | 🔴 Critical | Use **updated** values from surface-overlay.md (16/24/40px blur) |
| 3 | **Shadow dual system** | tokens.md vs surface-overlay.md | 🟡 Medium | Implement both systems; use semantic (resting/elevated/dragging) for surfaces, size-based (sm/md/lg/xl) for elevation |
| 4 | **Mesh gradient format** | tokens.md (rgba) vs layout-shell.md (oklch) | 🟢 Low | Standardize to `rgba()` for browser compat |
| 5 | **Missing `--color-accent-muted` token** | Referenced in 3+ docs, not defined in tokens.md | 🔴 Critical | Define in tokens.md and add to globals.css |
| 6 | **Missing `--z-content` token** | Used in explore and record pages, not in tokens.md or layout-shell.md | 🟡 Medium | Define as `z-index: 50` (between base=0 and dropdown=100) |
| 7 | **Missing surface tokens in CSS** | `--color-surface-base/raised/sunken`, `--color-status-*-bg` defined in tokens.md but flagged as not in globals.css | 🟡 Medium | Add to `@theme` block in globals.css |
| 8 | **Explore node colors hardcoded** | page-explore TSX uses Tailwind defaults, feedback-utility proposes warm tokens | 🟡 Medium | Replace with `--color-chart-node-*` tokens during Phase 4 |

### 9.2 Gaps

| Gap | Impact | Recommended Action |
|---|---|---|
| No focus-ring token defined | Focus visible styles may be inconsistent | Define `--ring-color: --color-accent` and `--ring-width: 2px` in tokens.md |
| No animation spec for glass transition | Surface opacity changes may feel inconsistent | Add `--duration-glass-transition: 280ms` with `--ease-out` |
| `--radius-2xl` used but only defined in surface-overlay | Missing from tokens.md canonical scale | Add to tokens.md §3 |
| No dark mode spec for BackgroundMesh | layout-shell.md only provides light values | Add oklch() dark mode gradient values |
| Card elevated state switches from thin to regular glass | Not documented in surface-overlay §1 table | Add "variant→glass tier" mapping table to Card spec |
| Checkbox indeterminate state missing mark spec | Only checked/unchecked defined | Add dash-icon spec for indeterminate |
| Settings → Vault page uses native `<details>` | No accordion component in design system | Either add Accordion component or style `<details>` with Card |

### 9.3 Recommended Fixes Before Implementation

1. **Update `tokens.md`** to reflect the authoritative values from `components-surface-overlay.md §1.7`:
   - Radius: 10/14/18/22/28px
   - Glass tiers: updated blur/alpha values
   - Add missing tokens: `accent-muted`, `z-content`, `radius-2xl`, `shadow-resting/elevated/dragging`

2. **Standardize mesh gradients** to `rgba()` format in `layout-shell.md`.

3. **Add dark mode BackgroundMesh** values to `layout-shell.md`.

4. **Add focus ring tokens** to `tokens.md`.

5. **Audit all Badge variants** for WCAG AA compliance and document pass/fail per variant.

---

## 10 · Document Index

| # | Document | Lines | Purpose | Key Deliverables |
|---|---|---|---|---|
| 1 | `tokens.md` | 713 | Foundation design tokens | Color palette, typography, radius, shadow, glass, spacing, motion, z-index, breakpoints |
| 2 | `components-button-badge.md` | 855 | Button & Badge components | Button (6 variants × 6 sizes), Badge (8 variants), inline button migration list |
| 3 | `components-form-inputs.md` | 1 478 | Form input components | Input, Textarea, Checkbox, Select, SegmentedControl, Switch; native element migration guide |
| 4 | `components-surface-overlay.md` | 1 763 | Surface & overlay components | Card, Dialog, Sheet, Popover, Tooltip, Tabs, Separator; **authoritative** radius/glass/shadow token updates |
| 5 | `components-feedback-utility.md` | 1 319 | Feedback & utility components | Avatar, ScrollArea, Skeleton, Progress, AlertBanner, EmptyState; hardcoded color audit table; chart node tokens |
| 6 | `layout-shell.md` | 948 | App layout shell | BackgroundMesh, Sidebar, Header, MobileDrawer, AppLayout, responsive behavior |
| 7 | `page-chat.md` | 1 643 | Chat page | SessionList, ChatArea, MessageBubble (user/AI), MessageInput, SourcesPanel, CitationBadge, StreamingIndicator, prose overrides |
| 8 | `page-explore.md` | 781 | Explore (knowledge graph) page | SearchBar, StatsPill, LegendPanel, GraphNode, NodeDetailPanel, MiniMapShell, ControlsShell, ReactFlow CSS theming |
| 9 | `page-settings.md` | 1 612 | Settings page | General/LLM/Vault/Advanced tabs, form layout patterns, native select/radio migration targets |
| 10 | `page-record-query-skills.md` | 2 575 | Record, Query & Skills pages | FileTreePanel, NoteEditor, AIAssistPanel, DiffPreview, SearchBar, ResultCard, SkillCard, SkillRunDialog |
| — | **HANDOFF.md** | **~650** | **This document** | Consolidated audit, token registry, migration lists, implementation guide |

---

*Generated from 10 source documents · 13 687 total source lines · 22 components · 5 pages · ~98 unique tokens*
