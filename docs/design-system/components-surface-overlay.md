# Surface & Overlay Component Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion specs:** `components-button-badge.md` · `components-form-inputs.md`
> **Implementation:** `web/src/components/ui/{card,dialog,sheet,popover,tooltip,tabs,separator}.tsx`

---

## Table of Contents

1. [Design Decisions](#1-design-decisions)
2. [Glass Tier Application Guide](#2-glass-tier-application-guide)
3. [Card](#3-card)
4. [Dialog (Radix)](#4-dialog-radix)
5. [Sheet (CVA — 4 sides)](#5-sheet-cva--4-sides)
6. [Popover (Radix)](#6-popover-radix)
7. [Tooltip (Radix)](#7-tooltip-radix)
8. [Tabs (Radix)](#8-tabs-radix)
9. [Separator (Radix)](#9-separator-radix)
10. [Figma Component Structure](#10-figma-component-structure)
11. [Appendix A: Accessibility Checklist](#appendix-a-accessibility-checklist)
12. [Appendix B: Token Cross-Reference](#appendix-b-token-cross-reference)
13. [Appendix C: Implementation Checklist](#appendix-c-implementation-checklist)

---

## 1. Design Decisions

### 1.1 Glass Tier Assignment Principle

Glass tiers follow a **visual weight ladder** aligned to component elevation and interaction depth. Higher-tier glass is reserved for components that demand the most visual separation from the background.

| Component | Glass Tier | Rationale |
|---|---|---|
| Card | thin | Content containers; moderate blur is readable but distinct |
| Dialog | thick | Focused overlays need maximum visual separation |
| Sheet | regular | Side panels sit between cards and full modal depth |
| Popover | thin | Lightweight menus — thin keeps them airy |
| Tooltip | **ultra-thin (inverted solid)** | Contrast-first exception for small text; see §1.2 |
| Tabs List | ultra-thin | Navigation chrome; minimal glass for subtle grouping |
| Separator | none (token-based) | Line element; no glass treatment |

### 1.2 Tooltip Contrast Exception

Tooltip is the **one deliberate non-glass surface** in the system. For 12px text in a tight container (max 250px), readability and edge definition beat glass consistency. Both modes use an **inverted** background for maximum contrast:

| Mode | Background | Text |
|---|---|---|
| Light | `#2B2116` (dark ink) | `#F8F1E7` (warm white) |
| Dark | `#F8F1E7` (warm white) | `#2B2116` (dark ink) |

This is an intentional exception documented in the glass application guide (§2), not a fallback. Any future micro-surface with similar contrast requirements (≤14px text, ≤250px width) should follow the same pattern.

### 1.3 Radius Principle: Scale + Modality

Radius follows a function of **component scale** and **interaction modality**, not elevation alone:

| Component | Radius | Scale Factor | Modality |
|---|---|---|---|
| Tooltip | 4px (`radius-xs`) | Small (≤250px) | Transient micro-surface |
| Tabs List | 10px (`radius-sm`) | Medium bar | Persistent navigation |
| Card | 14px (`radius-md`) | Medium container | Static content |
| Popover | 14px (`radius-md`) | Medium panel | Transient menu |
| Sheet edges | 18px (`radius-lg`) | Large panel | Side panel overlay |
| Dialog | 22px (`radius-xl`) | Large centered | Focused modal |

**Rule:** Larger, more modal surfaces get rounder corners. Small transient surfaces stay tight.

### 1.4 Sheet Implementation: Dialog + CVA

Sheet is built on **Radix Dialog** with CVA side variants rather than a dedicated Radix Sheet primitive. This preserves:

- Focus trapping via `Dialog.Content`
- Escape key handling via `Dialog.Root`
- Overlay click dismissal via `Dialog.Overlay`
- Consistent scroll locking behavior

**Modal behavior is explicit:** all Sheet instances are modal by default. Non-modal sheets (e.g., persistent side panels) must set `modal={false}` and handle scroll/focus independently.

### 1.5 Motion Hierarchy

| Component | Enter | Exit | Rationale |
|---|---|---|---|
| Tooltip | 100ms fade-in | 50ms fade-out | Fastest — transient, small |
| Popover | 150ms fade+scale | 100ms fade+scale | Quick — menu-level |
| Dialog | 180ms scale+fade | 120ms scale+fade | Substantial — focused task |
| Sheet | 300ms slide | 200ms slide | Slowest — large travel distance |
| Card hover | 200ms ease-out | 200ms ease-out | Gentle lift |
| Tabs indicator | 200ms spring | — | Intentional, not twitchy |

The hierarchy is: **Tooltip < Popover < Dialog < Sheet** — matching the visual weight ladder.

### 1.6 Radix Package Import Convention

All Radix primitives are imported from the unified `radix-ui` package:

```tsx
import { Dialog } from "radix-ui";   // Dialog.Root, Dialog.Trigger, etc.
import { Popover } from "radix-ui";  // Popover.Root, Popover.Trigger, etc.
import { Tooltip } from "radix-ui";  // Tooltip.Root, Tooltip.Trigger, etc.
import { Tabs } from "radix-ui";     // Tabs.Root, Tabs.List, etc.
import { Separator } from "radix-ui";// Separator.Root
```

### 1.7 Updated Token Reference

> ⚠️ **Note:** This spec uses the radius and glass tier values provided in the task specification, which differ from the initial `tokens.md` values. These values are **authoritative for Surface & Overlay components** and should be considered an update to the token system.

**Updated Radius Tokens:**

| Token | Value | Previous (tokens.md) |
|---|---|---|
| `radius-xs` | 4px | 4px (unchanged) |
| `radius-sm` | 10px | 6px |
| `radius-md` | 14px | 8px |
| `radius-lg` | 18px | 12px |
| `radius-xl` | 22px | 16px |
| `radius-full` | 9999px | 9999px (unchanged) |

**Updated Glass Tier Definitions:**

| Tier | `backdrop-filter` | Light BG | Dark BG | Border (light) | Border (dark) |
|---|---|---|---|---|---|
| **ultra-thin** | `blur(8px) saturate(120%)` | `white/0.45` | `#1A140F/0.50` | `white/0.35` | `white/0.10` |
| **thin** | `blur(16px) saturate(140%)` | `white/0.55` | `#1A140F/0.60` | `white/0.35` | `white/0.10` |
| **regular** | `blur(24px) saturate(160%)` | `white/0.65` | `#1A140F/0.70` | `white/0.40` | `white/0.12` |
| **thick** | `blur(40px) saturate(180%)` | `white/0.78` | `#1A140F/0.80` | `white/0.45` | `white/0.15` |

**Updated Shadow Tokens:**

| Token | CSS |
|---|---|
| `shadow-resting` | `0 1px 3px rgba(0,0,0,0.06)` |
| `shadow-elevated` | `0 4px 12px rgba(0,0,0,0.08)` |
| `shadow-dragging` | `0 12px 40px rgba(0,0,0,0.12)` |

---

## 2. Glass Tier Application Guide

### 2.1 Per-Component Assignment

| Component | Tier | Light Background | Dark Background | Border (Light) | Border (Dark) |
|---|---|---|---|---|---|
| **Card** (default) | thin | `rgba(255,255,255,0.55)` + `blur(16px)` | `rgba(26,20,15,0.60)` + `blur(16px)` | `rgba(255,255,255,0.35)` | `rgba(255,255,255,0.10)` |
| **Card** (elevated) | regular | `rgba(255,255,255,0.65)` + `blur(24px)` | `rgba(26,20,15,0.70)` + `blur(24px)` | `rgba(255,255,255,0.40)` | `rgba(255,255,255,0.12)` |
| **Dialog** content | thick | `rgba(255,255,255,0.78)` + `blur(40px)` | `rgba(26,20,15,0.80)` + `blur(40px)` | `rgba(255,255,255,0.45)` | `rgba(255,255,255,0.15)` |
| **Dialog** overlay | — | `rgba(0,0,0,0.40)` + `blur(4px)` | `rgba(0,0,0,0.40)` + `blur(4px)` | — | — |
| **Sheet** content | regular | `rgba(255,255,255,0.65)` + `blur(24px)` | `rgba(26,20,15,0.70)` + `blur(24px)` | `rgba(255,255,255,0.40)` | `rgba(255,255,255,0.12)` |
| **Sheet** overlay | — | `rgba(0,0,0,0.40)` + `blur(4px)` | `rgba(0,0,0,0.40)` + `blur(4px)` | — | — |
| **Popover** content | thin | `rgba(255,255,255,0.55)` + `blur(16px)` | `rgba(26,20,15,0.60)` + `blur(16px)` | `rgba(255,255,255,0.35)` | `rgba(255,255,255,0.10)` |
| **Tooltip** | **inverted solid** | `#2B2116` | `#F8F1E7` | — | — |
| **Tabs List** | ultra-thin | `rgba(255,255,255,0.45)` + `blur(8px)` | `rgba(26,20,15,0.50)` + `blur(8px)` | `rgba(255,255,255,0.35)` | `rgba(255,255,255,0.10)` |
| **Separator** (normal) | none | `border` token | `border` token | — | — |
| **Separator** (on glass) | none | `rgba(255,255,255,0.10)` | `rgba(255,255,255,0.06)` | — | — |

### 2.2 Decision Tree

When adding a new surface component, use this decision tree:

```
1. Does it contain text ≤14px at max width ≤250px?
   → YES: Use inverted solid background (Tooltip exception)
   → NO: Continue

2. Is it a persistent navigation chrome element?
   → YES: Use ultra-thin tier
   → NO: Continue

3. Is it a focused overlay that captures all attention?
   → YES: Use thick tier
   → NO: Continue

4. Is it a large side panel?
   → YES: Use regular tier
   → NO: Continue

5. Is it a content container or lightweight menu?
   → YES: Use thin tier
   → NO: Re-evaluate; likely needs no glass
```

---

## 3. Card

### 3.1 Anatomy

| Property | Default | Elevated |
|---|---|---|
| Border radius | 14px (`radius-md`) | 14px (`radius-md`) |
| Border | 1px solid glass-tier-thin border | 1px solid glass-tier-regular border |
| Background | glass-tier-thin | glass-tier-regular |
| Shadow | `shadow-resting` | `shadow-elevated` |
| Overflow | hidden (clips border-radius) | hidden |

### 3.2 Sub-Components

**Card (root):**
- Auto Layout: Vertical
- Padding: none (delegated to sub-components)
- Overflow: hidden

**CardHeader:**
- Padding: 24px (`p-6`)
- Flex direction: column
- Gap: 8px (`gap-2`)

**CardTitle:**
- Typography: `title-3` (18px / 600) or `headline` (16px / 600) depending on context
- Color: `foreground`

**CardDescription:**
- Typography: `callout` (14px / 400)
- Color: `muted-foreground`

**CardContent:**
- Padding: 0 24px 24px (`px-6 pb-6`)

**CardFooter:**
- Padding: 0 24px 24px (`px-6 pb-6`)
- Flex direction: row
- Align items: center
- Gap: 8px (`gap-2`)
- Optional: `border-top: 1px solid` when visually separating footer actions

### 3.3 State Color Matrix

| State | Light Background | Light Shadow | Light Border | Dark Background | Dark Shadow | Dark Border |
|---|---|---|---|---|---|---|
| **default** | `rgba(255,255,255,0.55)` + `blur(16px) saturate(140%)` | `0 1px 3px rgba(0,0,0,0.06)` | `rgba(255,255,255,0.35)` | `rgba(26,20,15,0.60)` + `blur(16px) saturate(140%)` | `0 1px 3px rgba(0,0,0,0.06)` | `rgba(255,255,255,0.10)` |
| **elevated** | `rgba(255,255,255,0.65)` + `blur(24px) saturate(160%)` | `0 4px 12px rgba(0,0,0,0.08)` | `rgba(255,255,255,0.40)` | `rgba(26,20,15,0.70)` + `blur(24px) saturate(160%)` | `0 4px 12px rgba(0,0,0,0.08)` | `rgba(255,255,255,0.12)` |
| **hover** | same as default | `0 4px 12px rgba(0,0,0,0.08)` | same | same as default | `0 4px 12px rgba(0,0,0,0.08)` | same |
| **hover elevated** | same as elevated | `0 4px 12px rgba(0,0,0,0.08)` | same | same as elevated | `0 4px 12px rgba(0,0,0,0.08)` | same |

### 3.4 Motion

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Hover (shadow + lift) | 200ms | ease-out | `transform: translateY(-1px)`, shadow elevation |

### 3.5 Component Code

```tsx
// web/src/components/ui/card.tsx
import { forwardRef, type HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

// ─── Card (root) ───
const Card = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement> & { elevated?: boolean }
>(({ className, elevated, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      [
        "rounded-[14px] overflow-hidden text-card-foreground",
        "border transition-[box-shadow,transform] duration-200 ease-out",
        // Default (glass-tier-thin)
        "bg-white/55 backdrop-blur-[16px] saturate-[140%]",
        "border-white/35",
        "dark:bg-[rgba(26,20,15,0.60)] dark:border-white/10",
        // Shadow
        "shadow-[0_1px_3px_rgba(0,0,0,0.06)]",
        // Hover
        "hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)] hover:-translate-y-px",
      ].join(" "),
      elevated && [
        // Glass-tier-regular
        "bg-white/65 backdrop-blur-[24px] saturate-[160%]",
        "border-white/40",
        "dark:bg-[rgba(26,20,15,0.70)] dark:border-white/12",
        // Elevated shadow
        "shadow-[0_4px_12px_rgba(0,0,0,0.08)]",
        "hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)]",
      ].join(" "),
      className,
    )}
    {...props}
  />
));
Card.displayName = "Card";

// ─── CardHeader ───
const CardHeader = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col gap-2 p-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

// ─── CardTitle ───
const CardTitle = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("text-[18px] font-semibold leading-tight text-foreground", className)}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

// ─── CardDescription ───
const CardDescription = forwardRef<
  HTMLParagraphElement,
  HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-[14px] text-muted-foreground", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

// ─── CardContent ───
const CardContent = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("px-6 pb-6", className)} {...props} />
));
CardContent.displayName = "CardContent";

// ─── CardFooter ───
const CardFooter = forwardRef<
  HTMLDivElement,
  HTMLAttributes<HTMLDivElement> & { separator?: boolean }
>(({ className, separator, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex items-center px-6 pb-6 gap-2",
      separator && "border-t border-white/10 dark:border-white/6",
      className,
    )}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };
```

---

## 4. Dialog (Radix)

### 4.1 Radix Composition

```
Dialog.Root
├── Dialog.Trigger          (user provides — typically a Button)
├── Dialog.Portal
│   ├── Dialog.Overlay      (black/40, backdrop-blur-sm)
│   └── Dialog.Content      (glass-tier-thick, radius-xl, centered)
│       ├── Dialog.Close    (ghost icon button, top-right)
│       ├── Dialog.Header   (flex-col, gap-2, p-6)
│       │   ├── Dialog.Title      (title-2: 22px/600)
│       │   └── Dialog.Description (callout: 14px, muted-foreground)
│       ├── div             (content area, px-6)
│       └── Dialog.Footer   (flex row, justify-end, gap-2, p-6)
```

### 4.2 Anatomy

**Overlay:**

| Property | Value |
|---|---|
| Background | `rgba(0,0,0,0.40)` |
| Backdrop filter | `blur(4px)` |
| Position | fixed, inset 0 |
| Z-index | `z-modal-backdrop` (40) |
| Animation | fade-in 180ms ease-out |

**Content:**

| Property | Value |
|---|---|
| Border radius | 22px (`radius-xl`) |
| Background | glass-tier-thick |
| Shadow | `shadow-dragging` (0 12px 40px rgba(0,0,0,0.12)) |
| Max width | 512px (`max-w-lg`) |
| Width | `w-full` (within max) |
| Position | fixed, centered |
| Z-index | `z-modal` (50) |
| Padding | 0 (delegated to sub-components) |
| Focus trap | enabled (Radix default) |

### 4.3 Sub-Components

**DialogHeader:**
- Padding: 24px (`p-6`)
- Flex direction: column
- Gap: 8px (`gap-2`)

**DialogTitle:**
- Typography: `title-2` (22px / 600)
- Color: `foreground`

**DialogDescription:**
- Typography: `callout` (14px / 400)
- Color: `muted-foreground`

**DialogFooter:**
- Padding: 24px (`p-6`)
- Flex direction: row
- Justify: flex-end
- Gap: 8px (`gap-2`)

**DialogClose:**
- Ghost icon button (X icon, 16px)
- Position: absolute, top 16px, right 16px
- Color: `muted-foreground`
- Hover: `accent` background

### 4.4 State Color Matrix

**Content:**

| Mode | Background | Border | Shadow |
|---|---|---|---|
| **Light** | `rgba(255,255,255,0.78)` + `blur(40px) saturate(180%)` | `rgba(255,255,255,0.45)` | `0 12px 40px rgba(0,0,0,0.12)` |
| **Dark** | `rgba(26,20,15,0.80)` + `blur(40px) saturate(180%)` | `rgba(255,255,255,0.15)` | `0 12px 40px rgba(0,0,0,0.12)` |

### 4.5 Motion

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Open (content) | 180ms | ease-out | `scale(0.95) → scale(1)` + `opacity 0 → 1` |
| Close (content) | 120ms | ease-in | `scale(1) → scale(0.95)` + `opacity 1 → 0` |
| Open (overlay) | 180ms | ease-out | `opacity 0 → 1` |
| Close (overlay) | 120ms | ease-in | `opacity 1 → 0` |

### 4.6 Component Code

```tsx
// web/src/components/ui/dialog.tsx
import { Dialog } from "radix-ui";
import { X } from "lucide-react";
import * as React from "react";
import { cn } from "@/lib/utils";

// ─── Overlay ───
const DialogOverlay = React.forwardRef<
  React.ComponentRef<typeof Dialog.Overlay>,
  React.ComponentPropsWithoutRef<typeof Dialog.Overlay>
>(({ className, ...props }, ref) => (
  <Dialog.Overlay
    ref={ref}
    className={cn(
      [
        "fixed inset-0 z-40",
        "bg-black/40 backdrop-blur-[4px]",
        "data-[state=open]:animate-in data-[state=open]:fade-in-0",
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0",
        "data-[state=closed]:duration-120 data-[state=open]:duration-180",
      ].join(" "),
      className,
    )}
    {...props}
  />
));
DialogOverlay.displayName = "DialogOverlay";

// ─── Content ───
const DialogContent = React.forwardRef<
  React.ComponentRef<typeof Dialog.Content>,
  React.ComponentPropsWithoutRef<typeof Dialog.Content>
>(({ className, children, ...props }, ref) => (
  <Dialog.Portal>
    <DialogOverlay />
    <Dialog.Content
      ref={ref}
      className={cn(
        [
          "fixed left-1/2 top-1/2 z-50 w-full max-w-lg",
          "-translate-x-1/2 -translate-y-1/2",
          "rounded-[22px] overflow-hidden",
          "border shadow-[0_12px_40px_rgba(0,0,0,0.12)]",
          // Glass-tier-thick
          "bg-white/78 backdrop-blur-[40px] saturate-[180%]",
          "border-white/45",
          "dark:bg-[rgba(26,20,15,0.80)] dark:border-white/15",
          "text-foreground",
          // Focus trap handled by Radix
          "focus:outline-none",
          // Animation
          "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95",
          "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
          "data-[state=closed]:duration-120 data-[state=open]:duration-180",
        ].join(" "),
        className,
      )}
      {...props}
    >
      {children}
      <Dialog.Close
        className={cn(
          [
            "absolute right-4 top-4",
            "inline-flex h-7 w-7 items-center justify-center rounded-md",
            "text-muted-foreground transition-colors duration-150",
            "hover:bg-accent hover:text-accent-foreground",
            "focus:outline-none focus:ring-2 focus:ring-ring",
          ].join(" "),
        )}
        aria-label="Close"
      >
        <X className="size-4" />
      </Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
));
DialogContent.displayName = "DialogContent";

// ─── Header ───
const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("flex flex-col gap-2 p-6", className)}
    {...props}
  />
);
DialogHeader.displayName = "DialogHeader";

// ─── Title ───
const DialogTitle = React.forwardRef<
  React.ComponentRef<typeof Dialog.Title>,
  React.ComponentPropsWithoutRef<typeof Dialog.Title>
>(({ className, ...props }, ref) => (
  <Dialog.Title
    ref={ref}
    className={cn("text-[22px] font-semibold text-foreground", className)}
    {...props}
  />
));
DialogTitle.displayName = "DialogTitle";

// ─── Description ───
const DialogDescription = React.forwardRef<
  React.ComponentRef<typeof Dialog.Description>,
  React.ComponentPropsWithoutRef<typeof Dialog.Description>
>(({ className, ...props }, ref) => (
  <Dialog.Description
    ref={ref}
    className={cn("text-[14px] text-muted-foreground", className)}
    {...props}
  />
));
DialogDescription.displayName = "DialogDescription";

// ─── Footer ───
const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("flex items-center justify-end gap-2 p-6", className)}
    {...props}
  />
);
DialogFooter.displayName = "DialogFooter";

export {
  Dialog,
  DialogOverlay,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
};
```

---

## 5. Sheet (CVA — 4 sides)

### 5.1 Architecture

Built on Radix Dialog. The `Sheet` component wraps `Dialog.Content` with CVA side variants controlling position, size, and rounded corners.

**Modal behavior:** All Sheet instances are **modal** by default (`Dialog.Root` default behavior). For persistent side panels that should not trap focus or lock scroll, set `modal={false}` on `Dialog.Root`.

### 5.2 Side Variants

| Side | Width/Height | Position | Border Radius | Rounded Sides |
|---|---|---|---|---|
| **left** | `w-64` (default) or `w-80` | fixed, left-0, top-0, bottom-0 | 18px | right edges |
| **right** | `w-64` (default) or `w-80` | fixed, right-0, top-0, bottom-0 | 18px | left edges |
| **top** | `h-auto` (content-driven) | fixed, top-0, left-0, right-0 | 18px | bottom edges |
| **bottom** | `h-auto` (content-driven) | fixed, bottom-0, left-0, right-0 | 18px | top edges |

### 5.3 Anatomy

**Overlay:** Same as Dialog overlay (§4.2).

**Content:**

| Property | Value |
|---|---|
| Background | glass-tier-regular |
| Shadow | `shadow-dragging` |
| Z-index | `z-modal` (50) |
| Focus trap | enabled (Radix default) |

### 5.4 State Color Matrix

**Content (same for all sides):**

| Mode | Background | Border | Shadow |
|---|---|---|---|
| **Light** | `rgba(255,255,255,0.65)` + `blur(24px) saturate(160%)` | `rgba(255,255,255,0.40)` | `0 12px 40px rgba(0,0,0,0.12)` |
| **Dark** | `rgba(26,20,15,0.70)` + `blur(24px) saturate(160%)` | `rgba(255,255,255,0.12)` | `0 12px 40px rgba(0,0,0,0.12)` |

### 5.5 Motion

| Side | Open Animation | Close Animation | Duration | Easing |
|---|---|---|---|---|
| **left** | `translateX(-100%) → translateX(0)` | reverse | 300ms | ease-out |
| **right** | `translateX(100%) → translateX(0)` | reverse | 300ms | ease-out |
| **top** | `translateY(-100%) → translateY(0)` | reverse | 300ms | ease-out |
| **bottom** | `translateY(100%) → translateY(0)` | reverse | 300ms | ease-out |

### 5.6 Close Button Placement

| Side | Close Position |
|---|---|
| left | top-right |
| right | top-left |
| top | top-right |
| bottom | top-right |

### 5.7 Component Code

```tsx
// web/src/components/ui/sheet.tsx
import { Dialog } from "radix-ui";
import { X } from "lucide-react";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "@/lib/utils";

// ─── Overlay (reuses Dialog overlay) ───
const SheetOverlay = React.forwardRef<
  React.ComponentRef<typeof Dialog.Overlay>,
  React.ComponentPropsWithoutRef<typeof Dialog.Overlay>
>(({ className, ...props }, ref) => (
  <Dialog.Overlay
    ref={ref}
    className={cn(
      [
        "fixed inset-0 z-40",
        "bg-black/40 backdrop-blur-[4px]",
        "data-[state=open]:animate-in data-[state=open]:fade-in-0",
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0",
        "data-[state=closed]:duration-200 data-[state=open]:duration-300",
      ].join(" "),
      className,
    )}
    {...props}
  />
));
SheetOverlay.displayName = "SheetOverlay";

// ─── Content Variants ───
const sheetVariants = cva(
  [
    "fixed z-50 overflow-hidden",
    "border shadow-[0_12px_40px_rgba(0,0,0,0.12)]",
    // Glass-tier-regular
    "bg-white/65 backdrop-blur-[24px] saturate-[160%]",
    "border-white/40",
    "dark:bg-[rgba(26,20,15,0.70)] dark:border-white/12",
    // Animation base
    "data-[state=open]:animate-in data-[state=closed]:animate-out",
    "data-[state=closed]:duration-200 data-[state=open]:duration-300",
    "focus:outline-none",
  ].join(" "),
  {
    variants: {
      side: {
        top: [
          "inset-x-0 top-0 rounded-b-[18px]",
          "data-[state=open]:slide-in-from-top data-[state=closed]:slide-out-to-top",
        ].join(" "),
        bottom: [
          "inset-x-0 bottom-0 rounded-t-[18px]",
          "data-[state=open]:slide-in-from-bottom data-[state=closed]:slide-out-to-bottom",
        ].join(" "),
        left: [
          "inset-y-0 left-0 h-full w-64 rounded-r-[18px]",
          "data-[state=open]:slide-in-from-left data-[state=closed]:slide-out-to-left",
        ].join(" "),
        right: [
          "inset-y-0 right-0 h-full w-64 rounded-l-[18px]",
          "data-[state=open]:slide-in-from-right data-[state=closed]:slide-out-to-right",
        ].join(" "),
      },
      size: {
        default: "",
        wide: "", // overridden per side below
      },
    },
    compoundVariants: [
      { side: "left", size: "wide", class: "w-80" },
      { side: "right", size: "wide", class: "w-80" },
    ],
    defaultVariants: {
      side: "right",
      size: "default",
    },
  },
);

// ─── Content ───
const SheetContent = React.forwardRef<
  React.ComponentRef<typeof Dialog.Content>,
  React.ComponentPropsWithoutRef<typeof Dialog.Content> &
    VariantProps<typeof sheetVariants>
>(({ side, size, className, children, ...props }, ref) => (
  <Dialog.Portal>
    <SheetOverlay />
    <Dialog.Content
      ref={ref}
      className={cn(sheetVariants({ side, size }), className)}
      {...props}
    >
      {children}
      <Dialog.Close
        className={cn(
          [
            "absolute top-4",
            side === "right" ? "left-4" : "right-4",
            "inline-flex h-7 w-7 items-center justify-center rounded-md",
            "text-muted-foreground transition-colors duration-150",
            "hover:bg-accent hover:text-accent-foreground",
            "focus:outline-none focus:ring-2 focus:ring-ring",
          ].join(" "),
        )}
        aria-label="Close"
      >
        <X className="size-4" />
      </Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
));
SheetContent.displayName = "SheetContent";

// ─── Header ───
const SheetHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("flex flex-col gap-2 p-6", className)}
    {...props}
  />
);
SheetHeader.displayName = "SheetHeader";

// ─── Title ───
const SheetTitle = React.forwardRef<
  React.ComponentRef<typeof Dialog.Title>,
  React.ComponentPropsWithoutRef<typeof Dialog.Title>
>(({ className, ...props }, ref) => (
  <Dialog.Title
    ref={ref}
    className={cn("text-[22px] font-semibold text-foreground", className)}
    {...props}
  />
));
SheetTitle.displayName = "SheetTitle";

// ─── Description ───
const SheetDescription = React.forwardRef<
  React.ComponentRef<typeof Dialog.Description>,
  React.ComponentPropsWithoutRef<typeof Dialog.Description>
>(({ className, ...props }, ref) => (
  <Dialog.Description
    ref={ref}
    className={cn("text-[14px] text-muted-foreground", className)}
    {...props}
  />
));
SheetDescription.displayName = "SheetDescription";

// ─── Footer ───
const SheetFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("flex items-center justify-end gap-2 p-6", className)}
    {...props}
  />
);
SheetFooter.displayName = "SheetFooter";

export {
  Dialog as SheetRoot,
  SheetOverlay,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  sheetVariants,
};
```

---

## 6. Popover (Radix)

### 6.1 Radix Composition

```
Popover.Root
├── Popover.Trigger        (user provides)
├── Popover.Anchor         (optional, for positioning)
├── Popover.Portal
│   └── Popover.Content    (glass-tier-thin, radius-md)
│       └── Popover.Arrow  (optional, 8px)
│           └── Items inside: padding 8px 12px, hover=accent bg
```

### 6.2 Anatomy

**Content:**

| Property | Value |
|---|---|
| Border radius | 14px (`radius-md`) |
| Background | glass-tier-thin |
| Shadow | `shadow-elevated` (0 4px 12px rgba(0,0,0,0.08)) |
| Default width | 288px (`w-72`) — configurable |
| Padding | 4px (`p-1`) |
| Z-index | `z-dropdown` (30) |
| Side offset | 8px from trigger |

**Arrow:**

| Property | Value |
|---|---|
| Size | 8px |
| Fill | Glass background color (matches content) |
| Visibility | Optional — controlled by `showArrow` prop |

### 6.3 State Color Matrix

**Content:**

| Mode | Background | Border | Shadow |
|---|---|---|---|
| **Light** | `rgba(255,255,255,0.55)` + `blur(16px) saturate(140%)` | `rgba(255,255,255,0.35)` | `0 4px 12px rgba(0,0,0,0.08)` |
| **Dark** | `rgba(26,20,15,0.60)` + `blur(16px) saturate(140%)` | `rgba(255,255,255,0.10)` | `0 4px 12px rgba(0,0,0,0.08)` |

**Items inside Popover (when used as a menu):**

| State | Light Background | Light Text | Dark Background | Dark Text |
|---|---|---|---|---|
| **default** | transparent | `foreground` #2B2116 | transparent | `foreground` #F8F1E7 |
| **hover** | `accent` #F6E6CA | `accent-foreground` #2B2116 | `accent` #31261C | `accent-foreground` #F8F1E7 |
| **disabled** | transparent, 50% opacity | `muted-foreground` | same | same |

### 6.4 Motion

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Open | 150ms | ease-out | `fade-in` + `scale(0.96) → scale(1)` |
| Close | 100ms | ease-in | `fade-out` + `scale(1) → scale(0.96)` |

### 6.5 Component Code

```tsx
// web/src/components/ui/popover.tsx
import { Popover } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

// ─── Content ───
const PopoverContent = React.forwardRef<
  React.ComponentRef<typeof Popover.Content>,
  React.ComponentPropsWithoutRef<typeof Popover.Content> & {
    showArrow?: boolean;
  }
>(({ className, children, showArrow = false, sideOffset = 8, ...props }, ref) => (
  <Popover.Portal>
    <Popover.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        [
          "z-30 w-72 rounded-[14px] p-1",
          "border shadow-[0_4px_12px_rgba(0,0,0,0.08)]",
          // Glass-tier-thin
          "bg-white/55 backdrop-blur-[16px] saturate-[140%]",
          "border-white/35",
          "dark:bg-[rgba(26,20,15,0.60)] dark:border-white/10",
          "text-foreground",
          // Animation
          "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-[0.96]",
          "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-[0.96]",
          "data-[state=closed]:duration-100 data-[state=open]:duration-150",
        ].join(" "),
        className,
      )}
      {...props}
    >
      {children}
      {showArrow && (
        <Popover.Arrow
          className="fill-white/55 dark:fill-[rgba(26,20,15,0.60)]"
          width={8}
          height={8}
        />
      )}
    </Popover.Content>
  </Popover.Portal>
));
PopoverContent.displayName = "PopoverContent";

// ─── Popover Item (for menu-like usage) ───
const PopoverItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { disabled?: boolean }
>(({ className, disabled, ...props }, ref) => (
  <div
    ref={ref}
    role="menuitem"
    tabIndex={disabled ? -1 : 0}
    aria-disabled={disabled}
    className={cn(
      [
        "flex cursor-pointer select-none items-center rounded-[8px] px-3 py-2",
        "text-[14px] text-foreground",
        "transition-colors duration-100 ease-out",
        "outline-none",
        "hover:bg-accent hover:text-accent-foreground",
        "focus-visible:bg-accent",
      ].join(" "),
      disabled && "pointer-events-none opacity-50",
      className,
    )}
    {...props}
  />
));
PopoverItem.displayName = "PopoverItem";

export {
  Popover,
  PopoverContent,
  PopoverItem,
};
```

---

## 7. Tooltip (Radix)

### 7.1 Contrast-First Design

Tooltip uses an **inverted solid background** in both modes — this is an intentional exception to the glass tier system. At 12px text in a ≤250px container, readability and edge clarity outweigh glass consistency.

> **Why not glass?** A glass-tier tooltip would blur its background content, reducing the contrast of 12px text against a noisy, partially-transparent surface. The solid inverted treatment guarantees ≥15:1 contrast in both modes.

### 7.2 Anatomy

| Property | Value |
|---|---|
| Border radius | 4px (`radius-xs`) |
| Background (light) | `#2B2116` (dark ink) |
| Background (dark) | `#F8F1E7` (warm white) |
| Text (light) | `#F8F1E7` (warm white) |
| Text (dark) | `#2B2116` (dark ink) |
| Shadow | `shadow-resting` (0 1px 3px rgba(0,0,0,0.06)) |
| Typography | `caption` (12px / 400) |
| Max width | 250px |
| Padding | 6px 10px |
| Z-index | `z-tooltip` (60) |
| Side offset | 6px from trigger |

### 7.3 Arrow

| Property | Value |
|---|---|
| Size | 6px |
| Fill | Same as background (`#2B2116` light, `#F8F1E7` dark) |

### 7.4 State Color Matrix

| Mode | Background | Text | Shadow |
|---|---|---|---|
| **Light** | `#2B2116` | `#F8F1E7` | `0 1px 3px rgba(0,0,0,0.06)` |
| **Dark** | `#F8F1E7` | `#2B2116` | `0 1px 3px rgba(0,0,0,0.06)` |

### 7.5 Motion

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Open | 100ms | ease-out | `fade-in` (opacity 0 → 1) |
| Close | 50ms | ease-in | `fade-out` (opacity 1 → 0) |
| Delay (show) | 0ms | — | Immediate on hover |
| Delay (hide) | 0ms | — | Immediate on leave |

> **Note:** The 0ms delay preserves the current application behavior. If tooltips feel jarring in dense UI areas, increase to `delayDuration={200}` on `Tooltip.Provider`.

### 7.6 Side Variants

| Side | Offset | Default? |
|---|---|---|
| **top** | 6px | ✅ default |
| **right** | 6px | |
| **bottom** | 6px | |
| **left** | 6px | |

### 7.7 Component Code

```tsx
// web/src/components/ui/tooltip.tsx
import { Tooltip } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

// ─── Provider ───
const TooltipProvider = Tooltip.Provider;

// ─── Content ───
const TooltipContent = React.forwardRef<
  React.ComponentRef<typeof Tooltip.Content>,
  React.ComponentPropsWithoutRef<typeof Tooltip.Content>
>(({ className, children, sideOffset = 6, ...props }, ref) => (
  <Tooltip.Content
    ref={ref}
    sideOffset={sideOffset}
    className={cn(
      [
        "z-60 max-w-[250px] rounded-[4px] px-2.5 py-1.5",
        "text-[12px] leading-[1.4]",
        "shadow-[0_1px_3px_rgba(0,0,0,0.06)]",
        // Inverted solid background — deliberate non-glass exception
        "bg-[#2B2116] text-[#F8F1E7]",
        "dark:bg-[#F8F1E7] dark:text-[#2B2116]",
        // Animation
        "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:duration-100",
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:duration-50",
      ].join(" "),
      className,
    )}
    {...props}
  >
    {children}
    <Tooltip.Arrow
      className="fill-[#2B2116] dark:fill-[#F8F1E7]"
      width={6}
      height={6}
    />
  </Tooltip.Content>
));
TooltipContent.displayName = "TooltipContent";

export {
  Tooltip,
  TooltipProvider,
  TooltipContent,
};
```

---

## 8. Tabs (Radix)

### 8.1 Radix Composition

```
Tabs.Root
├── Tabs.List              (glass-tier-ultra-thin, rounded-sm)
│   ├── TabsTrigger × N    (flex-1, centered, subhead typography)
│   └── [Sliding Indicator] (absolute pill, animated)
├── TabsContent × N        (mt-4, no special styling)
```

### 8.2 Anatomy

**TabsList:**

| Property | Value |
|---|---|
| Display | `inline-flex` |
| Height | 38px (`h-[38px]`) |
| Padding | 3px (`p-[3px]`) |
| Gap | 2px (`gap-0.5`) — between triggers |
| Border radius | 10px (`radius-sm`) |
| Background | glass-tier-ultra-thin |
| Position | relative (for sliding indicator) |

**TabsTrigger (inactive):**

| Property | Value |
|---|---|
| Flex | `flex-1` |
| Align | center (text + icon) |
| Border radius | 4px (`radius-xs`) — inside the list container |
| Typography | `subhead` (13px / 500) |
| Color | `muted-foreground` |
| Background | transparent |

**TabsTrigger (active):**

| Property | Value |
|---|---|
| Background | `surface-base` |
| Shadow | `shadow-resting` (0 1px 3px rgba(0,0,0,0.06)) |
| Color | `foreground` |
| Scale | `scale(1)` (no change — indicator conveys active state) |

**TabsTrigger hover (inactive):**

| Property | Value |
|---|---|
| Background | `accent` (subtle — #F6E6CA light, #31261C dark) |
| Color | `muted-foreground` (unchanged) |

**Sliding Indicator:**

| Property | Value |
|---|---|
| Position | absolute |
| Background | `surface-base` |
| Border radius | 4px (`radius-xs`) |
| Shadow | `shadow-resting` |
| Size | matches active trigger dimensions |
| Transition | 200ms spring (`cubic-bezier(0.34, 1.56, 0.64, 1)`) |
| Properties | `left`, `width` |
| Z-index | 0 (behind trigger text, z-10) |

**TabsContent:**

| Property | Value |
|---|---|
| Padding top | 16px (`mt-4`) |
| Styling | none — inherits from parent |

### 8.3 State Color Matrix

**TabsList:**

| Mode | Background | Border |
|---|---|---|
| **Light** | `rgba(255,255,255,0.45)` + `blur(8px) saturate(120%)` | `rgba(255,255,255,0.35)` |
| **Dark** | `rgba(26,20,15,0.50)` + `blur(8px) saturate(120%)` | `rgba(255,255,255,0.10)` |

**TabsTrigger:**

| State | Light BG | Light Text | Dark BG | Dark Text |
|---|---|---|---|---|
| **inactive** | transparent | `muted-foreground` #78624B | transparent | `muted-foreground` #C7B69F |
| **active** | `surface-base` #FFF9F2 | `foreground` #2B2116 | `surface-base` #1A140F | `foreground` #F8F1E7 |
| **hover (inactive)** | `accent` #F6E6CA | `muted-foreground` #78624B | `accent` #31261C | `muted-foreground` #C7B69F |
| **disabled** | transparent, 50% opacity | `muted-foreground` | same | same |

### 8.4 Motion

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Sliding indicator | 200ms | spring `cubic-bezier(0.34, 1.56, 0.64, 1)` | `left` + `width` transition |
| Hover (inactive) | 150ms | ease-out | Background color fade |
| Active text change | 150ms | ease-out | Color transition |

### 8.5 Component Code

```tsx
// web/src/components/ui/tabs.tsx
import { Tabs } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

// ─── List ───
const TabsList = React.forwardRef<
  React.ComponentRef<typeof Tabs.List>,
  React.ComponentPropsWithoutRef<typeof Tabs.List>
>(({ className, ...props }, ref) => (
  <Tabs.List
    ref={ref}
    className={cn(
      [
        "relative inline-flex h-[38px] items-center justify-center",
        "rounded-[10px] p-[3px] gap-0.5",
        // Glass-tier-ultra-thin
        "bg-white/45 backdrop-blur-[8px] saturate-[120%]",
        "border border-white/35",
        "dark:bg-[rgba(26,20,15,0.50)] dark:border-white/10",
      ].join(" "),
      className,
    )}
    {...props}
  />
));
TabsList.displayName = "TabsList";

// ─── Trigger ───
const TabsTrigger = React.forwardRef<
  React.ComponentRef<typeof Tabs.Trigger>,
  React.ComponentPropsWithoutRef<typeof Tabs.Trigger>
>(({ className, ...props }, ref) => (
  <Tabs.Trigger
    ref={ref}
    className={cn(
      [
        "relative z-10 flex flex-1 items-center justify-center",
        "rounded-[4px] px-3 py-1.5",
        "text-[13px] font-medium",
        "text-muted-foreground",
        "transition-colors duration-150 ease-out",
        "outline-none",
        "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
        // Hover (inactive)
        "hover:bg-accent",
        // Active state
        "data-[state=active]:bg-surface-base",
        "data-[state=active]:text-foreground",
        "data-[state=active]:shadow-[0_1px_3px_rgba(0,0,0,0.06)]",
        // Disabled
        "disabled:pointer-events-none disabled:opacity-50",
      ].join(" "),
      className,
    )}
    {...props}
  />
));
TabsTrigger.displayName = "TabsTrigger";

// ─── Content ───
const TabsContent = React.forwardRef<
  React.ComponentRef<typeof Tabs.Content>,
  React.ComponentPropsWithoutRef<typeof Tabs.Content>
>(({ className, ...props }, ref) => (
  <Tabs.Content
    ref={ref}
    className={cn(
      [
        "mt-4 outline-none",
        "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
      ].join(" "),
      className,
    )}
    {...props}
  />
));
TabsContent.displayName = "TabsContent";

export {
  Tabs,
  TabsList,
  TabsTrigger,
  TabsContent,
};
```

> **Note on Sliding Indicator:** The sliding pill indicator is implemented at the application level (not in the primitive) using a `useRef` + `useState` pattern that measures the active trigger's `offsetLeft` and `offsetWidth` and applies them as inline styles to an absolutely-positioned div inside `TabsList`. This keeps the primitive composable while allowing the animated pill pattern.

**Sliding indicator hook (application-level):**

```tsx
function useTabsIndicator(listRef: React.RefObject<HTMLDivElement>, activeValue: string) {
  const [indicator, setIndicator] = useState({ left: 0, width: 0 });

  useEffect(() => {
    const list = listRef.current;
    if (!list) return;
    const activeTrigger = list.querySelector(
      `[data-state="active"]`
    ) as HTMLElement | null;
    if (!activeTrigger) return;

    // Account for the 3px padding on the list
    setIndicator({
      left: activeTrigger.offsetLeft,
      width: activeTrigger.offsetWidth,
    });
  }, [activeValue, listRef]);

  return indicator;
}
```

---

## 9. Separator (Radix)

### 9.1 Anatomy

| Orientation | Width/Height | Background | Flex Behavior |
|---|---|---|---|
| **horizontal** | `h-px` (1px) | `border` token | `w-full` |
| **vertical** | `w-px` (1px) | `border` token | `h-full`, `shrink-0` |

### 9.2 State Color Matrix

| Context | Light | Dark |
|---|---|---|
| **Normal surface** | `border` #DCC7A7 | `border` #5A4630 |
| **On glass surface** | `rgba(255,255,255,0.10)` | `rgba(255,255,255,0.06)` |

### 9.3 Component Code

```tsx
// web/src/components/ui/separator.tsx
import { Separator } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

const UiSeparator = React.forwardRef<
  React.ComponentRef<typeof Separator.Root>,
  React.ComponentPropsWithoutRef<typeof Separator.Root> & {
    glass?: boolean;
  }
>(({ className, orientation = "horizontal", decorative = true, glass, ...props }, ref) => (
  <Separator.Root
    ref={ref}
    decorative={decorative}
    orientation={orientation}
    className={cn(
      [
        "shrink-0",
        orientation === "horizontal" ? "h-px w-full" : "w-px h-full",
      ].join(" "),
      glass
        ? "bg-white/10 dark:bg-white/6"
        : "bg-border",
      className,
    )}
    {...props}
  />
));
UiSeparator.displayName = "Separator";

export { UiSeparator as Separator };
```

---

## 10. Figma Component Structure

### 10.1 Card

**Component name:** `Card`

**Auto Layout:**
- Direction: Vertical
- Primary axis: Fill container
- Counter axis: Hug contents
- Padding: 0 (delegated to sub-components)
- Overflow: hidden (clips border-radius)
- Gap: 0 (sub-components manage their own spacing)

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Variant` | Variant | `default`, `elevated` | `default` |
| `State` | Variant | `default`, `hover` | `default` |
| `Has Header` | Boolean | `true`, `false` | `true` |
| `Has Footer` | Boolean | `true`, `false` | `false` |
| `Has Footer Separator` | Boolean | `true`, `false` | `false` |
| `Title` | Text | — | `Card Title` |
| `Description` | Text | — | `Card description text.` |
| `Content` | Text | — | `Card content goes here.` |

**Layer Structure:**
```
📦 Card (Component Set)
├── 🔀 Variant: Variant (2 values)
├── 🔀 Variant: State (2 values)
├── 🔘 Boolean: Has Header
├── 🔘 Boolean: Has Footer
├── 🔘 Boolean: Has Footer Separator
├── 📝 Text: Title
├── 📝 Text: Description
└── 📝 Text: Content

Layer Structure per variant:
Card (Frame, Auto Layout Vertical, rounded-14px, overflow hidden)
├── CardHeader (Frame, Auto Layout Vertical, p-24px, gap-8px, hidden when Has Header=false)
│   ├── CardTitle (Text, 18px/600, foreground)
│   └── CardDescription (Text, 14px/400, muted-foreground)
├── CardContent (Frame, px-24px, pb-24px)
│   └── Content (Text, 15px/400, foreground)
├── Separator (Line, 1px, hidden when Has FooterSeparator=false)
└── CardFooter (Frame, Auto Layout Horizontal, px-24px, pb-24px, gap-8px, hidden when Has Footer=false)
```

### 10.2 Dialog

**Component name:** `DialogContent`

Modeled as a **composition** — DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter are separate components.

**DialogContent (main component):**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `open`, `closed` | `open` |
| `Has Close Button` | Boolean | `true`, `false` | `true` |
| `Has Description` | Boolean | `true`, `false` | `true` |
| `Has Footer` | Boolean | `true`, `false` | `true` |
| `Title` | Text | — | `Dialog Title` |
| `Description` | Text | — | `Dialog description text.` |

**Layer Structure:**
```
📦 DialogContent (Component Set)
├── 🔀 Variant: State (2 values)
├── 🔘 Boolean: Has Close Button
├── 🔘 Boolean: Has Description
├── 🔘 Boolean: Has Footer
├── 📝 Text: Title
├── 📝 Text: Description

Layer Structure:
DialogContent (Frame, fixed center, 512px max-w, rounded-22px, glass-thick)
├── Close Button (Frame, absolute top-16px right-16px, 28×28, ghost icon)
│   └── X (SVG, 16px)
├── DialogHeader (Frame, Auto Layout Vertical, p-24px, gap-8px)
│   ├── DialogTitle (Text, 22px/600, foreground)
│   └── DialogDescription (Text, 14px/400, muted-foreground, hidden when Has Description=false)
├── Content Slot (Frame, px-24px)
└── DialogFooter (Frame, Auto Layout Horizontal, p-24px, justify-end, gap-8px, hidden when Has Footer=false)
    ├── Button (Instance, variant=outline) "Cancel"
    └── Button (Instance, variant=default) "Confirm"
```

**DialogOverlay (separate component):**
```
📦 DialogOverlay
├── 🔀 Variant: State (open, closed)

Layer Structure:
DialogOverlay (Frame, fixed inset-0, bg-black/40, blur-4px)
```

### 10.3 Sheet

**Component name:** `SheetContent`

| Property | Type | Values | Default |
|---|---|---|---|
| `Side` | Variant | `left`, `right`, `top`, `bottom` | `right` |
| `Size` | Variant | `default`, `wide` | `default` |
| `State` | Variant | `open`, `closed` | `open` |
| `Has Close Button` | Boolean | `true`, `false` | `true` |
| `Title` | Text | — | `Sheet Title` |

**Layer Structure (right side shown):**
```
📦 SheetContent (Component Set)
├── 🔀 Variant: Side (4 values)
├── 🔀 Variant: Size (2 values)
├── 🔀 Variant: State (2 values)
├── 🔘 Boolean: Has Close Button
├── 📝 Text: Title

Layer Structure (right side):
SheetContent (Frame, fixed right-0, w-256px/w-320px, full-height, rounded-l-18px, glass-regular)
├── Close Button (Frame, absolute top-16px left-16px, 28×28, ghost icon)
│   └── X (SVG, 16px)
├── SheetHeader (Frame, p-24px)
│   └── SheetTitle (Text, 22px/600)
└── Content Slot (Frame, p-24px)
```

### 10.4 Popover

**Component name:** `PopoverContent`

| Property | Type | Values | Default |
|---|---|---|---|
| `Side` | Variant | `top`, `right`, `bottom`, `left` | `bottom` |
| `State` | Variant | `open`, `closed` | `open` |
| `Show Arrow` | Boolean | `true`, `false` | `false` |
| `Width` | Variant | `default` (288px), `auto` | `default` |

**Layer Structure:**
```
📦 PopoverContent (Component Set)
├── 🔀 Variant: Side (4 values)
├── 🔀 Variant: State (2 values)
├── 🔘 Boolean: Show Arrow
├── 🔀 Variant: Width (2 values)

Layer Structure:
PopoverContent (Frame, rounded-14px, glass-thin, shadow-elevated, w-288px)
├── Arrow (Polygon, 8px, fill=glass-bg, hidden when Show Arrow=false)
└── Content Slot (Frame, p-4px)
    ├── PopoverItem (Frame, p-8px/12px, rounded-8px, hover=accent)
    │   └── Label (Text, 14px/400)
    └── PopoverItem ...
```

### 10.5 Tooltip

**Component name:** `TooltipContent`

| Property | Type | Values | Default |
|---|---|---|---|
| `Side` | Variant | `top`, `right`, `bottom`, `left` | `top` |
| `State` | Variant | `open`, `closed` | `open` |
| `Label` | Text | — | `Tooltip text` |
| `Mode` | Variant | `light`, `dark` | `light` |

**Layer Structure:**
```
📦 TooltipContent (Component Set)
├── 🔀 Variant: Side (4 values)
├── 🔀 Variant: State (2 values)
├── 📝 Text: Label
├── 🔀 Variant: Mode (light/dark — shows inverted colors)

Layer Structure:
TooltipContent (Frame, rounded-4px, p-6px/10px, max-w-250px, bg-#2B2116 dark:bg-#F8F1E7)
├── Label (Text, 12px/400, #F8F1E7 dark: #2B2116)
└── Arrow (Polygon, 6px, fill=bg)
```

### 10.6 Tabs

**Component name:** `TabsList`, `TabsTrigger`, `TabsContent`

**TabsList:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Tab Count` | Variant | `2-tab`, `3-tab`, `4-tab`, `5-tab` | `3-tab` |
| `Active` | Variant | `0`, `1`, `2`, `3`, `4` | `0` |
| `Label 1` | Text | — | `Tab 1` |
| `Label 2` | Text | — | `Tab 2` |
| `Label 3` | Text | — | `Tab 3` |
| `Label 4` | Text | — | `Tab 4` |
| `Label 5` | Text | — | `Tab 5` |

**Layer Structure:**
```
📦 TabsList (Component Set)
├── 🔀 Variant: Tab Count (4 values)
├── 🔀 Variant: Active (5 values)
├── 📝 Text: Label 1..5

Layer Structure:
TabsList (Frame, Auto Layout Horizontal, h-38px, p-3px, rounded-10px, glass-ultra-thin, relative)
├── Sliding Pill (Frame, absolute, rounded-4px, bg-surface-base, shadow-resting)
│   [left + width driven by Active variant]
├── TabsTrigger 0 (Frame, flex-1, center, rounded-4px)
│   └── Label (Text, 13px/500)
├── TabsTrigger 1 (Frame, flex-1, center, rounded-4px)
│   └── Label (Text, 13px/500)
└── TabsTrigger 2 (Frame, flex-1, center, rounded-4px)
    └── Label (Text, 13px/500)
```

### 10.7 Separator

**Component name:** `Separator`

| Property | Type | Values | Default |
|---|---|---|---|
| `Orientation` | Variant | `horizontal`, `vertical` | `horizontal` |
| `On Glass` | Boolean | `true`, `false` | `false` |

**Layer Structure:**
```
📦 Separator (Component Set)
├── 🔀 Variant: Orientation (2 values)
├── 🔘 Boolean: On Glass

Layer Structure (horizontal):
Separator (Line, 1px height, w-full, bg-border/glass-token)
```

---

## Appendix A: Accessibility Checklist

| Check | Card | Dialog | Sheet | Popover | Tooltip | Tabs | Separator |
|---|---|---|---|---|---|---|---|
| ARIA role | `role="group"` or semantic HTML | Radix `dialog` role | Radix `dialog` role | Radix `dialog` / menu | Radix `tooltip` role | Radix `tablist/tab/tabpanel` | Radix `separator` role |
| Focus trap | N/A | ✅ Radix default | ✅ Radix default | N/A | N/A | ✅ Arrow key nav | N/A |
| Escape close | N/A | ✅ Radix default | ✅ Radix default | ✅ Radix default | ✅ Radix default | N/A | N/A |
| Label association | `aria-labelledby` via CardTitle | `aria-labelledby` via DialogTitle | `aria-labelledby` via SheetTitle | Trigger described by Popover | `aria-describedby` on trigger | `aria-selected` on triggers | `aria-orientation` |
| Keyboard | N/A | Escape closes | Escape closes | Escape closes | Escape hides | Arrow keys, Home/End | N/A |
| Screen reader | Group announced | Dialog title + desc announced | Same | Content announced | Text announced | Tab + panel announced | Separator announced |
| Motion sensitivity | `prefers-reduced-motion` disables hover lift | Reduce to fade-only | Reduce to fade-only | Reduce to fade-only | Reduce to instant | Disable sliding indicator | N/A |
| Color contrast | `foreground` on glass AAA | Same AAA | Same AAA | Same AAA | ≥15:1 inverted ✅ AAA | `foreground` on surface AAA | N/A |

---

## Appendix B: Token Cross-Reference

### Color Tokens

| CSS Custom Property | Tailwind Class | Used In |
|---|---|---|
| `--color-foreground` | `text-foreground` | Card title, Dialog title, Tab active text |
| `--color-muted-foreground` | `text-muted-foreground` | Card description, Dialog description, Tab inactive text, Close buttons |
| `--color-card-foreground` | `text-card-foreground` | Card text |
| `--color-surface-base` | `bg-surface-base` | Tab active pill, Card elevated hover |
| `--color-accent` | `bg-accent` | Tab hover, Popover item hover, Close button hover |
| `--color-accent-foreground` | `text-accent-foreground` | Accented hover text |
| `--color-border` | `border-border` / `bg-border` | Separator normal |
| `--color-ring` | `ring-ring` | Focus rings (all components) |
| `--color-background` | `ring-offset-background` | Focus ring offset |

### Glass Tier Utility Classes

| Class | backdrop-filter | Light BG | Dark BG |
|---|---|---|---|
| `.glass-ultra-thin` | `blur(8px) saturate(120%)` | `white/0.45` | `#1A140F/0.50` |
| `.glass-thin` | `blur(16px) saturate(140%)` | `white/0.55` | `#1A140F/0.60` |
| `.glass-regular` | `blur(24px) saturate(160%)` | `white/0.65` | `#1A140F/0.70` |
| `.glass-thick` | `blur(40px) saturate(180%)` | `white/0.78` | `#1A140F/0.80` |

### Z-Index Tokens

| Token | Value | Used In |
|---|---|---|
| `z-dropdown` | 30 | Popover content |
| `z-modal-backdrop` | 40 | Dialog overlay, Sheet overlay |
| `z-modal` | 50 | Dialog content, Sheet content |
| `z-tooltip` | 60 | Tooltip content |

### Updated Radius Tokens (CSS)

```css
@theme {
  --radius-xs: 0.25rem;   /* 4px  */
  --radius-sm: 0.625rem;  /* 10px */
  --radius-md: 0.875rem;  /* 14px */
  --radius-lg: 1.125rem;  /* 18px */
  --radius-xl: 1.375rem;  /* 22px */
  --radius-full: 9999px;
}
```

### Updated Shadow Tokens (CSS)

```css
@theme {
  --shadow-resting: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-elevated: 0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-dragging: 0 12px 40px rgba(0, 0, 0, 0.12);
}
```

### Tailwind v4 Animation Keyframes

Add to `globals.css` or `tailwind.css`:

```css
@theme {
  --animate-in: enter 200ms ease-out;
  --animate-out: exit 200ms ease-in;
}

@keyframes enter {
  from {
    opacity: var(--tw-enter-opacity, 0);
    transform: translate3d(
        var(--tw-enter-translate-x, 0),
        var(--tw-enter-translate-y, 0),
        0
      )
      scale3d(
        var(--tw-enter-scale, 1),
        var(--tw-enter-scale, 1),
        var(--tw-enter-scale, 1)
      );
  }
}

@keyframes exit {
  to {
    opacity: var(--tw-exit-opacity, 0);
    transform: translate3d(
        var(--tw-exit-translate-x, 0),
        var(--tw-exit-translate-y, 0),
        0
      )
      scale3d(
        var(--tw-exit-scale, 1),
        var(--tw-exit-scale, 1),
        var(--tw-exit-scale, 1)
      );
  }
}
```

> **Note:** The `animate-in`, `animate-out`, `fade-in-0`, `zoom-in-95`, `slide-in-from-*` classes are provided by `tailwindcss-animate` plugin. If not installed, add via `npm install tailwindcss-animate` and register in the Tailwind config.

---

## Appendix C: Implementation Checklist

### Phase 1: Token Infrastructure
- [ ] Update `@theme` radius tokens in `globals.css` (xs=4px, sm=10px, md=14px, lg=18px, xl=22px)
- [ ] Add `--shadow-resting`, `--shadow-elevated`, `--shadow-dragging` to `globals.css`
- [ ] Verify `--color-surface-base`, `--color-surface-raised`, `--color-surface-sunken` tokens exist (prerequisite from form-inputs spec)
- [ ] Install `tailwindcss-animate` plugin if not present
- [ ] Add animation keyframes to `globals.css`

### Phase 2: Component Creation
- [ ] Create `card.tsx` — Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
- [ ] Create `dialog.tsx` — DialogContent, DialogOverlay, DialogHeader, DialogTitle, DialogDescription, DialogFooter
- [ ] Create `sheet.tsx` — SheetContent, SheetOverlay, SheetHeader, SheetTitle, SheetDescription, SheetFooter (CVA side variants)
- [ ] Create `popover.tsx` — PopoverContent, PopoverItem (optional arrow)
- [ ] Create `tooltip.tsx` — TooltipProvider, TooltipContent (inverted solid)
- [ ] Create `tabs.tsx` — TabsList, TabsTrigger, TabsContent (sliding indicator hook)
- [ ] Create `separator.tsx` — Separator (horizontal/vertical + glass variant)

### Phase 3: Integration
- [ ] Wrap app root in `<TooltipProvider delayDuration={0}>`
- [ ] Replace any inline card patterns with `<Card>` components
- [ ] Replace any inline dialog/modal patterns with `<Dialog>` components
- [ ] Replace any inline drawer/sheet patterns with `<Sheet>` components
- [ ] Replace any inline popover/dropdown patterns with `<Popover>` components
- [ ] Replace any inline tab patterns with `<Tabs>` components
- [ ] Replace any `<hr>` / border-based separators with `<Separator>` components

### Phase 4: Visual QA
- [ ] Verify light + dark mode across all 7 components
- [ ] Verify glass tier rendering (backdrop-filter support in target browsers)
- [ ] Verify tooltip contrast: ≥15:1 in both modes
- [ ] Verify Dialog focus trap (Tab cycles within dialog only)
- [ ] Verify Sheet slide animations for all 4 sides
- [ ] Verify Popover positioning and arrow rendering
- [ ] Verify Tabs sliding indicator animation (200ms spring)
- [ ] Verify Separator on normal vs glass surfaces
- [ ] Verify `prefers-reduced-motion` disables all animations
- [ ] Verify mobile responsiveness (Sheet as drawer, Dialog as bottom sheet on small screens)
- [ ] Add `aria-label` to all Dialog/Sheet close buttons

### Phase 5: Browser Compatibility
- [ ] Verify `backdrop-filter` support (Safari 9+, Chrome 76+, Firefox 103+)
- [ ] Test glass fallback: solid `surface-base` background when `backdrop-filter` unsupported
- [ ] Test on mobile Safari (known backdrop-filter rendering issues with nested scroll)

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
