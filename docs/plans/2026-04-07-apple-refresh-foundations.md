# Apple Refresh Foundations

**Date:** 2026-04-07
**Scope:** Extract a reusable Apple-inspired design language from the existing `Apple Refresh` Figma concept and define the shared foundations for all frontend pages.

---

## 1. Goal

Turn the current concept screens into a consistent system that can be reused across:

- Chat
- Query
- Record
- Explore
- Skills
- Settings

The design should feel:

- **Quiet**: less chrome, softer contrast, more whitespace discipline
- **Layered**: structure comes from translucent surfaces and depth, not heavy borders
- **Focused**: the content panel is always the visual anchor

---

## 2. Core Visual Principles

### 2.1 Layout Mood

- Use floating top-level containers instead of edge-to-edge panels
- Keep page backgrounds atmospheric and light, never flat white
- Treat every major region as a surface with a different visual weight

### 2.2 Apple-Inspired, Not Skeuomorphic

- Use restrained translucency, not exaggerated blur
- Use subtle highlight and shadow pairs, not obvious neumorphism
- Keep controls dense and clean, with calm spacing and strong typography hierarchy

### 2.3 Hierarchy Model

The entire app should use four visual layers only:

1. `Layer 0 / Ambient Background`
2. `Layer 1 / Navigation Glass`
3. `Layer 2 / Content Surface`
4. `Layer 3 / Active Control`

Do not invent extra layer styles per page.

---

## 3. Token Foundations

These tokens should become the shared source for Figma variables and frontend CSS variables.

### 3.1 Color Roles

Use semantic names first. Primitive values can be finalized in Figma later.

#### Background

- `color/bg/canvas`
- `color/bg/ambient-a`
- `color/bg/ambient-b`
- `color/bg/ambient-c`

#### Surface

- `color/surface/nav`
- `color/surface/panel`
- `color/surface/card`
- `color/surface/active`
- `color/surface/elevated`

#### Border

- `color/border/subtle`
- `color/border/default`
- `color/border/strong`

#### Text

- `color/text/primary`
- `color/text/secondary`
- `color/text/tertiary`
- `color/text/inverse`

#### Accent

- `color/accent/blue`
- `color/accent/green`
- `color/accent/orange`
- `color/accent/purple`

#### Status

- `color/status/success`
- `color/status/warning`
- `color/status/error`
- `color/status/info`

### 3.2 Opacity Guidance

For glass surfaces, keep opacity disciplined:

- Nav glass: `72-82%`
- Standard panel glass: `84-90%`
- Active chip or segmented thumb: `92-96%`

Avoid fully opaque white unless a component must become the visual focus.

### 3.3 Radius Scale

Use a fixed radius scale:

- `radius/12`
- `radius/16`
- `radius/20`
- `radius/24`
- `radius/full`

Usage:

- Inputs and segmented controls: `radius/16`
- Secondary cards: `radius/20`
- Main panels and top bars: `radius/24`
- Pills and status badges: `radius/full`

### 3.4 Spacing Scale

Keep spacing compact and consistent:

- `spacing/4`
- `spacing/8`
- `spacing/12`
- `spacing/16`
- `spacing/20`
- `spacing/24`
- `spacing/32`
- `spacing/40`

Usage:

- Internal micro spacing: `8-12`
- Component padding: `16-20`
- Major panel gutters: `24-32`

### 3.5 Shadow Scale

Only three shadow tokens are needed:

- `shadow/soft`
- `shadow/float`
- `shadow/focus`

Rules:

- `shadow/soft` for cards and inputs
- `shadow/float` for nav containers and large surfaces
- `shadow/focus` for active surfaces only

Shadows must be broad and low-contrast. Never use sharp black drop shadows.

---

## 4. Typography System

The current frontend uses Geist locally. Until a stronger type pairing is introduced, foundations should stay compatible with Geist.

### 4.1 Type Roles

- `type/eyebrow`
- `type/title/lg`
- `type/title/md`
- `type/title/sm`
- `type/body/lg`
- `type/body/md`
- `type/body/sm`
- `type/label/md`
- `type/label/sm`
- `type/meta`

### 4.2 Usage

- Eyebrow: uppercase, spaced, low emphasis
- Page titles: compact and crisp, not oversized
- Body copy: readable, editorial, slightly relaxed line height
- Labels: short operational text for controls and cards
- Meta: timestamps, statuses, helper lines

### 4.3 Typography Rules

- Prefer fewer sizes with stronger weight contrast
- Avoid mixing multiple display treatments on one page
- Every panel should have one dominant text anchor only

---

## 5. Shared Components

These components should define the language of the app before more screens are designed.

### 5.1 Top Bar

**Role**

Global control surface with brand, page title, app state, and quick actions.

**Spec**

- Height: `64-68`
- Radius: `24`
- Surface: `color/surface/nav`
- Border: `color/border/subtle`
- Shadow: `shadow/float`

