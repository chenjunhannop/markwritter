# Explore Page — Full Composition Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion specs:** `layout-shell.md` · `components-surface-overlay.md` · `components-form-inputs.md` · `components-feedback-utility.md`
> **Implementation:** `web/src/features/explore/{explore-page,graph-node,node-detail-panel}.tsx`

---

## Table of Contents

1. [Page Intent](#1-page-intent)
2. [Layout Diagrams](#2-layout-diagrams)
3. [Component Specifications](#3-component-specifications)
4. [State Frames Specification](#4-state-frames-specification)
5. [Glass Treatment Map](#5-glass-treatment-map)
6. [ReactFlow Theming CSS](#6-reactflow-theming-css)
7. [Responsive Behavior](#7-responsive-behavior)
8. [Figma Frames Specification](#8-figma-frames-specification)
9. [TSX Skeleton](#9-tsx-skeleton)
10. [Implementation Checklist](#10-implementation-checklist)

---

## 1. Page Intent

The Explore Page is a **full-bleed knowledge graph workspace**. The graph canvas is the page body; all product controls float above it as translucent amber-tinted glass. The composition should feel like looking through layered crystal over a warm parchment mesh, not like a dashboard with boxed sidebars.

### 1.1 Composition Principles

- **Canvas first:** the graph must own the full viewport width and height beneath the app header.
- **Lightweight chrome:** floating panels should read as tools, not walls.
- **Single strong anchor:** the Node Detail Panel is the only persistent heavy panel.
- **Readable motion:** zoom, pan, selection, and hover states must stay legible over blur.
- **Warm restraint:** the graph node hues remain categorical, while every neutral surface stays in the Warm Amber system.

### 1.2 Primary Structure

```
ExplorePage
├── BackgroundMesh (inherited from app shell)
├── GraphCanvasLayer
│   └── ReactFlow
│       ├── Background
│       ├── Edges
│       ├── Custom GraphNode instances
│       ├── MiniMap
│       └── Controls
└── OverlayChromeLayer
    ├── TopSearchDock
    │   ├── SearchBar
    │   └── StatsPill
    ├── LeftUtilityDock
    │   └── LegendPanel
    ├── RightDetailDock
    │   └── NodeDetailPanel
    └── BottomRightDock
        ├── MiniMapShell
        └── ZoomControlsShell
```

---

## 2. Layout Diagrams

### 2.1 Desktop Layout — 1440×1024

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Explore Page                                                                │
│                                                                              │
│  ┌──────────────────────────────────┐   ┌─────────────────────────────────┐ │
│  │ SearchBar                        │   │ StatsPill                       │ │
│  │ [⌕ Search nodes, tags, links...] │   │ 1,248 nodes | 3,912 edges      │ │
│  └──────────────────────────────────┘   └─────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────┐                              ┌──────────────────┐  │
│  │ LegendPanel          │                              │ NodeDetailPanel  │  │
│  │ Person  Topic        │                              │ Selected node    │  │
│  │ Concept Note         │                              │ metadata         │  │
│  │ Edge types           │                              │ relationships    │  │
│  └──────────────────────┘                              │ related nodes    │  │
│                                                        └──────────────────┘  │
│                                                                              │
│                                                                              │
│                    ReactFlow Full-Bleed Graph Canvas                         │
│                                                                              │
│                                                                              │
│                                                                              │
│                                                       ┌──────────────────┐   │
│                                                       │ MiniMapShell     │   │
│                                                       └──────────────────┘   │
│                                                       ┌──────────────────┐   │
│                                                       │ ControlsShell    │   │
│                                                       │ +  -  fit  lock  │   │
│                                                       └──────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Tablet Layout — 1024×768

```
┌──────────────────────────────────────────────────────────────────────┐
│ ┌───────────────────────────────┐ ┌───────────────────────────────┐ │
│ │ SearchBar                     │ │ StatsPill                     │ │
│ └───────────────────────────────┘ └───────────────────────────────┘ │
│                                                                      │
│ ┌────────────────────┐                           ┌────────────────┐  │
│ │ LegendPanel        │                           │ NodeDetail     │  │
│ └────────────────────┘                           │ Panel (320px)  │  │
│                                                  └────────────────┘  │
│                                                                      │
│                     Graph Canvas                                     │
│                                                                      │
│                                              ┌────────────────────┐  │
│                                              │ MiniMap + Controls │  │
│                                              └────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.3 Mobile Layout — 390×844

```
┌──────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────┐ │
│ │ SearchBar                                │ │
│ └──────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────┐ │
│ │ StatsPill + Legend summary               │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│              Graph Canvas                    │
│                                              │
│                                              │
│ ┌────────────────┐    ┌───────────────────┐ │
│ │ MiniMap toggle │    │ Controls cluster  │ │
│ └────────────────┘    └───────────────────┘ │
│                                              │
│ NodeDetailPanel becomes bottom sheet         │
└──────────────────────────────────────────────┘
```

### 2.4 Z-Index Layering

| Layer | Value | Element |
|---|---:|---|
| `z-base` | 0 | App shell background mesh |
| `z-canvas` | 1 | ReactFlow pane, edges, background |
| `z-overlay` | 10 | Search, legend, minimap, controls |
| `z-panel` | 20 | NodeDetailPanel |
| `z-sheet-backdrop` | 40 | Mobile detail sheet overlay |
| `z-sheet` | 50 | Mobile detail sheet content |

### 2.5 Spacing and Anchors

| Area | Desktop | Tablet | Mobile |
|---|---:|---:|---:|
| Overlay inset | 16px | 16px | 12px |
| Search dock gap | 12px | 8px | 8px |
| Bottom-right dock gap | 12px | 8px | 8px |
| Detail panel gutter | 16px | 12px | sheet mode |
| Canvas safe zone under header | 16px | 16px | 12px |

---

## 3. Component Specifications

### 3.1 ExplorePage Root

| Property | Value |
|---|---|
| Layout | `relative isolate h-full min-h-0 overflow-hidden` |
| Surface | Transparent; relies on app shell mesh |
| Interaction model | Canvas pointer events enabled, overlay containers `pointer-events-none`, panel children `pointer-events-auto` |
| Canvas padding | None; panels float inside absolute overlay anchors |

### 3.2 SearchBar

**Intent:** primary discovery entrypoint; must feel like a lens on top of the graph.

| Property | Value |
|---|---|
| Width | `clamp(320px, 42vw, 560px)` desktop, full width mobile |
| Height | 48px |
| Radius | `radius-lg` = 18px |
| Glass tier | thin |
| Internal padding | `pl-11 pr-14 py-3` |
| Icon | `Search`, 16px, `text-muted-foreground` |
| Placeholder | "Search nodes, tags, links, and relationships" |
| Action | inline clear text button on active query |
| Focus treatment | 2px `ring`, inner glow `0 0 0 4px color-mix(in srgb, var(--color-ring) 18%, transparent)` |

### 3.3 StatsPill

| Property | Value |
|---|---|
| Height | 36px |
| Min width | 180px |
| Radius | 9999px |
| Glass tier | ultra-thin |
| Content | node count, edge count, filtered count when search active |
| Typography | `caption` 12px/500, `text-muted-foreground` |

When search is active, use `Filtered: 48 / 1,248` instead of repeating totals alone.

### 3.4 LegendPanel

| Property | Value |
|---|---|
| Width | 224px desktop, 200px tablet |
| Padding | 12px |
| Radius | `radius-md` = 14px |
| Glass tier | ultra-thin |
| Layout | vertical stack, `gap-3` |
| Header | "Legend" + optional collapse chevron |
| Rows | four node chips + one edge semantics row |

**Node chip anatomy:**

| Part | Size | Value |
|---|---:|---|
| Swatch | 10×10 | Filled with node type color |
| Label | 12px | `Person`, `Topic`, `Concept`, `Note` |
| Optional count | 11px | muted count aligned right |

### 3.5 Graph Node

This spec intentionally moves away from the current circular implementation. The node should feel like a polished crystal tile, not a bubble.

| Property | Value |
|---|---|
| Frame | 72×72 |
| Outer shape | `rounded-[20px]` |
| Inner tile | 56×56, `rounded-[16px]` |
| Label | 2 lines max, centered, 11px/1.15, semibold |
| Selection | 2px categorical outline + amber focus halo |
| Hover | raise by 2px, shadow-elevated |
| Fill | tinted 14% node color wash over `surface-base` |
| Border | 1px `color-mix(in srgb, currentColor 32%, var(--color-border))` |

**Node type fills:**

| Type | Color |
|---|---|
| person | `#3B82F6` |
| topic | `#22C55E` |
| concept | `#A855F7` |
| note | `#F59E0B` |

### 3.6 Edge Styling

| Property | Value |
|---|---|
| Edge type | `smoothstep` |
| Default stroke | `color-mix(in srgb, var(--color-muted-foreground) 40%, transparent)` |
| Hover stroke | `color-mix(in srgb, var(--color-primary) 55%, var(--color-border))` |
| Width | 1.5px default, 2px selected |
| Label | 11px/500 on tiny glass capsule |
| Animation | only on actively traversed or filtered edges; do not animate all edges by default |

### 3.7 NodeDetailPanel

This is the main analytical panel and the only overlay allowed to feel substantial.

| Property | Value |
|---|---|
| Width | 320px desktop/tablet |
| Height | `calc(100% - 32px)` with 16px inset |
| Radius | `radius-lg` = 18px |
| Glass tier | regular |
| Shadow | `shadow-elevated` |
| Layout | header, summary, metadata grid, relationship sections, related nodes, footer actions |

**Panel anatomy:**

```
NodeDetailPanel
├── Header
│   ├── Node name
│   ├── Type badge
│   └── Close button
├── Summary Card
│   ├── Node id / source
│   ├── Degree / relationship counts
│   └── Last updated or created metadata
├── Incoming Links Section
├── Outgoing Links Section
├── Related Nodes Section
└── Footer
    ├── Center on graph
    └── Open note / inspect action
```

**Relationship row:**

| Property | Value |
|---|---|
| Height | 40px min |
| Radius | `radius-sm` = 10px |
| Background | `surface-base/65%` inside regular glass shell |
| Hover | `accent` wash |
| Leading marker | categorical dot 8px |
| Copy | source/target label + edge label |

### 3.8 MiniMapShell

| Property | Value |
|---|---|
| Size | 176×128 desktop, 152×112 tablet |
| Radius | `radius-md` = 14px |
| Glass tier | thin |
| Border | 1px glass border |
| Internal padding | 6px |
| Mask color | warm amber-tinted mask, never pure black |

### 3.9 ControlsShell

| Property | Value |
|---|---|
| Layout | vertical stack desktop, horizontal mobile |
| Button size | 40×40 |
| Radius | 10px per button, 14px group shell |
| Glass tier | thin |
| Buttons | zoom in, zoom out, fit view, lock pan/interaction |
| Hover | subtle amber wash |
| Active | `primary` fill with dark ink foreground |

### 3.10 Empty and Error States

Use the existing Explore feedback guidance from `components-feedback-utility.md`, but place it in a centered glass card above the canvas rather than replacing the whole page background.

| State | Title | Description | Action |
|---|---|---|---|
| Empty | "No connections yet" | "Add notes, tags, and links to build your knowledge graph." | optional `Refresh` |
| Error | "Failed to load graph data" | "Check your connection and try again." | `Retry` |
| Loading | spinner only | "Mapping your knowledge graph…" optional | none |

---

## 4. State Frames Specification

Create explicit Figma state frames for these compositions.

### 4.1 `Explore / Default`

- Search empty
- Legend expanded
- No node selected
- MiniMap visible
- Controls idle

### 4.2 `Explore / Search Active`

- Search field populated
- Stats pill switches to filtered counts
- Matching nodes keep full opacity
- Non-matching nodes drop to 28% opacity
- Matching edges increase to 2px and use `primary`-tinted stroke

### 4.3 `Explore / Node Selected`

- Selected node centered visually within the viewport
- Selected node uses categorical outline plus amber halo
- NodeDetailPanel visible
- Related nodes in the canvas receive 88% opacity while unrelated nodes drop to 40%

### 4.4 `Explore / Detail Loading`

- NodeDetailPanel open with skeleton sections
- Canvas remains interactive
- Search and legend stay enabled

### 4.5 `Explore / Empty`

- Centered empty-state card
- Legend hidden
- MiniMap hidden
- Controls disabled except `fit view`

### 4.6 `Explore / Error`

- Centered error card
- Retry action visible
- Search hidden until data loads again

### 4.7 `Explore / Mobile Detail Sheet`

- Search dock stacked top
- Detail panel becomes bottom sheet at 76% viewport height
- MiniMap collapsed to icon toggle
- Controls switch to horizontal row

---

## 5. Glass Treatment Map

| Surface | Tier | Light Background | Dark Background | Rationale |
|---|---|---|---|---|
| SearchBar | thin | `rgba(255,255,255,0.55)` | `rgba(26,20,15,0.60)` | Primary input must stay readable without feeling heavy |
| StatsPill | ultra-thin | `rgba(255,255,255,0.45)` | `rgba(26,20,15,0.50)` | Lightweight chrome |
| LegendPanel | ultra-thin | `rgba(255,255,255,0.45)` | `rgba(26,20,15,0.50)` | Informational, non-dominant |
| MiniMapShell | thin | `rgba(255,255,255,0.55)` | `rgba(26,20,15,0.60)` | Dense content needs clearer separation |
| ControlsShell | thin | `rgba(255,255,255,0.55)` | `rgba(26,20,15,0.60)` | High-frequency interaction zone |
| NodeDetailPanel | regular | `rgba(255,255,255,0.65)` | `rgba(26,20,15,0.70)` | Main analysis panel |
| Edge label capsule | ultra-thin | `rgba(255,255,255,0.45)` | `rgba(26,20,15,0.50)` | Small support label |
| Empty/Error card | regular | `rgba(255,255,255,0.65)` | `rgba(26,20,15,0.70)` | Need stronger focus than chrome |

### 5.1 Glass Fallback

When `backdrop-filter` is unavailable:

- Replace all glass surfaces with solid `surface-base` or `surface-raised`
- Keep the same border and shadow values
- Preserve overlay positioning and hierarchy

---

## 6. ReactFlow Theming CSS

```css
/* web/src/features/explore/explore-page.css */
.explore-flow {
  --explore-node-person: #3b82f6;
  --explore-node-topic: #22c55e;
  --explore-node-concept: #a855f7;
  --explore-node-note: #f59e0b;
  --explore-panel-border: color-mix(in srgb, var(--color-border) 72%, white 18%);
  --explore-edge: color-mix(in srgb, var(--color-muted-foreground) 40%, transparent);
  --explore-edge-active: color-mix(in srgb, var(--color-primary) 55%, var(--color-border));
  --explore-grid: color-mix(in srgb, var(--color-border) 70%, transparent);
  --explore-mask: color-mix(in srgb, var(--color-accent) 24%, transparent);
}

.explore-flow .react-flow__renderer,
.explore-flow .react-flow__pane {
  background: transparent;
}

.explore-flow .react-flow__background pattern {
  color: var(--explore-grid);
}

.explore-flow .react-flow__edge-path {
  stroke: var(--explore-edge);
  stroke-width: 1.5;
}

.explore-flow .react-flow__edge.selected .react-flow__edge-path,
.explore-flow .react-flow__edge:focus-visible .react-flow__edge-path {
  stroke: var(--explore-edge-active);
  stroke-width: 2;
}

.explore-flow .react-flow__edge-textbg {
  fill: color-mix(in srgb, var(--color-surface-base) 72%, transparent);
  stroke: var(--explore-panel-border);
  rx: 8;
  ry: 8;
}

.explore-flow .react-flow__controls,
.explore-flow .react-flow__minimap {
  border: 1px solid var(--explore-panel-border);
  background: color-mix(in srgb, var(--color-surface-base) 62%, transparent);
  backdrop-filter: blur(16px) saturate(140%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.explore-flow .react-flow__controls-button {
  width: 40px;
  height: 40px;
  border-color: transparent;
  background: transparent;
  color: var(--color-foreground);
}

.explore-flow .react-flow__controls-button:hover {
  background: color-mix(in srgb, var(--color-accent) 72%, transparent);
}

.explore-flow .react-flow__controls-button:focus-visible {
  outline: 2px solid var(--color-ring);
  outline-offset: -2px;
}

.explore-flow .react-flow__minimap-mask {
  fill: var(--explore-mask);
}

.explore-flow .react-flow__handle {
  width: 8px;
  height: 8px;
  border: 1px solid var(--color-surface-base);
  background: var(--color-muted-foreground);
}

.graph-node {
  width: 72px;
  height: 72px;
  padding: 8px;
  border-radius: 20px;
  border: 1px solid transparent;
  background: color-mix(in srgb, var(--color-surface-base) 76%, transparent);
  backdrop-filter: blur(8px) saturate(120%);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  transition:
    transform 180ms ease-out,
    box-shadow 180ms ease-out,
    border-color 180ms ease-out;
}

.graph-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.graph-node[data-selected="true"] {
  box-shadow:
    0 0 0 2px color-mix(in srgb, var(--node-color) 34%, transparent),
    0 0 0 6px color-mix(in srgb, var(--color-ring) 16%, transparent),
    0 12px 40px rgba(0, 0, 0, 0.12);
  border-color: color-mix(in srgb, var(--node-color) 45%, var(--color-border));
}

.graph-node__tile {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--node-color) 14%, var(--color-surface-base));
  color: var(--color-foreground);
  text-align: center;
}

.dark .explore-flow .react-flow__controls,
.dark .explore-flow .react-flow__minimap,
.dark .graph-node {
  background: color-mix(in srgb, var(--color-surface-base) 72%, transparent);
}
```

### 6.1 ReactFlow Defaults

| Prop | Value |
|---|---|
| `fitView` | `true` |
| `minZoom` | `0.2` |
| `maxZoom` | `1.8` |
| `proOptions.hideAttribution` | `true` |
| `nodesDraggable` | `true` |
| `elementsSelectable` | `true` |
| `panOnScroll` | `false` desktop, `true` with modifier on trackpad if needed |

---

## 7. Responsive Behavior

### 7.1 Desktop — `>= 1280px`

- SearchBar and StatsPill share the top dock on one row.
- LegendPanel sits bottom-left or mid-left depending on graph density.
- NodeDetailPanel is always a right-side floating panel when a node is selected.
- MiniMap and Controls are stacked bottom-right.

### 7.2 Laptop / Tablet — `1024px to 1279px`

- SearchBar width reduces to `min(440px, 55vw)`.
- StatsPill may wrap below search when counts are long.
- LegendPanel stays visible but can collapse to a 40px-tall summary row.
- NodeDetailPanel remains 320px but uses tighter internal padding.

### 7.3 Small Tablet — `768px to 1023px`

- SearchBar becomes full-width within the safe inset.
- StatsPill moves below SearchBar.
- LegendPanel collapses by default.
- MiniMap shrinks to 152×112.
- Controls remain vertical unless they collide with the detail panel.

### 7.4 Mobile — `< 768px`

- SearchBar and StatsPill stack.
- Legend becomes a pill-triggered popover or bottom sheet.
- NodeDetailPanel becomes a bottom sheet with drag handle.
- MiniMap hides behind a toggle by default.
- Controls switch to a horizontal row centered at the bottom.
- Keep a minimum 56px touch target band clear from device bottom safe areas.

---

## 8. Figma Frames Specification

### 8.1 Page Structure

```
Explore Page
├── Cover
├── 01 Foundations Hooks
│   ├── Warm mesh reference
│   ├── Graph color tokens
│   └── Glass tier swatches
├── 02 Layout Frames
│   ├── Desktop / 1440
│   ├── Tablet / 1024
│   └── Mobile / 390
├── 03 Component Frames
│   ├── SearchBar
│   ├── StatsPill
│   ├── LegendPanel
│   ├── GraphNode
│   ├── Edge label
│   ├── MiniMapShell
│   ├── ControlsShell
│   └── NodeDetailPanel
└── 04 State Frames
    ├── Default
    ├── Search Active
    ├── Node Selected
    ├── Detail Loading
    ├── Empty
    ├── Error
    └── Mobile Detail Sheet
```

### 8.2 Frame Naming

| Frame | Name |
|---|---|
| Main desktop | `Explore / Desktop / 1440` |
| Main tablet | `Explore / Tablet / 1024` |
| Main mobile | `Explore / Mobile / 390` |
| Search component | `Explore/SearchBar` |
| Graph node component | `Explore/GraphNode` |
| Detail panel component | `Explore/NodeDetailPanel` |

### 8.3 Grid and Constraints

| Frame | Grid | Notes |
|---|---|---|
| Desktop 1440 | 12 columns, 80px margins, 24px gutters | Panels align to safe insets, canvas ignores grid |
| Tablet 1024 | 8 columns, 32px margins, 20px gutters | Detail panel docks to 3 columns |
| Mobile 390 | 4 columns, 16px margins, 12px gutters | Overlays stack, sheet spans full width |

### 8.4 Auto Layout Rules

- Overlay docks should use Auto Layout even if the page frame itself does not.
- Search dock: horizontal, gap 12px, hug height.
- Bottom-right dock: vertical, gap 12px, bottom-right constrained.
- NodeDetailPanel content: vertical, gap 16px, padding 16px.
- Relationship lists: vertical stack, gap 8px.

### 8.5 Required Component Variants

| Component | Variants |
|---|---|
| SearchBar | `default`, `focus`, `filled`, `searching`, `disabled` |
| LegendPanel | `expanded`, `collapsed` |
| GraphNode | `person`, `topic`, `concept`, `note` × `default`, `hover`, `selected`, `dimmed` |
| NodeDetailPanel | `default`, `loading`, `empty` |
| ControlsShell | `vertical`, `horizontal` |
| MiniMapShell | `default`, `hidden`, `compact` |

---

## 9. TSX Skeleton

```tsx
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const NODE_COLORS = {
  person: "#3b82f6",
  topic: "#22c55e",
  concept: "#a855f7",
  note: "#f59e0b",
} as const;

export function ExplorePageSkeleton({
  nodes,
  edges,
  query,
  selectedNodeId,
}: {
  nodes: Node[];
  edges: Edge[];
  query: string;
  selectedNodeId: string | null;
}) {
  return (
    <section className="relative isolate h-full min-h-0 overflow-hidden">
      <div className="pointer-events-none absolute inset-0 z-10">
        <div className="absolute left-4 right-4 top-4 flex items-start justify-between gap-3">
          <div className="pointer-events-auto flex min-w-0 flex-1 items-center gap-3">
            <form className="relative w-full max-w-[560px]">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                defaultValue={query}
                placeholder="Search nodes, tags, links, and relationships"
                className="h-12 rounded-[18px] border-white/35 bg-white/55 pl-11 pr-14 backdrop-blur-[16px] dark:bg-[rgba(26,20,15,0.60)]"
              />
            </form>

            <div className="rounded-full border border-white/35 bg-white/45 px-3 py-2 text-xs text-muted-foreground backdrop-blur-[8px] dark:bg-[rgba(26,20,15,0.50)]">
              1,248 nodes · 3,912 edges
            </div>
          </div>
        </div>

        <aside className="pointer-events-auto absolute bottom-4 left-4 w-56 rounded-[14px] border border-white/35 bg-white/45 p-3 backdrop-blur-[8px] dark:bg-[rgba(26,20,15,0.50)]">
          Legend
        </aside>

        <div className="pointer-events-auto absolute bottom-4 right-4 flex flex-col gap-3">
          <div className="rounded-[14px] border border-white/35 bg-white/55 p-2 backdrop-blur-[16px] dark:bg-[rgba(26,20,15,0.60)]">
            <MiniMap
              pannable
              zoomable
              nodeColor={(node) => {
                const type = (node.data as { nodeType?: keyof typeof NODE_COLORS })
                  ?.nodeType;
                return type ? NODE_COLORS[type] : "var(--color-muted-foreground)";
              }}
              maskColor="color-mix(in srgb, var(--color-accent) 24%, transparent)"
            />
          </div>

          <div className="rounded-[14px] border border-white/35 bg-white/55 p-1 backdrop-blur-[16px] dark:bg-[rgba(26,20,15,0.60)]">
            <Controls showInteractive={false} />
          </div>
        </div>

        {selectedNodeId ? (
          <aside className="pointer-events-auto absolute bottom-4 right-4 top-4 w-80 rounded-[18px] border border-white/40 bg-white/65 shadow-lg backdrop-blur-[24px] dark:bg-[rgba(26,20,15,0.70)]">
            {/* Node detail content */}
          </aside>
        ) : null}
      </div>

      <ReactFlow
        className="explore-flow h-full w-full"
        nodes={nodes}
        edges={edges}
        fitView
        minZoom={0.2}
        maxZoom={1.8}
      >
        <Background gap={20} size={1} color="var(--color-border)" />
      </ReactFlow>
    </section>
  );
}
```

---

## 10. Implementation Checklist

- [ ] Replace opaque Explore overlays with glass-tier shells.
- [ ] Rebuild `GraphNode` from circular badge to 72×72 rounded crystal tile.
- [ ] Stop animating all edges by default; reserve animation for active paths.
- [ ] Wrap `MiniMap` and `Controls` in custom glass shells for consistent chrome.
- [ ] Convert `NodeDetailPanel` to inset floating panel on desktop and sheet on mobile.
- [ ] Add `explore-page.css` or equivalent scoped theme overrides for ReactFlow internals.
- [ ] Create Figma state frames before implementation polish.
- [ ] Verify contrast and hit areas in both light and dark modes.

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
