# App Layout Shell Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion specs:** `components-surface-overlay.md` · `components-button-badge.md`
> **Implementation:** `web/src/layout/{app-layout,sidebar,header,mobile-drawer}.tsx`

---

## Table of Contents

1. [Layout Structure Diagram](#1-layout-structure-diagram)
2. [Background Mesh Implementation](#2-background-mesh-implementation)
3. [Sidebar Specification](#3-sidebar-specification)
4. [Header Specification](#4-header-specification)
5. [MobileDrawer Specification](#5-mobiledrawer-specification)
6. [AppLayout Composition](#6-applayout-composition)
7. [Figma Frames Specification](#7-figma-frames-specification)
8. [Responsive Behavior](#8-responsive-behavior)
9. [Animation Specification](#9-animation-specification)

---

## 1. Layout Structure Diagram

### 1.1 Component Hierarchy

```
AppLayout (relative, h-screen, w-screen, overflow-hidden)
├── BackgroundMesh (fixed, inset-0, z-0, pointer-events-none)
├── Content Layer (relative, z-10, flex, h-full)
│   ├── Sidebar (hidden md:flex, flex-col, h-full, z-sidebar)
│   │   ├── Brand Row (h-14, flex, items-center, gap-2, px-4)
│   │   │   ├── PenLine Icon (20px, primary)
│   │   │   └── "Markwritter" Text (title-3, semibold) [hidden when collapsed]
│   │   ├── Separator (horizontal, on-glass)
│   │   ├── ScrollArea (flex-1, py-2, px-2)
│   │   │   └── Nav Items × 7 (flex-col, gap-1)
│   │   │       └── NavLink (h-10, items-center, gap-3, rounded-sm)
│   │   │           ├── Lucide Icon (16px, shrink-0)
│   │   │           └── Label Text (callout, 14px/500) [hidden when collapsed]
│   │   ├── Separator (horizontal, on-glass)
│   │   └── Footer (p-2, flex, justify-center)
│   │       └── Collapse Toggle (Button ghost icon-sm, 28px)
│   └── Main Column (flex-1, flex-col, min-w-0)
│       ├── Header (h-14, sticky top-0, z-sticky)
│       │   ├── Left Group (flex, items-center, gap-3)
│       │   │   ├── Hamburger [mobile only] (Button ghost icon-sm)
│       │   │   └── Page Title (title-3, semibold)
│       │   └── Right Group (flex, items-center, gap-2, ml-auto)
│       │       ├── Theme Toggle (Button ghost icon-sm, cycles light→dark→system)
│       │       └── Sidebar Toggle [desktop only] (Button ghost icon-sm)
│       └── Main Content (flex-1, overflow-auto, relative)
└── MobileDrawer [mobile only] (Sheet, side="left", w-64)
    ├── Drawer Header (h-14, flex-row, items-center, gap-2, px-4)
    │   ├── PenLine Icon (20px, primary)
    │   ├── "Markwritter" Text (title-3, semibold)
    │   └── Close Button (ghost icon-sm, ml-auto)
    ├── Separator (horizontal, on-glass)
    └── ScrollArea (flex-1, py-2, px-2)
        └── Nav Items × 7 (same as expanded sidebar)
```

### 1.2 Z-Index Layering

```
Layer              Token          Value   Element
─────────────────  ────────────   ─────   ──────────────────────
Background Mesh    z-base         0       Fixed mesh gradient
Content Base       z-content      1       Main flex container
Sidebar Chrome     z-sidebar      20      Sidebar panel
Sticky Header      z-sticky       10      Header bar (within main column)
Dropdown Content   z-dropdown     30      Popovers in header/sidebar
Sheet Overlay      z-modal-bk     40      MobileDrawer backdrop
Sheet Content      z-modal        50      MobileDrawer panel
Tooltip            z-tooltip      60      Nav tooltips (collapsed mode)
Toast              z-toast        70      Toast notifications
```

> **Note:** The sidebar sits at `z-sidebar` (20) above the sticky header (`z-sticky`, 10). This ensures the sidebar border-right paints over the header edge when they meet. The header is sticky within the main column only and does not need to overlay the sidebar.

---

## 2. Background Mesh Implementation

### 2.1 Design Intent

The mesh creates the warm luminous "alive" quality beneath all glass surfaces. Three radial-gradient layers compose into organic light pools — **sunlight through frosted glass** in light mode, **candlelight ember glow** in dark mode.

**Critical:** The mesh must be continuous, oversized, and fixed so that no glass surface ever reveals a hard edge or flat gap through its blur.

### 2.2 CSS — Dedicated Background Div

```css
/* ─── web/src/components/background-mesh.css ─── */

/* Light mode — sunlight through frosted glass */
.mesh-light {
  background:
    radial-gradient(
      ellipse 80% 60% at 15% 20%,
      oklch(0.88 0.06 75 / 0.40),
      transparent 50%
    ),
    radial-gradient(
      ellipse 70% 50% at 85% 10%,
      oklch(0.85 0.07 55 / 0.35),
      transparent 45%
    ),
    radial-gradient(
      ellipse 90% 70% at 65% 75%,
      oklch(0.88 0.04 95 / 0.25),
      transparent 55%
    ),
    var(--color-background);
}

/* Dark mode — candlelight ember glow */
.mesh-dark {
  background:
    radial-gradient(
      ellipse 80% 60% at 18% 18%,
      oklch(0.22 0.06 70 / 0.50),
      transparent 45%
    ),
    radial-gradient(
      ellipse 70% 50% at 82% 12%,
      oklch(0.18 0.05 50 / 0.40),
      transparent 40%
    ),
    radial-gradient(
      ellipse 90% 70% at 72% 78%,
      oklch(0.20 0.04 30 / 0.30),
      transparent 50%
    ),
    var(--color-background);
}
```

### 2.3 React Component

```tsx
// web/src/components/background-mesh.tsx
export function BackgroundMesh() {
  return (
    <div
      aria-hidden="true"
      className="
        fixed inset-0 -z-0
        pointer-events-none
        mesh-light dark:mesh-dark
      "
    />
  );
}
```

### 2.4 Application Strategy

| Aspect | Decision | Rationale |
|---|---|---|
| DOM placement | Dedicated `<div>` inside AppLayout, before the content flex | Keeps mesh scoped to the app shell; doesn't pollute `<body>` |
| Position | `fixed, inset-0` | Stays in place when content scrolls |
| Z-index | `z-base` (0) — content layer at `z-10` | Content always paints above mesh |
| Pointer events | `pointer-events-none` | Mesh is purely decorative |
| Fallback | `var(--color-background)` as the final gradient layer | Solid warm parchment / espresso when gradients fail |

### 2.5 Performance Notes

- Radial gradients are GPU-composited and do not repaint on scroll.
- Mesh is a single fixed div — no re-renders on route change.
- `will-change: auto` (default) — do not add `will-change: transform` as it forces a compositing layer without benefit for a static gradient.

---

## 3. Sidebar Specification

### 3.1 Glass Treatment

| Property | Value |
|---|---|
| Glass tier | **regular** (`blur(24px) saturate(160%)`) |
| Background (light) | `rgba(255, 255, 255, 0.65)` |
| Background (dark) | `rgba(26, 20, 15, 0.70)` |
| Border-right | `1px solid rgba(255, 255, 255, 0.40)` light · `1px solid rgba(255, 255, 255, 0.12)` dark |
| Z-index | `z-sidebar` (20) |

### 3.2 Dimensions

| State | Width | Behavior |
|---|---|---|
| **Expanded** | `w-64` (256px) | Default on `≥ lg` (1024px) |
| **Collapsed** | `w-14` (56px) | User-toggled; default on `md` to `< lg` |
| **Hidden** | — | Below `md` (< 768px); replaced by MobileDrawer |

### 3.3 Brand Row

| Property | Expanded | Collapsed |
|---|---|---|
| Height | 56px (`h-14`) | 56px (`h-14`) |
| Layout | `flex`, `items-center`, `gap-2`, `px-4` | `flex`, `items-center`, `justify-center` |
| Icon | PenLine, 20px, `text-sidebar-primary` | PenLine, 20px, `text-sidebar-primary` |
| Text | "Markwritter", 18px/600 (`title-3`), `text-sidebar-foreground` | Hidden |

### 3.4 Navigation Items

**7 items from `nav-config.ts`:**

| # | Icon | Label | Path |
|---|---|---|---|
| 1 | `MessageSquare` | Chat | `/chat` |
| 2 | `Boxes` | Skills | `/skills` |
| 3 | `GitGraph` | Explore | `/explore` |
| 4 | `Search` | Query | `/query` |
| 5 | `FileEdit` | Record | `/record` |
| 6 | `ScrollText` | Logs | `/logs` |
| 7 | `Settings` | Settings | `/settings` |

**Nav item anatomy:**

| Property | Expanded | Collapsed |
|---|---|---|
| Height | 40px (`h-10`) | 40px (`h-10`) |
| Layout | `flex`, `items-center`, `gap-3`, `px-3` | `flex`, `items-center`, `justify-center` |
| Icon | 16px Lucide, `shrink-0` | 16px Lucide, `shrink-0` |
| Label | 14px/500 (`callout` weight 500) | Hidden; shown via Tooltip `side="right"` |
| Radius | 10px (`rounded-[10px]`) | 10px (`rounded-[10px]`) |
| Gap between items | 4px (`gap-1`) | 4px (`gap-1`) |

**Nav item states:**

| State | Background | Text | Border |
|---|---|---|---|
| **Default** | transparent | `sidebar-foreground` at 70% opacity | none |
| **Hover** | `sidebar-accent` | `sidebar-accent-foreground` | none |
| **Active** | `sidebar-accent` | `sidebar-accent-foreground` | Optional: left 3px `primary` stripe |
| **Focus-visible** | same as hover | same | 2px `sidebar-ring` |

> **Active stripe detail:** A 3px-wide `primary`-colored bar on the left edge of the active nav item provides an additional visual anchor beyond the background fill. Implementation: a `::before` pseudo-element or an absolute-positioned div, `left-0`, `top-2`, `bottom-2`, `w-[3px]`, `rounded-full`, `bg-primary`.

### 3.5 Footer (Collapse Toggle)

| Property | Value |
|---|---|
| Container | `flex`, `items-center`, `justify-center`, `p-2` |
| Button | `Button variant="ghost" size="icon-sm"` (28×28px) |
| Icon (expanded) | `PanelLeftClose` (14px) |
| Icon (collapsed) | `PanelLeft` (14px) |
| Tooltip | `side="right"`, "Expand sidebar" / "Collapse sidebar" |

### 3.6 Separators

Two horizontal separators in the sidebar:
1. **After brand row** — separates logo from nav
2. **Before footer** — separates nav from collapse toggle

Both use the **on-glass separator token**: `rgba(255,255,255,0.10)` light · `rgba(255,255,255,0.06)` dark.

### 3.7 Tailwind Class Map

```tsx
// Sidebar root
const sidebarClasses = cn(
  // Visibility
  "hidden md:flex flex-col h-full",
  // Glass-tier-regular
  "bg-white/65 backdrop-blur-[24px] saturate-[160%]",
  "border-r border-white/40",
  "dark:bg-[rgba(26,20,15,0.70)] dark:border-white/12",
  // Transition
  "transition-[width] duration-300 ease-in-out",
  // Z-index
  "z-20",
  // Width
  collapsed ? "w-14" : "w-64",
);
```

---

## 4. Header Specification

### 4.1 Glass Treatment

| Property | Value |
|---|---|
| Glass tier | **thick** (`blur(40px) saturate(180%)`) |
| Background (light) | `rgba(255, 255, 255, 0.78)` |
| Background (dark) | `rgba(26, 20, 15, 0.80)` |
| Border-bottom | `1px solid rgba(255, 255, 255, 0.45)` light · `1px solid rgba(255, 255, 255, 0.15)` dark |
| Position | `sticky top-0` within main column |
| Z-index | `z-sticky` (10) |

### 4.2 Dimensions

| Property | Desktop | Mobile |
|---|---|---|
| Height | 56px (`h-14`) | 56px (`h-14`) |
| Padding | `px-6` (24px) | `px-4` (16px) |
| Layout | `flex`, `items-center`, `justify-between` | `flex`, `items-center`, `justify-between` |

### 4.3 Left Group

| Element | Desktop | Mobile |
|---|---|---|
| Hamburger button | Hidden | `Button ghost icon-sm` (28px), `Menu` icon 14px |
| Page title | 18px/600 (`title-3`), `text-foreground` | Same, with `ml-1` after hamburger |

**Page title** is derived from the current route matched against `navItems`. Falls back to `"Markwritter"`.

### 4.4 Right Group

| Element | Desktop | Mobile |
|---|---|---|
| Theme toggle | `Button ghost icon-sm` (28px), cycles: Sun → Moon → Monitor | Same |
| Sidebar toggle | `Button ghost icon-sm` (28px), `Menu` icon 14px | Hidden |
| Gap | `gap-2` (8px) | `gap-2` (8px) |

**Theme toggle icons:**

| Theme | Icon |
|---|---|
| `light` | `Sun` (14px) |
| `dark` | `Moon` (14px) |
| `system` | `Monitor` (14px) |

**Theme toggle tooltip:** "浅色模式" / "深色模式" / "跟随系统"

### 4.5 Tailwind Class Map

```tsx
// Header root
const headerClasses = cn(
  "flex h-14 items-center gap-4",
  "px-4 md:px-6",
  // Glass-tier-thick
  "bg-white/78 backdrop-blur-[40px] saturate-[180%]",
  "border-b border-white/45",
  "dark:bg-[rgba(26,20,15,0.80)] dark:border-white/15",
  // Sticky positioning
  "sticky top-0 z-10",
  // Text color
  "text-foreground",
);
```

---

## 5. MobileDrawer Specification

### 5.1 Glass Treatment

| Property | Value |
|---|---|
| Glass tier | **regular** (`blur(24px) saturate(160%)`) — same as sidebar |
| Background (light) | `rgba(255, 255, 255, 0.65)` |
| Background (dark) | `rgba(26, 20, 15, 0.70)` |
| Border-right | `1px solid rgba(255, 255, 255, 0.40)` light · `1px solid rgba(255, 255, 255, 0.12)` dark |
| Rounded corners | Right edges: 18px (`rounded-r-[18px]`) |

### 5.2 Dimensions

| Property | Value |
|---|---|
| Side | `left` |
| Width | 256px (`w-64`) |
| Height | Full viewport (`h-full`) |
| Visibility | `md:hidden` — only shown below 768px |

### 5.3 Overlay

| Property | Value |
|---|---|
| Background | `rgba(0, 0, 0, 0.40)` |
| Backdrop filter | `blur(4px)` |
| Z-index | `z-modal-backdrop` (40) |

### 5.4 Header

| Property | Value |
|---|---|
| Height | 56px (`h-14`) |
| Layout | `flex`, `items-center`, `gap-2`, `px-4` |
| Icon | PenLine, 20px, `text-sidebar-primary` |
| Text | "Markwritter", 18px/600, `text-foreground` |
| Close button | Absolute, top-right, `Button ghost icon-sm` (28px), `X` icon 14px |

### 5.5 Navigation

Identical to the expanded sidebar nav (§3.4 expanded state):
- Same 7 items, same icon + label layout
- Same hover/active states using `sidebar-accent` tokens
- Closes on NavLink click (`onClick={() => setDrawerOpen(false)}`)

**No collapse toggle** — drawer is always full width.

### 5.6 Motion

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Open (slide in) | 300ms | `ease-out` | `translateX(-100%) → translateX(0)` |
| Close (slide out) | 200ms | `ease-in` | `translateX(0) → translateX(-100%)` |
| Overlay fade in | 300ms | `ease-out` | `opacity 0 → 1` |
| Overlay fade out | 200ms | `ease-in` | `opacity 1 → 0` |

### 5.7 Implementation Notes

- Built on the existing `Sheet` component from `components-surface-overlay.md` §5.
- Uses `SheetContent` with `side="left"` variant.
- Glass treatment is applied by overriding the default Sheet glass tier from **thin** to **regular** (matching the sidebar) via className override.
- The Sheet's built-in close button is hidden; a custom close button is placed in the drawer header for layout consistency.

---

## 6. AppLayout Composition

### 6.1 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  AppLayout (relative, h-screen, w-screen, overflow-hidden)       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  BackgroundMesh (fixed, inset-0, z-0, pointer-events-none) │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Content Layer (relative, z-10, flex, h-full)               │  │
│  │  ┌──────┬─────────────────────────────────────────────┐    │  │
│  │  │      │ Header (h-14, glass-thick, sticky, z-10)    │    │  │
│  │  │      ├─────────────────────────────────────────────┤    │  │
│  │  │ Side │                                            │    │  │
│  │  │ bar  │ Main Content (flex-1, overflow-auto)        │    │  │
│  │  │      │                                            │    │  │
│  │  │ w-64 │                                            │    │  │
│  │  │ or   │                                            │    │  │
│  │  │ w-14 │                                            │    │  │
│  │  │      │                                            │    │  │
│  │  │ glass│                                            │    │  │
│  │  │ -reg │                                            │    │  │
│  │  └──────┴─────────────────────────────────────────────┘    │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  MobileDrawer (Sheet, left, w-64, glass-regular) [mobile]   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### 6.2 TSX Skeleton

```tsx
// web/src/layout/app-layout.tsx
import type { ReactNode } from "react";
import { BackgroundMesh } from "@/components/background-mesh";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useIsMobile } from "@/hooks/use-mobile";
import { useTheme } from "@/hooks/use-theme";
import { Header } from "./header";
import { MobileDrawer } from "./mobile-drawer";
import { Sidebar } from "./sidebar";

export function AppLayout({ children }: { children: ReactNode }) {
  useTheme();
  const isMobile = useIsMobile();

  return (
    <TooltipProvider delayDuration={0}>
      <div className="relative h-screen w-screen overflow-hidden">
        {/* ─── Background Mesh (z-0) ─── */}
        <BackgroundMesh />

        {/* ─── Content Layer (z-10) ─── */}
        <div className="relative z-10 flex h-full">
          {/* Desktop Sidebar — hidden on mobile */}
          {!isMobile && <Sidebar />}

          {/* Main Column */}
          <div className="flex flex-1 flex-col min-w-0">
            <Header />
            <main className="flex-1 overflow-auto relative">
              {children}
            </main>
          </div>
        </div>

        {/* Mobile Drawer — hidden on desktop */}
        {isMobile && <MobileDrawer />}
      </div>
    </TooltipProvider>
  );
}
```

### 6.3 CSS Token Additions

Add to `globals.css` `@theme` block:

```css
@theme {
  /* ─── Z-Index Scale ─── */
  --z-base: 0;
  --z-content: 1;
  --z-sticky: 10;
  --z-sidebar: 20;
  --z-dropdown: 30;
  --z-modal-backdrop: 40;
  --z-modal: 50;
  --z-tooltip: 60;
  --z-toast: 70;
}
```

### 6.4 Reduced Motion Fallback

```css
@media (prefers-reduced-motion: reduce) {
  /* Sidebar width transition: instant */
  /* Sheet slide: fade only */
  /* Nav hover: instant */
  .sidebar-transition,
  [data-sidebar] {
    transition-duration: 0ms !important;
  }
}
```

---

## 7. Figma Frames Specification

### 7.1 Frame Inventory

8 frames total — 4 layouts × 2 themes:

| # | Frame Name | Size | Theme | Description |
|---|---|---|---|---|
| 1 | `Desktop / Expanded / Light` | 1440 × 900 | Light | Full sidebar, header, content placeholder |
| 2 | `Desktop / Collapsed / Light` | 1440 × 900 | Light | Icon-only sidebar with tooltips, header |
| 3 | `Desktop / Expanded / Dark` | 1440 × 900 | Dark | Same as #1, dark theme |
| 4 | `Desktop / Collapsed / Dark` | 1440 × 900 | Dark | Same as #2, dark theme |
| 5 | `Mobile / Drawer Closed / Light` | 390 × 844 | Light | No sidebar, header with hamburger |
| 6 | `Mobile / Drawer Open / Light` | 390 × 844 | Light | Overlay + drawer, header behind |
| 7 | `Mobile / Drawer Closed / Dark` | 390 × 844 | Dark | Same as #5, dark theme |
| 8 | `Mobile / Drawer Open / Dark` | 390 × 844 | Dark | Same as #6, dark theme |

### 7.2 Frame Layout — Desktop Expanded (1440 × 900)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Background Mesh (full frame, warm amber radials)                     │
│ ┌──────────┬────────────────────────────────────────────────────┐   │
│ │ Sidebar  │ Header (56px, glass-thick)                         │   │
│ │ 256px    │ [Page Title]              [☀️ Theme] [≡ Toggle]    │   │
│ │ glass-reg├────────────────────────────────────────────────────┤   │
│ │          │                                                     │   │
│ │ ✏️ Mark  │  Content Area (placeholder)                         │   │
│ │ ──────── │  "Main content scrolls here"                        │   │
│ │ 💬 Chat  │                                                     │   │
│ │ 📦 Skills│                                                     │   │
│ │ 🌿 Explore                                                      │
│ │ 🔍 Query │                                                     │   │
│ │ 📝 Record│                                                     │   │
│ │ 📜 Logs  │                                                     │   │
│ │ ⚙️ Settings                                                     │
│ │ ──────── │                                                     │   │
│ │  [◄◄]    │                                                     │   │
│ └──────────┴────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Annotations per element:**

| Element | Width | Height | Glass | Radius | Z |
|---|---|---|---|---|---|
| BackgroundMesh | 1440 | 900 | — | — | 0 |
| Sidebar | 256px | 900px | regular | — | 20 |
| Header | 1184px (1440−256) | 56px | thick | — | 10 |
| Nav item (expanded) | 240px (256−8−8) | 40px | transparent/accent | 10px | — |
| Brand row | 256px | 56px | inherits sidebar | — | — |
| Collapse toggle | 28px | 28px | ghost | 10px | — |

### 7.3 Frame Layout — Desktop Collapsed (1440 × 900)

```
┌─────────────────────────────────────────────────────────────────────┐
│ Background Mesh                                                      │
│ ┌────┬───────────────────────────────────────────────────────────┐  │
│ │Side│ Header (56px, glass-thick)                                │  │
│ │56px│ [Page Title]                    [☀️ Theme] [≡ Toggle]      │  │
│ │glass├───────────────────────────────────────────────────────────┤  │
│ │    │                                                            │  │
│ │ ✏️ │  Content Area (placeholder)                                │  │
│ │────│                                                            │  │
│ │ 💬 │                                                            │  │
│ │ 📦 │                                                            │  │
│ │ 🌿 │                                                            │  │
│ │ 🔍 │                                                            │  │
│ │ 📝 │                                                            │  │
│ │ 📜 │                                                            │  │
│ │ ⚙️ │                                                            │  │
│ │────│                                                            │  │
│ │[►►]│                                                            │  │
│ └────┴───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

**Collapsed sidebar annotations:**

| Element | Width | Notes |
|---|---|---|
| Sidebar | 56px | Icons centered, labels hidden |
| Header | 1384px (1440−56) | Same content as expanded |
| Nav item (collapsed) | 40px centered | Icon only, Tooltip `side="right"` on hover |

### 7.4 Frame Layout — Mobile Drawer Closed (390 × 844)

```
┌───────────────────────────────┐
│ Background Mesh                │
│ ┌───────────────────────────┐ │
│ │ Header (56px, glass-thick)│ │
│ │ [≡] Page Title   [☀️]     │ │
│ ├───────────────────────────┤ │
│ │                            │ │
│ │ Content Area               │ │
│ │ (full width, no sidebar)   │ │
│ │                            │ │
│ │                            │ │
│ │                            │ │
│ │                            │ │
│ │                            │ │
│ └───────────────────────────┘ │
└───────────────────────────────┘
```

**Mobile annotations:**

| Element | Width | Height | Notes |
|---|---|---|---|
| Header | 390px | 56px | Hamburger left, title, theme toggle right |
| Content | 390px | 788px | Full bleed, no sidebar |
| Hamburger | 28px | 28px | Opens drawer via `setDrawerOpen(true)` |

### 7.5 Frame Layout — Mobile Drawer Open (390 × 844)

```
┌───────────────────────────────┐
│ Background Mesh                │
│ ┌───────────────────────────┐ │
│ │ Header (behind overlay)   │ │
│ ├───────────────────────────┤ │
│ │                            │ │
│ │ Content (dimmed by overlay)│ │
│ │                            │ │
│ │                            │ │
│ │                            │ │
│ │                            │ │
│ │                            │ │
│ └───────────────────────────┘ │
│ ┌────────────┬────────────────┤
│ │ Drawer     │ Overlay        │
│ │ 256px      │ (black/40,     │
│ │ glass-reg  │  blur(4px))    │
│ │            │                │
│ │ ✏️ Mark [✕]│                │
│ │ ────────── │                │
│ │ 💬 Chat    │                │
│ │ 📦 Skills  │                │
│ │ 🌿 Explore │                │
│ │ 🔍 Query   │                │
│ │ 📝 Record  │                │
│ │ 📜 Logs    │                │
│ │ ⚙️ Settings│                │
│ └────────────┴────────────────┤
└───────────────────────────────┘
```

**Drawer annotations:**

| Element | Width | Height | Glass | Radius | Z |
|---|---|---|---|---|---|
| Overlay | 390px | 844px | blur(4px), black/40 | — | 40 |
| Drawer panel | 256px | 844px | regular | right: 18px | 50 |
| Drawer header | 256px | 56px | inherits panel | — | — |
| Close button | 28px | 28px | ghost | 10px | — |
| Nav items | same as sidebar expanded | — | — | — |

### 7.6 Figma Component Structure

**Component names and variants:**

| Component | Variants | Properties |
|---|---|---|
| `BackgroundMesh` | `theme`: Light, Dark | — |
| `Sidebar` | `state`: Expanded, Collapsed; `theme`: Light, Dark | `activeRoute`: chat / skills / … |
| `SidebarNavItem` | `state`: Default, Hover, Active; `layout`: Expanded, Collapsed; `theme`: Light, Dark | `icon`, `label` |
| `Header` | `device`: Desktop, Mobile; `theme`: Light, Dark | `pageTitle` |
| `MobileDrawer` | `state`: Open, Closed; `theme`: Light, Dark | `activeRoute` |
| `AppLayout` | `layout`: Desktop-Expanded, Desktop-Collapsed, Mobile-Closed, Mobile-Open; `theme`: Light, Dark | — |

---

## 8. Responsive Behavior

### 8.1 Breakpoint Matrix

| Breakpoint | Viewport | Sidebar | Header | Nav Access |
|---|---|---|---|---|
| **< md** (< 768px) | Phone | Hidden | Hamburger + title + theme | MobileDrawer (Sheet) |
| **md** (768–1023px) | Tablet portrait | Collapsed (56px icons) | Title + theme + sidebar toggle | Sidebar with tooltips |
| **≥ lg** (≥ 1024px) | Desktop | Expanded (256px) | Title + theme + sidebar toggle | Full sidebar |

### 8.2 Behavior Rules

**Sidebar collapse state persistence:**
- User toggle is stored in `useUiStore.sidebarCollapsed` and persists across routes.
- On `≥ lg`, default state is **expanded** unless user has toggled collapsed.
- On `md` to `< lg`, default state is **collapsed** unless user has toggled expanded.
- On `< md`, sidebar is always hidden; collapse state is irrelevant.

**MobileDrawer behavior:**
- Opens via hamburger button in header.
- Closes on: overlay click, Escape key, NavLink click, close button click.
- Drawer state stored in `useUiStore.drawerOpen`.
- Route changes (NavLink click) always close the drawer.

**Header content shifts:**

| Breakpoint | Left Group | Right Group |
|---|---|---|
| < md | `[≡ Hamburger]` + Page Title | Theme Toggle |
| ≥ md | Page Title | Theme Toggle + Sidebar Toggle |

**Main content area:**
- Always takes `flex-1` of remaining space after sidebar/header.
- `overflow-auto` enables independent scrolling.
- Content never scrolls behind the header (header is sticky at top).

### 8.3 Transition Between Breakpoints

| Transition | Effect |
|---|---|
| Mobile → Tablet | Sidebar appears collapsed, hamburger disappears, sidebar toggle appears in header |
| Tablet → Desktop | Sidebar expands from collapsed to expanded (unless user toggled collapsed) |
| Desktop → Tablet | Sidebar collapses to icons |
| Tablet → Mobile | Sidebar disappears, hamburger appears, collapse state preserved |

---

## 9. Animation Specification

### 9.1 Sidebar Width Transition

| Property | Value |
|---|---|
| Duration | 300ms |
| Easing | `cubic-bezier(0.4, 0, 0.2, 1)` (ease-in-out) |
| Property | `width` |
| CSS | `transition-[width] duration-300 ease-in-out` |

**Content behavior during transition:**
- Nav labels fade out (opacity 1 → 0) in first 100ms.
- Width transitions over full 300ms.
- Nav labels (if expanding) fade in (opacity 0 → 1) in last 100ms after width settles.
- Implementation: conditionally render labels based on `collapsed` state with a small delay, or use `opacity` + `overflow-hidden` to clip content.

### 9.2 MobileDrawer Slide

| Phase | Duration | Easing | Transform |
|---|---|---|---|
| Open (slide in) | 300ms | `ease-out` | `translateX(-100%) → translateX(0)` |
| Close (slide out) | 200ms | `ease-in` | `translateX(0) → translateX(-100%)` |

**Overlay:**

| Phase | Duration | Easing | Effect |
|---|---|---|---|
| Fade in | 300ms | `ease-out` | `opacity 0 → 1` |
| Fade out | 200ms | `ease-in` | `opacity 1 → 0` |

### 9.3 Nav Item Hover

| Property | Duration | Easing |
|---|---|---|
| Background color | 150ms | `ease-out` |
| Text color | 150ms | `ease-out` |

CSS: `transition-colors duration-150 ease-out`

### 9.4 Theme Switch

| Property | Duration | Easing | Notes |
|---|---|---|---|
| Background mesh | 500ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Smooth gradient cross-fade |
| Glass surfaces | 500ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Background + border + blur transition |
| Text colors | 150ms | `ease-out` | Fast text swap |

CSS: Use `transition-glass` token (500ms) on all glass surfaces for the `background-color, backdrop-filter, border-color, box-shadow` properties.

> **Implementation note:** Theme switching toggles the `.dark` class on `<html>`. All CSS custom properties change simultaneously. The `transition-glass` class on the mesh, sidebar, and header ensures a smooth cross-fade rather than a hard swap.

### 9.5 Active Nav Indicator

| Property | Duration | Easing | Effect |
|---|---|---|---|
| Background fill | 150ms | `ease-out` | Transparent → `sidebar-accent` |
| Left stripe | 200ms | `spring cubic-bezier(0.34, 1.56, 0.64, 1)` | `scaleY(0) → scaleY(1)` from center |

### 9.6 Reduced Motion

Under `prefers-reduced-motion: reduce`:

| Animation | Fallback |
|---|---|
| Sidebar width | Instant (0ms) |
| Drawer slide | Fade only (opacity transition, no transform) |
| Nav hover | Instant |
| Theme switch | Instant |
| Active stripe | Instant, no spring |

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 9.7 Animation Token Summary

| Token | Duration | Easing | Usage |
|---|---|---|---|
| `motion/fast` | 120ms | ease-out | Hover colors |
| `motion/standard` | 200ms | ease-in-out | Most interactions |
| `motion/slow` | 300ms | ease-in-out | Sidebar width, drawer slide |
| `motion/spring` | 400ms | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Active stripe |
| `motion/glass` | 500ms | ease-in-out | Theme switch, glass material change |

---

## Appendix A: Accessibility Checklist

| Check | Details |
|---|---|
| **Sidebar landmarks** | `<aside role="navigation" aria-label="Main navigation">` |
| **MobileDrawer focus trap** | Radix Dialog default; focus cycles within drawer when open |
| **Escape key** | Closes MobileDrawer; no effect on fixed sidebar |
| **Hamburger `aria-label`** | `"Open navigation menu"` |
| **Collapse toggle `aria-label`** | `"Collapse sidebar"` / `"Expand sidebar"` |
| **Active nav `aria-current`** | `"page"` on the active NavLink |
| **Theme toggle tooltip** | Describes current theme: "浅色模式" / "深色模式" / "跟随系统" |
| **Reduced motion** | All animations disabled per §9.6 |
| **Color contrast** | All text/background pairs from tokens.md §1.6 (≥AA) |
| **Keyboard nav** | Tab order: hamburger → nav items → collapse toggle → header controls |
| **Skip link** | Consider adding `Skip to main content` link as first focusable element |

---

## Appendix B: Token Cross-Reference

### Color Tokens Used

| Token | Tailwind Class | Used In |
|---|---|---|
| `--color-background` | `bg-background` | Mesh base layer |
| `--color-foreground` | `text-foreground` | Page title, nav text |
| `--color-muted-foreground` | `text-muted-foreground` | Theme/collapse icons default |
| `--color-primary` | `text-primary` | PenLine icon, active stripe |
| `--color-accent` | `bg-accent` | Nav hover, button hover |
| `--color-accent-foreground` | `text-accent-foreground` | Nav hover text |
| `--color-sidebar-background` | `bg-sidebar-background` | Sidebar fallback (non-glass) |
| `--color-sidebar-foreground` | `text-sidebar-foreground` | Sidebar text |
| `--color-sidebar-primary` | `text-sidebar-primary` | Brand icon |
| `--color-sidebar-accent` | `bg-sidebar-accent` | Nav hover/active bg |
| `--color-sidebar-accent-foreground` | `text-sidebar-accent-foreground` | Nav hover/active text |
| `--color-sidebar-border` | `border-sidebar-border` | Sidebar border fallback |
| `--color-sidebar-ring` | `ring-sidebar-ring` | Sidebar focus ring |

### Glass Tier References

| Element | Tier | Class Pattern |
|---|---|---|
| Sidebar | regular | `bg-white/65 backdrop-blur-[24px] saturate-[160%] border-white/40` |
| Header | thick | `bg-white/78 backdrop-blur-[40px] saturate-[180%] border-white/45` |
| MobileDrawer | regular | Same as sidebar |
| MobileDrawer overlay | — | `bg-black/40 backdrop-blur-[4px]` |

### Z-Index References

| Element | Token | Value |
|---|---|---|
| BackgroundMesh | `z-base` | 0 |
| Content layer | — | 10 (relative) |
| Sticky Header | `z-sticky` | 10 |
| Sidebar | `z-sidebar` | 20 |
| MobileDrawer overlay | `z-modal-backdrop` | 40 |
| MobileDrawer panel | `z-modal` | 50 |
| Tooltips | `z-tooltip` | 60 |

---

## Appendix C: Implementation Checklist

### Phase 1: Token Infrastructure
- [ ] Add z-index custom properties to `globals.css` `@theme` block
- [ ] Add `--shadow-resting`, `--shadow-elevated`, `--shadow-dragging` tokens
- [ ] Verify updated radius tokens in `globals.css` (sm=10px, md=14px, lg=18px)
- [ ] Install `tailwindcss-animate` plugin if not present

### Phase 2: Background Mesh
- [ ] Create `web/src/components/background-mesh.tsx` + CSS
- [ ] Add mesh CSS classes to `globals.css` (`.mesh-light`, `.mesh-dark`)
- [ ] Verify mesh renders beneath all glass surfaces in both themes

### Phase 3: Shell Components
- [ ] Update `sidebar.tsx` — glass-tier-regular, nav item styling, active stripe, brand row
- [ ] Update `header.tsx` — glass-tier-thick, sticky positioning, responsive left/right groups
- [ ] Update `mobile-drawer.tsx` — glass-tier-regular override, drawer header, close on nav
- [ ] Update `app-layout.tsx` — BackgroundMesh, z-index layering, responsive flex structure

### Phase 4: Responsive Behavior
- [ ] Verify sidebar hidden on < md, collapsed on md–lg, expanded on ≥ lg
- [ ] Verify MobileDrawer opens/closes correctly on mobile
- [ ] Verify header content shifts between mobile and desktop
- [ ] Verify collapse state persists across route changes

### Phase 5: Animation & Motion
- [ ] Sidebar width transition (300ms ease-in-out)
- [ ] Nav hover transition (150ms ease-out)
- [ ] MobileDrawer slide (300ms open / 200ms close)
- [ ] Theme switch (500ms glass transition)
- [ ] Active nav stripe (200ms spring)
- [ ] Reduced motion fallback (instant)

### Phase 6: Visual QA
- [ ] Light mode: warm mesh visible through glass sidebar and header
- [ ] Dark mode: candlelight ember glow visible through glass
- [ ] No hard edges or flat gaps visible through any glass surface
- [ ] Glass surfaces readable: text contrast ≥AA on all backgrounds
- [ ] Mobile drawer overlay dims content appropriately
- [ ] Sidebar collapse/expand smooth without layout shift
- [ ] All 8 Figma frames match implemented behavior

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
