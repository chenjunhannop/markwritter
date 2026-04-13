# Feedback, Status & Utility Component Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion specs:** `components-button-badge.md` · `components-surface-overlay.md` · `components-form-inputs.md`
> **Implementation:** `web/src/components/ui/{avatar,scroll-area,skeleton,progress,alert-banner,empty-state}.tsx`

---

## Table of Contents

1. [Design Decisions](#1-design-decisions)
2. [Avatar — Restyled (Radix)](#2-avatar--restyled-radix)
3. [ScrollArea — Restyled (Radix)](#3-scrollarea--restyled-radix)
4. [Skeleton — Restyled](#4-skeleton--restyled)
5. [Progress — New](#5-progress--new)
6. [AlertBanner — New](#6-alertbanner--new)
7. [EmptyState — New](#7-emptystate--new)
8. [Figma Component Structure](#8-figma-component-structure)
9. [EmptyState Use-Case Mapping](#9-emptystate-use-case-mapping)
10. [Hardcoded Color Audit](#10-hardcoded-color-audit)
11. [Appendix A: Accessibility Checklist](#appendix-a-accessibility-checklist)
12. [Appendix B: Token Cross-Reference](#appendix-b-token-cross-reference)
13. [Appendix C: Implementation Checklist](#appendix-c-implementation-checklist)

---

## 1. Design Decisions

### 1.1 Responsibility Split

Four feedback components cover the full lifecycle of user-facing state:

| Component | Responsibility | When to Use |
|---|---|---|
| **Skeleton** | Pre-content loading placeholder | Data hasn't arrived yet; preserve layout rhythm |
| **Progress** | Active task metering (determinate or indeterminate) | Upload, sync, import, indexing, long-running AI tasks |
| **AlertBanner** | Inline recoverable system feedback | Connection lost, API error, save confirmation, unsaved changes warning |
| **EmptyState** | No-data / first-use guidance | No session selected, no search results, no skills, empty file tree |

**Overlap rule:** If data is arriving, use Skeleton. If a task is running with known %, use Progress. If the system needs to tell the user something, use AlertBanner. If there is nothing to show, use EmptyState.

### 1.2 Avatar Radius

Avatar uses `radius-full` (9999px) at all sizes — a deliberate circle-only treatment. No rounded-square avatar variant is needed for the current product (chat sessions, user identity, and entity icons all use circles).

### 1.3 ScrollArea Glass Thumb

The scrollbar thumb borrows from the glass material system. On standard surfaces, the thumb uses `bg-border` at rest and `bg-muted-foreground` on hover. When the ScrollArea sits on a glass-tier parent, the thumb shifts to a translucent white — `white/0.20` (light) or `white/0.10` (dark) — so it reads as part of the glass layer rather than an opaque intrusion.

### 1.4 Skeleton Treatment

Skeleton moves away from the generic `bg-primary/10` pulse. The new system uses `bg-muted` (light) / `bg-surface-raised` (dark) with the standard `animate-pulse` keyframe. Skeleton inherits the parent element's radius rather than imposing its own — this keeps loading skeletons faithful to the component they replace.

### 1.5 AlertBanner Glass Tier

AlertBanner uses `glass-ultra-thin` as its background tier. This keeps alerts lightweight and translucent, reading as a temporary overlay rather than a heavy blocking surface. The left accent stripe provides the status color signal at full opacity.

### 1.6 EmptyState Glass Background

The icon background circle in EmptyState uses `glass-ultra-thin` for subtle visual framing. The overall component has no glass treatment — it's a simple centered layout that fits into any parent surface.

### 1.7 Radius Decisions

| Component | Radius | Tailwind | Rationale |
|---|---|---|---|
| Avatar | full (9999px) | `rounded-full` | Identity circles |
| ScrollArea scrollbar thumb | full (9999px) | `rounded-full` | Pill-shaped thumb |
| Skeleton | inherits parent | (no override) | Faithful to replaced element |
| Progress track | full (9999px) | `rounded-full` | Pill-shaped meter |
| AlertBanner | 14px | `rounded-[14px]` | Matches `radius-md` extended |
| EmptyState | none | — | Pure layout, no surface |

---

## 2. Avatar — Restyled (Radix)

### 2.1 Anatomy

A Radix Avatar with three sub-components: `AvatarRoot`, `AvatarImage`, `AvatarFallback`. Supports an optional outline ring variant and a loading (skeleton) state.

### 2.2 Size Matrix

| Size | Dimension | Fallback Font | Fallback Weight | Ring (outline) |
|---|---|---|---|---|
| `sm` | 32px (h-8 w-8) | 12px (caption) | 500 | `ring-2 ring-offset-2` |
| `default` | 40px (h-10 w-10) | 14px (body-sm) | 500 | `ring-2 ring-offset-2` |
| `lg` | 56px (h-14 w-14) | 18px (h4) | 600 | `ring-2 ring-offset-2` |

### 2.3 Color Matrix

| Element | Light Mode | Dark Mode |
|---|---|---|
| Root background | `surface-base` #FFF9F2 | `surface-base` #1A140F |
| Image | `object-cover`, centered | Same |
| Fallback background | `primary` #E6A23C | `primary` #F0B04A |
| Fallback text | `primary-foreground` #2B2116 | `primary-foreground` #2B2116 |
| Outline ring | `ring` #E6A23C | `ring` #F0B04A |
| Ring offset | `ring-offset-background` #F7F1E8 | `ring-offset-background` #120E0A |
| Loading skeleton | `bg-muted` #F0E8DA | `bg-surface-raised` #231B14 |

### 2.4 States

| State | Visual |
|---|---|
| **Default** | Image or fallback initials, no ring |
| **Outline** | `ring-2 ring-primary ring-offset-2 ring-offset-background` |
| **Loading** | Skeleton pulse replaces entire avatar content |

### 2.5 Component Code

```tsx
// web/src/components/ui/avatar.tsx
import { Avatar as AvatarPrimitive } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

const avatarVariants = {
  size: {
    sm: "h-8 w-8 text-xs",
    default: "h-10 w-10 text-sm",
    lg: "h-14 w-14 text-lg font-semibold",
  },
};

interface AvatarProps
  extends React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Root> {
  size?: keyof typeof avatarVariants.size;
  outline?: boolean;
  loading?: boolean;
}

const Avatar = React.forwardRef<
  React.ComponentRef<typeof AvatarPrimitive.Root>,
  AvatarProps
>(({ className, size = "default", outline = false, loading = false, ...props }, ref) => (
  <AvatarPrimitive.Root
    ref={ref}
    className={cn(
      "relative flex shrink-0 overflow-hidden rounded-full",
      avatarVariants.size[size],
      outline && "ring-2 ring-primary ring-offset-2 ring-offset-background",
      loading && "animate-pulse bg-muted",
      className,
    )}
    {...props}
  >
    {!loading && props.children}
  </AvatarPrimitive.Root>
));
Avatar.displayName = AvatarPrimitive.Root.displayName;

const AvatarImage = React.forwardRef<
  React.ComponentRef<typeof AvatarPrimitive.Image>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Image>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Image
    ref={ref}
    className={cn("aspect-square h-full w-full object-cover", className)}
    {...props}
  />
));
AvatarImage.displayName = AvatarPrimitive.Image.displayName;

const AvatarFallback = React.forwardRef<
  React.ComponentRef<typeof AvatarPrimitive.Fallback>,
  React.ComponentPropsWithoutRef<typeof AvatarPrimitive.Fallback>
>(({ className, ...props }, ref) => (
  <AvatarPrimitive.Fallback
    ref={ref}
    className={cn(
      "flex h-full w-full items-center justify-center rounded-full",
      "bg-primary text-primary-foreground font-medium",
      className,
    )}
    {...props}
  />
));
AvatarFallback.displayName = AvatarPrimitive.Fallback.displayName;

export { Avatar, AvatarImage, AvatarFallback };
```

---

## 3. ScrollArea — Restyled (Radix)

### 3.1 Anatomy

Radix ScrollArea with Viewport, Scrollbar (vertical/horizontal), Thumb, and Corner.

### 3.2 Scrollbar Specification

| Property | Value |
|---|---|
| Width (vertical) | 6px |
| Height (horizontal) | 6px |
| Position | Right edge (vertical), bottom edge (horizontal) |
| Track | Transparent, no visible background |
| Thumb rest | `bg-border` with `rounded-full` |
| Thumb hover | `bg-muted-foreground` |
| Corner | `bg-border` (matches thumb) |
| Transition | `transition-colors duration-200` |

### 3.3 Glass Thumb Mode

When a ScrollArea is nested inside a glass-tier surface, pass the `glass` prop to switch the thumb to translucent white:

| Mode | Thumb Rest | Thumb Hover |
|---|---|---|
| Standard (default) | `bg-border` | `bg-muted-foreground` |
| Glass (light) | `bg-white/20` | `bg-white/30` |
| Glass (dark) | `bg-white/10` | `bg-white/15` |

### 3.4 Component Code

```tsx
// web/src/components/ui/scroll-area.tsx
import { ScrollArea as ScrollAreaPrimitive } from "radix-ui";
import * as React from "react";
import { cn } from "@/lib/utils";

interface ScrollAreaProps
  extends React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.Root> {
  glass?: boolean;
}

const ScrollArea = React.forwardRef<
  React.ComponentRef<typeof ScrollAreaPrimitive.Root>,
  ScrollAreaProps
>(({ className, children, glass = false, ...props }, ref) => (
  <ScrollAreaPrimitive.Root
    ref={ref}
    className={cn("relative overflow-hidden", className)}
    {...props}
  >
    <ScrollAreaPrimitive.Viewport className="h-full w-full rounded-[inherit]">
      {children}
    </ScrollAreaPrimitive.Viewport>
    <ScrollBar glass={glass} />
    <ScrollAreaPrimitive.Corner />
  </ScrollAreaPrimitive.Root>
));
ScrollArea.displayName = ScrollAreaPrimitive.Root.displayName;

interface ScrollBarProps
  extends React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.ScrollAreaScrollbar> {
  glass?: boolean;
}

const ScrollBar = React.forwardRef<
  React.ComponentRef<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>,
  ScrollBarProps
>(({ className, orientation = "vertical", glass = false, ...props }, ref) => (
  <ScrollAreaPrimitive.ScrollAreaScrollbar
    ref={ref}
    orientation={orientation}
    className={cn(
      "flex touch-none select-none transition-colors duration-200",
      orientation === "vertical" &&
        "h-full w-1.5 border-l border-l-transparent p-[1px]",
      orientation === "horizontal" &&
        "h-1.5 flex-col border-t border-t-transparent p-[1px]",
      className,
    )}
    {...props}
  >
    <ScrollAreaPrimitive.ScrollAreaThumb
      className={cn(
        "relative flex-1 rounded-full",
        glass
          ? "bg-white/20 hover:bg-white/30 dark:bg-white/10 dark:hover:bg-white/15"
          : "bg-border hover:bg-muted-foreground",
      )}
    />
  </ScrollAreaPrimitive.ScrollAreaScrollbar>
));
ScrollBar.displayName = ScrollAreaPrimitive.ScrollAreaScrollbar.displayName;

export { ScrollArea, ScrollBar };
```

---

## 4. Skeleton — Restyled

### 4.1 Animation

**Keyframe:** `animate-pulse` — opacity oscillates between 40% and 100% over 2 seconds.

```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
```

### 4.2 Background

| Mode | Background | Token |
|---|---|---|
| Light | `#F0E8DA` | `muted` |
| Dark | `#231B14` | `surface-raised` |

### 4.3 Variants

| Variant | Dimensions | Radius | Usage |
|---|---|---|---|
| `text` | h-4 (16px) w-full | `rounded-sm` (6px) | Text line placeholders |
| `circle` | Matches parent size | `rounded-full` | Avatar loading, icon placeholders |
| `card` | h-32 (128px) w-full | `rounded-md` (8px) | Card content placeholders |
| (default) | Custom (via className) | Inherits parent | General purpose |

### 4.4 No Glass Treatment

Skeleton never receives glass material. It is a flat muted surface simulating absent content.

### 4.5 Component Code

```tsx
// web/src/components/ui/skeleton.tsx
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const skeletonVariants = cva(
  "animate-pulse bg-muted dark:bg-surface-raised",
  {
    variants: {
      variant: {
        default: "rounded-[inherit]",
        text: "h-4 w-full rounded-sm",
        circle: "rounded-full",
        card: "h-32 rounded-md",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

interface SkeletonProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof skeletonVariants> {}

function Skeleton({ className, variant, ...props }: SkeletonProps) {
  return (
    <div
      className={cn(skeletonVariants({ variant }), className)}
      {...props}
    />
  );
}

export { Skeleton, skeletonVariants };
```

---

## 5. Progress — New

### 5.1 Linear Progress Bar

#### Track

| Property | Value |
|---|---|
| Height | 8px (h-2) |
| Radius | `rounded-full` (9999px) |
| Background | `bg-border` |
| Overflow | `hidden` |

#### Fill

| Property | Value |
|---|---|
| Height | 100% |
| Radius | `rounded-full` |
| Transition | `transition-[width] duration-300 ease-out` |
| Min width (determinate) | 0% |
| Max width (determinate) | 100% |

### 5.2 Variant Color Matrix

| Variant | Fill Color (Light) | Fill Color (Dark) | Use Case |
|---|---|---|---|
| `default` | `primary` #E6A23C → `primary-hover` #D89432 (gradient) | `primary` #F0B04A → `primary-hover` #F4C97B | Active task, upload, sync |
| `success` | `status-success` #496D3E | `status-success` #86B67A | Completed, verified |
| `warning` | `status-warning` #8A5A12 | `status-warning` #D2BF8B | Slow, nearly full storage |
| `destructive` | `destructive` #C0392B | `destructive` #E74C3C | Failed, error recovery |

### 5.3 Indeterminate Mode

When no `value` is provided, the fill enters an indeterminate shimmer animation:

```css
@keyframes progress-indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}
```

- Fill width: 33% of track
- Animation: `progress-indeterminate 2s ease-in-out infinite`
- Same variant colors apply

### 5.4 Circular Variant (Optional)

SVG-based circular progress. Uses `stroke-dasharray` and `stroke-dashoffset` for animation.

| Property | Value |
|---|---|
| SVG size | 48px (default), 32px (sm), 64px (lg) |
| Stroke width | 4px |
| Track stroke | `stroke-border` |
| Fill stroke | `stroke-primary` (or variant color) |
| Linecap | `round` |
| Transition | `stroke-dashoffset 300ms ease-out` |

### 5.5 Component Code

```tsx
// web/src/components/ui/progress.tsx
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "@/lib/utils";

const progressVariants = cva("", {
  variants: {
    variant: {
      default: "[&>.progress-fill]:bg-gradient-to-r [&>.progress-fill]:from-primary [&>.progress-fill]:to-primary-hover",
      success: "[&>.progress-fill]:bg-status-success",
      warning: "[&>.progress-fill]:bg-status-warning",
      destructive: "[&>.progress-fill]:bg-destructive",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

interface ProgressProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof progressVariants> {
  value?: number; // 0–100, undefined = indeterminate
  max?: number;
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value, max = 100, variant, ...props }, ref) => {
    const percentage = value != null ? Math.min(100, Math.max(0, (value / max) * 100)) : undefined;
    const isIndeterminate = percentage == null;

    return (
      <div
        ref={ref}
        role="progressbar"
        aria-valuenow={percentage}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={props["aria-label"] ?? "Progress"}
        className={cn(
          "relative h-2 w-full overflow-hidden rounded-full bg-border",
          progressVariants({ variant }),
          className,
        )}
        {...props}
      >
        <div
          className={cn(
            "progress-fill h-full rounded-full",
            "transition-[width] duration-300 ease-out",
            isIndeterminate
              ? "w-1/3 animate-[progress-indeterminate_2s_ease-in-out_infinite]"
              : undefined,
          )}
          style={!isIndeterminate ? { width: `${percentage}%` } : undefined}
        />
      </div>
    );
  },
);
Progress.displayName = "Progress";

export { Progress, progressVariants };
```

### 5.6 Required CSS Keyframe

Add to `globals.css`:

```css
@keyframes progress-indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(300%); }
}
```

---

## 6. AlertBanner — New

### 6.1 Anatomy

Horizontal flex row: **Left Accent Stripe** → **Icon** → **Content (Title + Message)** → **Action Button** (optional) → **Dismiss Button** (optional).

```
┌─┬──────────────────────────────────────────────────────┐
│▌│  🔔  Title                    [Action]         [✕]   │
│▌│      Message description                              │
└─┴──────────────────────────────────────────────────────┘
```

### 6.2 Layout

| Property | Value |
|---|---|
| Display | `flex`, `items-center` |
| Gap | 12px (`gap-3`) |
| Padding | 12px 16px (`p-3 px-4`) |
| Radius | 14px (`rounded-[14px]`) |
| Background | Glass ultra-thin |
| Min-height | 44px |

### 6.3 Left Accent Stripe

| Property | Value |
|---|---|
| Width | 3px |
| Radius | `rounded-full` |
| Position | Absolute left, inset-y 8px |

### 6.4 Variant Color Matrix — Light Mode

| Variant | Stripe / Icon Color | Title Color | Message Color | Background Tint | Icon |
|---|---|---|---|---|---|
| `info` | `status-info` #586B7A | `foreground` #2B2116 | `muted-foreground` #78624B | `status-info-bg` #E8EDF2 | `Info` |
| `success` | `status-success` #496D3E | `foreground` #2B2116 | `muted-foreground` #78624B | `status-success-bg` #EAF2E6 | `CheckCircle2` |
| `warning` | `status-warning` #8A5A12 | `foreground` #2B2116 | `muted-foreground` #78624B | `status-warning-bg` #FBF0D9 | `AlertTriangle` |
| `error` | `status-error` #A2432B | `foreground` #2B2116 | `muted-foreground` #78624B | `status-error-bg` #F8E6E0 | `AlertCircle` |

### 6.5 Variant Color Matrix — Dark Mode

| Variant | Stripe / Icon Color | Title Color | Message Color | Background Tint | Icon |
|---|---|---|---|---|---|
| `info` | `status-info` #9DB6C8 | `foreground` #F8F1E7 | `muted-foreground` #C7B69F | `status-info-bg` #161C24 | `Info` |
| `success` | `status-success` #86B67A | `foreground` #F8F1E7 | `muted-foreground` #C7B69F | `status-success-bg` #1A2616 | `CheckCircle2` |
| `warning` | `status-warning` #D2BF8B | `foreground` #F8F1E7 | `muted-foreground` #C7B69F | `status-warning-bg` #29201A | `AlertTriangle` |
| `error` | `status-error` #D88E74 | `foreground` #F8F1E7 | `muted-foreground` #C7B69F | `status-error-bg` #261612 | `AlertCircle` |

### 6.6 Typography

| Element | Size | Weight | Color Token |
|---|---|---|---|
| Icon | 16px (w-4 h-4) | — | variant status color |
| Title | 13px (`text-[13px]`) | 500 | `foreground` |
| Message | 14px (`text-sm`) | 400 | `muted-foreground` |
| Action button | sm ghost | — | — |
| Dismiss button | icon-sm ghost | — | `muted-foreground` |

### 6.7 Dismissible Behavior

- When `dismissible` is true, shows X button on the right
- On click: 200ms `slide-out` animation (translateY to -100% + opacity 0), then remove from DOM
- Parent component manages visibility state

```css
@keyframes alert-slide-out {
  from { opacity: 1; transform: translateY(0); max-height: 80px; }
  to { opacity: 0; transform: translateY(-8px); max-height: 0; padding: 0; margin: 0; }
}
```

### 6.8 Stacking

Multiple alerts stack vertically with `gap-2` (8px). Recommended wrapper:

```tsx
<div className="flex flex-col gap-2">
  {alerts.map((alert) => <AlertBanner key={alert.id} {...alert} />)}
</div>
```

### 6.9 Component Code

```tsx
// web/src/components/ui/alert-banner.tsx
import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Info,
  X,
} from "lucide-react";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const alertVariants = cva("", {
  variants: {
    variant: {
      info: {
        stripe: "bg-status-info",
        icon: "text-status-info",
        bg: "bg-status-info-bg",
      },
      success: {
        stripe: "bg-status-success",
        icon: "text-status-success",
        bg: "bg-status-success-bg",
      },
      warning: {
        stripe: "bg-status-warning",
        icon: "text-status-warning",
        bg: "bg-status-warning-bg",
      },
      error: {
        stripe: "bg-status-error",
        icon: "text-status-error",
        bg: "bg-status-error-bg",
      },
    },
  },
  defaultVariants: {
    variant: "info",
  },
});

const ICON_MAP = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  error: AlertCircle,
};

const VARIANT_CLASSES = {
  info: {
    stripe: "bg-status-info",
    icon: "text-status-info",
    bg: "bg-status-info-bg",
  },
  success: {
    stripe: "bg-status-success",
    icon: "text-status-success",
    bg: "bg-status-success-bg",
  },
  warning: {
    stripe: "bg-status-warning",
    icon: "text-status-warning",
    bg: "bg-status-warning-bg",
  },
  error: {
    stripe: "bg-status-error",
    icon: "text-status-error",
    bg: "bg-status-error-bg",
  },
} as const;

interface AlertBannerProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "info" | "success" | "warning" | "error";
  title: string;
  message?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  dismissible?: boolean;
  onDismiss?: () => void;
}

function AlertBanner({
  variant = "info",
  title,
  message,
  icon,
  action,
  dismissible = false,
  onDismiss,
  className,
  ...props
}: AlertBannerProps) {
  const v = VARIANT_CLASSES[variant];
  const IconComponent = ICON_MAP[variant];

  return (
    <div
      role="alert"
      className={cn(
        "relative flex items-center gap-3 rounded-[14px] p-3 px-4",
        "backdrop-blur-[8px] saturate-[120%]",
        v.bg,
        "border border-border/10 dark:border-border/10",
        className,
      )}
      {...props}
    >
      {/* Left accent stripe */}
      <div
        className={cn(
          "absolute left-2 top-2 bottom-2 w-[3px] rounded-full",
          v.stripe,
        )}
        aria-hidden="true"
      />

      {/* Icon */}
      <div className={cn("shrink-0 ml-2", v.icon)}>
        {icon ?? <IconComponent className="h-4 w-4" />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="text-[13px] font-medium leading-tight text-foreground">
          {title}
        </p>
        {message && (
          <p className="mt-0.5 text-sm text-muted-foreground leading-normal">
            {message}
          </p>
        )}
      </div>

      {/* Optional action */}
      {action && <div className="shrink-0">{action}</div>}

      {/* Dismiss */}
      {dismissible && (
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={onDismiss}
          aria-label="Dismiss"
          className="shrink-0"
        >
          <X />
        </Button>
      )}
    </div>
  );
}

export { AlertBanner };
```

### 6.10 Use Cases

| Use Case | Variant | Title | Message | Action |
|---|---|---|---|---|
| API connection lost | `error` | "Connection lost" | "Check your network and retry." | "Retry" |
| Save confirmation | `success` | "Changes saved" | — | — |
| Unsaved changes warning | `warning` | "Unsaved changes" | "You have unsaved edits that may be lost." | "Save now" |
| API rate limit | `warning` | "Rate limit reached" | "Please wait before making more requests." | — |
| Feature info | `info` | "Keyboard shortcuts" | "Press Ctrl+S to save, Ctrl+K for command palette." | — |

---

## 7. EmptyState — New

### 7.1 Anatomy

Vertical centered layout: **Icon** → **Title** → **Description** → **Optional Action Button**.

```
         ┌──────┐
         │ Icon │  (40px, muted-foreground/50)
         └──────┘

        Title
   (18px/600, foreground)

   Description text
 (15px/400, muted-foreground)

       [ Action ]
```

### 7.2 Layout

| Property | Value |
|---|---|
| Display | `flex`, `flex-col`, `items-center`, `justify-center` |
| Gap | 12px (`gap-3`) |
| Text align | `text-center` |
| Vertical padding | 64px (`py-16`) |
| Max-width (description) | 320px (`max-w-xs`) |

### 7.3 Icon Specification

| Property | Value |
|---|---|
| Size | 40px (w-10 h-10) |
| Color | `text-muted-foreground/50` |
| Background circle | Optional, 56px (w-14 h-14), `glass-ultra-thin`, `rounded-full` |

### 7.4 Typography

| Element | Size | Weight | Color |
|---|---|---|---|
| Title | 18px (`text-lg`) | 600 (`font-semibold`) | `foreground` |
| Description | 15px (`text-[15px]`) | 400 | `muted-foreground` |

### 7.5 Component Code

```tsx
// web/src/components/ui/empty-state.tsx
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import type { LucideIcon } from "lucide-react";

interface EmptyStateAction {
  label: string;
  onClick: () => void;
  variant?: "default" | "outline";
}

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  action?: EmptyStateAction;
  className?: string;
  /** Show the glass background circle behind the icon */
  iconBackground?: boolean;
}

function EmptyState({
  icon: Icon,
  title,
  description,
  action,
  className,
  iconBackground = false,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 py-16 text-center",
        className,
      )}
    >
      {/* Icon with optional glass background */}
      <div
        className={cn(
          iconBackground &&
            "flex h-14 w-14 items-center justify-center rounded-full",
          iconBackground &&
            "backdrop-blur-[8px] saturate-[120%] bg-white/45 dark:bg-[rgba(26,20,15,0.40)]",
          iconBackground && "border border-border/10",
        )}
      >
        <Icon className="h-10 w-10 text-muted-foreground/50" />
      </div>

      {/* Title */}
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>

      {/* Description */}
      {description && (
        <p className="max-w-xs text-[15px] text-muted-foreground">
          {description}
        </p>
      )}

      {/* Action */}
      {action && (
        <Button
          variant={action.variant ?? "default"}
          size="sm"
          onClick={action.onClick}
          className="mt-1"
        >
          {action.label}
        </Button>
      )}
    </div>
  );
}

export { EmptyState };
```

---

## 8. Figma Component Structure

### 8.1 Avatar

**Component name:** `Avatar`

**Auto Layout:**
- Direction: Horizontal (for content centering)
- Primary axis: Center
- Counter axis: Center
- Size: Fixed square (32 / 40 / 56)

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Size` | Variant | `sm`, `default`, `lg` | `default` |
| `State` | Variant | `default`, `outline`, `loading` | `default` |
| `Image` | Instance Swap | — | `None` |
| `Initials` | Text | — | `AB` |

**Layer Structure:**
```
📦 Avatar (Component Set)
├── 🔀 Variant property: Size (3 values)
├── 🔀 Variant property: State (3 values)
├── 📝 Text property: Initials
├── 🔄 Instance swap property: Image
│
└── Avatar (Frame, Auto Layout, rounded-full)
    ├── Image (Frame, aspect-square, hidden when State=loading)
    │   └── [Image instance or placeholder]
    ├── Fallback (Frame, bg-primary, centered)
    │   └── Initials (Text, primary-foreground, centered)
    └── LoadingOverlay (Frame, bg-muted, animate-pulse, visible when State=loading)
```

### 8.2 ScrollArea

**Component name:** `ScrollArea`

ScrollArea is a structural component that wraps content. The visible sub-component is the scrollbar.

**ScrollBar Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Orientation` | Variant | `vertical`, `horizontal` | `vertical` |
| `Glass` | Boolean | `true`, `false` | `false` |
| `State` | Variant | `rest`, `hover` | `rest` |

**Layer Structure:**
```
📦 ScrollArea (Component)
└── ScrollArea (Frame, overflow hidden)
    ├── Viewport (Frame, fill container)
    ├── Scrollbar (Frame, w-1.5, right-aligned)
    │   └── Thumb (Frame, rounded-full, bg-border)
    └── Corner (Frame, bg-border)
```

### 8.3 Skeleton

**Component name:** `Skeleton`

**Auto Layout:** Fill container (width), fixed height per variant.

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Variant` | Variant | `default`, `text`, `circle`, `card` | `default` |

**Layer Structure:**
```
📦 Skeleton (Component Set)
├── 🔀 Variant property: Variant (4 values)
│
└── Skeleton (Rectangle, bg-muted, animate-pulse)
```

### 8.4 Progress

**Component name:** `Progress`

**Auto Layout:** Fill width, fixed height 8px.

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Variant` | Variant | `default`, `success`, `warning`, `destructive` | `default` |
| `Mode` | Variant | `determinate`, `indeterminate` | `determinate` |
| `Value` | Number | 0–100 | 60 |

**Layer Structure:**
```
📦 Progress (Component Set)
├── 🔀 Variant property: Variant (4 values)
├── 🔀 Variant property: Mode (2 values)
├── 🔢 Number property: Value
│
└── Progress (Frame, h-8px, rounded-full, bg-border, overflow hidden)
    └── Fill (Frame, h-full, rounded-full, bg-primary)
```

### 8.5 AlertBanner

**Component name:** `AlertBanner`

**Auto Layout:**
- Direction: Horizontal
- Primary axis: Center (align)
- Counter axis: Center
- Gap: 12px
- Padding: 12px 16px

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Variant` | Variant | `info`, `success`, `warning`, `error` | `info` |
| `Dismissible` | Boolean | `true`, `false` | `false` |
| `Has Action` | Boolean | `true`, `false` | `false` |
| `Title` | Text | — | `Alert title` |
| `Message` | Text | — | `Alert description` |

**Layer Structure:**
```
📦 AlertBanner (Component Set)
├── 🔀 Variant property: Variant (4 values)
├── 🔘 Boolean property: Dismissible
├── 🔘 Boolean property: Has Action
├── 📝 Text property: Title
├── 📝 Text property: Message
│
└── AlertBanner (Frame, Auto Layout, rounded-[14px], glass-ultra-thin)
    ├── Stripe (Rectangle, w-3px, absolute, rounded-full, variant color)
    ├── Icon (Frame, 16×16, variant color)
    │   └── [Icon instance: Info / CheckCircle2 / AlertTriangle / AlertCircle]
    ├── Content (Frame, Auto Layout vertical, flex-1)
    │   ├── Title (Text, 13px/500, foreground)
    │   └── Message (Text, 14px/400, muted-foreground)
    ├── ActionSlot (Frame, hidden when Has Action=false)
    │   └── Button (Instance, ghost, sm, "Action")
    └── Dismiss (Frame, hidden when Dismissible=false)
        └── Button (Instance, ghost, icon-sm, X)
```

### 8.6 EmptyState

**Component name:** `EmptyState`

**Auto Layout:**
- Direction: Vertical
- Primary axis: Center (align)
- Counter axis: Center (justify)
- Gap: 12px
- Padding: 64px vertical

**Component Properties:**

| Property | Type | Values | Default |
|---|---|---|---|
| `Icon` | Instance Swap | Lucide icon set | `MessageSquarePlus` |
| `Has Background` | Boolean | `true`, `false` | `true` |
| `Has Description` | Boolean | `true`, `false` | `true` |
| `Has Action` | Boolean | `true`, `false` | `true` |
| `Title` | Text | — | `No data` |
| `Description` | Text | — | `No items to display.` |
| `Action Label` | Text | — | `Get started` |

**Layer Structure:**
```
📦 EmptyState (Component Set)
├── 🔄 Instance swap property: Icon
├── 🔘 Boolean property: Has Background
├── 🔘 Boolean property: Has Description
├── 🔘 Boolean property: Has Action
├── 📝 Text property: Title
├── 📝 Text property: Description
├── 📝 Text property: Action Label
│
└── EmptyState (Frame, Auto Layout vertical, py-16, center)
    ├── IconContainer (Frame, 56×56, rounded-full, glass-ultra-thin, optional)
    │   └── Icon (Instance, 40×40, muted-foreground/50)
    ├── Title (Text, 18px/600, foreground)
    ├── Description (Text, 15px/400, muted-foreground, max-w-320px)
    └── Action (Instance, Button default/outline sm)
```

---

## 9. EmptyState Use-Case Mapping

| # | Feature | Context | Icon | Title | Description | Action Label | Action Variant |
|---|---|---|---|---|---|---|---|
| 1 | Chat | No session selected | `MessageSquarePlus` | "No conversation selected" | "Create a new chat to get started" | "New Chat" | `default` |
| 2 | Chat | No messages in session | `MessageSquarePlus` | "Start a conversation" | "Ask questions about your notes, get summaries, or brainstorm ideas." | — | — |
| 3 | Query | No search performed | `Search` | "Search your notes" | "Use keywords or natural language to find relevant content." | — | — |
| 4 | Query | No results found | `FileText` | "No results found" | "Try different keywords or switch search mode." | — | — |
| 5 | Skills | No skills available | `Boxes` | "No skills available" | — | — | — |
| 6 | File tree | Empty directory | `FolderOpen` | "No files found" | "Add markdown files to your vault to get started." | — | — |
| 7 | Explore | No graph data | `Share2` | "No connections yet" | "Add notes, tags, and links to build your knowledge graph." | — | — |
| 8 | Settings | Load error | `AlertCircle` | "Failed to load settings" | "Check your connection and try again." | "Retry" | `outline` |

---

## 10. Hardcoded Color Audit

### 10.1 Full Audit Table

| # | File:Line | Current Code | Current Color | Replacement Token | Replacement Class |
|---|---|---|---|---|---|
| 1 | `settings-page.tsx:111` | `bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300` | Green badge | `Badge variant="success"` | `bg-status-success-bg text-status-success` |
| 2 | `settings-page.tsx:112` | `bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300` | Red badge | `Badge variant="warning"` | `bg-status-warning-bg text-status-warning` |
| 3 | `settings-page.tsx:174` | `bg-green-500` | Green dot | `status-success` | `bg-status-success` |
| 4 | `settings-page.tsx:174` | `bg-red-500` | Red dot | `status-error` | `bg-status-error` |
| 5 | `explore-page.tsx:28` | `person: "#3b82f6"` | Blue | `chart-node-person` (new) | `#6B8DB5` — warm mineral blue |
| 6 | `explore-page.tsx:29` | `topic: "#22c55e"` | Green | `chart-node-topic` (new) | `#6D9B5E` — sage green |
| 7 | `explore-page.tsx:30` | `concept: "#a855f7"` | Purple | `chart-node-concept` (new) | `#9B7B8E` — muted mauve |
| 8 | `explore-page.tsx:31` | `note: "#f59e0b"` | Amber | `chart-1` (existing) | `#E6A23C` — system amber |
| 9 | `explore-page.tsx:208` | `"#6b7280"` (fallback) | Gray | `muted-foreground` | `var(--color-muted-foreground)` |
| 10 | `explore-page.tsx:210` | `rgba(0, 0, 0, 0.1)` | Mask | `border/10` | `rgba(220,199,167,0.1)` light |
| 11 | `diff-preview.tsx:24` | `bg-green-200/60 dark:bg-green-900/40` | Insert highlight | `status-success-bg` with alpha | `bg-status-success/15` |
| 12 | `diff-preview.tsx:31` | `bg-red-200/60 dark:bg-red-900/40` | Delete highlight | `status-error-bg` with alpha | `bg-status-error/15` |
| 13 | `diff-preview.tsx:97` | `border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-950` | Accepted border | `status-success` border | `border-status-success/40 bg-status-success-bg` |
| 14 | `diff-preview.tsx:98` | `text-green-600 dark:text-green-400` | Check icon | `status-success` | `text-status-success` |
| 15 | `diff-preview.tsx:99` | `text-green-700 dark:text-green-300` | Accepted text | `status-success` | `text-status-success` |
| 16 | `note-editor.tsx:159` | `text-green-600 dark:text-green-400` | Saved status | `status-success` | `text-status-success` |
| 17 | `note-editor.tsx:163` | `text-orange-500` | Unsaved status | `status-warning` | `text-status-warning` |

### 10.2 Recommended New Tokens for Explore NODE_COLORS

The explore graph uses node-type colors that don't fit the existing `chart-*` tokens. Introduce entity-specific semantic tokens:

| Token | Figma Variable | Light Hex | Dark Hex | Usage |
|---|---|---|---|---|
| `chart-node-person` | `color/chart-node-person` | `#6B8DB5` | `#8BAEC8` | Person nodes — warm mineral blue |
| `chart-node-topic` | `color/chart-node-topic` | `#6D9B5E` | `#8FBC7F` | Topic nodes — sage green |
| `chart-node-concept` | `color/chart-node-concept` | `#9B7B8E` | `#BC9CB0` | Concept nodes — muted mauve |
| `chart-node-note` | `color/chart-node-note` | `#E6A23C` | `#F0B04A` | Note nodes — amber (= chart-1) |

### 10.3 DiffPreview Migration Code

**Before — `diff-preview.tsx:24`:**
```tsx
<span className="bg-green-200/60 dark:bg-green-900/40 rounded-sm px-0.5">
```

**After:**
```tsx
<span className="bg-status-success/15 rounded-sm px-0.5">
```

**Before — `diff-preview.tsx:31`:**
```tsx
<span className="bg-red-200/60 dark:bg-red-900/40 line-through rounded-sm px-0.5">
```

**After:**
```tsx
<span className="bg-status-error/15 line-through rounded-sm px-0.5">
```

**Before — `diff-preview.tsx:97`:**
```tsx
<div className="flex items-center gap-2 rounded-md border border-green-300 bg-green-50 px-3 py-2 dark:border-green-800 dark:bg-green-950">
  <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
  <span className="text-sm text-green-700 dark:text-green-300">
```

**After:**
```tsx
<div className="flex items-center gap-2 rounded-md border border-status-success/40 bg-status-success-bg px-3 py-2">
  <Check className="h-4 w-4 text-status-success" />
  <span className="text-sm text-status-success">
```

### 10.4 NoteEditor Migration Code

**Before — `note-editor.tsx:157-164`:**
```tsx
className={
  saveStatus === "saved"
    ? "text-xs text-green-600 dark:text-green-400"
    : saveStatus === "saving"
      ? "text-xs text-muted-foreground"
      : saveStatus === "dirty"
        ? "text-xs text-orange-500"
        : "text-xs text-muted-foreground"
}
```

**After:**
```tsx
className={cn(
  "text-xs",
  saveStatus === "saved" && "text-status-success",
  saveStatus === "saving" && "text-muted-foreground",
  saveStatus === "dirty" && "text-status-warning",
  saveStatus === "idle" && "text-muted-foreground",
)}
```

### 10.5 Settings Migration Code

**Before — `settings-page.tsx:108-116`:**
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

**Before — `settings-page.tsx:172-175`:**
```tsx
<div
  className={`h-2.5 w-2.5 rounded-full ${
    health?.vault_connected ? "bg-green-500" : "bg-red-500"
  }`}
/>
```

**After:**
```tsx
<div
  className={cn(
    "h-2.5 w-2.5 rounded-full",
    health?.vault_connected ? "bg-status-success" : "bg-status-error",
  )}
/>
```

---

## Appendix A: Accessibility Checklist

| Check | Avatar | ScrollArea | Skeleton | Progress | AlertBanner | EmptyState |
|---|---|---|---|---|---|---|
| Color contrast | Initials: #2B2116 on #E6A23C = 7.21:1 ✅ AAA | N/A | N/A | Track: border on bg ✅ | Status colors pass AA on tint bg ✅ | Muted text: 5.51:1 ✅ AA |
| Focus indicator | Ring on outline variant ✅ | N/A (chrome) | N/A | N/A | `role="alert"` ✅ | Action button focusable ✅ |
| ARIA | `alt` on image, fallback as accessible name | ScrollArea handles internally | `aria-hidden="true"` | `role="progressbar"`, `aria-valuenow` ✅ | `role="alert"` ✅ | Title as heading ✅ |
| Motion | Pulse respects `prefers-reduced-motion` | N/A | Pulse respects `prefers-reduced-motion` | Shimmer respects `prefers-reduced-motion` | Slide-out respects `prefers-reduced-motion` | N/A |
| Keyboard | N/A | Scrollable via keyboard | N/A | N/A | Dismiss button focusable ✅ | Action button focusable ✅ |
| Screen reader | Fallback text as label | Native scroll | Hidden from SR | Value announced | Alert announced | Title + description announced |

---

## Appendix B: Token Cross-Reference

| CSS Custom Property | Tailwind Class | Used In |
|---|---|---|
| `--color-primary` | `bg-primary` | Avatar fallback bg, Progress fill gradient start |
| `--color-primary-foreground` | `text-primary-foreground` | Avatar fallback text |
| `--color-primary-hover` | `bg-primary-hover` | Progress fill gradient end |
| `--color-muted` | `bg-muted` | Skeleton background (light) |
| `--color-surface-raised` | `bg-surface-raised` | Skeleton background (dark) |
| `--color-border` | `bg-border` | ScrollArea thumb, Progress track |
| `--color-muted-foreground` | `bg-muted-foreground`, `text-muted-foreground` | ScrollArea thumb hover, EmptyState icon/description |
| `--color-ring` | `ring-ring` | Avatar outline ring |
| `--color-background` | `ring-offset-background` | Avatar ring offset |
| `--color-status-success` | `bg-status-success`, `text-status-success` | Progress variant, AlertBanner success, DiffPreview accepted, NoteEditor saved |
| `--color-status-success-bg` | `bg-status-success-bg` | AlertBanner success bg, Badge success bg |
| `--color-status-warning` | `text-status-warning` | Progress variant, NoteEditor dirty, Badge warning |
| `--color-status-warning-bg` | `bg-status-warning-bg` | AlertBanner warning bg, Badge warning bg |
| `--color-status-error` | `bg-status-error`, `text-status-error` | Progress variant, AlertBanner error, Settings dot |
| `--color-status-error-bg` | `bg-status-error-bg` | AlertBanner error bg, Badge error bg |
| `--color-status-info` | `text-status-info` | AlertBanner info icon |
| `--color-status-info-bg` | `bg-status-info-bg` | AlertBanner info bg |
| `--color-destructive` | `bg-destructive` | Progress destructive variant |
| `--color-foreground` | `text-foreground` | AlertBanner title, EmptyState title |
| `--color-chart-1` | — | Explore note node color |
| `--color-chart-node-person` | — | Explore person node (new token) |
| `--color-chart-node-topic` | — | Explore topic node (new token) |
| `--color-chart-node-concept` | — | Explore concept node (new token) |

---

## Appendix C: Implementation Checklist

### Phase 1: Token Foundation
- [ ] Add `--color-status-*-bg` tokens to `globals.css` `@theme` and `.dark` blocks (prerequisite from `components-button-badge.md`)
- [ ] Add `--color-chart-node-*` tokens to `globals.css` for explore graph nodes
- [ ] Verify `--color-muted`, `--color-surface-raised`, `--color-primary-hover` are in `globals.css`

### Phase 2: Restyle Existing Components
- [ ] Update `avatar.tsx` — add `size`, `outline`, `loading` props; update fallback to use `bg-primary text-primary-foreground`
- [ ] Update `scroll-area.tsx` — narrow to 6px, add `glass` prop, update thumb classes
- [ ] Update `skeleton.tsx` — replace `bg-primary/10` with `bg-muted dark:bg-surface-raised`, add `variant` prop via CVA

### Phase 3: New Components
- [ ] Create `progress.tsx` — linear bar with 4 variants, determinate/indeterminate modes
- [ ] Create `alert-banner.tsx` — 4 variants, dismissible, glass-ultra-thin background
- [ ] Create `empty-state.tsx` — icon + title + description + optional action
- [ ] Add `@keyframes progress-indeterminate` to `globals.css`

### Phase 4: Hardcoded Color Migration
- [ ] Replace settings API key badge → `<Badge variant="success/warning">`
- [ ] Replace settings connection dot → `bg-status-success` / `bg-status-error`
- [ ] Replace explore NODE_COLORS → new `chart-node-*` tokens
- [ ] Replace DiffPreview insert/delete → `bg-status-success/15` / `bg-status-error/15`
- [ ] Replace DiffPreview accepted → `border-status-success/40 bg-status-success-bg`
- [ ] Replace NoteEditor save status → `text-status-success` / `text-status-warning`

### Phase 5: Feature Integration
- [ ] Replace ad-hoc empty states in `chat-area.tsx` (no session, no messages) with `<EmptyState>`
- [ ] Replace ad-hoc empty states in `query-page.tsx` (no search, no results) with `<EmptyState>`
- [ ] Replace ad-hoc empty state in `skills-page.tsx` (no skills) with `<EmptyState>`
- [ ] Replace ad-hoc empty state in `file-tree-panel.tsx` (no files) with `<EmptyState>`
- [ ] Add `<AlertBanner>` for API errors, connection status, save confirmations
- [ ] Add `<Progress>` for file import, sync, and long-running AI tasks
- [ ] Replace inline loading skeletons in `query-page.tsx` and `skills-page.tsx` with `<Skeleton variant="card">`

### Phase 6: QA
- [ ] Visual QA: light + dark mode for all 6 components across all variants
- [ ] Accessibility: verify contrast ratios, ARIA attributes, keyboard navigation
- [ ] `prefers-reduced-motion`: verify animations are disabled
- [ ] Mobile: verify ScrollArea touch behavior, EmptyState responsive padding

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
