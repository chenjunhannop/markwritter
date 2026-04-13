# Button & Badge Component Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.1
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Implementation:** `web/src/components/ui/button.tsx` · `web/src/components/ui/badge.tsx`

---

## Table of Contents

1. [Design Decisions](#1-design-decisions)
2. [Button Specification](#2-button-specification)
3. [Badge Specification](#3-badge-specification)
4. [CVA Code — buttonVariants](#4-cva-code--buttonvariants)
5. [CVA Code — badgeVariants](#5-cva-code--badgevariants)
6. [Figma Component Structure](#6-figma-component-structure)
7. [Inline Button Migration Mapping](#7-inline-button-migration-mapping)
8. [Hardcoded Badge Replacements](#8-hardcoded-badge-replacements)

---

## 1. Design Decisions

### 1.1 Radius Token Resolution

The core token scale (`tokens.md`) defines `radius-xs=4px`, `radius-sm=6px`, `radius-md=8px`. This specification introduces **component-level radius aliases** instead of renaming the core scale:

| Component | Alias | Value | Rationale |
|---|---|---|---|
| Button | `radius-button` | 10px (between `sm` 6px and `md` 8px — maps to custom `rounded-[10px]`) | Larger hit targets deserve slightly rounder corners |
| Badge | `radius-badge` | 6px (maps to `radius-sm`) | Compact chips stay tight |

In Tailwind: Button uses `rounded-[10px]`, Badge uses `rounded-sm` (which maps to 6px per tokens).

### 1.2 Destructive Ghost Treatment

Destructive icon actions are handled via an optional **`data-destructive`** attribute on `ghost` variant buttons rather than adding a new variant. This keeps the API surface small while allowing hover/active states to shift to destructive colors.

**Current usage: 1 confirmed instance** — the session delete button in `session-list.tsx:42-50`. The close button in `sources-panel.tsx` is a neutral close action and does **not** use destructive styling.

```tsx
<Button variant="ghost" size="icon-sm" data-destructive aria-label="Delete">
  <Trash2 />
</Button>
```

CSS selector in CVA: `data-[destructive]:hover:bg-destructive/10 data-[destructive]:hover:text-destructive data-[destructive]:active:bg-destructive/20 data-[destructive]:active:text-destructive`

### 1.3 Loading State

Loading is a primitive-level concern, not a variant. The Button component accepts a `loading?: boolean` prop that:

- Sets `aria-busy="true"` and `disabled`
- **Text buttons:** spinner appears before text label (preserves button width)
- **Icon-only buttons (`icon` / `icon-sm`):** spinner **replaces** the icon entirely — no text, no original icon
- Spinner size matches the active size variant (12px for xs/icon-sm, 14px for sm, 16px for default/lg/icon)
- Spinner color: `currentColor`
- Suppresses hover, press, and pointer events

### 1.4 Status Badge Token Prerequisite

> ⚠️ **Implementation note:** The Badge's `success`, `warning`, `error`, and `info` variants require status background tokens that are **approved in `tokens.md` §1.5** but **not yet wired into `web/src/globals.css`**. Before implementing the new badge variants, add `--color-status-*-bg` entries to both the `@theme` and `.dark` blocks (see §5.1 for the exact CSS).

---

## 2. Button Specification

### 2.1 Variant Color Matrix — Light Mode

| Variant | Background | Text | Border | Hover BG | Hover Text | Active BG | Focus Ring | Shadow |
|---|---|---|---|---|---|---|---|---|
| **default** | `primary` #E6A23C | `primary-foreground` #2B2116 | none | `primary-hover` #D89432 | #2B2116 | `primary-active` #C98328 | `ring` 2px, offset 2px | `shadow-md` |
| **destructive** | `destructive` #C0392B | `destructive-foreground` #FFF9F2 | none | `destructive/90` | #FFF9F2 | `destructive/80` | `destructive` ring 2px | `shadow-md` |
| **outline** | transparent | `foreground` #2B2116 | `border` 1px #DCC7A7 | `accent` #F6E6CA | `accent-foreground` #2B2116 | `accent/80` | `ring` 2px | `shadow-sm` |
| **secondary** | `secondary` #FCF6EE | `secondary-foreground` #2B2116 | `border` 1px #DCC7A7 | `accent` #F6E6CA | #2B2116 | `accent/70` | `ring` 2px | `shadow-sm` |
| **ghost** | transparent | `muted-foreground` #78624B | none | `accent` #F6E6CA | `accent-foreground` #2B2116 | `accent/70` | `ring` 2px | none |
| **link** | transparent | `primary` #E6A23C | none | none (underline) | #D89432 | #C98328 | `ring` 2px | none |

### 2.2 Variant Color Matrix — Dark Mode

| Variant | Background | Text | Border | Hover BG | Hover Text | Active BG | Focus Ring | Shadow |
|---|---|---|---|---|---|---|---|---|
| **default** | `primary` #F0B04A | `primary-foreground` #2B2116 | none | `primary-hover` #F4C97B | #2B2116 | `primary-active` #D89432 | `ring` 2px | `shadow-md` |
| **destructive** | `destructive` #E74C3C | `destructive-foreground` #F8F1E7 | none | `destructive/90` | #F8F1E7 | `destructive/80` | `destructive` ring 2px | `shadow-md` |
| **outline** | transparent | `foreground` #F8F1E7 | `border` 1px #5A4630 | `accent` #31261C | `accent-foreground` #F8F1E7 | `accent/80` | `ring` 2px | `shadow-sm` |
| **secondary** | `secondary` #231B14 | `secondary-foreground` #F8F1E7 | `border` 1px #5A4630 | `accent` #31261C | #F8F1E7 | `accent/70` | `ring` 2px | `shadow-sm` |
| **ghost** | transparent | `muted-foreground` #C7B69F | none | `accent` #31261C | `accent-foreground` #F8F1E7 | `accent/70` | `ring` 2px | none |
| **link** | transparent | `primary` #F0B04A | none | none (underline) | #F4C97B | #D89432 | `ring` 2px | none |

### 2.3 Size Matrix

| Size | Height | Padding X | Padding Y | Font Size | Font Weight | Icon Size | Gap | Min-Width |
|---|---|---|---|---|---|---|---|---|
| **xs** | 26px | 8px | 2px | 12px (caption) | 500 | 12px | 4px | — |
| **sm** | 32px | 12px | 4px | 14px (body-sm) | 400 | 14px | 6px | — |
| **default** | 36px | 16px | 6px | 15px (body) | 400 | 16px | 8px | — |
| **lg** | 44px | 24px | 8px | 16px (body) | 400 | 18px | 8px | — |
| **icon** | 36px | 0 | 0 | — | — | 16px | — | 36px |
| **icon-sm** | 28px | 0 | 0 | — | — | 14px | — | 28px |

### 2.4 States

#### Default
All variants render in their default state as specified in the color matrices above.

#### Hover
- Transition: `transition-fast` (120ms ease-out) for color changes
- `shadow-md` variants elevate to `shadow-lg` on hover
- `ghost` gains `accent` background
- `link` gains `underline` decoration

#### Active / Pressed
- Transition: immediate (no delay)
- Background shifts to `active` token
- Shadow compresses slightly: `shadow-sm` for all variants

#### Disabled
- `opacity: 0.5` on the entire control
- `pointer-events: none`
- `cursor: not-allowed`
- No shadow (shadow removed)
- No ring on focus

#### Focus-visible
- `outline: none`
- `ring: 2px solid var(--color-ring)` (amber #E6A23C light / #F0B04A dark)
- `ring-offset: 2px`
- `ring-offset-color: var(--color-background)`
- Destructive variant: `ring-color: var(--color-destructive)`

#### Loading

**Text buttons (xs, sm, default, lg):**
- Spinner renders before the text label
- Text label remains visible to preserve button width
- `aria-busy="true"`, `disabled`

**Icon-only buttons (icon, icon-sm):**
- Spinner **replaces** the icon — original icon is hidden
- No text label
- `aria-busy="true"`, `disabled`

| Size | Spinner Size |
|---|---|
| xs | 12px |
| sm | 14px |
| default | 16px |
| lg | 16px |
| icon | 16px |
| icon-sm | 14px |

### 2.5 Destructive Ghost (data attribute)

When `data-destructive` is present on a `ghost` variant button:

| State | Background | Text |
|---|---|---|
| Default | transparent | `muted-foreground` |
| Hover | `destructive/10` | `destructive` |
| Active | `destructive/20` | `destructive` |

**Scope:** This attribute is only meaningful on `ghost` variant. Other variants ignore it.

### 2.6 Motion Tokens

| Interaction | Token | Duration | Easing |
|---|---|---|---|
| Color change (hover/press) | `transition-fast` | 120ms | ease-out |
| Shadow change | `transition-standard` | 200ms | ease-out |
| Focus ring appear | `transition-fast` | 120ms | ease-out |
| Loading spinner | continuous | 1000ms/rotation | linear |

---

## 3. Badge Specification

### 3.1 Anatomy

| Property | Value |
|---|---|
| Min-height | 20px |
| Padding | `0 8px` (`px-2`) |
| Vertical padding | `2px` (`py-0.5`) |
| Font size | 11px (caption / `text-[11px]`) |
| Font weight | 500 (`font-medium`) |
| Border radius | 6px (`rounded-sm` → `radius-sm`) |
| Border width | 1px (all variants) |
| Line-height | 1.4 |
| Letter-spacing | 0.01em |

### 3.2 Variant Color Matrix — Light Mode

| Variant | Background | Text | Border |
|---|---|---|---|
| **default** | `primary` #E6A23C | `primary-foreground` #2B2116 | transparent |
| **secondary** | `secondary` #FCF6EE | `secondary-foreground` #2B2116 | `border` #DCC7A7 |
| **destructive** | `destructive` #C0392B | `destructive-foreground` #FFF9F2 | transparent |
| **outline** | transparent | `muted-foreground` #78624B | `border` #DCC7A7 |
| **success** | `status-success-bg` #EAF2E6 | `status-success` #496D3E | `status-success/20` |
| **warning** | `status-warning-bg` #FBF0D9 | `status-warning` #8A5A12 | `status-warning/20` |
| **error** | `status-error-bg` #F8E6E0 | `status-error` #A2432B | `status-error/20` |
| **info** | `status-info-bg` #E8EDF2 | `status-info` #586B7A | `status-info/20` |

### 3.3 Variant Color Matrix — Dark Mode

| Variant | Background | Text | Border |
|---|---|---|---|
| **default** | `primary` #F0B04A | `primary-foreground` #2B2116 | transparent |
| **secondary** | `secondary` #231B14 | `secondary-foreground` #F8F1E7 | `border` #5A4630 |
| **destructive** | `destructive` #E74C3C | `destructive-foreground` #F8F1E7 | transparent |
| **outline** | transparent | `muted-foreground` #C7B69F | `border` #5A4630 |
| **success** | `status-success-bg` #1A2616 | `status-success` #86B67A | `status-success/20` |
| **warning** | `status-warning-bg` #29201A | `status-warning` #D2BF8B | `status-warning/20` |
| **error** | `status-error-bg` #261612 | `status-error` #D88E74 | `status-error/20` |
| **info** | `status-info-bg` #161C24 | `status-info` #9DB6C8 | `status-info/20` |

### 3.4 States

| State | Behavior |
|---|---|
| **Default** | As specified in color matrices |
| **Hover** | Slight background darkening (8% opacity overlay). Only for interactive badges. Transition: `transition-fast` 120ms |
| **Disabled** | `opacity: 0.5`, `pointer-events: none` |
| **Focus** | `ring: 2px solid var(--color-ring)`, `ring-offset: 2px` (only when badge is interactive/clickable) |

---

## 4. CVA Code — buttonVariants

```tsx
// web/src/components/ui/button.tsx
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "radix-ui";
import { type ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  [
    "inline-flex items-center justify-center gap-2 whitespace-nowrap",
    "rounded-[10px] font-medium",
    "transition-[color,background-color,border-color,box-shadow] duration-120 ease-out",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
    "disabled:pointer-events-none disabled:opacity-50",
    "[&_svg]:pointer-events-none [&_svg]:shrink-0",
  ].join(" "),
  {
    variants: {
      variant: {
        default: [
          "bg-primary text-primary-foreground shadow-md",
          "hover:bg-primary-hover hover:shadow-lg",
          "active:bg-primary-active active:shadow-sm",
        ].join(" "),
        destructive: [
          "bg-destructive text-destructive-foreground shadow-md",
          "hover:bg-destructive/90 hover:shadow-lg",
          "active:bg-destructive/80 active:shadow-sm",
          "focus-visible:ring-destructive",
        ].join(" "),
        outline: [
          "border border-border bg-transparent text-foreground shadow-sm",
          "hover:bg-accent hover:text-accent-foreground",
          "active:bg-accent/80",
        ].join(" "),
        secondary: [
          "border border-border bg-secondary text-secondary-foreground shadow-sm",
          "hover:bg-accent hover:text-accent-foreground",
          "active:bg-accent/70",
        ].join(" "),
        ghost: [
          "bg-transparent text-muted-foreground",
          "hover:bg-accent hover:text-accent-foreground",
          "active:bg-accent/70",
          "data-[destructive]:hover:bg-destructive/10",
          "data-[destructive]:hover:text-destructive",
          "data-[destructive]:active:bg-destructive/20",
          "data-[destructive]:active:text-destructive",
        ].join(" "),
        link: [
          "bg-transparent text-primary underline-offset-4",
          "hover:underline hover:text-primary-hover",
          "active:text-primary-active",
        ].join(" "),
      },
      size: {
        xs: "h-[26px] px-2 py-0.5 text-xs gap-1 [&_svg]:size-3",
        sm: "h-8 px-3 py-1 text-sm gap-1.5 [&_svg]:size-3.5",
        default: "h-9 px-4 py-1.5 text-[15px] gap-2 [&_svg]:size-4",
        lg: "h-11 px-6 py-2 text-base gap-2 [&_svg]:size-[18px]",
        icon: "h-9 w-9 [&_svg]:size-4",
        "icon-sm": "h-7 w-7 [&_svg]:size-3.5",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      asChild = false,
      loading = false,
      disabled,
      children,
      ...props
    },
    ref,
  ) => {
    const Comp = asChild ? Slot.Root : "button";
    const isIconButton =
      size === "icon" || size === "icon-sm";

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        aria-busy={loading || undefined}
        {...props}
      >
        {loading ? (
          isIconButton ? (
            /* Icon-only: spinner replaces icon entirely */
            <svg
              className="animate-spin"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          ) : (
            /* Text button: spinner before label */
            <>
              <svg
                className="animate-spin"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              {children}
            </>
          )
        ) : (
          children
        )}
      </Comp>
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
```

---

## 5. CVA Code — badgeVariants

```tsx
// web/src/components/ui/badge.tsx
import { cva, type VariantProps } from "class-variance-authority";
import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  [
    "inline-flex items-center rounded-sm border px-2 py-0.5",
    "text-[11px] font-medium leading-[1.4] tracking-[0.01em]",
    "transition-[color,background-color,border-color] duration-120 ease-out",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
  ].join(" "),
  {
    variants: {
      variant: {
        default: [
          "border-transparent bg-primary text-primary-foreground shadow-sm",
          "hover:bg-primary-hover",
        ].join(" "),
        secondary: [
          "border-border bg-secondary text-secondary-foreground",
          "hover:bg-secondary/80",
        ].join(" "),
        destructive: [
          "border-transparent bg-destructive text-destructive-foreground shadow-sm",
          "hover:bg-destructive/80",
        ].join(" "),
        outline: "border-border bg-transparent text-muted-foreground",
        success:
          "border-status-success/20 bg-status-success-bg text-status-success",
        warning:
          "border-status-warning/20 bg-status-warning-bg text-status-warning",
        error: "border-status-error/20 bg-status-error-bg text-status-error",
        info: "border-status-info/20 bg-status-info-bg text-status-info",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
```

### 5.1 Required CSS Token Updates

> ⚠️ **Prerequisite:** These status background tokens are approved in `tokens.md` §1.5 but must be added to `web/src/globals.css` before the status badge variants will work.

Add to the `@theme` block (Light mode):

```css
--color-status-success-bg: oklch(0.944 0.024 139);
--color-status-warning-bg: oklch(0.960 0.040 90);
--color-status-error-bg: oklch(0.928 0.038 30);
--color-status-info-bg: oklch(0.938 0.016 242);
```

Add to the `.dark` block:

```css
--color-status-success-bg: oklch(0.200 0.024 139);
--color-status-warning-bg: oklch(0.248 0.030 80);
--color-status-error-bg: oklch(0.192 0.028 30);
--color-status-info-bg: oklch(0.195 0.016 242);
```

---

## 6. Figma Component Structure

### 6.1 Button Component

**Component name:** `Button`

**Auto Layout:**
- Direction: Horizontal
- Primary axis: Center (justify)
- Counter axis: Center (align)
- Gap: varies by size (4px xs, 6px sm, 8px default/lg)
- Padding: varies by size (see §2.3)
- Fill container: false
- Absolute bounding box: false

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Variant` | Variant | `default`, `destructive`, `outline`, `secondary`, `ghost`, `link` | `default` |
| `Size` | Variant | `xs`, `sm`, `default`, `lg`, `icon`, `icon-sm` | `default` |
| `State` | Variant | `default`, `hover`, `active`, `disabled`, `focus`, `loading` | `default` |
| `Destructive` | Boolean | `true`, `false` | `false` |
| `Icon (Left)` | Instance Swap | Lucide icon set | `None` |
| `Label` | Text | — | `Button` |

**Label Visibility Rules by Size:**

| Size | Label | Icon | Notes |
|---|---|---|---|
| xs | ✅ visible | ✅ optional | Text + optional icon |
| sm | ✅ visible | ✅ optional | Text + optional icon |
| default | ✅ visible | ✅ optional | Text + optional icon |
| lg | ✅ visible | ✅ optional | Text + optional icon |
| icon | ❌ hidden | ✅ required | Icon-only, set `aria-label` |
| icon-sm | ❌ hidden | ✅ required | Icon-only, set `aria-label` |

**Destructive Boolean Scoping:**

The `Destructive` boolean only applies when `Variant = ghost`. In Figma, this is expressed by only changing visual properties for ghost + destructive=true combinations. For all other variants, the destructive boolean is a no-op visually.

**Loading State Rules:**

| Size Category | Loading Behavior |
|---|---|
| Text sizes (xs, sm, default, lg) | Spinner replaces `Icon (Left)`, label text stays visible |
| Icon sizes (icon, icon-sm) | Spinner replaces `Icon (Left)`, label stays hidden |

**Recommended Figma Structure:**
```
📦 Button (Component Set)
├── 🔀 Variant property: Variant (6 values)
├── 🔀 Variant property: Size (6 values)
├── 🔀 Variant property: State (6 values)
├── 📝 Text property: Label
├── 🔄 Instance swap property: Icon (Left)
└── 🔘 Boolean property: Destructive (scoped to ghost)

Layer Structure per variant:
Button (Frame, Auto Layout)
├── Spinner (Frame, hidden when State≠loading)
│   └── Loader2 (SVG, size varies by Size prop)
├── Icon (Frame, optional)
│   └── [Icon instance from swap]
└── Label (Text, "Button", hidden for icon/icon-sm sizes)
```

### 6.2 Badge Component

**Component name:** `Badge`

**Auto Layout:**
- Direction: Horizontal
- Primary axis: Center
- Counter axis: Center
- Gap: 4px
- Padding: `0 8px`, vertical 2px
- Fixed height: 20px

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Variant` | Variant | `default`, `secondary`, `destructive`, `outline`, `success`, `warning`, `error`, `info` | `default` |
| `State` | Variant | `default`, `hover`, `disabled` | `default` |
| `Label` | Text | — | `Badge` |
| `Icon` | Instance Swap | Lucide icon set | `None` |

**Layer Structure:**
```
📦 Badge (Component Set)
├── 🔀 Variant property: Variant (8 values)
├── 🔀 Variant property: State (3 values)
├── 📝 Text property: Label
└── 🔄 Instance swap property: Icon

Layer Structure per variant:
Badge (Frame, Auto Layout, h-20px)
├── Icon (Frame, 12×12, optional, hidden when Icon=None)
│   └── [Icon instance]
└── Label (Text, 11px/500)
```

**Text Style:** `caption` — 11px / weight 500 / line-height 1.4 / letter-spacing 0.01em

---

## 7. Inline Button Migration Mapping

### 7.1 Full Mapping Table

| # | File (line) | Current Height | Current Classes | Target Component | Size | Δ Height | Notes |
|---|---|---|---|---|---|---|---|
| 1 | `session-list.tsx:15-21` | 28px (h-7 w-7) | inline ghost with `MessageSquarePlus` | `<Button variant="ghost" size="icon-sm">` | icon-sm (28px) | 0px | Exact match ✅ |
| 2 | `session-list.tsx:42-50` | 24px (h-6 w-6) | destructive hover ghost with `Trash2` | `<Button variant="ghost" size="icon-sm" data-destructive>` | icon-sm (28px) | +4px | **Intentional:** 24px is below the min touch target; 28px is the smallest safe size |
| 3 | `sources-panel.tsx:161-167` | 24px (h-6 w-6) | neutral ghost with `X` | `<Button variant="ghost" size="icon-sm">` | icon-sm (28px) | +4px | **Intentional:** Same touch-target rationale as #2 |
| 4 | `sources-panel.tsx:180-185` | auto | text ghost "Clear" | `<Button variant="ghost" size="xs">` | xs (26px) | — | Matches compact text style |
| 5 | `sources-panel.tsx:187-193` | auto | bg-primary "Done" | `<Button variant="default" size="xs">` | xs (26px) | — | Matches compact text style |
| 6 | `message-input.tsx:77-84` | 36px (h-9 w-9) | bg-primary icon `SendHorizonal` | `<Button variant="default" size="icon">` | icon (36px) | 0px | Exact match ✅ |
| 7 | `message-input.tsx:69-75` | 36px (h-9 w-9) | bg-destructive icon `Square` | `<Button variant="destructive" size="icon">` | icon (36px) | 0px | Exact match ✅ |
| 8 | `chat-area.tsx:47-53` | auto | bg-primary "New Chat" | `<Button variant="default" size="default">` | default (36px) | — | Upgrades from ad-hoc styling |
| 9 | `chat-area.tsx:76-84` | 32px (h-8) | ghost "Sources" with `FileText` | `<Button variant="ghost" size="sm">` | sm (32px) | 0px | Exact match ✅ |
| 10 | `chat-area.tsx:85-93` | 32px (h-8) | ghost "New" with `MessageSquarePlus` | `<Button variant="ghost" size="sm">` | sm (32px) | 0px | Exact match ✅ |

**Height change summary:** 8 of 10 mappings preserve exact dimensions. Mappings #2 and #3 intentionally grow from 24px → 28px to meet minimum touch target guidelines.

### 7.2 Migration Code Examples

**Before — session-list.tsx new chat (mapping #1):**
```tsx
<button
  type="button"
  onClick={() => createSession()}
  className="inline-flex h-7 w-7 items-center justify-center rounded-md text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
>
  <MessageSquarePlus className="h-4 w-4" />
</button>
```

**After:**
```tsx
<Button
  variant="ghost"
  size="icon-sm"
  onClick={() => createSession()}
  aria-label="New chat"
>
  <MessageSquarePlus />
</Button>
```

**Before — session-list.tsx delete (mapping #2):**
```tsx
<button
  type="button"
  onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }}
  className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded opacity-0 transition-opacity group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive"
>
  <Trash2 className="h-3 w-3" />
</button>
```

**After:**
```tsx
<Button
  variant="ghost"
  size="icon-sm"
  data-destructive
  onClick={(e) => { e.stopPropagation(); deleteSession(session.id); }}
  className="opacity-0 group-hover:opacity-100"
  aria-label="Delete chat"
>
  <Trash2 />
</Button>
```

**Before — sources-panel.tsx done (mapping #5):**
```tsx
<button
  type="button"
  onClick={handleConfirm}
  className="rounded-md bg-primary px-3 py-1 text-xs text-primary-foreground hover:bg-primary/90"
>
  Done
</button>
```

**After:**
```tsx
<Button variant="default" size="xs" onClick={handleConfirm}>
  Done
</Button>
```

**Before — message-input.tsx send (mapping #6):**
```tsx
<button
  type="button"
  onClick={handleSubmit}
  disabled={!value.trim() || disabled}
  className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary text-primary-foreground shadow-sm transition-colors hover:bg-primary/90 disabled:pointer-events-none disabled:opacity-50"
>
  <SendHorizonal className="h-4 w-4" />
</button>
```

**After:**
```tsx
<Button
  variant="default"
  size="icon"
  onClick={handleSubmit}
  disabled={!value.trim() || disabled}
  aria-label="Send message"
>
  <SendHorizonal />
</Button>
```

**Before — message-input.tsx stop (mapping #7):**
```tsx
<button
  type="button"
  onClick={onCancel}
  className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-destructive text-destructive-foreground shadow-sm transition-colors hover:bg-destructive/90"
>
  <Square className="h-4 w-4" />
</button>
```

**After:**
```tsx
<Button
  variant="destructive"
  size="icon"
  onClick={onCancel}
  aria-label="Stop generation"
>
  <Square />
</Button>
```

**Before — chat-area.tsx sources toggle (mapping #9):**
```tsx
<button
  type="button"
  onClick={onToggleSources}
  className="inline-flex h-8 items-center gap-1.5 rounded-md px-2 text-xs text-muted-foreground hover:bg-accent hover:text-accent-foreground"
>
  <FileText className="h-3.5 w-3.5" />
  Sources
</button>
```

**After:**
```tsx
<Button variant="ghost" size="sm" onClick={onToggleSources}>
  <FileText /> Sources
</Button>
```

---

## 8. Hardcoded Badge Replacements

### 8.1 Settings Page — API Key Status

**File:** `web/src/features/settings/settings-page.tsx:108-116`

**Before:**
```tsx
<span
  className={`rounded px-2 py-0.5 text-xs ${
    settings.api_key_set
      ? "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300"
      : "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300"
  }`}
>
  {settings.api_key_set ? "已设置" : "未设置"}
</span>
```

**After:**
```tsx
<Badge variant={settings.api_key_set ? "success" : "warning"}>
  {settings.api_key_set ? "已设置" : "未设置"}
</Badge>
```

**Rationale:** `warning` for "未设置" (not yet configured) rather than `error` (reserved for invalid or failed states). `error` would be appropriate for a future "API key verification failed" state.

### 8.2 Settings Page — Connection Status (Future)

**File:** `web/src/features/settings/settings-page.tsx:171-181`

The current vault connection status uses a colored dot + text, not a badge pattern. If badgeified in the future:

```tsx
<Badge variant={health?.vault_connected ? "success" : "error"}>
  {health?.vault_connected ? "Connected" : "Disconnected"}
</Badge>
```

### 8.3 Citation Badge (Custom — Do Not Replace)

**File:** `web/src/features/chat/citation-badge.tsx`

The citation badge is a specialized interactive component (popover trigger) and should **not** be replaced with the generic Badge primitive. It uses its own inline classes and should remain a custom component. If styling alignment is needed, adopt `rounded-sm`, `border`, and `text-[11px]` from the Badge spec.

---

## Appendix A: Accessibility Checklist

| Check | Button | Badge |
|---|---|---|
| Color contrast (default) | #2B2116 on #E6A23C = 7.21:1 ✅ AAA | Same ✅ |
| Color contrast (disabled) | 50% opacity on AAA base → ~3.6:1 ⚠️ acceptable for disabled | Same ⚠️ |
| Focus indicator | 2px amber ring, 2px offset ✅ | 2px ring on interactive badges ✅ |
| Icon-only labels | `aria-label` required on `icon` / `icon-sm` sizes | N/A |
| Loading state | `aria-busy="true"`, `disabled` ✅ | N/A |
| Motion sensitivity | `prefers-reduced-motion` should disable spinner | N/A |
| Keyboard | Native `<button>` semantics, Enter/Space activation ✅ | `role="status"` or native `<div>` semantics |

## Appendix B: Token Cross-Reference

| CSS Custom Property | Tailwind Class | Used In |
|---|---|---|
| `--color-primary` | `bg-primary` | Button default, Badge default |
| `--color-primary-hover` | `bg-primary-hover` | Button default hover |
| `--color-primary-active` | `bg-primary-active` | Button default active |
| `--color-primary-foreground` | `text-primary-foreground` | Button default text, Badge default text |
| `--color-destructive` | `bg-destructive` | Button destructive, Badge destructive |
| `--color-destructive-foreground` | `text-destructive-foreground` | Button/ Badge destructive text |
| `--color-secondary` | `bg-secondary` | Button secondary, Badge secondary |
| `--color-secondary-foreground` | `text-secondary-foreground` | Button/ Badge secondary text |
| `--color-border` | `border-border` | Button outline/secondary, Badge outline/secondary |
| `--color-accent` | `bg-accent` | Button ghost/outline/secondary hover |
| `--color-accent-foreground` | `text-accent-foreground` | Button ghost/outline/secondary hover text |
| `--color-muted-foreground` | `text-muted-foreground` | Button ghost default, Badge outline |
| `--color-ring` | `ring-ring` | Focus ring |
| `--color-background` | `ring-offset-background` | Focus ring offset |
| `--color-status-success` | `text-status-success` | Badge success |
| `--color-status-success-bg` | `bg-status-success-bg` | Badge success background |
| `--color-status-warning` | `text-status-warning` | Badge warning |
| `--color-status-warning-bg` | `bg-status-warning-bg` | Badge warning background |
| `--color-status-error` | `text-status-error` | Badge error |
| `--color-status-error-bg` | `bg-status-error-bg` | Badge error background |
| `--color-status-info` | `text-status-info` | Badge info |
| `--color-status-info-bg` | `bg-status-info-bg` | Badge info background |

## Appendix C: Implementation Checklist

- [ ] Add `--color-status-*-bg` tokens to `globals.css` `@theme` and `.dark` blocks
- [ ] Update `button.tsx` with new CVA variants, sizes, and loading prop
- [ ] Update `badge.tsx` with 4 new status variants
- [ ] Replace inline button #1 (session-list new chat)
- [ ] Replace inline button #2 (session-list delete — with `data-destructive`)
- [ ] Replace inline button #3 (sources-panel close)
- [ ] Replace inline button #4 (sources-panel clear)
- [ ] Replace inline button #5 (sources-panel done)
- [ ] Replace inline button #6 (message-input send)
- [ ] Replace inline button #7 (message-input stop)
- [ ] Replace inline button #8 (chat-area new chat empty state)
- [ ] Replace inline button #9 (chat-area sources toggle)
- [ ] Replace inline button #10 (chat-area new button)
- [ ] Replace hardcoded badge (settings API key status)
- [ ] Verify `prefers-reduced-motion` disables spinner animation
- [ ] Add `aria-label` to all icon-only button instances
- [ ] Visual QA: verify light + dark mode across all variants

---

*Document version: 1.0.1 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
