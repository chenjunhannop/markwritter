# Form Input Primitives — Component Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion spec:** `docs/design-system/components-button-badge.md`
> **Implementation:** `web/src/components/ui/{input,textarea,checkbox,select,segmented-control,switch}.tsx`

---

## Table of Contents

1. [Design Decisions](#1-design-decisions)
2. [Input — Restyled](#2-input--restyled)
3. [Textarea — Restyled](#3-textarea--restyled)
4. [Checkbox — Restyled (Radix)](#4-checkbox--restyled-radix)
5. [Select — New (Radix)](#5-select--new-radix)
6. [SegmentedControl — New (Custom)](#6-segmentedcontrol--new-custom)
7. [Switch / Toggle — New (Radix)](#7-switch--toggle--new-radix)
8. [Figma Component Structure](#8-figma-component-structure)
9. [Native Element Migration Mapping](#9-native-element-migration-mapping)

---

## 1. Design Decisions

### 1.1 Component-Level Radius

The core token scale (`tokens.md`) defines `radius-xs=4px`, `radius-sm=6px`, `radius-md=8px`. Form inputs use a **component-level radius override** of 10px — the same treatment established for Buttons in `components-button-badge.md §1.1`:

| Component | Radius | Tailwind | Rationale |
|---|---|---|---|
| Input | 10px | `rounded-[10px]` | Matches Button height; larger targets need rounder corners |
| Textarea | 10px | `rounded-[10px]` | Visual parity with Input |
| Select Trigger | 10px | `rounded-[10px]` | Same as Input |
| Select Content (dropdown) | 14px | `rounded-[14px]` | Slightly rounder dropdown to differentiate from trigger |
| SegmentedControl container | 10px | `rounded-[10px]` | Matches Input |
| SegmentedControl segment pill | 7px | `rounded-[7px]` | Inner pill with 3px clearance to container edge |
| Checkbox | 4px | `rounded-xs` | Small control stays tight (token `radius-xs`) |
| Switch track | full | `rounded-full` | Pill shape |

### 1.2 Glass Background Treatment

On glass surfaces (sidebar, top bar), Input adopts the `glass/ultra-thin` tier instead of `surface-base`. This is handled via an optional `data-glass` attribute or a `.glass` CSS modifier class:

```tsx
<Input data-glass />  // → uses glass background instead of surface-base
```

Textarea, Select Content, and SegmentedControl items **always** use solid surfaces — glass treatment is too distracting for multi-line or dropdown contexts.

### 1.3 Height Harmonization

All single-line form controls share the same 38px height, matching the Button default (36px) with a 2px increase for better text padding:

| Component | Height |
|---|---|
| Input | 38px (`h-[38px]`) |
| Select Trigger | 38px (`h-[38px]`) |
| SegmentedControl | 38px (`h-[38px]`) |
| Textarea | min 60px, max 144px |
| Checkbox | 18×18px (inline) |
| Switch | 44×24px (track) |

### 1.4 Radix Package Import Convention

The project uses the unified `radix-ui` package (v1.4.3+). All Radix primitives are imported as namespace objects:

```tsx
import { Checkbox } from "radix-ui";    // → Checkbox.Root, Checkbox.Indicator
import { Select } from "radix-ui";      // → Select.Root, Select.Trigger, etc.
import { Switch } from "radix-ui";      // → Switch.Root, Switch.Thumb
```

### 1.5 Focus Ring Standard

All form inputs use the same focus ring treatment established by Buttons:

```css
focus-visible:outline-none
focus-visible:ring-2
focus-visible:ring-ring
focus-visible:ring-offset-2
focus-visible:ring-offset-background
```

Error-state inputs change the ring color to `destructive`.

---

## 2. Input — Restyled

### 2.1 Anatomy

| Property | Value |
|---|---|
| Height | 38px |
| Padding X | 12px (`px-3`) |
| Padding Y | 0 (single-line, centered via flex) |
| Border radius | 10px (`rounded-[10px]`) |
| Border | 1px solid `border` |
| Background | `surface-base` (solid) / `glass/ultra-thin` (on glass) |
| Typography | body (15px / 400 / 1.5) |
| Placeholder color | `muted-foreground` |
| Shadow | none (resting), `shadow-resting` on glass |

### 2.2 State Color Matrix

| State | Light Background | Light Border | Light Ring | Dark Background | Dark Border | Dark Ring |
|---|---|---|---|---|---|---|
| **default** | `surface-base` #FFF9F2 | `border` #DCC7A7 | — | `surface-base` #1A140F | `border` #5A4630 | — |
| **focus** | `surface-base` #FFF9F2 | `ring` #E6A23C | `ring/20%` | `surface-base` #1A140F | `ring` #F0B04A | `ring/20%` |
| **error** | `surface-base` #FFF9F2 | `destructive` #C0392B | `destructive/20%` | `surface-base` #1A140F | `destructive` #E74C3C | `destructive/20%` |
| **disabled** | `surface-base` at 50% opacity | `border` at 50% | — | `surface-base` at 50% | `border` at 50% | — |
| **glass default** | `rgba(255,249,242,0.45)` | `rgba(220,199,167,0.10)` | — | `rgba(26,20,15,0.40)` | `rgba(90,70,48,0.12)` | — |
| **glass focus** | same | `ring` #E6A23C | `ring/20%` | same | `ring` #F0B04A | `ring/20%` |

### 2.3 Icon Slots

| Slot | Padding | Icon Size | Position |
|---|---|---|---|
| `leading-icon` | `padding-left: 40px` (`pl-10`) | 16px (`size-4`) | absolute, left 12px |
| `trailing-icon` | `padding-right: 40px` (`pr-10`) | 16px (`size-4`) | absolute, right 12px |

Common uses for trailing icon: clear button (`X`), password toggle (`Eye` / `EyeOff`).

### 2.4 Motion

| Interaction | Duration | Easing |
|---|---|---|
| Border color change (focus/error) | 150ms | ease-out |
| Ring appear | 150ms | ease-out |

### 2.5 Component Code

```tsx
// web/src/components/ui/input.tsx
import { forwardRef, type InputHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

const Input = forwardRef<
  HTMLInputElement,
  InputHTMLAttributes<HTMLInputElement> & {
    iconLeft?: React.ReactNode;
    iconRight?: React.ReactNode;
    glass?: boolean;
  }
>(({ className, type, iconLeft, iconRight, glass, ...props }, ref) => {
  return (
    <div className="relative">
      {iconLeft && (
        <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground [&_svg]:size-4">
          {iconLeft}
        </span>
      )}
      <input
        type={type}
        className={cn(
          [
            "flex h-[38px] w-full rounded-[10px] border border-border px-3",
            "bg-surface-base text-foreground text-[15px]",
            "placeholder:text-muted-foreground",
            "transition-[border-color,box-shadow] duration-150 ease-out",
            "focus-visible:outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/20 focus-visible:ring-offset-2 focus-visible:ring-offset-background",
            "disabled:cursor-not-allowed disabled:opacity-50",
            // Error state (via data attribute or aria-invalid)
            "aria-[invalid=true]:border-destructive aria-[invalid=true]:focus-visible:ring-destructive/20",
          ].join(" "),
          iconLeft && "pl-10",
          iconRight && "pr-10",
          glass && [
            "bg-white/45 backdrop-blur-[8px] saturate-[120%]",
            "dark:bg-[rgba(26,20,15,0.40)]",
            "border-white/10 dark:border-[rgba(90,70,48,0.12)]",
          ].join(" "),
          className,
        )}
        ref={ref}
        {...props}
      />
      {iconRight && (
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground [&_svg]:size-4">
          {iconRight}
        </span>
      )}
    </div>
  );
});
Input.displayName = "Input";

export { Input };
```

---

## 3. Textarea — Restyled

### 3.1 Anatomy

| Property | Value |
|---|---|
| Min height | 60px |
| Max height | 144px (6 × 24px lines) |
| Padding X | 12px (`px-3`) |
| Padding Y | 8px (`py-2`) |
| Border radius | 10px (`rounded-[10px]`) |
| Border | 1px solid `border` |
| Background | `surface-base` (always solid — never glass) |
| Typography | body (15px / 400 / 1.5) |
| Auto-resize | Yes — JavaScript-driven up to max-height |
| Placeholder color | `muted-foreground` |

### 3.2 State Color Matrix

Same as Input §2.2, minus glass variants (Textarea never uses glass).

| State | Light Background | Light Border | Dark Background | Dark Border |
|---|---|---|---|---|
| **default** | `surface-base` #FFF9F2 | `border` #DCC7A7 | `surface-base` #1A140F | `border` #5A4630 |
| **focus** | `surface-base` | `ring` #E6A23C | `surface-base` | `ring` #F0B04A |
| **error** | `surface-base` | `destructive` #C0392B | `surface-base` | `destructive` #E74C3C |
| **disabled** | 50% opacity | 50% opacity | 50% opacity | 50% opacity |

### 3.3 Auto-Resize Behavior

```tsx
// Auto-resize: grows from min-height (60px) to max-height (144px)
// then shows scrollbar. Shrinks back on delete.
const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
  const el = e.target;
  el.style.height = "60px";           // reset
  el.style.height = `${el.scrollHeight}px`; // grow to content
};
```

### 3.4 Component Code

```tsx
// web/src/components/ui/textarea.tsx
import { forwardRef, type TextareaHTMLAttributes, useCallback } from "react";
import { cn } from "@/lib/utils";

const Textarea = forwardRef<
  HTMLTextAreaElement,
  TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, onInput, ...props }, ref) => {
  const handleInput = useCallback(
    (e: React.FormEvent<HTMLTextAreaElement>) => {
      const el = e.currentTarget;
      el.style.height = "60px";
      el.style.height = `${Math.min(el.scrollHeight, 144)}px`;
      onInput?.(e as React.FormEvent<HTMLTextAreaElement>);
    },
    [onInput],
  );

  return (
    <textarea
      className={cn(
        [
          "flex min-h-[60px] max-h-[144px] w-full rounded-[10px] border border-border",
          "bg-surface-base px-3 py-2 text-[15px] text-foreground",
          "placeholder:text-muted-foreground",
          "transition-[border-color,box-shadow] duration-150 ease-out",
          "focus-visible:outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/20 focus-visible:ring-offset-2 focus-visible:ring-offset-background",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "aria-[invalid=true]:border-destructive aria-[invalid=true]:focus-visible:ring-destructive/20",
          "overflow-y-auto resize-none",
        ].join(" "),
        className,
      )}
      ref={ref}
      onInput={handleInput}
      {...props}
    />
  );
});
Textarea.displayName = "Textarea";

export { Textarea };
```

---

## 4. Checkbox — Restyled (Radix)

### 4.1 Anatomy

| Property | Value |
|---|---|
| Size | 18 × 18px |
| Border radius | 4px (`rounded-xs`) → token `radius-xs` |
| Border | 1px solid `border` |
| Background (unchecked) | `surface-base` |
| Background (checked) | `primary` |
| Checkmark | white SVG, 14px, stroke-width 3 |
| Focus ring | 2px `ring`, offset 2px |

### 4.2 State Color Matrix

| State | Light Background | Light Border | Light Icon | Dark Background | Dark Border | Dark Icon |
|---|---|---|---|---|---|---|
| **unchecked** | `surface-base` #FFF9F2 | `border` #DCC7A7 | — | `surface-base` #1A140F | `border` #5A4630 | — |
| **checked** | `primary` #E6A23C | transparent | white | `primary` #F0B04A | transparent | white |
| **indeterminate** | `primary` #E6A23C | transparent | white minus | `primary` #F0B04A | transparent | white minus |
| **disabled** | 50% opacity | 50% opacity | 50% opacity | 50% opacity | 50% opacity | 50% opacity |
| **focus** | unchanged | `ring` #E6A23C | — | unchanged | `ring` #F0B04A | — |

### 4.3 Animation

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Check / Uncheck | 150ms | ease-out | Scale: 0.8 → 1.0 (check), 1.0 → 0.8 (uncheck) |

### 4.4 Component Code

```tsx
// web/src/components/ui/checkbox.tsx
import { Checkbox } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

const UiCheckbox = React.forwardRef<
  React.ComponentRef<typeof Checkbox.Root>,
  React.ComponentPropsWithoutRef<typeof Checkbox.Root>
>(({ className, ...props }, ref) => (
  <Checkbox.Root
    ref={ref}
    className={cn(
      [
        "peer h-[18px] w-[18px] shrink-0 rounded-xs",
        "border border-border bg-surface-base",
        "transition-all duration-150 ease-out",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "disabled:cursor-not-allowed disabled:opacity-50",
        // Checked state
        "data-[state=checked]:border-transparent data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground",
        // Indeterminate state
        "data-[state=indeterminate]:border-transparent data-[state=indeterminate]:bg-primary data-[state=indeterminate]:text-primary-foreground",
        // Scale animation
        "data-[state=checked]:scale-100 data-[state=unchecked]:scale-100",
        "active:data-[state=unchecked]:scale-[0.8] active:data-[state=checked]:scale-[0.8]",
      ].join(" "),
      className,
    )}
    {...props}
  >
    <Checkbox.Indicator
      className={cn("flex items-center justify-center text-current")}
    >
      {/* Check icon */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="h-[14px] w-[14px]"
        role="img"
        aria-label="Check"
      >
        <path d="M20 6 9 17l-5-5" />
      </svg>
    </Checkbox.Indicator>
  </Checkbox.Root>
));
UiCheckbox.displayName = "Checkbox";

export { UiCheckbox as Checkbox };
```

> **Note:** For indeterminate state, replace the checkmark SVG path with `<line x1="5" y1="12" x2="19" y2="12" />` (horizontal minus line). This can be handled via a compound component pattern or by using two separate Indicator children with conditional visibility.

---

## 5. Select — New (Radix)

### 5.1 Radix Composition

Built on Radix Select. The component wraps these sub-components:

```
Select.Root
├── Select.Trigger        (styled like Input)
│   ├── Select.Value      (selected text / placeholder)
│   └── Select.Icon       (chevron-down, 16px)
├── Select.Portal
│   └── Select.Content    (glass-tier-thin dropdown)
│       ├── Select.ScrollUpButton
│       ├── Select.Viewport
│       │   ├── Select.Group (optional)
│       │   │   ├── Select.Label
│       │   │   └── Select.Item
│       │   │       ├── Select.ItemText
│       │   │       └── Select.ItemIndicator  (checkmark)
│       │   ├── Select.Separator
│       │   └── Select.Item ...
│       └── Select.ScrollDownButton
```

### 5.2 Trigger Anatomy

Identical to Input (38px height, 10px radius) with a right-aligned chevron-down icon.

| Property | Value |
|---|---|
| Height | 38px |
| Padding X | 12px left, 36px right (for chevron) |
| Border radius | 10px |
| Border | 1px solid `border` |
| Background | `surface-base` |
| Typography | body (15px / 400) |
| Chevron icon | 16px `ChevronDown` from Lucide, `muted-foreground` |
| Placeholder | `muted-foreground`, shown via `data-placeholder` |

### 5.3 Content (Dropdown) Anatomy

| Property | Value |
|---|---|
| Background | glass-tier-thin (solid surface fallback: `popover`) |
| Border radius | 14px |
| Shadow | `shadow-xl` |
| Max height | 240px with scroll |
| Padding Y | 4px |
| Position | Popper (bottom-start), 4px offset from trigger |
| Animation | fade-in + slide-down 150ms ease-out |

### 5.4 Item Anatomy

| Property | Value |
|---|---|
| Padding | 8px 12px |
| Border radius | 8px (`rounded-md`) |
| Typography | body-sm (14px / 400) |
| Hover | `accent` background |
| Focus-visible | `ring` outline |
| Selected | `primary` text color + checkmark icon on right |
| Disabled | opacity 50% |

### 5.5 Supporting Elements

**Separator:** 1px `border`, horizontal, full width within viewport, margin 4px vertical.

**Label:** `caption` (12px / 500), `muted-foreground`, padding 8px 12px 4px.

**Scroll buttons:** 24px height, centered chevron, `muted-foreground`, fade in/out on overflow.

### 5.6 State Color Matrix — Trigger

Same as Input §2.2 (default, focus, error, disabled). No glass variant for trigger.

### 5.7 State Color Matrix — Content & Items

| Element | Light | Dark |
|---|---|---|
| **Content background** | `rgba(255,249,242,0.58)` + `blur(12px)` | `rgba(26,20,15,0.52)` + `blur(12px)` |
| **Content fallback** | `popover` #FFF9F2 | `popover` #1A140F |
| **Item default** | transparent | transparent |
| **Item hover** | `accent` #F6E6CA | `accent` #31261C |
| **Item selected text** | `primary` #E6A23C | `primary` #F0B04A |
| **Item disabled** | 50% opacity | 50% opacity |
| **Separator** | `border` #DCC7A7 | `border` #5A4630 |
| **Label text** | `muted-foreground` #78624B | `muted-foreground` #C7B69F |

### 5.8 Component Code

```tsx
// web/src/components/ui/select.tsx
import { Select } from "radix-ui";
import { Check, ChevronDown, ChevronUp } from "lucide-react";
import * as React from "react";
import { cn } from "@/lib/utils";

// ─── Trigger ───
const SelectTrigger = React.forwardRef<
  React.ComponentRef<typeof Select.Trigger>,
  React.ComponentPropsWithoutRef<typeof Select.Trigger>
>(({ className, children, ...props }, ref) => (
  <Select.Trigger
    ref={ref}
    className={cn(
      [
        "flex h-[38px] w-full items-center justify-between rounded-[10px]",
        "border border-border bg-surface-base px-3 pr-9",
        "text-[15px] text-foreground",
        "transition-[border-color,box-shadow] duration-150 ease-out",
        "focus-visible:outline-none focus-visible:border-ring focus-visible:ring-2 focus-visible:ring-ring/20 focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "data-[placeholder]:text-muted-foreground",
      ].join(" "),
      className,
    )}
    {...props}
  >
    {children}
    <Select.Icon asChild>
      <ChevronDown className="size-4 text-muted-foreground" />
    </Select.Icon>
  </Select.Trigger>
));
SelectTrigger.displayName = "SelectTrigger";

// ─── Value ───
const SelectValue = Select.Value;

// ─── Content ───
const SelectContent = React.forwardRef<
  React.ComponentRef<typeof Select.Content>,
  React.ComponentPropsWithoutRef<typeof Select.Content>
>(({ className, children, position = "popper", ...props }, ref) => (
  <Select.Portal>
    <Select.Content
      ref={ref}
      position={position}
      className={cn(
        [
          "relative z-50 max-h-[240px] min-w-[8rem] overflow-hidden",
          "rounded-[14px]",
          "border border-border/50",
          "shadow-xl",
          // Glass-tier-thin background
          "bg-[rgba(255,249,242,0.58)] backdrop-blur-[12px] saturate-[130%]",
          "dark:bg-[rgba(26,20,15,0.52)]",
          "text-foreground",
          // Animation
          "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95",
          "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
          "data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2",
          "data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2",
        ].join(" "),
        position === "popper" &&
          "data-[side=bottom]:translate-y-1 data-[side=top]:-translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1",
        className,
      )}
      {...props}
    >
      <SelectScrollUpButton />
      <Select.Viewport
        className={cn(
          "p-1",
          position === "popper" &&
            "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]",
        )}
      >
        {children}
      </Select.Viewport>
      <SelectScrollDownButton />
    </Select.Content>
  </Select.Portal>
));
SelectContent.displayName = "SelectContent";

// ─── Item ───
const SelectItem = React.forwardRef<
  React.ComponentRef<typeof Select.Item>,
  React.ComponentPropsWithoutRef<typeof Select.Item>
>(({ className, children, ...props }, ref) => (
  <Select.Item
    ref={ref}
    className={cn(
      [
        "relative flex w-full cursor-pointer select-none items-center rounded-md",
        "py-2 pl-3 pr-8",
        "text-sm text-foreground outline-none",
        "transition-colors duration-100 ease-out",
        "data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        "hover:bg-accent",
        "focus-visible:bg-accent",
        "data-[highlighted]:bg-accent",
        // Selected state
        "data-[state=checked]:text-primary",
      ].join(" "),
      className,
    )}
    {...props}
  >
    <Select.ItemText>{children}</Select.ItemText>
    <Select.ItemIndicator className="absolute right-3 flex items-center">
      <Check className="size-4 text-primary" />
    </Select.ItemIndicator>
  </Select.Item>
));
SelectItem.displayName = "SelectItem";

// ─── Separator ───
const SelectSeparator = React.forwardRef<
  React.ComponentRef<typeof Select.Separator>,
  React.ComponentPropsWithoutRef<typeof Select.Separator>
>(({ className, ...props }, ref) => (
  <Select.Separator
    ref={ref}
    className={cn("-mx-1 my-1 h-px bg-border", className)}
    {...props}
  />
));
SelectSeparator.displayName = "SelectSeparator";

// ─── Label ───
const SelectLabel = React.forwardRef<
  React.ComponentRef<typeof Select.Label>,
  React.ComponentPropsWithoutRef<typeof Select.Label>
>(({ className, ...props }, ref) => (
  <Select.Label
    ref={ref}
    className={cn("px-3 pt-2 pb-1 text-xs font-medium text-muted-foreground", className)}
    {...props}
  />
));
SelectLabel.displayName = "SelectLabel";

// ─── Scroll Buttons ───
const SelectScrollUpButton = React.forwardRef<
  React.ComponentRef<typeof Select.ScrollUpButton>,
  React.ComponentPropsWithoutRef<typeof Select.ScrollUpButton>
>(({ className, ...props }, ref) => (
  <Select.ScrollUpButton
    ref={ref}
    className={cn("flex cursor-default items-center justify-center py-1", className)}
    {...props}
  >
    <ChevronUp className="size-4 text-muted-foreground" />
  </Select.ScrollUpButton>
));
SelectScrollUpButton.displayName = "SelectScrollUpButton";

const SelectScrollDownButton = React.forwardRef<
  React.ComponentRef<typeof Select.ScrollDownButton>,
  React.ComponentPropsWithoutRef<typeof Select.ScrollDownButton>
>(({ className, ...props }, ref) => (
  <Select.ScrollDownButton
    ref={ref}
    className={cn("flex cursor-default items-center justify-center py-1", className)}
    {...props}
  >
    <ChevronDown className="size-4 text-muted-foreground" />
  </Select.ScrollDownButton>
));
SelectScrollDownButton.displayName = "SelectScrollDownButton";

// ─── Group ───
const SelectGroup = Select.Group;

export {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
  SelectItem as SelectItemText, // deprecated alias; use SelectItem children directly
  SelectSeparator,
  SelectLabel,
  SelectGroup,
  SelectScrollUpButton,
  SelectScrollDownButton,
};
```

---

## 6. SegmentedControl — New (Custom)

### 6.1 Rationale

No Radix primitive exists for segmented controls. A custom implementation provides:
- Animated sliding indicator pill
- Spring-based motion for playful feel
- Support for 2–5 segments
- Full keyboard navigation (arrow keys)

### 6.2 Anatomy

**Container:**
| Property | Value |
|---|---|
| Display | `inline-flex` |
| Height | 38px |
| Padding | 3px |
| Border radius | 10px |
| Background | `surface-sunken` (solid) / glass-ultra-thin (on glass) |
| Role | `radiogroup` |

**Segment (each option):**
| Property | Value |
|---|---|
| Flex | `flex-1` |
| Align | center |
| Padding | 0 12px |
| Border radius | 7px (inner pill) |
| Typography | subhead (13px / 500) |
| Min width | 48px |

**Active segment:**
| Property | Value |
|---|---|
| Background | `surface-base` |
| Shadow | `shadow-resting` |
| Text color | `primary` |
| Sliding indicator | absolute-position bg pill |

**Inactive segment:**
| Property | Value |
|---|---|
| Background | transparent |
| Text color | `muted-foreground` |
| Hover | `accent` background (subtle) |

### 6.3 State Color Matrix

| Element | Light | Dark |
|---|---|---|
| **Container bg** | `surface-sunken` #F6E6CA | `surface-sunken` #0F0B08 |
| **Active pill bg** | `surface-base` #FFF9F2 | `surface-base` #1A140F |
| **Active text** | `primary` #E6A23C | `primary` #F0B04A |
| **Inactive text** | `muted-foreground` #78624B | `muted-foreground` #C7B69F |
| **Inactive hover bg** | `accent` #F6E6CA | `accent` #31261C |
| **Disabled** | 50% opacity (entire control) | 50% opacity |

### 6.4 Sliding Indicator

An absolutely-positioned pill element that animates between segment positions:

| Property | Value |
|---|---|
| Position | absolute |
| Background | `surface-base` |
| Border radius | 7px |
| Shadow | `shadow-resting` |
| Size | matches active segment dimensions |
| Transition | 300ms spring (`cubic-bezier(0.34, 1.56, 0.64, 1)`) |
| Properties animated | `left`, `width` |

### 6.5 Motion

| Interaction | Duration | Easing |
|---|---|---|
| Pill slide | 300ms | spring (`cubic-bezier(0.34, 1.56, 0.64, 1)`) |
| Hover (inactive) | 150ms | ease-out |

### 6.6 Keyboard Navigation

| Key | Action |
|---|---|
| `ArrowRight` / `ArrowDown` | Select next segment (wrap) |
| `ArrowLeft` / `ArrowUp` | Select previous segment (wrap) |
| `Home` | Select first segment |
| `End` | Select last segment |

### 6.7 Component Code

```tsx
// web/src/components/ui/segmented-control.tsx
import { useCallback, useId, useRef, useState } from "react";
import { cn } from "@/lib/utils";

export interface SegmentedControlOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SegmentedControlProps {
  options: SegmentedControlOption[];
  value: string;
  onValueChange: (value: string) => void;
  disabled?: boolean;
  className?: string;
  glass?: boolean;
  "aria-label"?: string;
}

export function SegmentedControl({
  options,
  value,
  onValueChange,
  disabled = false,
  className,
  glass = false,
  "aria-label": ariaLabel,
}: SegmentedControlProps) {
  const baseId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const activeIndex = options.findIndex((o) => o.value === value);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      let nextIndex = activeIndex;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        nextIndex = (activeIndex + 1) % options.length;
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        nextIndex = (activeIndex - 1 + options.length) % options.length;
      } else if (e.key === "Home") {
        nextIndex = 0;
      } else if (e.key === "End") {
        nextIndex = options.length - 1;
      } else {
        return;
      }
      e.preventDefault();
      const next = options[nextIndex];
      if (!next.disabled) {
        onValueChange(next.value);
      }
    },
    [activeIndex, options, onValueChange],
  );

  return (
    <div
      ref={containerRef}
      role="radiogroup"
      aria-label={ariaLabel}
      aria-disabled={disabled}
      className={cn(
        [
          "relative inline-flex h-[38px] items-center gap-0.5 rounded-[10px]",
          "bg-surface-sunken p-[3px]",
        ].join(" "),
        glass && [
          "bg-white/45 backdrop-blur-[8px] saturate-[120%]",
          "dark:bg-[rgba(26,20,15,0.40)]",
        ].join(" "),
        disabled && "opacity-50 pointer-events-none",
        className,
      )}
      onKeyDown={handleKeyDown}
    >
      {/* Sliding indicator pill */}
      {activeIndex >= 0 && (
        <div
          className="absolute top-[3px] bottom-[3px] rounded-[7px] bg-surface-base shadow-[0_1px_3px_rgba(0,0,0,0.06)] transition-[left,width] duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]"
          style={{
            left: `calc(${(activeIndex / options.length) * 100}% + 3px)`,
            width: `calc(${100 / options.length}% - 3px * ${(options.length - 1) / options.length})`,
          }}
          aria-hidden="true"
        />
      )}

      {options.map((option, index) => {
        const isActive = option.value === value;
        const isHovered = hoveredIndex === index;
        return (
          <button
            key={option.value}
            id={`${baseId}-${option.value}`}
            type="button"
            role="radio"
            aria-checked={isActive}
            disabled={disabled || option.disabled}
            className={cn(
              [
                "relative z-10 flex flex-1 items-center justify-center",
                "h-full min-w-[48px] rounded-[7px] px-3",
                "text-[13px] font-medium",
                "transition-colors duration-150 ease-out",
                "outline-none",
                "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1",
              ].join(" "),
              isActive
                ? "text-primary"
                : [
                    "text-muted-foreground",
                    isHovered && !isActive && "bg-accent/60",
                  ].join(" "),
              (disabled || option.disabled) && "opacity-50 cursor-not-allowed",
            )}
            onClick={() => !option.disabled && onValueChange(option.value)}
            onMouseEnter={() => setHoveredIndex(index)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
```

---

## 7. Switch / Toggle — New (Radix)

### 7.1 Anatomy

**Track:**
| Property | Value |
|---|---|
| Width | 44px |
| Height | 24px |
| Border radius | full (9999px) |
| Border | 1px solid `border` (off) / transparent (on) |
| Background (off) | `surface-raised` |
| Background (on) | `primary` |
| Transition | 150ms ease-out (background) |

**Thumb:**
| Property | Value |
|---|---|
| Size | 18 × 18px |
| Border radius | full (9999px) |
| Background | white |
| Shadow | `shadow-xl` |
| Margin | 3px from track edge |
| Slide distance | 20px (44 - 18 - 3×2) |
| Transition | 150ms ease-out (transform) |

### 7.2 State Color Matrix

| State | Light Track BG | Light Track Border | Light Thumb | Dark Track BG | Dark Track Border | Dark Thumb |
|---|---|---|---|---|---|---|
| **off** | `surface-raised` #FCF6EE | `border` #DCC7A7 | white | `surface-raised` #231B14 | `border` #5A4630 | white |
| **on** | `primary` #E6A23C | transparent | white | `primary` #F0B04A | transparent | white |
| **disabled** | 50% opacity | 50% opacity | 50% opacity | 50% opacity | 50% opacity | 50% opacity |
| **focus** | unchanged | `ring` #E6A23C | — | unchanged | `ring` #F0B04A | — |

### 7.3 Motion

| Interaction | Duration | Easing | Effect |
|---|---|---|---|
| Toggle (on ↔ off) | 150ms | ease-out | Thumb slides 20px |
| Background change | 150ms | ease-out | Color transition |
| Disabled | none | — | No animation |

### 7.4 Component Code

```tsx
// web/src/components/ui/switch.tsx
import { Switch } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

const UiSwitch = React.forwardRef<
  React.ComponentRef<typeof Switch.Root>,
  React.ComponentPropsWithoutRef<typeof Switch.Root>
>(({ className, ...props }, ref) => (
  <Switch.Root
    ref={ref}
    className={cn(
      [
        "group relative inline-flex h-6 w-11 shrink-0 cursor-pointer",
        "rounded-full border border-border",
        "bg-surface-raised",
        "transition-[background-color,border-color] duration-150 ease-out",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        "disabled:cursor-not-allowed disabled:opacity-50",
        // On state
        "data-[state=checked]:border-transparent data-[state=checked]:bg-primary",
      ].join(" "),
      className,
    )}
    {...props}
  >
    <Switch.Thumb
      className={cn(
        [
          "pointer-events-none block h-[18px] w-[18px] rounded-full",
          "bg-white shadow-xl",
          "transition-transform duration-150 ease-out",
          "translate-x-[3px]",
          "data-[state=checked]:translate-x-[23px]",
        ].join(" "),
      )}
    />
  </Switch.Root>
));
UiSwitch.displayName = "Switch";

export { UiSwitch as Switch };
```

**Thumb position math:**
- Off: `translate-x-[3px]` (3px from left edge)
- On: `translate-x-[23px]` (44px track - 18px thumb - 3px right margin = 23px)
- Slide distance: 23 - 3 = 20px ✓

---

## 8. Figma Component Structure

### 8.1 Input

**Component name:** `Input`

**Auto Layout:**
- Direction: Horizontal
- Primary axis: Fill container
- Counter axis: Fixed (38px)
- Padding: 0 12px
- Gap: 0

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `default`, `focus`, `error`, `disabled` | `default` |
| `Has Leading Icon` | Boolean | `true`, `false` | `false` |
| `Has Trailing Icon` | Boolean | `true`, `false` | `false` |
| `On Glass` | Boolean | `true`, `false` | `false` |
| `Placeholder` | Text | — | `Placeholder...` |
| `Value` | Text | — | `` (empty) |
| `Leading Icon` | Instance Swap | Lucide icon set | `Search` |
| `Trailing Icon` | Instance Swap | Lucide icon set | `X` |

**Layer Structure:**
```
📦 Input (Component Set)
├── 🔀 Variant: State (4 values)
├── 🔀 Variant: Has Leading Icon (2 values)
├── 🔀 Variant: Has Trailing Icon (2 values)
├── 🔘 Boolean: On Glass
├── 📝 Text property: Placeholder
├── 📝 Text property: Value
├── 🔄 Instance swap: Leading Icon
└── 🔄 Instance swap: Trailing Icon

Layer Structure:
Input (Frame, Auto Layout, h-38px, rounded-10px)
├── Leading Icon (Frame, 16×16, hidden when Has Leading Icon=false)
│   └── [Icon instance]
├── Text Content (Frame, flex-1)
│   ├── Value (Text, 15px/400, foreground)
│   └── Placeholder (Text, 15px/400, muted-foreground)
└── Trailing Icon (Frame, 16×16, hidden when Has Trailing Icon=false)
    └── [Icon instance]
```

### 8.2 Textarea

**Component name:** `Textarea`

Same variant structure as Input, minus icon slots and glass boolean. Min-height 60px, max-height 144px.

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `default`, `focus`, `error`, `disabled` | `default` |
| `Rows` | Variant | `2`, `3`, `4`, `5`, `6` | `3` |
| `Placeholder` | Text | — | `Type here...` |
| `Value` | Text | — | `` |

### 8.3 Checkbox

**Component name:** `Checkbox`

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `unchecked`, `checked`, `indeterminate`, `disabled` | `unchecked` |
| `Focus` | Boolean | `true`, `false` | `false` |

**Layer Structure:**
```
📦 Checkbox (Component Set)
├── 🔀 Variant: State (4 values)
├── 🔘 Boolean: Focus

Layer Structure:
Checkbox (Frame, 18×18, rounded-4px, border)
├── Check Icon (SVG, hidden when unchecked)
├── Minus Icon (SVG, hidden unless indeterminate)
└── Focus Ring (Frame, hidden unless Focus=true)
```

### 8.4 Select

**Component name:** `SelectTrigger`, `SelectContent`, `SelectItem`

Modeled as 3 separate components that compose together:

**SelectTrigger:**
| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `default`, `focus`, `error`, `disabled` | `default` |
| `Has Value` | Boolean | `true`, `false` | `true` |
| `Value` | Text | — | `English` |
| `Placeholder` | Text | — | `Select...` |

**SelectContent:**
| Property | Type | Values | Default |
|---|---|---|---|
| `Items` | Instance Swap | SelectItem instances | 3 default items |

**SelectItem:**
| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `default`, `hover`, `selected`, `disabled` | `default` |
| `Label` | Text | — | `Option` |

### 8.5 SegmentedControl

**Component name:** `SegmentedControl`

**Auto Layout:**
- Direction: Horizontal
- Primary axis: Fill container
- Counter axis: Fixed (38px)
- Padding: 3px
- Gap: 0
- Position: relative (for sliding indicator)

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Segments` | Variant | `2-segment`, `3-segment`, `4-segment`, `5-segment` | `3-segment` |
| `Active` | Variant | `0`, `1`, `2`, `3`, `4` | `0` |
| `State` | Variant | `default`, `disabled` | `default` |
| `On Glass` | Boolean | `true`, `false` | `false` |
| `Label 1` | Text | — | `Light` |
| `Label 2` | Text | — | `Dark` |
| `Label 3` | Text | — | `System` |

**Layer Structure:**
```
📦 SegmentedControl (Component Set)
├── 🔀 Variant: Segments (4 values)
├── 🔀 Variant: Active (5 values)
├── 🔀 Variant: State (2 values)
├── 🔘 Boolean: On Glass
├── 📝 Text property: Label 1..5

Layer Structure:
SegmentedControl (Frame, Auto Layout, h-38px, rounded-10px, bg-surface-sunken)
├── Sliding Pill (Frame, absolute, rounded-7px, bg-surface-base, shadow-resting)
├── Segment 0 (Frame, flex-1, center)
│   └── Label (Text, 13px/500)
├── Segment 1 (Frame, flex-1, center)
│   └── Label (Text, 13px/500)
└── Segment 2 (Frame, flex-1, center)
    └── Label (Text, 13px/500)
```

### 8.6 Switch

**Component name:** `Switch`

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `State` | Variant | `off`, `on`, `disabled-off`, `disabled-on` | `off` |
| `Focus` | Boolean | `true`, `false` | `false` |

**Layer Structure:**
```
📦 Switch (Component Set)
├── 🔀 Variant: State (4 values)
├── 🔘 Boolean: Focus

Layer Structure:
Switch (Frame, 44×24, rounded-full, border)
├── Thumb (Ellipse, 18×18, white, shadow-xl)
└── Focus Ring (Frame, hidden unless Focus=true)
```

---

## 9. Native Element Migration Mapping

### 9.1 `<select>` → Select Component (4 locations)

| # | File | Line | Current | Replaces | Options |
|---|---|---|---|---|---|
| 1 | `settings-page.tsx` | :58–66 | `<select id="language-select">` | Language selector | en → English, zh → 中文 |
| 2 | `settings-page.tsx` | :238–248 | `<select id="log-level">` | Log level selector | DEBUG, INFO, WARNING, ERROR |
| 3 | `query-page.tsx` | :76–86 | `<select value={mode}>` | Search mode selector | Hybrid, Keyword, Semantic |
| 4 | `skills-page.tsx` | :44–56 | `<select id={selectId}>` | Enum parameter selector | Dynamic (from `input.enum`) |

#### Migration #1: Settings — Language

**Before** (`settings-page.tsx:58–66`):
```tsx
<select
  id="language-select"
  value={language}
  onChange={(e) => setLanguage(e.target.value)}
  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
>
  <option value="en">English</option>
  <option value="zh">中文</option>
</select>
```

**After:**
```tsx
<Select value={language} onValueChange={setLanguage}>
  <SelectTrigger id="language-select" className="w-full max-w-[200px]">
    <SelectValue placeholder="Select language..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="en">English</SelectItem>
    <SelectItem value="zh">中文</SelectItem>
  </SelectContent>
</Select>
```

#### Migration #2: Settings — Log Level

**Before** (`settings-page.tsx:238–248`):
```tsx
<select
  id="log-level"
  value={logLevel}
  onChange={(e) => setLogLevel(e.target.value)}
  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
>
  <option value="DEBUG">DEBUG</option>
  <option value="INFO">INFO</option>
  <option value="WARNING">WARNING</option>
  <option value="ERROR">ERROR</option>
</select>
```

**After:**
```tsx
<Select value={logLevel} onValueChange={setLogLevel}>
  <SelectTrigger id="log-level" className="w-full max-w-[200px]">
    <SelectValue placeholder="Select log level..." />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="DEBUG">DEBUG</SelectItem>
    <SelectItem value="INFO">INFO</SelectItem>
    <SelectItem value="WARNING">WARNING</SelectItem>
    <SelectItem value="ERROR">ERROR</SelectItem>
  </SelectContent>
</Select>
```

#### Migration #3: Query — Search Mode

**Before** (`query-page.tsx:76–86`):
```tsx
<select
  value={mode}
  onChange={(e) => setMode(e.target.value)}
  className="h-9 rounded-md border border-input bg-transparent px-3 text-sm"
>
  {SEARCH_MODES.map((m) => (
    <option key={m.value} value={m.value}>
      {m.label}
    </option>
  ))}
</select>
```

**After:**
```tsx
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
```

#### Migration #4: Skills — Enum Parameter

**Before** (`skills-page.tsx:44–56`):
```tsx
<select
  id={selectId}
  value={(value as string) ?? (input.default as string) ?? ""}
  onChange={(e) => onChange(e.target.value)}
  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
>
  <option value="">Select...</option>
  {input.enum.map((opt) => (
    <option key={opt} value={opt}>{opt}</option>
  ))}
</select>
```

**After:**
```tsx
<Select
  value={(value as string) ?? (input.default as string) ?? ""}
  onValueChange={(v) => onChange(v || undefined)}
>
  <SelectTrigger id={selectId} className="w-full">
    <SelectValue placeholder="Select..." />
  </SelectTrigger>
  <SelectContent>
    {input.enum.map((opt) => (
      <SelectItem key={opt} value={opt}>{opt}</SelectItem>
    ))}
  </SelectContent>
</Select>
```

### 9.2 `<input type="radio">` → SegmentedControl (1 location)

| # | File | Line | Current | Replaces | Options |
|---|---|---|---|---|---|
| 1 | `settings-page.tsx` | :38–51 | 3× `<input type="radio">` | Theme selector | Light, Dark, System |

**Before** (`settings-page.tsx:36–52`):
```tsx
<div className="space-y-2">
  <span className="text-sm font-medium">Theme</span>
  <div className="flex gap-4">
    {(["light", "dark", "system"] as const).map((t) => (
      <label key={t} className="flex cursor-pointer items-center gap-2">
        <input
          type="radio"
          name="theme"
          value={t}
          checked={theme === t}
          onChange={() => setTheme(t)}
          className="accent-primary"
        />
        <span className="text-sm capitalize">{t}</span>
      </label>
    ))}
  </div>
</div>
```

**After:**
```tsx
<div className="space-y-2">
  <span className="text-sm font-medium">Theme</span>
  <SegmentedControl
    aria-label="Theme"
    options={[
      { value: "light", label: "Light" },
      { value: "dark", label: "Dark" },
      { value: "system", label: "System" },
    ]}
    value={theme}
    onValueChange={setTheme}
  />
</div>
```

### 9.3 Checkbox → Switch (where boolean toggle needed)

The existing Checkbox remains the correct component for multi-select / agreement patterns. Switch replaces Checkbox **only** where the UX is an on/off toggle.

| # | File | Line | Current | Replaces | Type |
|---|---|---|---|---|---|
| 1 | `settings-page.tsx` | :224–228 | `<Checkbox>` | Cache Enabled toggle | Boolean setting |
| 2 | `skills-page.tsx` | :66–81 | `<Checkbox>` | Boolean skill parameter | Boolean param |

**Migration #1: Settings — Cache Enabled** (recommended Switch)

**Before** (`settings-page.tsx:223–232`):
```tsx
<div className="flex items-center gap-2">
  <Checkbox
    id="cache-enabled"
    checked={cacheEnabled}
    onCheckedChange={(v) => setCacheEnabled(v === true)}
  />
  <label htmlFor="cache-enabled" className="text-sm font-medium">
    Cache Enabled
  </label>
</div>
```

**After:**
```tsx
<div className="flex items-center gap-3">
  <Switch
    id="cache-enabled"
    checked={cacheEnabled}
    onCheckedChange={setCacheEnabled}
  />
  <label htmlFor="cache-enabled" className="text-sm font-medium">
    Cache Enabled
  </label>
</div>
```

**Migration #2: Skills — Boolean Parameter** (optional; keep Checkbox if in a multi-field form)

The skills dialog renders boolean parameters alongside other input types. In this mixed-form context, Checkbox may be more appropriate than Switch. Decision should be made at implementation time based on visual density.

---

## Appendix A: Accessibility Checklist

| Check | Input | Textarea | Checkbox | Select | SegmentedControl | Switch |
|---|---|---|---|---|---|---|
| Native semantics | `<input>` | `<textarea>` | Radix (role=checkbox) | Radix (composite) | role=radiogroup | Radix (role=switch) |
| Focus indicator | 2px ring ✅ | 2px ring ✅ | 2px ring ✅ | 2px ring ✅ | 2px ring ✅ | 2px ring ✅ |
| Error state | `aria-invalid` | `aria-invalid` | — | — | — | — |
| Disabled state | `disabled` attr | `disabled` attr | Radix handled | Radix handled | aria-disabled | Radix handled |
| Keyboard | Native | Native | Space toggle | Arrow keys, Enter | Arrow keys, Home/End | Space toggle |
| Label association | `id` + `<label htmlFor>` | Same | Same | Same | `aria-label` | Same |
| Screen reader | Value announced | Same | checked/unchecked | option announced | radio pattern | on/off |

## Appendix B: Token Cross-Reference

| CSS Custom Property | Tailwind Class | Used In |
|---|---|---|
| `--color-surface-base` | `bg-surface-base` | Input bg, Select trigger bg, SegmentedControl active pill, Switch track (off) |
| `--color-surface-raised` | `bg-surface-raised` | Switch track (off) |
| `--color-surface-sunken` | `bg-surface-sunken` | SegmentedControl container |
| `--color-foreground` | `text-foreground` | Input text, Select item text |
| `--color-muted-foreground` | `text-muted-foreground` | Placeholder, chevron, inactive segment |
| `--color-primary` | `bg-primary` / `text-primary` | Checkbox checked bg, Switch on bg, Select selected item text, SegmentedControl active text |
| `--color-border` | `border-border` | Input border, Select trigger border, Switch track border, Separator |
| `--color-ring` | `ring-ring` | Focus rings (all components) |
| `--color-accent` | `bg-accent` | Select item hover, SegmentedControl inactive hover |
| `--color-destructive` | `border-destructive` | Input/Textarea error border |

> ⚠️ **Token prerequisite:** `--color-surface-base`, `--color-surface-raised`, `--color-surface-sunken` are defined in `tokens.md` but must be added to `globals.css` `@theme` and `.dark` blocks before these components will render correctly.

### Required CSS Token Additions

Add to the `@theme` block (Light mode):

```css
--color-surface-base: oklch(0.985 0.011 72);
--color-surface-raised: oklch(0.976 0.012 75);
--color-surface-sunken: oklch(0.930 0.041 82);
```

Add to the `.dark` block:

```css
--color-surface-base: oklch(0.197 0.014 62);
--color-surface-raised: oklch(0.229 0.018 63);
--color-surface-sunken: oklch(0.152 0.012 65);
```

## Appendix C: Implementation Checklist

### Phase 1: Token Infrastructure
- [ ] Add `--color-surface-base`, `--color-surface-raised`, `--color-surface-sunken` to `globals.css`
- [ ] Add `--color-status-*-bg` tokens (from button/badge spec prerequisite)
- [ ] Update `@theme` radius: add `--radius-xs: 0.25rem` if missing

### Phase 2: Component Updates
- [ ] Update `input.tsx` with new heights, radii, icon slots, glass support
- [ ] Update `textarea.tsx` with new styling and auto-resize
- [ ] Update `checkbox.tsx` with new sizing (18×18), colors, and animation
- [ ] Create `select.tsx` (new file — full Radix Select wrapper)
- [ ] Create `segmented-control.tsx` (new file — custom implementation)
- [ ] Create `switch.tsx` (new file — Radix Switch wrapper)

### Phase 3: Migration (Native → Component)
- [ ] Replace `<select>` in `settings-page.tsx:58–66` (language) → `<Select>`
- [ ] Replace `<select>` in `settings-page.tsx:238–248` (log level) → `<Select>`
- [ ] Replace `<select>` in `query-page.tsx:76–86` (search mode) → `<Select>`
- [ ] Replace `<select>` in `skills-page.tsx:44–56` (enum params) → `<Select>`
- [ ] Replace `<input type="radio">` in `settings-page.tsx:38–51` (theme) → `<SegmentedControl>`
- [ ] Consider replacing `Checkbox` → `Switch` in `settings-page.tsx:224–228` (cache toggle)

### Phase 4: Visual QA
- [ ] Verify light + dark mode across all components
- [ ] Verify glass treatment on Input and SegmentedControl
- [ ] Verify keyboard navigation (Tab, Arrow keys, Space, Enter)
- [ ] Verify focus ring visibility on all components
- [ ] Verify error states on Input and Textarea
- [ ] Verify Select dropdown animation and positioning
- [ ] Verify SegmentedControl sliding indicator animation
- [ ] Verify Switch thumb slide animation
- [ ] Verify disabled states across all components
- [ ] Add `aria-label` to all icon-only and composite controls

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