**Behavior**

- Floats with margin from viewport edges
- Never becomes a solid app bar
- Right-side controls use icon buttons and compact status pills

### 5.2 Sidebar

**Role**

Navigation tray, not a dark rail.

**Spec**

- Main nav width: `168-184`
- Chat left rail: `280-320`
- Chat right rail: `360-408`
- Radius: `24`
- Surface: `color/surface/nav` or `color/surface/panel`

**Behavior**

- Active item uses a soft selected pill
- Inactive items remain low contrast
- Icons are monochrome and slightly softened

### 5.3 Card

Create three card types:

- `Card / Primary`
- `Card / Secondary`
- `Card / Utility`

**Primary**

- Main work panels
- Strongest surface weight

**Secondary**

- Result cards, tool cards, detail cards
- Slightly lighter surface

**Utility**

- Stats blocks, tags, secondary grouped information
- Smaller padding and lower prominence

### 5.4 Segmented Control

Use for:

- `Quick / Editor`
- `Results / Q&A`
- Any small-mode switch

**Spec**

- Height: `32-36`
- Radius: `full` or `16`
- Container surface: `color/surface/card`
- Active thumb: `color/surface/active`
- Shadow on active thumb only

**Rule**

This should feel like iOS segmented control, not classic tabs.

### 5.5 Input Family

Define:

- `Input / Search`
- `Input / Single Line`
- `Input / Composer`

**Shared traits**

- Radius: `16`
- Border: subtle
- Focus: slight glow and contrast lift, not a bright outline
- Surface: glass panel with stronger legibility than surrounding cards

**Sizes**

- Search: `40-44`
- Single line: `44`
- Composer: `44-52`

### 5.6 Button Family

Minimal set:

- `Button / Primary`
- `Button / Secondary`
- `Button / Ghost`
- `Button / Pill`
- `Button / Icon`

Rules:

- Primary buttons should remain compact and restrained
- Secondary buttons should look integrated into glass UI
- Ghost buttons should be used for panel controls and utility actions

---

## 6. Glassmorphism Rules

This project should use **controlled glass**, not decorative glass.

### 6.1 What Creates the Effect

Every glass surface should combine:

- Light translucent fill
- Soft background blur
- Low-contrast 1px border
- Slight top highlight
- Broad shallow shadow

### 6.2 What to Avoid

- Heavy frosted blur
- Strong white bloom
- Multiple nested glass boxes inside each other
- Large saturated gradients inside component surfaces

### 6.3 Page Background

Each page should share one ambient background recipe:

- soft neutral base
- 2-3 oversized blurred color or light blobs
- no hard patterns
- no dark mode bias by default

---

## 7. Page-Level Structure Rules

### 7.1 Chat

- Three-panel workspace remains valid
- Center panel must remain the strongest surface
- Side rails must feel lighter and quieter than the conversation area

### 7.2 Query

- Search header and results/answer split should share the same card language
- Search should feel editorial, not dashboard-like

### 7.3 Record

- Editor stays primary
- Metadata and AI assist become calm side decks
- Segmented control is the key mode switch

### 7.4 Explore

- Graph canvas should become a large glass stage
- Detail drawer should reuse side deck language from Chat and Record

### 7.5 Skills

- Skill cards should reuse `Card / Secondary`
- Search/filter area should reuse `Input / Search`
- Grid should feel like a product gallery, not an admin table

### 7.6 Settings

- Settings should become grouped stacked panels
- Each section should feel like a preference card, not a form dump

---

## 8. Figma Foundations Board Structure

Before designing more screens, add a dedicated foundations section to the `Apple Refresh` file.

Recommended frames:

- `Foundations / Overview`
- `Foundations / Color`
- `Foundations / Type`
- `Foundations / Radius + Shadow`
- `Foundations / Top Bar`
- `Foundations / Sidebar`
- `Foundations / Card`
- `Foundations / Segmented Control`
- `Foundations / Input`

Each frame should show:

- token names
- one canonical example
- dos and don'ts only if needed

---

## 9. Frontend Mapping

These foundations map directly to current frontend structure:

- Layout shell: `web/components/layout/*`
- Chat workspace: `web/components/chat/*`
- Query controls: `web/components/query/*`
- Record editor shell: `web/components/record/*`
- Shared controls: `web/components/ui/*`
- Global theme: `web/app/globals.css`

Implementation order after Figma foundations are approved:

1. global tokens in `globals.css`
2. top bar and sidebar shell
3. shared card/input/button/segmented components
4. page-specific layout refinements

---

## 10. Immediate Next Step

The next design action should be:

1. Build a `Foundations` area inside `Apple Refresh`
2. Freeze the shared component recipes above
3. Use those recipes to design `Explore`
4. Rework `Skills`
5. Rework `Settings`

Do not continue drawing new pages until the shared foundations are visually locked.
