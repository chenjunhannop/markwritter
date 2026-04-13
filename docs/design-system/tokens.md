# Liquid Crystal — Warm Amber

## Design System Token Reference

> **Single source of truth** for the Markwritter design system.
> Every surface is a translucent glass material layer atop a warm mesh background — premium, alive, warm.

| Field | Value |
|---|---|
| System name | Liquid Crystal — Warm Amber |
| Version | 1.0.0 |
| Last updated | 2026-04-11 |
| Tech stack | React 19 · Tailwind CSS v4 · Radix UI · Lucide Icons |
| Color space | OKLCH (primary) with hex fallbacks |

---

## Table of Contents

1. [Color Tokens](#1-color-tokens)
2. [Background Mesh Gradients](#2-background-mesh-gradients)
3. [Typography Scale](#3-typography-scale)
4. [Border Radius Tokens](#4-border-radius-tokens)
5. [Shadow System](#5-shadow-system)
6. [Glass Material Tiers](#6-glass-material-tiers)
7. [Spacing System](#7-spacing-system)
8. [Motion & Animation](#8-motion--animation)
9. [Z-Index Scale](#9-z-index-scale)
10. [Responsive Breakpoints](#10-responsive-breakpoints)

---

## 1. Color Tokens

### Design Principles

- **Warm-first neutrals:** All grays carry a warm parchment undertone (hue 67–82). No cool-blue slate.
- **Amber is the hero:** `primary` = amber. It is the single high-chroma accent. Everything else is restrained.
- **Accessible pairings:** `primary-foreground` stays **dark ink** (`#2B2116`) in both themes. Amber text on pale glass is banned — amber is for fills, focus rings, and selected states.
- **Semantic overrides:** Status colors (success, warning, error, info) are defined as new first-class tokens, not derived from the primary palette.

### 1.1 Light Mode — Foundation Palette

| Token | Figma Variable | OKLCH | Hex | Usage |
|---|---|---|---|---|
| `background` | `color/background` | `oklch(0.960 0.014 78)` | `#F7F1E8` | Page base — warm parchment |
| `surface-base` | `color/surface-base` | `oklch(0.985 0.011 72)` | `#FFF9F2` | Base card/popover surface |
| `surface-raised` | `color/surface-raised` | `oklch(0.976 0.012 75)` | `#FCF6EE` | Raised panels, secondary cards |
| `surface-sunken` | `color/surface-sunken` | `oklch(0.930 0.041 82)` | `#F6E6CA` | Sunken wells, inset areas |
| `foreground` | `color/foreground` | `oklch(0.256 0.025 69)` | `#2B2116` | Primary body text, headings |
| `primary` | `color/primary` | `oklch(0.761 0.139 73)` | `#E6A23C` | CTAs, active states, links |
| `primary-foreground` | `color/primary-foreground` | `oklch(0.256 0.025 69)` | `#2B2116` | Text on primary fills |
| `primary-hover` | `color/primary-hover` | `oklch(0.718 0.136 72)` | `#D89432` | Primary hover state |
| `primary-active` | `color/primary-active` | `oklch(0.668 0.132 68)` | `#C98328` | Primary pressed state |
| `secondary` | `color/secondary` | `oklch(0.976 0.012 75)` | `#FCF6EE` | Secondary buttons, badges |
| `secondary-foreground` | `color/secondary-foreground` | `oklch(0.256 0.025 69)` | `#2B2116` | Text on secondary |
| `muted` | `color/muted` | `oklch(0.940 0.016 76)` | `#F0E8DA` | Muted backgrounds, skeleton |
| `muted-foreground` | `color/muted-foreground` | `oklch(0.512 0.045 68)` | `#78624B` | Tertiary text, timestamps |
| `accent` | `color/accent` | `oklch(0.930 0.041 82)` | `#F6E6CA` | Amber-tinted hover wash |
| `accent-foreground` | `color/accent-foreground` | `oklch(0.256 0.025 69)` | `#2B2116` | Text on accent surfaces |
| `accent-muted` | `color/accent-muted` | `oklch(0.950 0.028 78)` | `#F8EDD5` | Soft amber background |
| `destructive` | `color/destructive` | `oklch(0.558 0.148 27)` | `#C0392B` | Destructive actions |
| `destructive-foreground` | `color/destructive-foreground` | `oklch(0.985 0.011 72)` | `#FFF9F2` | Text on destructive fills |
| `card` | `color/card` | `oklch(0.985 0.011 72)` | `#FFF9F2` | Card background |
| `card-foreground` | `color/card-foreground` | `oklch(0.256 0.025 69)` | `#2B2116` | Card text |
| `popover` | `color/popover` | `oklch(0.985 0.011 72)` | `#FFF9F2` | Popover/dropdown background |
| `popover-foreground` | `color/popover-foreground` | `oklch(0.256 0.025 69)` | `#2B2116` | Popover text |
| `border` | `color/border` | `oklch(0.839 0.049 78)` | `#DCC7A7` | Default borders |
| `input` | `color/input` | `oklch(0.839 0.049 78)` | `#DCC7A7` | Input borders |
| `ring` | `color/ring` | `oklch(0.761 0.139 73)` | `#E6A23C` | Focus ring (amber) |

### 1.2 Dark Mode — Foundation Palette

| Token | Figma Variable | OKLCH | Hex | Usage |
|---|---|---|---|---|
| `background` | `color/background` | `oklch(0.120 0.011 67)` | `#120E0A` | Page base — deep espresso |
| `surface-base` | `color/surface-base` | `oklch(0.197 0.014 62)` | `#1A140F` | Base card/popover surface |
| `surface-raised` | `color/surface-raised` | `oklch(0.229 0.018 63)` | `#231B14` | Raised panels |
| `surface-sunken` | `color/surface-sunken` | `oklch(0.152 0.012 65)` | `#0F0B08` | Sunken wells |
| `foreground` | `color/foreground` | `oklch(0.961 0.015 77)` | `#F8F1E7` | Primary body text, headings |
| `primary` | `color/primary` | `oklch(0.799 0.138 76)` | `#F0B04A` | CTAs, active states |
| `primary-foreground` | `color/primary-foreground` | `oklch(0.256 0.025 69)` | `#2B2116` | Text on primary (dark ink) |
| `primary-hover` | `color/primary-hover` | `oklch(0.857 0.108 81)` | `#F4C97B` | Primary hover state |
| `primary-active` | `color/primary-active` | `oklch(0.718 0.136 72)` | `#D89432` | Primary pressed state |
| `secondary` | `color/secondary` | `oklch(0.229 0.018 63)` | `#231B14` | Secondary buttons, badges |
| `secondary-foreground` | `color/secondary-foreground` | `oklch(0.961 0.015 77)` | `#F8F1E7` | Text on secondary |
| `muted` | `color/muted` | `oklch(0.197 0.014 62)` | `#1A140F` | Muted backgrounds |
| `muted-foreground` | `color/muted-foreground` | `oklch(0.784 0.037 76)` | `#C7B69F` | Tertiary text, timestamps |
| `accent` | `color/accent` | `oklch(0.278 0.024 64)` | `#31261C` | Amber-tinted hover wash |
| `accent-foreground` | `color/accent-foreground` | `oklch(0.961 0.015 77)` | `#F8F1E7` | Text on accent surfaces |
| `accent-muted` | `color/accent-muted` | `oklch(0.248 0.020 63)` | `#29201A` | Soft amber background |
| `destructive` | `color/destructive` | `oklch(0.627 0.184 25)` | `#E74C3C` | Destructive actions |
| `destructive-foreground` | `color/destructive-foreground` | `oklch(0.961 0.015 77)` | `#F8F1E7` | Text on destructive fills |
| `card` | `color/card` | `oklch(0.197 0.014 62)` | `#1A140F` | Card background |
| `card-foreground` | `color/card-foreground` | `oklch(0.961 0.015 77)` | `#F8F1E7` | Card text |
| `popover` | `color/popover` | `oklch(0.197 0.014 62)` | `#1A140F` | Popover/dropdown background |
| `popover-foreground` | `color/popover-foreground` | `oklch(0.961 0.015 77)` | `#F8F1E7` | Popover text |
| `border` | `color/border` | `oklch(0.329 0.034 68)` | `#5A4630` | Default borders |
| `input` | `color/input` | `oklch(0.329 0.034 68)` | `#5A4630` | Input borders |
| `ring` | `color/ring` | `oklch(0.799 0.138 76)` | `#F0B04A` | Focus ring (amber) |

### 1.3 Sidebar Tokens

| Token | Figma Variable | Light Hex | Dark Hex | Usage |
|---|---|---|---|---|
| `sidebar-background` | `color/sidebar-background` | `#FFF5E6` | `#15100B` | Sidebar panel |
| `sidebar-foreground` | `color/sidebar-foreground` | `#2B2116` | `#F8F1E7` | Sidebar text |
| `sidebar-primary` | `color/sidebar-primary` | `#2B2116` | `#F8F1E7` | Active nav item text |
| `sidebar-primary-foreground` | `color/sidebar-primary-foreground` | `#FFF9F2` | `#2B2116` | Text on active nav bg |
| `sidebar-accent` | `color/sidebar-accent` | `#F6E6CA` | `#29201A` | Nav hover/selected bg |
| `sidebar-accent-foreground` | `color/sidebar-accent-foreground` | `#2B2116` | `#F8F1E7` | Nav hover text |
| `sidebar-border` | `color/sidebar-border` | `#DCC7A7` | `#3D2F22` | Sidebar edge border |
| `sidebar-ring` | `color/sidebar-ring` | `#E6A23C` | `#F0B04A` | Sidebar focus ring |

### 1.4 Chart Colors

5 data-visualization colors, warm-first with one restrained mineral blue accent per chart max.

| Token | Figma Variable | Light/Dark Hex | OKLCH | Usage |
|---|---|---|---|---|
| `chart-1` | `color/chart-1` | `#E6A23C` | `oklch(0.761 0.139 73)` | Primary data series — amber |
| `chart-2` | `color/chart-2` | `#B89565` | `oklch(0.691 0.077 75)` | Secondary — bronze |
| `chart-3` | `color/chart-3` | `#8B5E3C` | `oklch(0.537 0.083 63)` | Tertiary — umber |
| `chart-4` | `color/chart-4` | `#5C7A4D` | `oklch(0.495 0.083 139)` | Quaternary — moss |
| `chart-5` | `color/chart-5` | `#7A8B9C` | `oklch(0.583 0.033 240)` | Quinary — mineral (use sparingly) |

### 1.5 Semantic Status Colors

First-class status tokens. Status chips use these hues over 12–18% alpha fills rather than opaque blocks.

| Token | Figma Variable | Light Hex | Light OKLCH | Dark Hex | Dark OKLCH | Usage |
|---|---|---|---|---|---|---|
| `status-success` | `color/status-success` | `#496D3E` | `oklch(0.495 0.083 139)` | `#86B67A` | `oklch(0.727 0.099 140)` | Connected, saved, completed |
| `status-success-bg` | `color/status-success-bg` | `#EAF2E6` | `oklch(0.944 0.024 139)` | `#1A2616` | `oklch(0.200 0.024 139)` | Success surface tint |
| `status-warning` | `color/status-warning` | `#8A5A12` | `oklch(0.509 0.103 71)` | `#D2BF8B` | `oklch(0.808 0.072 90)` | Caution, attention needed |
| `status-warning-bg` | `color/status-warning-bg` | `#FBF0D9` | `oklch(0.960 0.040 90)` | `#29201A` | `oklch(0.248 0.030 80)` | Warning surface tint |
| `status-error` | `color/status-error` | `#A2432B` | `oklch(0.506 0.132 35)` | `#D88E74` | `oklch(0.716 0.098 40)` | Failed, disconnected, invalid |
| `status-error-bg` | `color/status-error-bg` | `#F8E6E0` | `oklch(0.928 0.038 30)` | `#261612` | `oklch(0.192 0.028 30)` | Error surface tint |
| `status-info` | `color/status-info` | `#586B7A` | `oklch(0.518 0.033 242)` | `#9DB6C8` | `oklch(0.763 0.038 239)` | Informational, neutral note |
| `status-info-bg` | `color/status-info-bg` | `#E8EDF2` | `oklch(0.938 0.016 242)` | `#161C24` | `oklch(0.195 0.016 242)` | Info surface tint |

### 1.6 Accessibility Reference

Approved AA pairings. **Never** use amber text on pale glass or ivory text on amber fills.

| Foreground | Background | Contrast Ratio | Passes |
|---|---|---|---|
| `#2B2116` on `#F7F1E8` | Light mode body | ~14.04:1 | ✅ AAA |
| `#F8F1E7` on `#120E0A` | Dark mode body | ~17.14:1 | ✅ AAA |
| `#2B2116` on `#E6A23C` | Text on amber button | ~7.21:1 | ✅ AAA |
| `#2B2116` on `#F0B04A` | Text on dark-mode amber | ~8.45:1 | ✅ AAA |
| `#78624B` on `#FFF9F2` | Muted text on cards | ~5.51:1 | ✅ AA |
| `#C7B69F` on `#1A140F` | Dark muted text | ~9.23:1 | ✅ AAA |
| `#FFF9F2` on `#C0392B` | Text on destructive (light) | ~5.82:1 | ✅ AA |
| `#F8F1E7` on `#E74C3C` | Text on destructive (dark) | ~4.92:1 | ✅ AA |

### 1.7 Tailwind v4 CSS Mapping

```css
/* ─── Light Mode (default) ─── */
@theme {
  --color-background: oklch(0.960 0.014 78);
  --color-foreground: oklch(0.256 0.025 69);
  --color-primary: oklch(0.761 0.139 73);
  --color-primary-foreground: oklch(0.256 0.025 69);
  --color-primary-hover: oklch(0.718 0.136 72);
  --color-primary-active: oklch(0.668 0.132 68);
  --color-secondary: oklch(0.976 0.012 75);
  --color-secondary-foreground: oklch(0.256 0.025 69);
  --color-muted: oklch(0.940 0.016 76);
  --color-muted-foreground: oklch(0.512 0.045 68);
  --color-accent: oklch(0.930 0.041 82);
  --color-accent-foreground: oklch(0.256 0.025 69);
  --color-accent-muted: oklch(0.950 0.028 78);
  --color-destructive: oklch(0.558 0.148 27);
  --color-destructive-foreground: oklch(0.985 0.011 72);
  --color-card: oklch(0.985 0.011 72);
  --color-card-foreground: oklch(0.256 0.025 69);
  --color-popover: oklch(0.985 0.011 72);
  --color-popover-foreground: oklch(0.256 0.025 69);
  --color-border: oklch(0.839 0.049 78);
  --color-input: oklch(0.839 0.049 78);
  --color-ring: oklch(0.761 0.139 73);
  --color-sidebar-background: oklch(0.970 0.024 72);
  --color-sidebar-foreground: oklch(0.256 0.025 69);
  --color-sidebar-primary: oklch(0.256 0.025 69);
  --color-sidebar-primary-foreground: oklch(0.985 0.011 72);
  --color-sidebar-accent: oklch(0.930 0.041 82);
  --color-sidebar-accent-foreground: oklch(0.256 0.025 69);
  --color-sidebar-border: oklch(0.839 0.049 78);
  --color-sidebar-ring: oklch(0.761 0.139 73);
  --color-chart-1: oklch(0.761 0.139 73);
  --color-chart-2: oklch(0.691 0.077 75);
  --color-chart-3: oklch(0.537 0.083 63);
  --color-chart-4: oklch(0.495 0.083 139);
  --color-chart-5: oklch(0.583 0.033 240);
  --color-status-success: oklch(0.495 0.083 139);
  --color-status-warning: oklch(0.509 0.103 71);
  --color-status-error: oklch(0.506 0.132 35);
  --color-status-info: oklch(0.518 0.033 242);
}

/* ─── Dark Mode ─── */
.dark {
  --color-background: oklch(0.120 0.011 67);
  --color-foreground: oklch(0.961 0.015 77);
  --color-primary: oklch(0.799 0.138 76);
  --color-primary-foreground: oklch(0.256 0.025 69);
  --color-primary-hover: oklch(0.857 0.108 81);
  --color-primary-active: oklch(0.718 0.136 72);
  --color-secondary: oklch(0.229 0.018 63);
  --color-secondary-foreground: oklch(0.961 0.015 77);
  --color-muted: oklch(0.197 0.014 62);
  --color-muted-foreground: oklch(0.784 0.037 76);
  --color-accent: oklch(0.278 0.024 64);
  --color-accent-foreground: oklch(0.961 0.015 77);
  --color-accent-muted: oklch(0.248 0.020 63);
  --color-destructive: oklch(0.627 0.184 25);
  --color-destructive-foreground: oklch(0.961 0.015 77);
  --color-card: oklch(0.197 0.014 62);
  --color-card-foreground: oklch(0.961 0.015 77);
  --color-popover: oklch(0.197 0.014 62);
  --color-popover-foreground: oklch(0.961 0.015 77);
  --color-border: oklch(0.329 0.034 68);
  --color-input: oklch(0.329 0.034 68);
  --color-ring: oklch(0.799 0.138 76);
  --color-sidebar-background: oklch(0.145 0.012 65);
  --color-sidebar-foreground: oklch(0.961 0.015 77);
  --color-sidebar-primary: oklch(0.961 0.015 77);
  --color-sidebar-primary-foreground: oklch(0.256 0.025 69);
  --color-sidebar-accent: oklch(0.248 0.020 63);
  --color-sidebar-accent-foreground: oklch(0.961 0.015 77);
  --color-sidebar-border: oklch(0.290 0.030 66);
  --color-sidebar-ring: oklch(0.799 0.138 76);
  --color-chart-1: oklch(0.799 0.138 76);
  --color-chart-2: oklch(0.691 0.077 75);
  --color-chart-3: oklch(0.537 0.083 63);
  --color-chart-4: oklch(0.727 0.099 140);
  --color-chart-5: oklch(0.763 0.038 239);
  --color-status-success: oklch(0.727 0.099 140);
  --color-status-warning: oklch(0.808 0.072 90);
  --color-status-error: oklch(0.716 0.098 40);
  --color-status-info: oklch(0.763 0.038 239);
}
```

---

## 2. Background Mesh Gradients

The mesh creates the warm luminous "alive" quality beneath all glass surfaces. Three radial-gradient layers per mode.

### 2.1 Light Mode — Sunlight Through Frosted Glass

```css
.mesh-light {
  background:
    radial-gradient(
      ellipse 80% 60% at 15% 20%,
      rgba(230, 162, 60, 0.18),
      transparent 50%
    ),
    radial-gradient(
      ellipse 70% 50% at 85% 10%,
      rgba(244, 201, 123, 0.15),
      transparent 45%
    ),
    radial-gradient(
      ellipse 90% 70% at 65% 75%,
      rgba(217, 185, 140, 0.14),
      transparent 55%
    ),
    linear-gradient(180deg, #FFF9F2 0%, #F7F1E8 100%);
}
```

### 2.2 Dark Mode — Candlelight Through Dark Glass

```css
.mesh-dark {
  background:
    radial-gradient(
      ellipse 80% 60% at 18% 18%,
      rgba(240, 176, 74, 0.16),
      transparent 45%
    ),
    radial-gradient(
      ellipse 70% 50% at 82% 12%,
      rgba(201, 131, 40, 0.12),
      transparent 40%
    ),
    radial-gradient(
      ellipse 90% 70% at 72% 78%,
      rgba(90, 70, 48, 0.22),
      transparent 50%
    ),
    linear-gradient(180deg, #1A140F 0%, #120E0A 100%);
}
```

### 2.3 Figma Variable

| Variable | Value |
|---|---|
| `mesh/light` | CSS above (Light mode) |
| `mesh/dark` | CSS above (Dark mode) |

---

## 3. Typography Scale

### 3.1 Font Stacks

```css
--font-sans: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
--font-mono: 'SF Mono', 'JetBrains Mono', 'Cascadia Code', ui-monospace, monospace;
```

Ligatures enabled: `font-feature-settings: "rlig" 1, "calt" 1;`

### 3.2 Type Scale — 10 Levels

| Level | Figma Variable | Size (px) | rem | Weight | Line-Height | Letter-Spacing | Usage |
|---|---|---|---|---|---|---|---|
| `display` | `type/display` | 36 | 2.25 | 700 | 1.15 | −0.02em | Hero headings, onboarding |
| `h1` | `type/h1` | 30 | 1.875 | 700 | 1.2 | −0.015em | Page titles |
| `h2` | `type/h2` | 24 | 1.5 | 600 | 1.25 | −0.01em | Section headings |
| `h3` | `type/h3` | 20 | 1.25 | 600 | 1.3 | −0.005em | Card titles, subsections |
| `h4` | `type/h4` | 18 | 1.125 | 600 | 1.35 | 0 | Panel headers, sidebar items |
| `body-lg` | `type/body-lg` | 18 | 1.125 | 400 | 1.6 | 0 | Chat message bubbles |
| `body` | `type/body` | 16 | 1.0 | 400 | 1.5 | 0 | Body text, descriptions |
| `body-sm` | `type/body-sm` | 14 | 0.875 | 400 | 1.5 | 0 | Form labels, secondary text |
| `caption` | `type/caption` | 12 | 0.75 | 500 | 1.4 | 0.01em | Badges, timestamps, metadata |
| `overline` | `type/overline` | 11 | 0.6875 | 600 | 1.4 | 0.06em | Section labels, category tags |

### 3.3 Monospace Scale

| Level | Figma Variable | Size (px) | rem | Weight | Line-Height | Usage |
|---|---|---|---|---|---|---|
| `mono` | `type/mono` | 14 | 0.875 | 400 | 1.6 | Code blocks, log entries |
| `mono-sm` | `type/mono-sm` | 13 | 0.8125 | 400 | 1.5 | File paths, inline code |
| `mono-xs` | `type/mono-xs` | 12 | 0.75 | 400 | 1.5 | Timestamps, status codes |

---

## 4. Border Radius Tokens

| Token | Figma Variable | Value (px) | rem | Usage |
|---|---|---|---|---|
| `radius-xs` | `radius/xs` | 4 | 0.25 | Tags, small chips, inline badges |
| `radius-sm` | `radius/sm` | 6 | 0.375 | Buttons, inputs, select triggers |
| `radius-md` | `radius/md` | 8 | 0.5 | Cards, dialogs, panels |
| `radius-lg` | `radius/lg` | 12 | 0.75 | Large cards, modal containers |
| `radius-xl` | `radius/xl` | 16 | 1.0 | Feature cards, hero sections |
| `radius-full` | `radius/full` | 9999 | — | Pills, avatars, circular badges |

### Tailwind v4 CSS

```css
@theme {
  --radius-xs: 0.25rem;
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
}
```

---

## 5. Shadow System

### 5.1 Light Mode Shadows

| Token | Figma Variable | CSS `box-shadow` | Usage |
|---|---|---|---|
| `shadow-sm` | `shadow/sm` | `0 1px 2px rgba(43, 33, 22, 0.04)` | Subtle lift — tags, chips |
| `shadow-md` | `shadow/md` | `0 2px 8px rgba(43, 33, 22, 0.06), 0 1px 2px rgba(43, 33, 22, 0.04)` | Cards, list items |
| `shadow-lg` | `shadow/lg` | `0 4px 16px rgba(43, 33, 22, 0.08), 0 2px 4px rgba(43, 33, 22, 0.04)` | Dropdowns, popovers |
| `shadow-xl` | `shadow/xl` | `0 8px 32px rgba(43, 33, 22, 0.10), 0 4px 8px rgba(43, 33, 22, 0.05)` | Modals, command palette |

### 5.2 Dark Mode Shadows

| Token | Figma Variable | CSS `box-shadow` | Usage |
|---|---|---|---|
| `shadow-sm` | `shadow/sm` | `0 1px 2px rgba(0, 0, 0, 0.20)` | Subtle lift |
| `shadow-md` | `shadow/md` | `0 2px 8px rgba(0, 0, 0, 0.28), 0 1px 2px rgba(0, 0, 0, 0.14)` | Cards |
| `shadow-lg` | `shadow/lg` | `0 4px 16px rgba(0, 0, 0, 0.36), 0 2px 4px rgba(0, 0, 0, 0.18)` | Dropdowns |
| `shadow-xl` | `shadow/xl` | `0 8px 32px rgba(0, 0, 0, 0.44), 0 4px 8px rgba(0, 0, 0, 0.22)` | Modals |

### 5.3 Accent Glow Shadow

Used for active/selected states with amber glow:

| Mode | CSS |
|---|---|
| Light | `0 0 0 3px rgba(230, 162, 60, 0.28), 0 0 12px rgba(230, 162, 60, 0.12)` |
| Dark | `0 0 0 3px rgba(240, 176, 74, 0.32), 0 0 16px rgba(240, 176, 74, 0.16)` |

```css
/* Utility classes */
.shadow-glow-light {
  box-shadow: 0 0 0 3px rgba(230, 162, 60, 0.28), 0 0 12px rgba(230, 162, 60, 0.12);
}
.shadow-glow-dark {
  box-shadow: 0 0 0 3px rgba(240, 176, 74, 0.32), 0 0 16px rgba(240, 176, 74, 0.16);
}
```

---

## 6. Glass Material Tiers

Four translucent glass tiers. Each defines `backdrop-filter`, background alpha for both modes, border, and usage.

### 6.1 Tier Definitions

| Tier | Figma Variable | `backdrop-filter` | Light Alpha | Dark Alpha | Border |
|---|---|---|---|---|---|
| **Ultra-thin** | `glass/ultra-thin` | `blur(8px) saturate(120%)` | `rgba(255,249,242, 0.45)` | `rgba(26,20,15, 0.40)` | `1px solid rgba(220,199,167, 0.10)` light · `1px solid rgba(90,70,48, 0.12)` dark |
| **Thin** | `glass/thin` | `blur(12px) saturate(130%)` | `rgba(255,249,242, 0.58)` | `rgba(26,20,15, 0.52)` | `1px solid rgba(220,199,167, 0.14)` light · `1px solid rgba(90,70,48, 0.16)` dark |
| **Regular** | `glass/regular` | `blur(20px) saturate(150%)` | `rgba(252,246,238, 0.72)` | `rgba(35,27,20, 0.64)` | `1px solid rgba(220,199,167, 0.18)` light · `1px solid rgba(90,70,48, 0.22)` dark |
| **Thick** | `glass/thick` | `blur(28px) saturate(170%)` | `rgba(247,241,232, 0.84)` | `rgba(49,38,28, 0.78)` | `1px solid rgba(220,199,167, 0.28)` light · `1px solid rgba(90,70,48, 0.28)` dark |

### 6.2 Usage Mapping

| Tier | UI Elements |
|---|---|
| **Ultra-thin** | Sidebar background, top bar, navigation chrome |
| **Thin** | Cards, list items, secondary panels |
| **Regular** | Primary content panels, chat area, editor panes |
| **Thick** | Modals, dialogs, command palette, focused overlays |

### 6.3 CSS Utilities

```css
.glass-ultra-thin {
  backdrop-filter: blur(8px) saturate(120%);
  -webkit-backdrop-filter: blur(8px) saturate(120%);
}
.glass-ultra-thin.light {
  background: rgba(255, 249, 242, 0.45);
  border: 1px solid rgba(220, 199, 167, 0.10);
}
.glass-ultra-thin.dark {
  background: rgba(26, 20, 15, 0.40);
  border: 1px solid rgba(90, 70, 48, 0.12);
}

.glass-thin {
  backdrop-filter: blur(12px) saturate(130%);
  -webkit-backdrop-filter: blur(12px) saturate(130%);
}
.glass-thin.light {
  background: rgba(255, 249, 242, 0.58);
  border: 1px solid rgba(220, 199, 167, 0.14);
}
.glass-thin.dark {
  background: rgba(26, 20, 15, 0.52);
  border: 1px solid rgba(90, 70, 48, 0.16);
}

.glass-regular {
  backdrop-filter: blur(20px) saturate(150%);
  -webkit-backdrop-filter: blur(20px) saturate(150%);
}
.glass-regular.light {
  background: rgba(252, 246, 238, 0.72);
  border: 1px solid rgba(220, 199, 167, 0.18);
}
.glass-regular.dark {
  background: rgba(35, 27, 20, 0.64);
  border: 1px solid rgba(90, 70, 48, 0.22);
}

.glass-thick {
  backdrop-filter: blur(28px) saturate(170%);
  -webkit-backdrop-filter: blur(28px) saturate(170%);
}
.glass-thick.light {
  background: rgba(247, 241, 232, 0.84);
  border: 1px solid rgba(220, 199, 167, 0.28);
}
.glass-thick.dark {
  background: rgba(49, 38, 28, 0.78);
  border: 1px solid rgba(90, 70, 48, 0.28);
}
```

---

## 7. Spacing System

Apple's 4px base grid. All values are multiples of 4.

| Token | Figma Variable | px | rem | Usage |
|---|---|---|---|---|
| `space-0` | `space/0` | 0 | 0 | Reset |
| `space-1` | `space/1` | 4 | 0.25 | Inline gaps, icon-to-text |
| `space-1.5` | `space/1.5` | 6 | 0.375 | Compact element gaps |
| `space-2` | `space/2` | 8 | 0.5 | Component internal padding |
| `space-3` | `space/3` | 12 | 0.75 | Standard padding, input padding |
| `space-4` | `space/4` | 16 | 1.0 | Card section gaps, form spacing |
| `space-5` | `space/5` | 20 | 1.25 | Medium section gaps |
| `space-6` | `space/6` | 24 | 1.5 | Card padding, large gaps |
| `space-8` | `space/8` | 32 | 2.0 | Page margins, major sections |
| `space-10` | `space/10` | 40 | 2.5 | Page-level padding |
| `space-12` | `space/12` | 48 | 3.0 | Max section spacing, hero padding |

### Tailwind Mapping

These map directly to Tailwind's default spacing scale:
`p-1` → 4px, `p-2` → 8px, `p-3` → 12px, `p-4` → 16px, `p-5` → 20px, `p-6` → 24px, `p-8` → 32px, `p-10` → 40px, `p-12` → 48px.

---

## 8. Motion & Animation

### 8.1 Transition Tokens

| Token | Figma Variable | Duration | Easing | Usage |
|---|---|---|---|---|
| `transition-fast` | `motion/fast` | 120ms | `cubic-bezier(0.25, 0.1, 0.25, 1)` | Hover states, color changes |
| `transition-standard` | `motion/standard` | 200ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Most interactions, toggles |
| `transition-slow` | `motion/slow` | 300ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Panel expand/collapse |
| `transition-spring` | `motion/spring` | 400ms | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Segmented controls, modals, sheets |
| `transition-glass` | `motion/glass` | 500ms | `cubic-bezier(0.4, 0, 0.2, 1)` | Glass material/blur transitions |

### 8.2 CSS Utilities

```css
/* Standard transition */
.transition-standard {
  transition-duration: 200ms;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Spring — overshoot for playful elements */
.transition-spring {
  transition-duration: 400ms;
  transition-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Glass material change (blur, opacity) */
.transition-glass {
  transition-duration: 500ms;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-property: background-color, backdrop-filter, border-color, box-shadow;
}
```

### 8.3 Keyframe Animations

```css
/* Pulse — for loading skeletons, active indicators */
@keyframes pulse-amber {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Shimmer — for skeleton placeholders */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Fade-in-up — for toast notifications, cards appearing */
@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scale-in — for modals, dialogs */
@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
```

### 8.4 Animation Presets

| Name | Value | Usage |
|---|---|---|
| `animate-pulse` | `pulse-amber 2s ease-in-out infinite` | Loading skeletons |
| `animate-shimmer` | `shimmer 2s linear infinite` | Skeleton placeholders |
| `animate-fade-in` | `fade-in-up 200ms cubic-bezier(0.4,0,0.2,1)` | Cards, toasts appearing |
| `animate-scale-in` | `scale-in 300ms cubic-bezier(0.34,1.56,0.64,1)` | Modals opening |

---

## 9. Z-Index Scale

| Token | Figma Variable | Value | Usage |
|---|---|---|---|
| `z-base` | `z/base` | 0 | Normal content flow |
| `z-sticky` | `z/sticky` | 10 | Sticky headers, top bars |
| `z-sidebar` | `z/sidebar` | 20 | Sidebar panels |
| `z-dropdown` | `z/dropdown` | 30 | Dropdowns, select menus |
| `z-modal-backdrop` | `z/modal-backdrop` | 40 | Modal overlay backdrop |
| `z-modal` | `z/modal` | 50 | Modal content |
| `z-tooltip` | `z/tooltip` | 60 | Tooltips |
| `z-toast` | `z/toast` | 70 | Toast notifications |
| `z-command-palette` | `z/command-palette` | 80 | Command palette (topmost) |

### CSS Custom Properties

```css
:root {
  --z-base: 0;
  --z-sticky: 10;
  --z-sidebar: 20;
  --z-dropdown: 30;
  --z-modal-backdrop: 40;
  --z-modal: 50;
  --z-tooltip: 60;
  --z-toast: 70;
  --z-command-palette: 80;
}
```

---

## 10. Responsive Breakpoints

Following Tailwind CSS v4 defaults.

| Token | Figma Variable | Min Width | Typical Device | Usage |
|---|---|---|---|---|
| `sm` | `breakpoint/sm` | 640px | Phone landscape | Two-column mobile, larger touch targets |
| `md` | `breakpoint/md` | 768px | Tablet portrait | Sidebar becomes visible, drawer → fixed |
| `lg` | `breakpoint/lg` | 1024px | Tablet landscape / small desktop | Three-column layouts, side panels |
| `xl` | `breakpoint/xl` | 1280px | Desktop | Full desktop layout |
| `2xl` | `breakpoint/2xl` | 1536px | Large desktop | Max-width container, extra breathing room |

### Responsive Behavior Summary

| Breakpoint | Sidebar | Chat Panels | Notes |
|---|---|---|---|
| `< md` (mobile) | Drawer overlay | Single column, panels → sheet | Touch-optimized |
| `md – lg` (tablet) | Collapsed icons | Panels collapsed by default | Expand available |
| `≥ lg` (desktop) | Expandable sidebar | Three-column workspace | Full feature set |

---

## Figma Variable Naming Convention

All tokens use a flat namespace with `/` separators for grouping:

```
color/background
color/foreground
color/primary
color/primary-foreground
color/status-success
color/sidebar-background
radius/sm
radius/md
shadow/md
shadow/glow
glass/thin
glass/regular
space/4
type/h2
type/body-sm
motion/standard
motion/spring
z/modal
breakpoint/md
```

### Figma Collections & Modes

| Collection | Modes | Variables |
|---|---|---|
| `Color` | `Light`, `Dark` | All `color/*` tokens |
| `Spacing` | (single mode) | All `space/*` tokens |
| `Radius` | (single mode) | All `radius/*` tokens |
| `Elevation` | `Light`, `Dark` | All `shadow/*` tokens |
| `Glass` | `Light`, `Dark` | All `glass/*` tokens |
| `Typography` | (single mode) | All `type/*` tokens |
| `Motion` | (single mode) | All `motion/*` tokens |
| `Z-Index` | (single mode) | All `z/*` tokens |

---

## Migration Notes

When updating from the current hue-261 slate system to Liquid Crystal — Warm Amber:

1. **Replace ALL tokens at once.** Do not partially update — mixing warm amber with cold slate creates visual dissonance.
2. **Update `web/src/globals.css` `@theme` block** with all Light mode OKLCH values from Section 1.7.
3. **Update `.dark` block** with all Dark mode values from Section 1.7.
4. **Add mesh gradient** to the `<body>` or app shell wrapper.
5. **Apply glass tiers** to sidebar, cards, panels, and modals via the CSS utilities from Section 6.3.
6. **Verify contrast** for any custom components using the AA pairings table in Section 1.6.
7. **`primary-foreground` stays dark ink** (`#2B2116`) in both themes. Never switch to light text on amber.

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
