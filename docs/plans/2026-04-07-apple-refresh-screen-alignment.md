# Apple Refresh Screen Alignment

**Date:** 2026-04-07
**Scope:** Align the existing `Chat`, `Query`, and `Record` concept screens to the shared Apple Refresh foundations and freeze their common components.

---

## 1. Goal

The three existing screens already point in the right direction, but they still behave like separate mockups.

This pass standardizes them so they feel like one system:

- same shell
- same surface hierarchy
- same interaction controls
- same panel logic

The target is not to redraw everything. The target is to remove inconsistencies.

---

## 2. Shared Shell

All three screens should use the same outer structure.

### 2.1 Global Frame

- Canvas width remains `1440`
- Outer safe margin stays `56` horizontally
- Use the same ambient background recipe across all three screens
- Keep the large blurred light forms in the same visual family

### 2.2 Top Bar

Use one canonical top bar component across all three screens.

**Structure**

- Brand capsule on the left
- Page title in the center-left
- Status pill on the right
- Optional utility icon slot on the far right

**Rules**

- Height must stay consistent
- Corner radius must stay consistent
- Right status pill must always use the same size and weight
- Brand lockup must not shift style between pages

### 2.3 Panel Language

All large panels should use:

- same radius
- same border treatment
- same shadow family
- same glass opacity family

Differences should come from size and content, not different styling recipes.

---

## 3. Chat Screen Changes

### 3.1 Keep

- Three-panel layout
- Large center conversation surface
- Left source rail
- Right studio rail

### 3.2 Change

#### Top Bar

- Increase consistency with Query and Record top bars
- Match left brand capsule size exactly
- Match right status pill scale exactly

#### Left Sources Rail

- Turn search row into the standard shared search input
- Convert source items into one shared `Card / List Item` component
- Normalize spacing between title, meta line, and item blocks
- Make the rail slightly lighter than the center conversation panel

#### Center Conversation Panel

- Keep this as the strongest surface on the page
- Hero message block should become a reusable `Empty State / Conversation` module
- Suggestion actions should become shared pill buttons, not page-specific primitives
- Bottom composer should become the standard `Input / Composer`

#### Right Studio Rail

- Convert tool blocks into shared `Card / Utility Tool`
- Make all tool blocks equal height
- Use one shared icon tile style
- Keep rail quieter than center panel by reducing visual weight

### 3.3 Chat-Specific Outcome

After revision, Chat should establish the main app grammar:

- shell
- side deck behavior
- content-first hierarchy
- action pills

It becomes the reference page for all multi-panel surfaces.

---

## 4. Query Screen Changes

### 4.1 Keep

- Search-first flow
- Results and answer split
- Mode toggle in the header zone

### 4.2 Change

#### Top Bar

- Reuse the exact same top bar component from Chat
- Only change title and status label

#### Intro Search Header

- Convert search field into the shared `Input / Search`
- Convert results/Q&A toggle into the shared segmented control
- Keep intro copy, but align spacing and text style with the foundations doc

#### Results Column

- Convert result cards into shared `Card / Secondary / Search Result`
- Standardize result card anatomy:
  - title
  - snippet
  - confidence pill
  - hover or selected affordance

#### Answer Column

- Turn answer body into shared `Card / Primary / Reading Surface`
- Convert source badges and action pills into the same shared chip family used by Chat
- Follow-up box becomes the same input family as the composer, but in a read-and-ask format

### 4.3 Query-Specific Outcome

After revision, Query should feel like:

- a reading product
- not a dashboard
- not a search admin tool

Its unique role is editorial scanning plus answer review, but it should still inherit the same shell and controls.

---

## 5. Record Screen Changes

### 5.1 Keep

- Dual-mode capture structure
- Main editor surface
- Metadata side panel
- AI assist side panel

### 5.2 Change

#### Top Bar

- Reuse the exact same shared top bar
- Only update title and right status state

#### Capture Mode Toggle

- Replace page-specific toggle styling with the shared segmented control
- Match Query toggle geometry and Chat action weight

#### Main Editor Surface

- Convert editor wrapper into shared `Card / Primary / Work Surface`
- Keep the editor as the strongest panel on the page
- Save button should use the shared primary button
- Helper text should use shared meta text style

