# Settings Page — Full Composition Specification

> **System:** Liquid Crystal — Warm Amber
> **Version:** 1.0.0
> **Last updated:** 2026-04-11
> **Token source:** `docs/design-system/tokens.md`
> **Companion specs:** `layout-shell.md` · `components-button-badge.md` · `components-surface-overlay.md` · `components-form-inputs.md` · `components-feedback-utility.md`
> **Implementation:** `web/src/features/settings/settings-page.tsx` · `web/src/features/settings/settings-api.ts`
> **Types:** `web/src/types/api.ts` (`AppSettings`, `SettingsUpdateResponse`)

---

## Table of Contents

1. [Page Layout Structure](#1-page-layout-structure)
2. [Form Layout Pattern](#2-form-layout-pattern)
3. [General Tab Specification](#3-general-tab-specification)
4. [LLM Tab Specification](#4-llm-tab-specification)
5. [Vault Tab Specification](#5-vault-tab-specification)
6. [Advanced Tab Specification](#6-advanced-tab-specification)
7. [Save Action Pattern](#7-save-action-pattern)
8. [State Frames Specification](#8-state-frames-specification)
9. [Glass Treatment Map](#9-glass-treatment-map)
10. [Responsive Behavior](#10-responsive-behavior)
11. [Figma Frames Specification](#11-figma-frames-specification)
12. [TSX Skeleton](#12-tsx-skeleton)
13. [Native Element Migration Checklist](#13-native-element-migration-checklist)
14. [Appendix A: Accessibility Checklist](#appendix-a-accessibility-checklist)
15. [Appendix B: Token Cross-Reference](#appendix-b-token-cross-reference)
16. [Appendix C: Implementation Checklist](#appendix-c-implementation-checklist)

---

## 1. Page Layout Structure

### 1.1 Component Hierarchy

```
SettingsPage (flex-col, gap-6, p-4 md:p-6, max-w-2xl, mx-auto)
├── Page Header
│   └── Title: "Settings" (title-1: 28px/600, foreground)
└── Tabs (defaultValue="general", flex-1)
    ├── TabsList (glass-tier-ultra-thin, radius-sm: 10px, h-[38px])
    │   ├── TabsTrigger: "General"
    │   ├── TabsTrigger: "LLM"
    │   ├── TabsTrigger: "Vault"
    │   └── TabsTrigger: "Advanced"
    ├── TabsContent "general" (mt-6)
    │   └── GeneralTab
    ├── TabsContent "llm" (mt-6)
    │   └── LLMTab
    ├── TabsContent "vault" (mt-6)
    │   └── VaultTab
    └── TabsContent "advanced" (mt-6)
        └── AdvancedTab
```

### 1.2 ASCII Layout — Desktop (1440×900)

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Settings                                                    │
│  (title-1: 28px/600)                                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ General │   LLM   │  Vault  │ Advanced               │    │
│  │ [glass-ultra-thin, h-38px, rounded-10px]              │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  Section: "Appearance" (headline: 16px/600)                  │
│  ────────────────────────                                    │
│                                                              │
│  Theme                                                       │
│  Choose how the interface looks                              │
│  ┌──────────┬──────────┬──────────┐                         │
│  │  Light   │   Dark   │  System  │                         │
│  │ (active, │          │          │                         │
│  │  pill)   │          │          │                         │
│  └──────────┴──────────┴──────────┘                         │
│                                                              │
│  Language                                                    │
│  Set the display language for the interface                  │
│  ┌──────────────────────┐                                   │
│  │ English          ▼   │                                    │
│  └──────────────────────┘                                   │
│                                                              │
│                                              [Save]          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 1.3 Layout Constraints

| Property | Value | Tailwind |
|---|---|---|
| Max width | 672px (2× 336px) | `max-w-2xl` |
| Horizontal margin | auto (centered) | `mx-auto` |
| Page padding (mobile) | 16px | `p-4` |
| Page padding (desktop) | 24px | `md:p-6` |
| Page gap | 24px | `gap-6` |
| Tab content top margin | 24px | `mt-6` |
| Section bottom margin | 32px | `mb-8` |
| Section heading bottom margin | 16px | `mb-4` |

---

## 2. Form Layout Pattern

### 2.1 Reusable Field Block

Every form field on this page follows the same composition:

```
FormField (space-y-2)
├── Label (subhead: 13px/500, foreground)
├── Optional description (caption: 12px/400, muted-foreground)
├── Control (Input / Select / SegmentedControl / Switch)
└── Optional validation/help text (caption: 12px/400)
    ├── Default: hidden (no layout shift)
    ├── Error: destructive color
    ├── Success: status-success color
    └── Warning: status-warning color
```

### 2.2 Section Structure

```
SettingsSection (space-y-6)
├── Section heading (headline: 16px/600, foreground)
├── Optional section description (callout: 14px/400, muted-foreground)
├── Separator (1px, border token)
└── FormField × N
```

### 2.3 Field Spacing Rules

| Spacing | Value | Tailwind |
|---|---|---|
| Between sections | 32px | `space-y-8` |
| Between fields within section | 24px | `space-y-6` |
| Between label and control | 8px | `space-y-2` |
| Between label and description | 2px | implicit in label+desc stack |
| Between control and help text | 4px | `mt-1` |

### 2.4 Label Typography

| Element | Size | Weight | Color Token | Tailwind |
|---|---|---|---|---|
| Label | 13px | 500 | `foreground` | `text-[13px] font-medium text-foreground` |
| Description | 12px | 400 | `muted-foreground` | `text-xs text-muted-foreground` |
| Section heading | 16px | 600 | `foreground` | `text-[16px] font-semibold text-foreground` |
| Section description | 14px | 400 | `muted-foreground` | `text-sm text-muted-foreground` |
| Validation error | 12px | 400 | `destructive` | `text-xs text-destructive` |
| Validation success | 12px | 400 | `status-success` | `text-xs text-status-success` |

### 2.5 Switch Field Variant

Boolean toggle fields use a horizontal layout instead of vertical:

```
SwitchField (flex, items-start, justify-between, gap-4)
├── Text block
│   ├── Label (subhead: 13px/500, foreground)
│   └── Description (caption: 12px/400, muted-foreground)
└── Switch (mt-0.5 for optical alignment with label baseline)
```

---

## 3. General Tab Specification

### 3.1 Composition

```
GeneralTab (max-w-lg, space-y-8)
├── SettingsSection: "Appearance"
│   ├── Separator
│   ├── FormField: Theme
│   │   ├── Label: "Theme"
│   │   ├── Description: "Choose how the interface looks"
│   │   └── SegmentedControl (Light / Dark / System)
│   │       └── options: [{value:"light",label:"Light"}, {value:"dark",label:"Dark"}, {value:"system",label:"System"}]
│   └── FormField: Language
│       ├── Label: "Language"
│       ├── Description: "Set the display language for the interface"
│       └── Select (English / 中文)
│           └── options: [{value:"en",label:"English"}, {value:"zh",label:"中文"}]
└── SettingsActionBar
    └── Button variant="default" size="sm" (Save icon + "Save")
```

### 3.2 Theme — SegmentedControl

**Control:** `SegmentedControl` from `components-form-inputs.md §6`

| Property | Value |
|---|---|
| Segments | 3 (Light, Dark, System) |
| Default value | `"system"` |
| Width | `w-full max-w-[240px]` |
| aria-label | `"Theme"` |
| Glass | `false` |

**Interaction:** Immediate visual preview — selecting a theme segment applies it instantly (no save required). The save button persists the preference to the backend.

### 3.3 Language — Select

**Control:** `Select` from `components-form-inputs.md §5`

| Property | Value |
|---|---|
| Trigger width | `w-full max-w-[200px]` |
| Options | English (`en`), 中文 (`zh`) |
| Default value | `"en"` |
| Placeholder | `"Select language..."` |

### 3.4 Save Button

| Property | Value |
|---|---|
| Component | `Button` from `components-button-badge.md §4` |
| Variant | `default` |
| Size | `sm` (32px) |
| Icon | `Save` (Lucide, 14px) |
| Label | `"Save"` |
| Loading | Shows `Loader2` spinner + disabled state |
| Alignment | Right-aligned (`flex justify-end`) |

---

## 4. LLM Tab Specification

### 4.1 Composition

```
LLMTab (max-w-lg, space-y-8)
├── SettingsSection: "Language Model"
│   ├── Separator
│   ├── FormField: Model
│   │   ├── Label: "Model"
│   │   ├── Description: "The language model used for generating responses"
│   │   └── Input (text)
│   │       └── placeholder: "e.g., gpt-4o, claude-3.5-sonnet"
│   └── FormField: API Key
│       ├── Label row: "API Key" + Badge (variant=status)
│       ├── Description: "Your API key is stored securely and never displayed"
│       └── Input (password)
│           └── placeholder: "Enter new API key..."
└── SettingsActionBar
    └── Button variant="default" size="sm" (Save icon + "Save")
```

### 4.2 Model — Input

**Control:** `Input` from `components-form-inputs.md §2`

| Property | Value |
|---|---|
| Type | `text` |
| Width | `w-full` |
| Placeholder | `"e.g., gpt-4o, claude-3.5-sonnet"` |
| Default value | `settings.llm_model ?? ""` |

### 4.3 API Key — Input + Badge

**Label row** uses a flex layout with label and badge side-by-side:

```
Label Row (flex, items-center, gap-2)
├── Label: "API Key" (subhead: 13px/500, foreground)
└── Badge (variant based on api_key_set)
    ├── settings.api_key_set === true  → variant="success", text="已设置"
    └── settings.api_key_set === false → variant="warning", text="未设置"
```

**Badge component** from `components-button-badge.md §5`:

| State | Badge Variant | Text | Light Background | Light Text | Dark Background | Dark Text |
|---|---|---|---|---|---|---|
| Key set | `success` | "已设置" | `status-success-bg` #EAF2E6 | `status-success` #496D3E | `status-success-bg` #1A2616 | `status-success` #86B67A |
| Key not set | `warning` | "未设置" | `status-warning-bg` #FBF0D9 | `status-warning` #8A5A12 | `status-warning-bg` #29201A | `status-warning` #D2BF8B |

**Password input:**

| Property | Value |
|---|---|
| Type | `password` |
| Width | `w-full` |
| Placeholder | `"Enter new API key..."` |
| Default value | `""` (always empty — never pre-fill keys) |

### 4.4 Credential Handling Notes

- After successful save with a new key, the badge transitions from `warning` → `success` (the response includes `api_key_set: true`)
- The password input clears on save (`setApiKey("")`) to prevent accidental re-submission
- If the API rejects the key (validation error), show an inline validation message below the input: "API key verification failed" in `destructive` color

---

## 5. Vault Tab Specification

### 5.1 Composition

```
VaultTab (max-w-lg, space-y-8)
├── SettingsSection: "Knowledge Vault"
│   ├── Separator
│   ├── FormField: Vault Path
│   │   ├── Label: "Vault Path"
│   │   ├── Description: "The directory containing your markdown notes"
│   │   └── Input group (flex, gap-2)
│   │       ├── Input (text, flex-1)
│   │       └── Button variant="outline" size="sm" (disabled)
│   │           └── "Browse" (placeholder for future file picker)
│   └── FormField: Connection Status
│       ├── Label: "Connection Status"
│       ├── Description: "Live status of the vault connection (refreshes every 10s)"
│       └── StatusIndicator (flex, items-center, gap-2)
│           ├── StatusDot (8px circle, status token, optional pulse)
│           ├── StatusLabel (callout: 14px/400)
│           └── Last checked: (caption, muted-foreground)
└── SettingsActionBar
    └── Button variant="default" size="sm" (Save icon + "Save")
```

### 5.2 Vault Path — Input Group

```
InputGroup (flex, gap-2)
├── Input (flex-1, text)
│   └── value: settings.vault_path ?? ""
└── Button variant="outline" size="sm" disabled
    └── "Browse"
```

The Browse button is intentionally disabled — file system picker requires backend support (Tauri dialog or similar). Visual presence communicates intent.

### 5.3 Connection Status — Status Indicator

**StatusDot anatomy:**

| Property | Connected | Disconnected |
|---|---|---|
| Size | 8×8px (`h-2 w-2`) | 8×8px (`h-2 w-2`) |
| Shape | `rounded-full` | `rounded-full` |
| Background (light) | `status-success` #496D3E | `status-error` #A2432B |
| Background (dark) | `status-success` #86B67A | `status-error` #D88E74 |
| Animation | `animate-pulse` (2s cycle) | none |
| Aria | `aria-label="Connected"` | `aria-label="Disconnected"` |

**StatusLabel:**

| State | Text | Color |
|---|---|---|
| Connected | `"Connected"` | `foreground` |
| Disconnected | `"Disconnected"` | `muted-foreground` |
| Loading | `"Checking..."` | `muted-foreground` |
| Error | `"Connection error"` | `status-error` |

**Pulse animation** only fires when connected AND the health query is actively refetching (`refetchInterval: 10000`). Between refetches, the dot is solid (no pulse) to reduce visual noise. When the refetch is in-flight (`isFetching`), a brief subtle pulse indicates live polling.

**Health query:**

```tsx
const { data: health, isFetching } = useQuery({
  queryKey: ["health"],
  queryFn: getHealth,
  refetchInterval: 10000,
});
```

### 5.4 Connection Status — Full Component Code

```tsx
function ConnectionStatus({ health, isFetching }: {
  health?: { vault_connected: boolean };
  isFetching: boolean;
}) {
  const connected = health?.vault_connected;

  return (
    <div className="flex items-center gap-2">
      <div
        className={cn(
          "h-2 w-2 rounded-full",
          connected ? "bg-status-success" : "bg-status-error",
          connected && isFetching && "animate-pulse",
        )}
        aria-label={connected ? "Connected" : "Disconnected"}
      />
      <span className={cn(
        "text-sm",
        connected ? "text-foreground" : "text-muted-foreground",
      )}>
        {connected ? "Connected" : "Disconnected"}
      </span>
    </div>
  );
}
```

---

## 6. Advanced Tab Specification

### 6.1 Composition

```
AdvancedTab (max-w-lg, space-y-8)
├── SettingsSection: "API Configuration"
│   ├── Separator
│   └── FormField: API URL
│       ├── Label: "API URL"
│       ├── Description: "The base URL for the backend API server"
│       └── Input (text)
│           └── placeholder: "http://localhost:8000"
├── SettingsSection: "Runtime"
│   ├── Separator
│   ├── SwitchField: Cache Enabled
│   │   ├── Label: "Cache Enabled"
│   │   ├── Description: "Enable response caching for faster queries"
│   │   └── Switch (checked: cacheEnabled)
│   └── FormField: Log Level
│       ├── Label: "Log Level"
│       ├── Description: "Set the verbosity of application logs"
│       └── Select (DEBUG / INFO / WARNING / ERROR)
└── SettingsActionBar
    └── Button variant="default" size="sm" (Save icon + "Save")
```

### 6.2 API URL — Input

| Property | Value |
|---|---|
| Type | `text` |
| Width | `w-full` |
| Placeholder | `"http://localhost:8000"` |
| Default value | `settings.api_url ?? ""` |

### 6.3 Cache Enabled — Switch

**Control:** `Switch` from `components-form-inputs.md §7`

Uses the horizontal Switch field variant (§2.5):

```
SwitchField (flex, items-start, justify-between, gap-4)
├── div (flex-1, space-y-1)
│   ├── Label: "Cache Enabled" (subhead: 13px/500, foreground)
│   └── Description: "Enable response caching for faster queries" (caption, muted-foreground)
└── Switch (mt-0.5)
    ├── checked: cacheEnabled
    └── onCheckedChange: setCacheEnabled
```

| Property | Value |
|---|---|
| Default checked | `settings.cache_enabled ?? true` |
| Track width | 44px |
| Track height | 24px |
| On background | `primary` |
| Off background | `surface-raised` |

### 6.4 Log Level — Select

**Control:** `Select` from `components-form-inputs.md §5`

| Property | Value |
|---|---|
| Trigger width | `w-full max-w-[200px]` |
| Options | DEBUG, INFO, WARNING, ERROR |
| Default value | `"INFO"` |
| Placeholder | `"Select log level..."` |

---

## 7. Save Action Pattern

### 7.1 Action Bar

Each tab renders a consistent action bar at the bottom:

```
SettingsActionBar (flex, items-center, justify-between, pt-6, mt-2)
├── Optional: dirty indicator (caption, muted-foreground)
│   └── "Unsaved changes" (visible when form is dirty)
└── Button (flex, items-center, gap-2)
```

### 7.2 Button States

| State | Visual | Behavior |
|---|---|---|
| **Default** | `Save` icon + "Save" text | Enabled, clickable |
| **Loading** | `Loader2` spinner + "Saving..." text | `disabled`, `aria-busy="true"` |
| **Disabled (clean)** | `opacity-50`, "Save" text | Form unchanged — no save needed |
| **Success** | Brief toast via `sonner` | `toast.success("Settings saved")` |
| **Error** | `AlertBanner variant="error"` above action bar | `"Failed to save settings. Please try again."` |

### 7.3 Mutation Pattern

```tsx
const mutation = useMutation({
  mutationFn: (settings: Partial<AppSettings>) => updateSettings(settings),
  onSuccess: () => {
    toast.success("Settings saved");
  },
  onError: () => {
    // AlertBanner rendered inline above the action bar
    setErrorBanner(true);
  },
});
```

### 7.4 Error AlertBanner

When save fails, an `AlertBanner` from `components-feedback-utility.md §6` appears above the action bar:

```
AlertBanner (variant="error", mb-4)
├── Title: "Failed to save settings"
├── Message: "Your changes were not saved. Please try again."
└── Action: Button ghost xs "Retry" → mutation.mutate(payload)
```

---

## 8. State Frames Specification

### 8.1 Default States (4 frames)

| # | Frame Name | Tab | Description |
|---|---|---|---|
| F1 | `Settings — General Default` | General | Theme=System selected, Language=English |
| F2 | `Settings — LLM Default (key set)` | LLM | Model filled, API key badge=success |
| F3 | `Settings — LLM Default (no key)` | LLM | Model filled, API key badge=warning |
| F4 | `Settings — Vault Default (connected)` | Vault | Path filled, green dot, "Connected" |
| F5 | `Settings — Vault Default (disconnected)` | Vault | Path filled, red dot, "Disconnected" |
| F6 | `Settings — Advanced Default` | Advanced | API URL filled, Cache=on, Log=INFO |

### 8.2 SegmentedControl States (3 frames)

| # | Frame Name | Description |
|---|---|---|
| F7 | `General — Theme: Light` | Active pill on "Light" segment |
| F8 | `General — Theme: Dark` | Active pill on "Dark" segment |
| F9 | `General — Theme: System` | Active pill on "System" segment |

### 8.3 Interaction States (2 frames)

| # | Frame Name | Description |
|---|---|---|
| F10 | `LLM — API Key Set vs Not Set` | Side-by-side comparison of badge states |
| F11 | `Vault — Connected vs Disconnected` | Side-by-side comparison of status dots |

### 8.4 Save States (3 frames)

| # | Frame Name | Description |
|---|---|---|
| F12 | `Save — Loading` | Button shows spinner, "Saving..." text |
| F13 | `Save — Error` | AlertBanner (error variant) above action bar |
| F14 | `Save — Success` | Toast notification (sonner) in bottom-right |

### 8.5 Page-Level States (2 frames)

| # | Frame Name | Description |
|---|---|---|
| F15 | `Settings — Loading (skeleton)` | Full page skeleton |
| F16 | `Settings — Error` | Error state with retry button |

### 8.6 Full Loading Skeleton

The loading state uses `Skeleton` from `components-feedback-utility.md §4`:

```
SettingsPageSkeleton (max-w-2xl, mx-auto, p-4 md:p-6)
├── Skeleton (h-8 w-32, rounded-sm) — page title "Settings"
├── gap-6
└── Skeleton area
    ├── Skeleton (h-[38px] w-full, rounded-[10px]) — TabsList
    ├── gap-6
    ├── Skeleton (h-5 w-32, rounded-sm) — section heading
    ├── gap-4
    ├── Skeleton (h-4 w-20, rounded-sm) — label
    ├── Skeleton (h-[38px] w-full, rounded-[10px]) — control
    ├── gap-4
    ├── Skeleton (h-4 w-24, rounded-sm) — label
    ├── Skeleton (h-[38px] w-48, rounded-[10px]) — control
    ├── gap-6
    ├── Skeleton (h-5 w-28, rounded-sm) — section heading
    ├── gap-4
    ├── Skeleton (h-4 w-16, rounded-sm) — label
    ├── Skeleton (h-[38px] w-full, rounded-[10px]) — control
    ├── gap-6
    └── Skeleton (h-8 w-20, rounded-[10px]) — save button (right-aligned)
```

### 8.7 Error State

```
SettingsPageError (flex, flex-col, items-center, justify-center, h-full, gap-4)
├── AlertCircle (48px, muted-foreground)
├── Title: "Failed to load settings" (headline: 16px/600, foreground)
├── Description: "Check your connection and try again." (callout: 14px/400, muted-foreground)
└── Button variant="outline" size="sm" (RefreshCw icon + "Retry")
```

---

## 9. Glass Treatment Map

### 9.1 Per-Element Assignment

The Settings page uses **minimal glass** — only the TabsList. All form surfaces are solid for maximum readability.

| Element | Glass Tier | Background | Rationale |
|---|---|---|---|
| **TabsList** | ultra-thin | `white/45` + `blur(8px)` (light) / `#1A140F/50` + `blur(8px)` (dark) | Navigation chrome; matches L4 spec |
| **Form sections** | none | `transparent` (on page background) | Clean, readable, high-contrast |
| **Input / Select controls** | none | `surface-base` (solid) | Form controls always solid — per L3 spec |
| **SegmentedControl** | none | `surface-sunken` (solid) | Per L3 spec; glass=off |
| **Switch** | none | `surface-raised` (off) / `primary` (on) | Per L3 spec |
| **Badge** | none | Status variant bg (solid) | Per L2 spec |
| **Save button** | none | `primary` (solid) | Per L2 spec |
| **AlertBanner** | ultra-thin | Status bg + `blur(8px)` | Per L5 spec |
| **Status dot** | none | Status token (solid) | Solid color indicator |

### 9.2 Dark Mode Surface Separation

In dark mode, the form section content sits on the `background` (#120E0A) token directly. The TabsList glass creates enough visual separation. If future sections need grouping, use `surface-raised` (#231B14) as a solid background — never glass.

---

## 10. Responsive Behavior

### 10.1 Breakpoint Matrix

| Property | Mobile (<640px) | Desktop (≥640px) |
|---|---|---|
| Page padding | `p-4` (16px) | `md:p-6` (24px) |
| Max width | 100% (fluid) | `max-w-2xl` (672px) centered |
| TabsList | Full width | Full width within max-w-2xl |
| Form fields | Full width | Full width (single column) |
| Select controls | Full width | `max-w-[200px]` |
| SegmentedControl | Full width | `max-w-[240px]` |
| SwitchField | Label above, switch below | Label left, switch right |
| Input group (vault path) | Stack (input above, browse below) | Row (input left, browse right) |
| Save button | Full width, sticky bottom | Right-aligned, inline |
| Section gap | 24px (`space-y-6`) | 32px (`space-y-8`) |

### 10.2 Mobile Adaptations

```
Mobile SwitchField (<640px):
┌────────────────────────┐
│ Cache Enabled          │
│ Enable response        │
│ caching for faster     │
│ queries                │
│                        │
│ [====○        ] Switch │
└────────────────────────┘

Desktop SwitchField (≥640px):
┌────────────────────────────────────────┐
│ Cache Enabled                    [○==] │
│ Enable response caching for faster     │
│ queries                                │
└────────────────────────────────────────┘
```

### 10.3 Mobile Save Button

On mobile, the save button should be full width at the bottom of each tab content area. No sticky behavior needed since the page content fits within a single scroll on most devices.

---

## 11. Figma Frames Specification

### 11.1 Frame List

All frames are **1440×900** (desktop) or **375×812** (mobile) with the Liquid Crystal mesh background.

| # | Frame Name | Size | Content |
|---|---|---|---|
| 1 | `Settings / General — Default (Light)` | 1440×900 | General tab, System theme, English, light mode |
| 2 | `Settings / General — Default (Dark)` | 1440×900 | General tab, System theme, English, dark mode |
| 3 | `Settings / General — Theme Light` | 1440×900 | Light segment active |
| 4 | `Settings / General — Theme Dark` | 1440×900 | Dark segment active |
| 5 | `Settings / General — Theme System` | 1440×900 | System segment active |
| 6 | `Settings / LLM — Key Set (Light)` | 1440×900 | LLM tab, Badge=success |
| 7 | `Settings / LLM — Key Not Set (Light)` | 1440×900 | LLM tab, Badge=warning |
| 8 | `Settings / LLM — Key Set (Dark)` | 1440×900 | LLM tab, Badge=success, dark |
| 9 | `Settings / Vault — Connected (Light)` | 1440×900 | Vault tab, green dot + pulse |
| 10 | `Settings / Vault — Disconnected (Light)` | 1440×900 | Vault tab, red dot |
| 11 | `Settings / Vault — Connected (Dark)` | 1440×900 | Vault tab, green dot, dark |
| 12 | `Settings / Advanced — Default (Light)` | 1440×900 | Advanced tab, Cache=on, Log=INFO |
| 13 | `Settings / Advanced — Default (Dark)` | 1440×900 | Advanced tab, dark mode |
| 14 | `Settings / Save — Loading` | 1440×900 | Any tab, save button in loading state |
| 15 | `Settings / Save — Error` | 1440×900 | Any tab, AlertBanner (error) above action |
| 16 | `Settings / Page — Loading Skeleton` | 1440×900 | Full skeleton state |
| 17 | `Settings / Page — Error` | 1440×900 | Error state with retry |
| 18 | `Settings / Mobile — General` | 375×812 | General tab, mobile layout |
| 19 | `Settings / Mobile — LLM` | 375×812 | LLM tab, mobile layout |

### 11.2 Figma Component Instances

Each frame should use component instances from the design system:

| Figma Component | Used In |
|---|---|
| `TabsList` (4-tab variant, glass-ultra-thin) | All frames |
| `TabsTrigger` (active/inactive states) | All frames |
| `Input` (default state) | LLM (×2), Vault (×1), Advanced (×1) |
| `Select` (trigger + content open) | General (language), Advanced (log level) |
| `SegmentedControl` (3-segment) | General (theme) |
| `Switch` (on/off) | Advanced (cache) |
| `Badge` (success, warning) | LLM (API key status) |
| `Button` (default sm, outline sm disabled) | All tabs (save), Vault (browse) |
| `Skeleton` (default, text variants) | Loading frame |
| `AlertBanner` (error variant) | Save error frame |
| `Separator` | All tabs (section dividers) |

---

## 12. TSX Skeleton

### 12.1 Shared Types and Hooks

```tsx
// web/src/features/settings/settings-shared.tsx
import { Loader2, Save } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { AlertBanner } from "@/components/ui/alert-banner";
import type { AppSettings } from "@/types/api";
import { updateSettings } from "./settings-api";

// ─── Shared Mutation Hook ───
export function useSettingsMutation() {
  return useMutation({
    mutationFn: (settings: Partial<AppSettings>) => updateSettings(settings),
    onSuccess: () => {
      toast.success("Settings saved");
    },
    onError: () => {
      toast.error("Failed to save settings");
    },
  });
}

// ─── Form Field Components ───
export function SettingsSection({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-[16px] font-semibold text-foreground">{title}</h3>
        {description && (
          <p className="mt-1 text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      <div className="h-px bg-border" />
      <div className="space-y-6">{children}</div>
    </div>
  );
}

export function FormField({
  label,
  description,
  children,
  id,
}: {
  label: string;
  description?: string;
  children: React.ReactNode;
  id?: string;
}) {
  return (
    <div className="space-y-2">
      {label && (
        <label htmlFor={id} className="text-[13px] font-medium text-foreground">
          {label}
        </label>
      )}
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
      {children}
    </div>
  );
}

export function SwitchField({
  label,
  description,
  children,
  id,
}: {
  label: string;
  description?: string;
  children: React.ReactNode;
  id?: string;
}) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="flex-1 space-y-1">
        <label htmlFor={id} className="text-[13px] font-medium text-foreground">
          {label}
        </label>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
      <div className="mt-0.5">{children}</div>
    </div>
  );
}

export function SettingsActionBar({
  mutation,
  onSave,
  errorBanner,
  onDismissError,
}: {
  mutation: ReturnType<typeof useSettingsMutation>;
  onSave: () => void;
  errorBanner?: boolean;
  onDismissError?: () => void;
}) {
  return (
    <div className="pt-4 mt-2">
      {errorBanner && (
        <AlertBanner
          variant="error"
          title="Failed to save settings"
          message="Your changes were not saved. Please try again."
          dismissible
          onDismiss={onDismissError}
          action={
            <Button
              variant="ghost"
              size="xs"
              onClick={onSave}
            >
              Retry
            </Button>
          }
          className="mb-4"
        />
      )}
      <div className="flex justify-end">
        <Button
          variant="default"
          size="sm"
          onClick={onSave}
          loading={mutation.isPending}
          disabled={mutation.isPending}
        >
          <Save className="h-3.5 w-3.5" />
          Save
        </Button>
      </div>
    </div>
  );
}
```

### 12.2 General Tab

```tsx
// Settings General Tab — TSX Skeleton
import { useState } from "react";
import { SegmentedControl } from "@/components/ui/segmented-control";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AppSettings } from "@/types/api";
import {
  FormField,
  SettingsSection,
  SettingsActionBar,
  useSettingsMutation,
} from "./settings-shared";

export function GeneralTab({ settings }: { settings: AppSettings }) {
  const [theme, setTheme] = useState(settings.theme ?? "system");
  const [language, setLanguage] = useState(settings.language ?? "en");
  const mutation = useSettingsMutation();

  const handleSave = () => {
    mutation.mutate({ theme, language });
  };

  return (
    <div className="max-w-lg space-y-8">
      <SettingsSection title="Appearance">
        <FormField label="Theme" description="Choose how the interface looks">
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
        </FormField>
        <FormField
          label="Language"
          description="Set the display language for the interface"
          id="language-select"
        >
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger id="language-select" className="w-full max-w-[200px]">
              <SelectValue placeholder="Select language..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="zh">中文</SelectItem>
            </SelectContent>
          </Select>
        </FormField>
      </SettingsSection>
      <SettingsActionBar mutation={mutation} onSave={handleSave} />
    </div>
  );
}
```

### 12.3 LLM Tab

```tsx
// Settings LLM Tab — TSX Skeleton
import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import type { AppSettings } from "@/types/api";
import {
  FormField,
  SettingsSection,
  SettingsActionBar,
  useSettingsMutation,
} from "./settings-shared";

export function LLMTab({ settings }: { settings: AppSettings }) {
  const [model, setModel] = useState(settings.llm_model ?? "");
  const [apiKey, setApiKey] = useState("");
  const mutation = useSettingsMutation();

  const handleSave = () => {
    const payload: Partial<AppSettings> = { llm_model: model };
    if (apiKey) payload.api_key = apiKey;
    mutation.mutate(payload);
    setApiKey("");
  };

  return (
    <div className="max-w-lg space-y-8">
      <SettingsSection title="Language Model">
        <FormField
          label="Model"
          description="The language model used for generating responses"
          id="llm-model"
        >
          <Input
            id="llm-model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            placeholder="e.g., gpt-4o, claude-3.5-sonnet"
          />
        </FormField>
        <FormField
          label="API Key"
          description="Your API key is stored securely and never displayed"
          id="llm-api-key"
        >
          {/* Label row with badge — override label slot */}
          <div slot="label-row" className="flex items-center gap-2 -mb-1">
            <label
              htmlFor="llm-api-key"
              className="text-[13px] font-medium text-foreground"
            >
              API Key
            </label>
            <Badge variant={settings.api_key_set ? "success" : "warning"}>
              {settings.api_key_set ? "已设置" : "未设置"}
            </Badge>
          </div>
          <Input
            id="llm-api-key"
            type="password"
            placeholder="Enter new API key..."
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
        </FormField>
      </SettingsSection>
      <SettingsActionBar mutation={mutation} onSave={handleSave} />
    </div>
  );
}
```

### 12.4 Vault Tab

```tsx
// Settings Vault Tab — TSX Skeleton
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import type { AppSettings } from "@/types/api";
import {
  FormField,
  SettingsSection,
  SettingsActionBar,
  useSettingsMutation,
} from "./settings-shared";
import { getHealth } from "./settings-api";

export function VaultTab({ settings }: { settings: AppSettings }) {
  const [vaultPath, setVaultPath] = useState(settings.vault_path ?? "");
  const mutation = useSettingsMutation();

  const { data: health, isFetching } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 10000,
  });

  const connected = health?.vault_connected;

  const handleSave = () => {
    mutation.mutate({ vault_path: vaultPath });
  };

  return (
    <div className="max-w-lg space-y-8">
      <SettingsSection title="Knowledge Vault">
        <FormField
          label="Vault Path"
          description="The directory containing your markdown notes"
          id="vault-path"
        >
          <div className="flex gap-2">
            <Input
              id="vault-path"
              value={vaultPath}
              onChange={(e) => setVaultPath(e.target.value)}
              className="flex-1"
            />
            <Button variant="outline" size="sm" disabled>
              Browse
            </Button>
          </div>
        </FormField>
        <FormField
          label="Connection Status"
          description="Live status of the vault connection (refreshes every 10s)"
        >
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "h-2 w-2 rounded-full",
                connected ? "bg-status-success" : "bg-status-error",
                connected && isFetching && "animate-pulse",
              )}
              aria-label={connected ? "Connected" : "Disconnected"}
            />
            <span
              className={cn(
                "text-sm",
                connected ? "text-foreground" : "text-muted-foreground",
              )}
            >
              {connected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </FormField>
      </SettingsSection>
      <SettingsActionBar mutation={mutation} onSave={handleSave} />
    </div>
  );
}
```

### 12.5 Advanced Tab

```tsx
// Settings Advanced Tab — TSX Skeleton
import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { AppSettings } from "@/types/api";
import {
  FormField,
  SettingsSection,
  SwitchField,
  SettingsActionBar,
  useSettingsMutation,
} from "./settings-shared";

export function AdvancedTab({ settings }: { settings: AppSettings }) {
  const [apiUrl, setApiUrl] = useState(settings.api_url ?? "");
  const [cacheEnabled, setCacheEnabled] = useState(
    (settings.cache_enabled as boolean) ?? true,
  );
  const [logLevel, setLogLevel] = useState(
    (settings.log_level as string) ?? "INFO",
  );
  const mutation = useSettingsMutation();

  const handleSave = () => {
    mutation.mutate({
      api_url: apiUrl,
      cache_enabled: cacheEnabled,
      log_level: logLevel,
    });
  };

  return (
    <div className="max-w-lg space-y-8">
      <SettingsSection title="API Configuration">
        <FormField
          label="API URL"
          description="The base URL for the backend API server"
          id="api-url"
        >
          <Input
            id="api-url"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            placeholder="http://localhost:8000"
          />
        </FormField>
      </SettingsSection>

      <SettingsSection title="Runtime">
        <SwitchField
          label="Cache Enabled"
          description="Enable response caching for faster queries"
          id="cache-enabled"
        >
          <Switch
            id="cache-enabled"
            checked={cacheEnabled}
            onCheckedChange={setCacheEnabled}
          />
        </SwitchField>
        <FormField
          label="Log Level"
          description="Set the verbosity of application logs"
          id="log-level"
        >
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
        </FormField>
      </SettingsSection>

      <SettingsActionBar mutation={mutation} onSave={handleSave} />
    </div>
  );
}
```

### 12.6 SettingsPage Root

```tsx
// SettingsPage Root — TSX Skeleton
import { AlertCircle } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { getSettings } from "./settings-api";
import { GeneralTab } from "./general-tab";
import { LLMTab } from "./llm-tab";
import { VaultTab } from "./vault-tab";
import { AdvancedTab } from "./advanced-tab";

function SettingsPageSkeleton() {
  return (
    <div className="flex flex-col gap-6 p-4 md:p-6 max-w-2xl mx-auto">
      {/* Page title */}
      <Skeleton className="h-8 w-32 rounded-sm" />

      {/* TabsList */}
      <Skeleton className="h-[38px] w-full rounded-[10px]" />

      {/* Section heading */}
      <Skeleton className="h-5 w-32 rounded-sm mt-2" />

      {/* Field 1: label + control */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-16 rounded-sm" />
        <Skeleton className="h-[38px] w-full max-w-[240px] rounded-[10px]" />
      </div>

      {/* Field 2: label + control */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-20 rounded-sm" />
        <Skeleton className="h-[38px] w-full max-w-[200px] rounded-[10px]" />
      </div>

      {/* Section 2 heading */}
      <Skeleton className="h-5 w-28 rounded-sm mt-4" />

      {/* Field 3: label + control */}
      <div className="space-y-2">
        <Skeleton className="h-4 w-24 rounded-sm" />
        <Skeleton className="h-[38px] w-full rounded-[10px]" />
      </div>

      {/* Save button */}
      <div className="flex justify-end mt-4">
        <Skeleton className="h-8 w-20 rounded-[10px]" />
      </div>
    </div>
  );
}

function SettingsPageError({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4">
      <AlertCircle className="h-12 w-12 text-muted-foreground" />
      <h2 className="text-[16px] font-semibold text-foreground">
        Failed to load settings
      </h2>
      <p className="text-sm text-muted-foreground">
        Check your connection and try again.
      </p>
      <Button variant="outline" size="sm" onClick={onRetry}>
        Retry
      </Button>
    </div>
  );
}

export function SettingsPage() {
  const {
    data: settings,
    isLoading,
    isError,
    refetch,
  } = useQuery({
    queryKey: ["settings"],
    queryFn: getSettings,
  });

  if (isLoading) {
    return <SettingsPageSkeleton />;
  }

  if (isError || !settings) {
    return <SettingsPageError onRetry={() => refetch()} />;
  }

  return (
    <div className="flex flex-col gap-6 p-4 md:p-6 max-w-2xl mx-auto">
      <h1 className="text-[28px] font-semibold text-foreground">Settings</h1>

      <Tabs defaultValue="general" className="flex-1">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="llm">LLM</TabsTrigger>
          <TabsTrigger value="vault">Vault</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="general">
          <GeneralTab settings={settings} />
        </TabsContent>

        <TabsContent value="llm">
          <LLMTab settings={settings} />
        </TabsContent>

        <TabsContent value="vault">
          <VaultTab settings={settings} />
        </TabsContent>

        <TabsContent value="advanced">
          <AdvancedTab settings={settings} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## 13. Native Element Migration Checklist

### 13.1 Full Migration Table

| # | File:Line | Current Code | Replacement | New Component |
|---|---|---|---|---|
| 1 | `settings-page.tsx:38-51` | 3× `<input type="radio">` for theme | `SegmentedControl` with Light/Dark/System | `components-form-inputs.md §6` |
| 2 | `settings-page.tsx:58-66` | `<select>` for language | `Select` with English/中文 | `components-form-inputs.md §5` |
| 3 | `settings-page.tsx:238-248` | `<select>` for log level | `Select` with DEBUG/INFO/WARNING/ERROR | `components-form-inputs.md §5` |
| 4 | `settings-page.tsx:224-228` | `<Checkbox>` for cache toggle | `Switch` (boolean toggle) | `components-form-inputs.md §7` |
| 5 | `settings-page.tsx:108-116` | Hardcoded `bg-green-100 text-green-700` badge | `Badge variant="success"` | `components-button-badge.md §5` |
| 6 | `settings-page.tsx:108-116` | Hardcoded `bg-red-100 text-red-700` badge | `Badge variant="warning"` | `components-button-badge.md §5` |
| 7 | `settings-page.tsx:174` | Hardcoded `bg-green-500` dot | `bg-status-success` token | `tokens.md §1.5` |
| 8 | `settings-page.tsx:174` | Hardcoded `bg-red-500` dot | `bg-status-error` token | `tokens.md §1.5` |
| 9 | `settings-page.tsx:294` | `text-2xl font-bold` page title | `text-[28px] font-semibold` (title-1) | Typography token |
| 10 | `settings-page.tsx:36` | `text-sm font-medium` label | `text-[13px] font-medium` (subhead) | Typography token |
| 11 | `settings-page.tsx:271-277` | Centered spinner loading state | Full page skeleton | `components-feedback-utility.md §4` |
| 12 | `settings-page.tsx:279-290` | Inline error with retry | `SettingsPageError` component | This spec §8.7 |
| 13 | `settings-page.tsx:293` | `gap-4` page spacing | `gap-6` page spacing | Layout token |
| 14 | `settings-page.tsx:34` | `max-w-lg` form width | `max-w-lg` (keep) | Layout consistency |

### 13.2 Migration Code — Before / After

#### Migration #1: Theme — Radio → SegmentedControl

**Before** (`settings-page.tsx:36-52`):
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
<FormField label="Theme" description="Choose how the interface looks">
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
</FormField>
```

#### Migration #2: Language — Native Select → Select Component

**Before** (`settings-page.tsx:54-67`):
```tsx
<div className="space-y-2">
  <label htmlFor="language-select" className="text-sm font-medium">
    Language
  </label>
  <select
    id="language-select"
    value={language}
    onChange={(e) => setLanguage(e.target.value)}
    className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm"
  >
    <option value="en">English</option>
    <option value="zh">中文</option>
  </select>
</div>
```

**After:**
```tsx
<FormField
  label="Language"
  description="Set the display language for the interface"
  id="language-select"
>
  <Select value={language} onValueChange={setLanguage}>
    <SelectTrigger id="language-select" className="w-full max-w-[200px]">
      <SelectValue placeholder="Select language..." />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="en">English</SelectItem>
      <SelectItem value="zh">中文</SelectItem>
    </SelectContent>
  </Select>
</FormField>
```

#### Migration #4: Cache — Checkbox → Switch

**Before** (`settings-page.tsx:223-232`):
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
<SwitchField
  label="Cache Enabled"
  description="Enable response caching for faster queries"
  id="cache-enabled"
>
  <Switch
    id="cache-enabled"
    checked={cacheEnabled}
    onCheckedChange={setCacheEnabled}
  />
</SwitchField>
```

#### Migration #5-6: API Key Badge

**Before** (`settings-page.tsx:108-116`):
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

#### Migration #7-8: Connection Status Dot

**Before** (`settings-page.tsx:172-175`):
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
    "h-2 w-2 rounded-full",
    connected ? "bg-status-success" : "bg-status-error",
    connected && isFetching && "animate-pulse",
  )}
  aria-label={connected ? "Connected" : "Disconnected"}
/>
```

---

## Appendix A: Accessibility Checklist

| Check | General | LLM | Vault | Advanced |
|---|---|---|---|---|
| Label association | `aria-label` on SegmentedControl ✅ | `htmlFor` on label → `id` on Input ✅ | `htmlFor` on label → `id` on Input ✅ | `htmlFor` on label → `id` on Input/Switch ✅ |
| Keyboard — SegmentedControl | Arrow keys, Home/End ✅ | — | — | — |
| Keyboard — Select | — | — | — | Arrow keys, Enter ✅ |
| Keyboard — Switch | — | — | — | Space toggle ✅ |
| Focus indicator | 2px ring on SegmentedControl ✅ | 2px ring on Input ✅ | 2px ring on Input ✅ | 2px ring on all controls ✅ |
| Error announcement | `toast.error` via sonner ✅ | Same ✅ | Same ✅ | Same ✅ |
| Status dot | — | — | `aria-label` on dot ✅ | — |
| Badge | — | Semantic text "已设置"/"未设置" ✅ | — | — |
| Loading state | `aria-busy` on button ✅ | Same ✅ | Same ✅ | Same ✅ |
| Skeleton | `aria-hidden` on all skeletons ✅ | — | — | — |
| Tab navigation | Arrow keys between tabs ✅ | Same ✅ | Same ✅ | Same ✅ |
| `prefers-reduced-motion` | Pulse disabled on status dot ✅ | Spinner disabled on save ✅ | Pulse disabled ✅ | Same ✅ |

---

## Appendix B: Token Cross-Reference

| CSS Custom Property | Tailwind Class | Used In |
|---|---|---|
| `--color-foreground` | `text-foreground` | Page title, section headings, labels, active tab text, connected status |
| `--color-muted-foreground` | `text-muted-foreground` | Descriptions, inactive tab text, disconnected status, section descriptions |
| `--color-primary` | `bg-primary` | Save button (default variant), Switch (on), SegmentedControl active text |
| `--color-primary-foreground` | `text-primary-foreground` | Save button text |
| `--color-border` | `bg-border`, `border-border` | Separators, Input border, Select trigger border |
| `--color-ring` | `ring-ring` | Focus ring on all form controls |
| `--color-surface-base` | `bg-surface-base` | Input bg, Select trigger bg, TabsTrigger active bg, SegmentedControl active pill |
| `--color-surface-sunken` | `bg-surface-sunken` | SegmentedControl container bg |
| `--color-surface-raised` | `bg-surface-raised` | Switch track (off) |
| `--color-status-success` | `bg-status-success` | Vault connected dot |
| `--color-status-success-bg` | `bg-status-success-bg` | Badge success bg |
| `--color-status-warning` | `text-status-warning` | Badge warning text |
| `--color-status-warning-bg` | `bg-status-warning-bg` | Badge warning bg |
| `--color-status-error` | `bg-status-error` | Vault disconnected dot |
| `--color-status-error-bg` | `bg-status-error-bg` | AlertBanner error bg |
| `--color-accent` | `bg-accent` | TabsTrigger hover, SegmentedControl inactive hover |
| `--color-destructive` | `text-destructive` | Inline validation error text |
| `--color-muted` | `bg-muted` | Skeleton (light) |
| `--color-background` | `ring-offset-background` | Focus ring offset |

---

## Appendix C: Implementation Checklist

### Phase 1: Prerequisites (from companion specs)
- [ ] Add `--color-status-*-bg` tokens to `globals.css` (from `components-button-badge.md §5.1`)
- [ ] Add `--color-surface-base`, `--color-surface-raised`, `--color-surface-sunken` to `globals.css` (from `components-form-inputs.md Appendix B`)
- [ ] Implement `Select` component (`components-form-inputs.md §5`)
- [ ] Implement `SegmentedControl` component (`components-form-inputs.md §6`)
- [ ] Implement `Switch` component (`components-form-inputs.md §7`)
- [ ] Update `Badge` with `success`, `warning`, `error`, `info` variants (`components-button-badge.md §5`)
- [ ] Update `Button` with `loading` prop (`components-button-badge.md §4`)
- [ ] Implement `AlertBanner` component (`components-feedback-utility.md §6`)
- [ ] Update `Skeleton` with `variant` prop (`components-feedback-utility.md §4`)
- [ ] Update `Tabs` with glass TabsList (`components-surface-overlay.md §8`)

### Phase 2: Shared Settings Utilities
- [ ] Create `settings-shared.tsx` with `SettingsSection`, `FormField`, `SwitchField`, `SettingsActionBar`
- [ ] Extract `useSettingsMutation` hook into shared module

### Phase 3: Tab Refactoring
- [ ] Refactor `GeneralTab` — replace radio with `SegmentedControl`, replace native `<select>` with `Select`
- [ ] Refactor `LLMTab` — replace hardcoded badge with `Badge` component, add description text
- [ ] Refactor `VaultTab` — replace hardcoded dot with tokenized `bg-status-*`, add `isFetching` pulse, add description text
- [ ] Refactor `AdvancedTab` — replace `<Checkbox>` with `Switch`, replace native `<select>` with `Select`

### Phase 4: Page-Level States
- [ ] Implement `SettingsPageSkeleton` component with structured Skeleton placeholders
- [ ] Implement `SettingsPageError` component with `AlertCircle` icon and retry button
- [ ] Update page title from `text-2xl font-bold` to `text-[28px] font-semibold`
- [ ] Update page spacing from `gap-4` to `gap-6`
- [ ] Add `max-w-2xl mx-auto` to page container

### Phase 5: Save Action Pattern
- [ ] Add `loading` prop usage on save Button
- [ ] Add optional inline `AlertBanner` for save errors
- [ ] Wire `onDismissError` to clear error banner state

### Phase 6: Visual QA
- [ ] Verify all 4 tabs render correctly in light mode
- [ ] Verify all 4 tabs render correctly in dark mode
- [ ] Verify SegmentedControl spring animation (theme selector)
- [ ] Verify Select dropdown glass-tier-thin background
- [ ] Verify Switch thumb slide animation
- [ ] Verify Badge success/warning color in both modes
- [ ] Verify connection status dot pulse (connected + fetching)
- [ ] Verify connection status dot static (disconnected)
- [ ] Verify save button loading state (spinner + disabled)
- [ ] Verify page skeleton loading state
- [ ] Verify page error state with retry
- [ ] Verify focus ring visibility on all controls in both modes
- [ ] Verify keyboard navigation: Tab between controls, Arrow keys in SegmentedControl and Select, Space on Switch
- [ ] Verify mobile responsive layout (<640px)
- [ ] Verify `prefers-reduced-motion` disables pulse and spinner animations

---

*Document version: 1.0.0 · Last updated: 2026-04-11 · System: Liquid Crystal — Warm Amber*