#### Metadata Panel

- Convert into shared `Card / Secondary / Detail Section`
- Form rows should use the shared single-line input or select container shape
- Spacing between labels and fields must match across all rows

#### AI Assist Panel

- Convert into shared `Card / Secondary / Assistant Section`
- Use the same action button family as Chat
- Keep this panel visually quieter than metadata and editor

### 5.3 Record-Specific Outcome

After revision, Record should feel like the app’s writing studio:

- editor-first
- calm side assistance
- progressive structure

It should not introduce a new visual system of its own.

---

## 6. Shared Components To Freeze

These components should be considered locked and reused across all three screens.

### 6.1 Shell Components

- `Top Bar / Global`
- `Brand Capsule`
- `Status Pill`
- `Page Shell / Ambient Background`
- `Panel / Primary`
- `Panel / Secondary`
- `Panel / Side Deck`

### 6.2 Navigation and Switching

- `Sidebar Item / Default`
- `Sidebar Item / Active`
- `Segmented Control / 2 Items`
- `Segmented Control / 3 Items`

### 6.3 Inputs

- `Input / Search`
- `Input / Single Line`
- `Input / Composer`
- `Input / Select Shell`

### 6.4 Cards

- `Card / Search Result`
- `Card / Source Item`
- `Card / Tool Item`
- `Card / Detail Section`
- `Card / Assistant Section`
- `Card / Reading Surface`
- `Card / Work Surface`

### 6.5 Buttons and Chips

- `Button / Primary`
- `Button / Secondary`
- `Button / Ghost`
- `Button / Icon`
- `Chip / Status`
- `Chip / Match Score`
- `Chip / Action`

### 6.6 Empty and Utility States

- `Empty State / Conversation`
- `Empty State / Search`
- `Stat Block / Compact`
- `Meta Row / Label + Value`

---

## 7. Component Ownership Matrix

This matrix defines where each shared component is first proven and then reused.

| Component | Primary Source Screen | Reused In |
|----------|------------------------|-----------|
| `Top Bar / Global` | Chat | Query, Record |
| `Status Pill` | Chat | Query, Record |
| `Segmented Control` | Query + Record | both, later Settings |
| `Input / Search` | Query | Chat Sources, Skills, Explore |
| `Input / Composer` | Chat | Query follow-up, future assistants |
| `Panel / Side Deck` | Chat | Record, Explore |
| `Card / Search Result` | Query | future content lists |
| `Card / Source Item` | Chat | Explore lists, future notes panels |
| `Card / Tool Item` | Chat | Skills |
| `Card / Detail Section` | Record | Settings, Explore details |
| `Card / Assistant Section` | Record | Chat Studio, future AI panels |
| `Button / Primary` | Record | all pages |
| `Chip / Action` | Chat | Query, Record |

---

## 8. Suggested Figma Board Organization

To keep the file maintainable, split the work into three areas inside the same file:

### Board 1: `Shared Components`

Contains frozen primitives and reusable patterns:

- top bar
- status pill
- sidebar item
- segmented control
- input family
- button family
- chip family
- card family

### Board 2: `Screen Alignment`

Contains the three revised page frames:

- Chat Screen v2
- Query Screen v2
- Record Screen v2

### Board 3: `Usage Mapping`

Contains a visual matrix showing:

- which components are shared
- which are screen-specific
- which screen acts as the reference source

This board is lightweight documentation, not a polished marketing frame.

---

## 9. Execution Order

To avoid visual drift, revise in this order:

1. Freeze shared top bar
2. Freeze shared card and panel styles
3. Freeze segmented control and input family
4. Update Chat using only frozen shared pieces
5. Update Query using the same pieces
6. Update Record using the same pieces
7. Build the usage mapping board

If a screen needs a new primitive while being revised, stop and add it to `Shared Components` first.

---

## 10. Definition of Done

This alignment pass is complete when:

- all three screens share the same top bar and shell language
- all major surfaces use the same panel recipe
- all mode switches use the same segmented control
- all search and composer fields belong to one input family
- repeated blocks are no longer redrawn independently
- the shared component matrix is visible in the Figma file

At that point, `Explore`, `Skills`, and `Settings` can be designed without inventing new UI grammar.
