# Markwritter Frontend Greenfield Rewrite Plan

> Complete frontend rewrite plan for Markwritter, researched against 2026 ecosystem standards.
> Date: April 9, 2026 | Status: Planning

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Current State Assessment](#2-current-state-assessment)
3. [New Tech Stack](#3-new-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Architecture Decisions](#5-architecture-decisions)
6. [Figma Integration Plan](#6-figma-integration-plan)
7. [Migration Strategy](#7-migration-strategy)
8. [Subagent Workflow](#8-subagent-workflow)
9. [Implementation Phases](#9-implementation-phases)
10. [Risk Register](#10-risk-register)

---

## 1. Executive Summary

Markwritter is an AI-native knowledge management tool (Obsidian + memU + AI Agent) with three core modules: Query, Record, and Explore. The current frontend runs on **Next.js 15 + React 19 + Tailwind CSS v4 + Radix UI + Zustand v5** — already a solid stack. However, this is a **complete greenfield rewrite**, not a refactor. The goal is to build a new frontend from scratch using the latest 2026 best practices, correct architectural debt, and establish a Figma-first development workflow.

**Key decisions:**

- Upgrade to **Next.js 16.2** with Turbopack, Cache Components, `proxy.ts`, and React Compiler
- Adopt **Tailwind CSS v4.2** CSS-first configuration (eliminate `tailwind.config.ts`)
- Use **shadcn/ui** with New York style as the component foundation
- Implement **Figma-first workflow** via MCP Server + Code Connect
- No legacy code is carried over — every component is rewritten fresh

---

## 2. Current State Assessment

### 2.1 Current Tech Stack

| Layer | Current | Version |
|-------|---------|---------|
| Framework | Next.js | 15.2 |
| React | React + ReactDOM | 19.0 |
| Styling | Tailwind CSS | 4.0 |
| Components | Radix UI | 1.4.3 |
| State | Zustand | 5.0.12 |
| Forms | React Hook Form + Zod | 7.54 / 3.24 |
| Testing | Vitest + Playwright | 3.0.9 / 1.58 |
| Build | webpack (Next.js default) | via Next.js 15 |
| Config | `tailwind.config.ts` + `next.config.mjs` | JS config files |

### 2.2 Current Project Structure

```
web/
├── app/                    # App Router pages
│   ├── chat/
│   ├── explore/
│   ├── query/
│   ├── record/
│   ├── settings/
│   ├── skills/
│   └── logs/
├── components/
│   ├── chat/               # Chat components (14 files)
│   ├── editor/             # Markdown editor + AI assist
│   ├── explore/            # Knowledge graph
│   ├── layout/             # Sidebar, header, drawer
│   ├── query/              # Search + results
│   ├── record/             # Note capture
│   ├── settings/           # Settings panel
│   ├── skills/             # Skill cards/list/executor
│   └── ui/                 # Base UI (input only)
├── hooks/                  # Custom hooks
├── lib/                    # API, stores, utilities (30 files)
├── e2e/                    # Playwright E2E tests
└── test/                   # Test utilities
```

### 2.3 Architectural Issues to Address in Rewrite

1. **Flat store architecture** — 7+ separate Zustand stores (`store.ts`, `query-store.ts`, `record-store.ts`, `explore-store.ts`, `settings-store.ts`, `sources-store.ts`, `ui-store.ts`) with no clear domain boundaries
2. **No RSC utilization** — components are predominantly client components; server component boundaries not leveraged
3. **Tailwind v4 not fully adopted** — still uses `tailwind.config.ts` (v3 pattern) instead of CSS-first configuration
4. **Minimal shadcn/ui adoption** — only `input.tsx` in `components/ui/`, rest is hand-built Radix
5. **No design token pipeline** — CSS variables in `globals.css` are disconnected from Figma
6. **No Server Actions** — all API calls go through `lib/*-api.ts` client-side fetch wrappers
7. **No caching strategy** — no `"use cache"`, no revalidation, no ISR
8. **Webpack bundler** — not using Turbopack (only available in Next.js 16+)
9. **ESLint config is legacy** — using `.eslintrc.json` instead of flat config
10. **No Storybook** — components have no visual documentation or isolated development

---

## 3. New Tech Stack

### 3.1 Core Stack

| Layer | Tool | Version | Justification |
|-------|------|---------|---------------|
| **Framework** | Next.js (App Router) | 16.2 | Turbopack default, Cache Components, React Compiler, `proxy.ts`, async APIs. Latest stable with all 2026 features. |
| **React** | React + ReactDOM | 19.2 | `<Activity>`, `useEffectEvent()`, View Transitions, `cacheSignal()`, React Compiler support. |
| **Language** | TypeScript | 5.x | `satisfies`, `const` type params, isolated declarations, `using` keyword. |
| **Runtime** | Node.js | 22.x LTS | Required by Next.js 16 (20.9+ minimum). 22.x LTS for stability. |
| **Package Manager** | pnpm | 10.x | Fast, strict dependency hoisting, workspace support, industry standard for monorepos. |
| **Bundler** | Turbopack | (built into Next.js 16) | Default in Next.js 16. 2-5x faster builds, 10x faster Fast Refresh. No config needed. |

### 3.2 UI & Styling

| Layer | Tool | Version | Justification |
|-------|------|---------|---------------|
| **Styling** | Tailwind CSS | 4.2 | CSS-first config (no `tailwind.config.ts`), Oxide engine (Rust), auto content detection, dynamic utilities, P3 colors. |
| **Components** | shadcn/ui | latest | 112k stars, AI-ready with MCP Server, copy-paste ownership, New York style, Radix primitives underneath. |
| **Primitives** | Radix UI | latest | Underlying shadcn/ui primitives. Accessible, unstyled, composable. |
| **Icons** | Lucide React | latest | Already in use, consistent with shadcn/ui, tree-shakeable. |
| **Animations** | tailwindcss-animate + View Transitions | latest | CSS-based animations, React 19 View Transitions API for page transitions. |

### 3.3 State Management

| Layer | Tool | Version | Justification |
|-------|------|---------|---------------|
| **Server State** | TanStack Query | 5.97+ | Purpose-built for async server state. Caching, deduplication, background refetch, optimistic updates. Replaces manual SSE + fetch patterns. |
| **Client State** | Zustand | 5.x | Minimal API, excellent TypeScript support. Keep only for true client-only state (UI panels, preferences). |
| **URL State** | nuqs | latest | Type-safe URL search params for Next.js App Router. Shareable, bookmarkable state. |
| **Form State** | React Hook Form + Zod | 7.x + 4.x | Proven combo. Zod v4 is a major upgrade with better perf. shadcn/ui Form integrates natively. |
| **Server Cache** | Next.js `"use cache"` | built-in | Explicit, opt-in caching with `updateTag()` for invalidation. Replaces any client-side caching. |

### 3.4 Testing

| Layer | Tool | Justification |
|-------|------|---------------|
| **Unit/Integration** | Vitest 4.1 + Testing Library | Standard for Vite/Turbopack projects. Drop-in Jest replacement. |
| **E2E** | Playwright | Already in use. Cross-browser, auto-wait, excellent TypeScript support. |
| **Visual Regression** | Chromatic | Storybook-native visual testing. Catches UI regressions in CI. |
| **Component Isolation** | Storybook 8 | Component-driven development, visual documentation, Chromatic integration. |

### 3.5 Developer Tooling

| Tool | Justification |
|------|---------------|
| **Biome** | Replaces ESLint + Prettier. Single Rust-based tool, faster, consistent. Next.js 16 removed `next lint`. |
| **Figma MCP Server** | AI agents read Figma context directly, generate accurate code with Code Connect. |
| **Figma Dev Mode** | Inspect, compare changes, component playground, "Ready for Dev" view. |
| **Figma Code Connect** | Link code components to Figma components for live code snippets in Dev Mode. |

### 3.6 What We're NOT Using (and Why)

| Tool | Reason |
|------|--------|
| **Bun (as runtime)** | Not stable enough for production Next.js. Use only as a faster `pnpm install` alternative if desired. |
| **Vite** | Next.js 16 uses Turbopack internally. Vite is for non-Next.js projects. |
| **Redux Toolkit** | Overkill for this app. Zustand + TanStack Query is simpler and sufficient. |
| **styled-components / Emotion** | Runtime CSS-in-JS is incompatible with RSC. Zero-runtime alternatives exist but Tailwind is the standard. |
| **tRPC** | Server Actions + Zod provide end-to-end type safety within Next.js. tRPC adds complexity for marginal benefit. |
| **Pages Router** | Legacy. All new features target App Router only. |

---

## 4. Project Structure

### 4.1 New Directory Layout

```
web-v2/                              # New greenfield project (separate from web/)
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Lint, typecheck, test, build
│       └── chromatic.yml            # Visual regression
├── .storybook/
│   ├── main.ts
│   ├── preview.ts
│   └── figma/                       # Figma addon config
├── public/
│   ├── fonts/
│   └── images/
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── (auth)/                  # Route group: auth pages
│   │   │   ├── login/
│   │   │   └── layout.tsx
│   │   ├── (main)/                  # Route group: authenticated app
│   │   │   ├── layout.tsx           # Main app shell (sidebar + content)
│   │   │   ├── page.tsx             # Dashboard / home
│   │   │   ├── chat/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── [sessionId]/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── loading.tsx
│   │   │   ├── query/
│   │   │   │   ├── page.tsx
│   │   │   │   └── loading.tsx
│   │   │   ├── record/
│   │   │   │   ├── page.tsx
│   │   │   │   └── [noteId]/
│   │   │   │       └── page.tsx
│   │   │   ├── explore/
│   │   │   │   ├── page.tsx
│   │   │   │   └── loading.tsx
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   └── skills/
│   │   │       └── page.tsx
│   │   ├── api/                     # API routes (only for webhooks / SSE)
│   │   │   └── chat/
│   │   │       └── stream/
│   │   │           └── route.ts
│   │   ├── actions/                 # Server Actions (co-located by domain)
│   │   │   ├── chat.ts
│   │   │   ├── query.ts
│   │   │   ├── record.ts
│   │   │   ├── explore.ts
│   │   │   └── settings.ts
│   │   ├── global-error.tsx
│   │   ├── layout.tsx               # Root layout (providers, fonts)
│   │   ├── loading.tsx
│   │   ├── not-found.tsx
│   │   └── globals.css              # Tailwind v4 CSS-first config
│   │
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components (auto-generated)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── dropdown-menu.tsx
│   │   │   ├── tabs.tsx
│   │   │   ├── toast.tsx
│   │   │   ├── card.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── tooltip.tsx
│   │   │   ├── command.tsx
│   │   │   ├── sidebar.tsx
│   │   │   ├── form.tsx
│   │   │   ├── data-table.tsx
│   │   │   └── ...
│   │   ├── chat/
│   │   │   ├── chat-panel.tsx       # Server Component wrapper
│   │   │   ├── chat-messages.tsx    # Server Component (message list)
│   │   │   ├── chat-input.tsx       # Client Component (interactive)
│   │   │   ├── chat-stream.tsx      # Client Component (SSE consumer)
│   │   │   ├── citation-badge.tsx   # Server Component
│   │   │   ├── sources-panel.tsx    # Client Component
│   │   │   └── studio-panel.tsx     # Client Component
│   │   ├── editor/
│   │   │   ├── markdown-editor.tsx  # Client Component (rich editor)
│   │   │   ├── editor-toolbar.tsx   # Client Component
│   │   │   ├── ai-assist-panel.tsx  # Client Component
│   │   │   └── diff-preview.tsx     # Client Component
│   │   ├── query/
│   │   │   ├── search-bar.tsx       # Client Component (with URL state)
│   │   │   ├── results-list.tsx     # Server Component
│   │   │   └── result-card.tsx      # Server Component
│   │   ├── record/
│   │   │   ├── note-form.tsx        # Client Component
│   │   │   ├── metadata-editor.tsx  # Client Component
│   │   │   └── classify-suggestions.tsx # Client Component
│   │   ├── explore/
│   │   │   ├── knowledge-graph.tsx  # Client Component (@xyflow/react)
│   │   │   └── node-details.tsx     # Client Component
│   │   ├── layout/
│   │   │   ├── app-sidebar.tsx      # Client Component (navigation)
│   │   │   ├── top-bar.tsx          # Client Component
│   │   │   └── command-palette.tsx  # Client Component (Cmd+K)
│   │   └── shared/
│   │       ├── file-tree.tsx        # Client Component
│   │       ├── empty-state.tsx      # Server Component
│   │       ├── loading-skeleton.tsx # Server Component
│   │       └── error-boundary.tsx   # Client Component
│   │
│   ├── lib/
│   │   ├── api-client.ts            # Typed API client for FastAPI backend
│   │   ├── sse.ts                   # SSE stream utilities
│   │   ├── utils.ts                 # cn(), formatters, helpers
│   │   └── constants.ts             # App constants
│   │
│   ├── stores/                      # Zustand stores (client-only state)
│   │   ├── ui-store.ts              # Sidebar state, panels, modals
│   │   └── preferences-store.ts     # User preferences (theme, etc.)
│   │
│   ├── hooks/                       # Custom React hooks
│   │   ├── use-chat-stream.ts       # SSE chat with TanStack Query
│   │   ├── use-skill-execution.ts
│   │   └── use-file-tree.ts
│   │
│   ├── types/                       # Shared TypeScript types
│   │   ├── api.ts                   # API response/request types
│   │   ├── chat.ts
│   │   ├── record.ts
│   │   ├── explore.ts
│   │   └── query.ts
│   │
│   ├── figma/                       # Figma Code Connect files
│   │   ├── button.figma.ts
│   │   ├── card.figma.ts
│   │   └── ...
│   │
│   └── stories/                     # Storybook stories
│       ├── components/
│       │   ├── chat/
│       │   ├── editor/
│       │   └── ui/
│       └── pages/
│
├── e2e/                             # Playwright E2E tests
│   ├── chat.spec.ts
│   ├── query.spec.ts
│   ├── record.spec.ts
│   └── explore.spec.ts
│
├── proxy.ts                         # Next.js 16 proxy (replaces middleware.ts)
├── next.config.ts                   # TypeScript config (replaces .mjs)
├── globals.css                      # Root of CSS-first Tailwind config
├── tsconfig.json
├── vitest.config.ts
├── playwright.config.ts
├── biome.json                       # Biome config (replaces .eslintrc + .prettierrc)
├── components.json                  # shadcn/ui config
├── package.json
├── pnpm-lock.yaml
└── AGENTS.md                        # AI agent instructions
```

### 4.2 Key Structural Decisions

1. **`src/` directory** — Colocate all source code under `src/` for clean separation from config files.
2. **Route groups** — `(auth)` and `(main)` route groups for different layouts.
3. **`actions/` at app root** — Server Actions co-located by domain, not per-route.
4. **`figma/` directory** — Code Connect files alongside code, not in Figma plugin.
5. **Separate `stores/`** — Only true client-side state. Server state via TanStack Query.
6. **`stories/` separate from `components/`** — Keeps component directories clean.
7. **`proxy.ts`** — Next.js 16 replaces `middleware.ts` with `proxy.ts` on Node.js runtime.

---

## 5. Architecture Decisions

### 5.1 Server vs Client Component Boundary

The most critical architectural decision. Follow this principle: **Server Components by default, `"use client"` only at the leaf boundary.**

```
Server Components (default)          Client Components ("use client")
─────────────────────────           ─────────────────────────────────
├── Page layouts                     ├── Interactive form inputs
├── Data fetching (TanStack Query    ├── Event handlers (onClick, etc.)
│   prefetch in Server Components)   ├── Browser APIs (localStorage, etc.)
├── Static content rendering         ├── React hooks (useState, useEffect)
├── SEO-critical content             ├── SSE stream consumers
├── Navigation shells                ├── Rich text editors
└── Message lists (static render)    ├── Knowledge graph canvas
                                     ├── Command palette
                                     └── Drag-and-drop interactions
```

**Pattern: Server Component wrapper + Client Component island**

```tsx
// app/(main)/chat/[sessionId]/page.tsx (Server Component)
import { prefetchChatSession } from "@/lib/api-client";
import { ChatPanel } from "@/components/chat/chat-panel";

export default async function ChatSessionPage({ params }) {
  const { sessionId } = await params;
  const session = await prefetchChatSession(sessionId);

  return <ChatPanel initialSession={session} />;
}

// components/chat/chat-panel.tsx (Server Component wrapper)
import { ChatMessages } from "./chat-messages";
import { ChatInput } from "./chat-input";

export function ChatPanel({ initialSession }) {
  return (
    <div className="flex flex-col h-full">
      <ChatMessages messages={initialSession.messages} />
      <ChatInput sessionId={initialSession.id} />
    </div>
  );
}
```

### 5.2 Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                           │
│  (Python, LangGraph, RAG, memU, SQLite)                      │
│  REST API + SSE streaming endpoints                          │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTP / SSE
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Next.js 16 Server                           │
│                                                              │
│  Server Actions (mutations)    Server Components (reads)     │
│  ├── chat.ts (send message)    ├── page.tsx (prefetch)       │
│  ├── record.ts (save note)     └── layout.tsx (shared)       │
│  ├── query.ts (search)                                       │
│  └── settings.ts (update)     TanStack Query (hydration)     │
│                               ├── useQuery (reads)            │
│                               └── useMutation + invalidation  │
│                                                              │
│  "use cache" (explicit caching with updateTag)               │
│  proxy.ts (auth, redirects)                                  │
└──────────────────────────┬───────────────────────────────────┘
                           │ Serialized props
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                   Client Components                          │
│                                                              │
│  Zustand (UI state only)                                     │
│  ├── ui-store: sidebar, panels, modals                       │
│  └── preferences-store: theme, layout                        │
│                                                              │
│  nuqs (URL state)                                            │
│  ├── search queries, filters, pagination                     │
│  └── shareable, bookmarkable URLs                            │
│                                                              │
│  React Hook Form + Zod (form state)                          │
│  SSE streams (chat, logs)                                    │
└──────────────────────────────────────────────────────────────┘
```

### 5.3 State Management Strategy

| State Type | Tool | Examples |
|-----------|------|---------|
| **Server data** | TanStack Query + Server Actions | Chat messages, notes, search results, knowledge graph data |
| **URL params** | nuqs | Search query, active tab, page number, filters |
| **Form state** | React Hook Form + Zod | Note editor, settings form, search input |
| **UI state** | Zustand | Sidebar open/closed, active panel, modal visibility |
| **User preferences** | Zustand + localStorage | Theme, font size, layout preferences |
| **Streaming state** | React state + refs | SSE stream buffer, typing indicators |

**Zustand stores are reduced to 2** (from 7 in current codebase). Everything else moves to the appropriate tool.

### 5.4 API Communication Pattern

**Current approach (client-side fetch wrappers):**
```ts
// lib/chat-api.ts
export async function sendMessage(message: string) {
  const res = await fetch("/api/chat", { method: "POST", body: JSON.stringify({ message }) });
  return res.json();
}
```

**New approach (Server Actions + TanStack Query):**
```ts
// app/actions/chat.ts
"use server";

import { chatSchema } from "@/types/chat";
import { apiClient } from "@/lib/api-client";

export async function sendMessage(formData: FormData) {
  const input = chatSchema.parse({
    message: formData.get("message"),
    sessionId: formData.get("sessionId"),
    sources: formData.getAll("sources"),
  });

  const result = await apiClient.chat(input);
  return result;
}

// hooks/use-chat-stream.ts (client-side SSE consumer)
export function useChatStream(sessionId: string) {
  return useQuery({
    queryKey: ["chat", sessionId],
    queryFn: () => apiClient.getChatSession(sessionId),
    initialData: () => prefetchChatSession(sessionId),
  });
}
```

### 5.5 Caching Strategy

Leverage Next.js 16 `"use cache"` directive for explicit, opt-in caching:

```ts
// app/actions/query.ts
"use server";
"use cache";

import { cacheLife } from "next/cache";

export async function searchNotes(query: string) {
  "use cache";
  cacheLife("hours");
  return apiClient.search(query);
}

export async function invalidateSearchCache() {
  "use server";
  await updateTag("search-results");
}
```

### 5.6 CSS Architecture (Tailwind v4 CSS-First)

**Current:** `tailwind.config.ts` + `globals.css` with CSS variables

**New:** Pure CSS configuration, no JavaScript config file

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --color-background: oklch(100% 0 0);
  --color-foreground: oklch(13% 0.028 261.692);
  --color-primary: oklch(13% 0.028 261.692);
  --color-primary-foreground: oklch(98% 0.016 259.415);
  --color-secondary: oklch(96% 0.006 259.267);
  --color-muted: oklch(96% 0.006 259.267);
  --color-muted-foreground: oklch(55% 0.016 259.415);
  --color-accent: oklch(96% 0.006 259.267);
  --color-destructive: oklch(63% 0.237 25.331);
  --color-border: oklch(91% 0.006 259.267);
  --color-ring: oklch(13% 0.028 261.692);

  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  --radius-lg: 0.5rem;
  --radius-md: calc(var(--radius-lg) - 2px);
  --radius-sm: calc(var(--radius-lg) - 4px);
}

@layer base {
  :root {
    color-scheme: light;
  }

  .dark {
    color-scheme: dark;
    --color-background: oklch(13% 0.028 261.692);
    --color-foreground: oklch(98% 0.016 259.415);
  }
}
```

**No `tailwind.config.ts` file needed.** Everything is configured in CSS.

---

## 6. Figma Integration Plan

### 6.1 Figma-First Development Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Design System Foundation                            │
│                                                             │
│ Figma Library                                                │
│ ├── Variables (colors, spacing, typography, radius)          │
│ ├── Base Components (Button, Input, Card, Badge, etc.)      │
│ ├── Composite Components (ChatPanel, NoteForm, etc.)        │
│ └── Page Frames (mobile, tablet, desktop)                   │
│                                                             │
│ ↓ Export tokens                                              │
│ Style Dictionary → Tailwind CSS @theme values               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Code Connect                                       │
│                                                             │
│ Code Components ↔ Figma Components                          │
│ ├── button.figma.ts  → Button variant mapping               │
│ ├── card.figma.ts    → Card variant mapping                 │
│ └── form.figma.ts    → Form component mapping               │
│                                                             │
│ Published to Figma → Dev Mode shows real code snippets       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 3: AI-Assisted Implementation                         │
│                                                             │
│ Figma MCP Server → Cursor / VS Code                         │
│ ├── Select frame in Figma                                    │
│ ├── Agent reads Auto Layout structure, tokens, components    │
│ ├── Agent generates code using real shadcn/ui components     │
│ └── Code Connect ensures agent uses correct component APIs   │
│                                                             │
│ Skills: Implement Design, Build Screen, Create Component     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Visual Regression                                  │
│                                                             │
│ Storybook → Chromatic                                       │
│ ├── Every component has a Story                              │
│ ├── Chromatic compares screenshot vs Figma design            │
│ ├── CI blocks merge on visual regression                     │
│ └── Designer reviews via Chromatic UI Review                 │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Design Token Pipeline

```
Figma Variables
    ↓ (Tokens Studio plugin → JSON export)
Style Dictionary
    ↓ (transform: json → CSS custom properties)
src/app/globals.css (@theme block)
    ↓ (Tailwind v4 auto-detects)
React Components (using Tailwind utilities)
```

**Automation:** GitHub Action triggered by Figma webhook to re-export tokens when design system updates.

### 6.3 Component Parity Workflow

For each component:

1. **Design** component in Figma with proper variants and Auto Layout
2. **Mark "Ready for Dev"** with annotations and measurements
3. **Create Code Connect** file mapping Figma props → code props
4. **Implement** code component using shadcn/ui primitives + Tailwind
5. **Write Storybook story** with all variants and states
6. **Verify** via Chromatic visual comparison
7. **Link** Storybook story to Figma via Chromatic plugin

### 6.4 Figma MCP Server Configuration

```json
// .cursor/mcp.json or .vscode/mcp.json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--figma-api-key=<KEY>"],
      "env": {}
    }
  }
}
```

Agent skills available:
- **Implement Design:** Select a Figma frame, generate matching React code
- **Code Connect:** Map Figma components to code components
- **Create Design System Rules:** Extract tokens and constraints from Figma

---

## 7. Migration Strategy

### 7.1 Greenfield Approach: Parallel Existence

The new frontend (`web-v2/`) lives alongside the old (`web/`). No legacy code is carried over.

```
markwritter/
├── web/          # Legacy frontend (frozen, no new features)
├── web-v2/       # New frontend (greenfield rewrite)
├── markwritter/  # Backend (unchanged, shared API)
└── ...
```

### 7.2 Migration Phases

```
Phase 0: Scaffolding
├── Create web-v2/ with Next.js 16.2
├── Configure Tailwind v4 CSS-first
├── Install shadcn/ui components
├── Set up Biome, Vitest, Playwright, Storybook
├── Set up Figma Code Connect + MCP Server
└── Establish CI/CD pipeline

Phase 1: Design System + Layout Shell
├── Import design tokens from Figma → globals.css
├── Build app shell: sidebar, top bar, command palette
├── Implement responsive layout (mobile, tablet, desktop)
├── Dark mode support
├── Authentication flow (if applicable)
└── Proxy.ts for auth redirects

Phase 2: Query Module
├── Search input with nuqs URL state
├── Results list (Server Component)
├── Semantic search integration
├── Loading/empty/error states
└── TanStack Query caching

Phase 3: Chat Module (Core)
├── Chat session list
├── Message display (Server Component)
├── Chat input (Client Component)
├── SSE streaming integration
├── Citation badges + source panel
├── File tree + source selection
└── Studio panel

Phase 4: Record Module
├── Note form with React Hook Form + Zod
├── Markdown editor (Client Component)
├── AI assist panel
├── Diff preview for AI suggestions
├── Metadata editor
└── Classification suggestions

Phase 5: Explore Module
├── Knowledge graph canvas (@xyflow/react)
├── Node details panel
├── Relationship discovery UI
└── Topic clustering visualization

Phase 6: Settings + Skills + Polish
├── Settings panel
├── Skill list, detail, executor
├── Log stream viewer
├── Keyboard shortcuts
├── Accessibility audit
├── Performance optimization
└── E2E test coverage

Phase 7: Cutover
├── Final QA pass
├── Switch routing from web/ to web-v2/
├── Update Docker/build configs
├── Archive web/ directory
└── Update documentation
```

### 7.3 Backend API Compatibility

The FastAPI backend remains unchanged. The new frontend communicates with the same REST API endpoints:

- `POST /api/chat/send` — Send chat message
- `GET /api/chat/stream` — SSE streaming
- `POST /api/query/search` — Semantic search
- `GET /api/notes` — List notes
- `POST /api/notes` — Create note
- `GET /api/explore/graph` — Knowledge graph data

**No backend changes are required for the frontend rewrite.**

### 7.4 Data Migration

No data migration needed. The new frontend consumes the same backend API. Chat sessions, notes, and settings data persists in SQLite/PostgreSQL via the existing backend.

---

## 8. Subagent Workflow

### 8.1 Recommended Agent Types per Phase

| Phase | Primary Agent | Supporting Agents | Rationale |
|-------|--------------|-------------------|-----------|
| Phase 0 | `frontend-implementer` | `planner` | Scaffold needs implementation, initial plan needs validation |
| Phase 1 | `frontend-implementer` | `ui-reviewer`, `responsive-states` | Layout shell needs visual + responsive review |
| Phase 2 | `frontend-implementer` | `backend-implementer` (API types) | Query needs typed API contracts |
| Phase 3 | `frontend-implementer` | `bug-investigator` (SSE edge cases) | Chat is the most complex module |
| Phase 4 | `frontend-implementer` | `ui-reviewer` | Editor UX needs careful review |
| Phase 5 | `frontend-implementer` | `ui-reviewer` | Graph visualization needs visual review |
| Phase 6 | `frontend-implementer` | `codex-reviewer` (security), `test-writer` | Final phase needs security review + test coverage |

### 8.2 Iterative Development Loop

For each feature within a phase:

```
1. planner     → Break feature into tasks, identify affected files
2. frontend-implementer → Implement the feature
3. ui-reviewer → Review visual structure, states, accessibility
4. test-writer → Write unit tests + integration tests
5. codex-reviewer → Second review for complex/cross-layer changes
```

### 8.3 Quality Gates

Each phase must pass before proceeding:

```bash
# Lint + Format
pnpm biome check src/

# Type Check
pnpm tsc --noEmit

# Unit Tests
pnpm vitest run

# E2E Tests (for completed modules)
pnpm playwright test

# Build
pnpm next build

# Visual Regression
pnpm chromatic
```

### 8.4 AGENTS.md Configuration

The new `web-v2/AGENTS.md` should include:

```markdown
# Web V2 - Markwritter Frontend

## Commands
- Dev: `pnpm dev`
- Build: `pnpm build`
- Lint: `pnpm biome check src/`
- Typecheck: `pnpm tsc --noEmit`
- Unit tests: `pnpm vitest run`
- E2E tests: `pnpm playwright test`
- Storybook: `pnpm storybook`

## Architecture
- Next.js 16 App Router with Server Components by default
- "use client" only at leaf boundaries
- Server Actions for mutations, TanStack Query for reads
- Tailwind v4 CSS-first (no tailwind.config.ts)
- shadcn/ui components in components/ui/
- Zustand only for UI state (2 stores max)
- nuqs for URL state

## Figma Integration
- MCP Server configured in .cursor/mcp.json
- Code Connect files in src/figma/
- Design tokens in globals.css @theme block
```

---

## 9. Implementation Phases

### Phase 0: Project Scaffolding (1-2 days)

**Deliverables:**
- [ ] Initialize Next.js 16.2 project with `create-next-app`
- [ ] Configure `next.config.ts` (TypeScript config)
- [ ] Set up Tailwind v4 CSS-first in `globals.css`
- [ ] Install and configure shadcn/ui (New York style, neutral base)
- [ ] Set up Biome for linting + formatting
- [ ] Configure Vitest 4.1 + Testing Library
- [ ] Configure Playwright for E2E
- [ ] Set up Storybook 8 with Figma addon
- [ ] Create `proxy.ts` template
- [ ] Create `AGENTS.md` with project conventions
- [ ] Set up GitHub Actions CI pipeline
- [ ] Install and configure Figma MCP Server
- [ ] Create `src/types/` with initial type definitions from backend API

**Verification:** `pnpm dev` starts, `pnpm build` succeeds, `pnpm biome check` passes, Storybook loads.

### Phase 1: Design System + Layout Shell (3-5 days)

**Deliverables:**
- [ ] Import design tokens from Figma → `globals.css` `@theme` block
- [ ] Install all required shadcn/ui components
- [ ] Build `AppSidebar` with navigation links (Chat, Query, Record, Explore, Skills, Settings)
- [ ] Build `TopBar` with breadcrumb + command palette trigger
- [ ] Build `CommandPalette` (Cmd+K) using shadcn Command
- [ ] Implement responsive layout: sidebar collapses to drawer on mobile
- [ ] Implement dark mode toggle (class-based, persisted to localStorage)
- [ ] Build `LoadingSkeleton`, `EmptyState`, `ErrorBoundary` shared components
- [ ] Set up Figma Code Connect for base components
- [ ] Write Storybook stories for all base components

**Verification:** App shell renders, sidebar navigates, dark mode works, responsive at 375px/768px/1440px.

### Phase 2: Query Module (3-4 days)

**Deliverables:**
- [ ] `SearchBar` with nuqs URL state (search query, filters)
- [ ] `ResultsList` Server Component with TanStack Query prefetch
- [ ] `ResultCard` Server Component with citation highlighting
- [ ] Loading skeleton for search results
- [ ] Empty state for no results
- [ ] Error state for search failures
- [ ] TanStack Query caching with `"use cache"` for popular queries
- [ ] E2E test for search flow

**Verification:** Type query → see results → click result → URL updates, shareable URL works.

### Phase 3: Chat Module (5-7 days)

**Deliverables:**
- [ ] Chat session list (Server Component)
- [ ] `ChatMessages` (Server Component for initial render)
- [ ] `ChatInput` (Client Component with form)
- [ ] `ChatStream` (Client Component, SSE consumer)
- [ ] `CitationBadge` (Server Component)
- [ ] `SourcesPanel` (Client Component, file tree)
- [ ] `StudioPanel` (Client Component, answer context)
- [ ] `AnswerContextPanel` for contextual information display
- [ ] Server Action for sending messages
- [ ] TanStack Query for chat history
- [ ] SSE streaming with proper error handling and reconnection
- [ ] "New chat" and "resume chat" flows
- [ ] E2E test for full chat flow

**Verification:** Send message → see streaming response with citations → view sources → resume session.

### Phase 4: Record Module (4-5 days)

**Deliverables:**
- [ ] `NoteForm` with React Hook Form + Zod validation
- [ ] `MarkdownEditor` (Client Component, rich text editing)
- [ ] `EditorToolbar` with formatting actions
- [ ] `AiAssistPanel` for AI writing suggestions
- [ ] `DiffPreview` for viewing AI-suggested changes
- [ ] `MetadataEditor` for tags, categories
- [ ] `ClassifySuggestions` for AI-powered classification
- [ ] Server Actions for note CRUD
- [ ] TanStack Query for note data with optimistic updates
- [ ] E2E test for note creation + editing

**Verification:** Create note → edit with AI assist → view diff → accept changes → save.

### Phase 5: Explore Module (4-5 days)

**Deliverables:**
- [ ] `KnowledgeGraph` canvas using @xyflow/react
- [ ] `NodeDetails` panel for selected node
- [ ] Graph layout algorithms (force-directed, hierarchical)
- [ ] Interactive: zoom, pan, click-to-select, drag nodes
- [ ] Color-coded node types (person, topic, concept, note)
- [ ] Edge labels showing relationship types
- [ ] Responsive: full canvas on desktop, simplified on mobile
- [ ] Server Action for graph data
- [ ] TanStack Query caching for graph structure
- [ ] E2E test for graph exploration

**Verification:** Graph renders → click node → see details → zoom/pan → filter by type.

### Phase 6: Settings + Skills + Polish (3-4 days)

**Deliverables:**
- [ ] `SettingsPanel` with React Hook Form + Zod
- [ ] Theme settings, LLM config, preferences
- [ ] `SkillList`, `SkillCard`, `SkillDetail` components
- [ ] `SkillExecutor` with progress display
- [ ] `LogStream` viewer
- [ ] Keyboard shortcuts (Cmd+K palette, Cmd+N new note, etc.)
- [ ] Accessibility audit (keyboard nav, ARIA, focus management)
- [ ] Performance optimization (code splitting, lazy loading graph)
- [ ] Full E2E test suite
- [ ] Visual regression baseline via Chromatic

**Verification:** All features accessible via keyboard, all tests pass, Lighthouse score > 90.

### Phase 7: Cutover (1-2 days)

**Deliverables:**
- [ ] Final QA pass on all modules
- [ ] Update `docker-compose.yml` to point to `web-v2/`
- [ ] Update `Dockerfile.web` to build from `web-v2/`
- [ ] Update README with new frontend instructions
- [ ] Archive `web/` to `web-legacy/`
- [ ] Rename `web-v2/` to `web/`
- [ ] Update CI/CD pipelines
- [ ] Deploy to staging and verify

**Verification:** All features work in staging environment, no regressions from legacy.

---

## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Next.js 16 breaking changes** cause unexpected issues | Medium | High | Next.js 16.2 is stable (March 2026). Test in Phase 0. Read migration guide thoroughly. |
| **Turbopack production bundler bugs** | Low | High | Turbopack is default in Next.js 16. Fallback: `next build --webpack` flag exists. |
| **Figma MCP Server pricing changes** (currently free beta) | Medium | Low | MCP Server is convenience, not critical. Manual Dev Mode inspection is fallback. |
| **Backend API incompatibility** | Low | High | Same API, no backend changes. Verify with existing tests. Create typed API client in Phase 0. |
| **SSE streaming behavior changes** | Medium | Medium | SSE is standard HTTP. Test streaming early in Phase 3. |
| **@xyflow/react compatibility with RSC** | Medium | Low | Knowledge graph is a Client Component island. Wrapper pattern handles this. |
| **Tailwind v4 migration pain** | Low | Medium | Greenfield project, no migration needed. CSS-first config is simpler than v3. |
| **TanStack Query SSR hydration issues** | Medium | Medium | Use `initialData` from Server Component prefetch. Follow TanStack Query SSR guide. |
| **React Compiler performance regression** | Low | Low | Opt-in via `reactCompiler: true`. Can disable if issues arise. |
| **Timeline overrun** | Medium | Medium | Phases are independent. Ship incrementally. Phase 1-3 are MVP. |

---

## Appendix A: Full Dependency List

### Production Dependencies

```json
{
  "dependencies": {
    "next": "^16.2.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "@tanstack/react-query": "^5.97.0",
    "@xyflow/react": "^12.10.1",
    "zustand": "^5.0.12",
    "nuqs": "^2.0.0",
    "react-hook-form": "^7.72.0",
    "@hookform/resolvers": "^4.1.0",
    "zod": "^4.3.0",
    "radix-ui": "^1.4.3",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.5.0",
    "lucide-react": "^0.577.0",
    "sonner": "^2.0.0",
    "react-markdown": "^10.1.0",
    "remark-gfm": "^4.0.1",
    "dompurify": "^3.3.3"
  }
}
```

### Dev Dependencies

```json
{
  "devDependencies": {
    "@tailwindcss/vite": "^4.2.0",
    "tailwindcss": "^4.2.0",
    "typescript": "^5.7.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@biomejs/biome": "^1.9.0",
    "vitest": "^4.1.0",
    "@vitejs/plugin-react": "^6.0.0",
    "@testing-library/react": "^16.2.0",
    "@testing-library/jest-dom": "^6.9.0",
    "@testing-library/user-event": "^14.6.0",
    "@playwright/test": "^1.58.0",
    "jsdom": "^26.1.0",
    "@vitest/coverage-v8": "^4.1.0",
    "storybook": "^8.0.0",
    "@storybook/react-vite": "^8.0.0",
    "chromatic": "^11.0.0"
  }
}
```

---

## Appendix B: Configuration Files

### `next.config.ts`

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  experimental: {
    cacheComponents: true,
  },
};

export default nextConfig;
```

### `biome.json`

```json
{
  "$schema": "https://biomejs.dev/schemas/1.9.0/schema.json",
  "organizeImports": { "enabled": true },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2
  }
}
```

### `vitest.config.ts`

```ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import { resolve } from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./test/setup.ts"],
    globals: true,
    css: true,
  },
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
});
```

### `components.json` (shadcn/ui)

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

---

## Appendix C: Research Sources

| Topic | Source | URL | Access Date |
|-------|--------|-----|-------------|
| Next.js 16 | Next.js Blog | https://nextjs.org/blog/next-16 | April 9, 2026 |
| Next.js 16.2 | Next.js Blog | https://nextjs.org/blog/next-16-2 | April 9, 2026 |
| React 19.2 | React Blog | https://react.dev/blog/2025/10/01/react-19-2 | April 9, 2026 |
| Vite 8 | Vite Blog | https://vite.dev/blog/announcing-vite8 | April 9, 2026 |
| Tailwind CSS v4 | Tailwind Blog | https://tailwindcss.com/blog/tailwindcss-v4 | April 9, 2026 |
| shadcn/ui | shadcn/ui Docs | https://ui.shadcn.com/docs | April 9, 2026 |
| Zustand | GitHub Releases | https://github.com/pmndrs/zustand/releases | April 9, 2026 |
| TanStack Query | GitHub Releases | https://github.com/TanStack/query/releases | April 9, 2026 |
| Figma MCP Server | Figma Developers | https://developers.figma.com/docs/figma-mcp-server/ | April 9, 2026 |
| Figma Code Connect | Figma Developers | https://developers.figma.com/docs/code-connect/ | April 9, 2026 |
| Figma Dev Mode | Figma | https://www.figma.com/dev-mode/ | April 9, 2026 |
| Turborepo | Turborepo Blog | https://turbo.build/blog | April 9, 2026 |
| Bun | Bun Blog / GitHub | https://bun.sh/blog | April 9, 2026 |
| Zod v4 | GitHub Releases | https://github.com/colinhacks/zod/releases | April 9, 2026 |
| Vitest | Vitest Blog | https://vitest.dev/blog/ | April 9, 2026 |
| pnpm | GitHub Releases | https://github.com/pnpm/pnpm/releases | April 9, 2026 |
| React RSC Security | React Blog | https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components | April 9, 2026 |
| React Foundation | React Blog | https://react.dev/blog/2026/02/24/the-react-foundation | April 9, 2026 |
| Chromatic | Chromatic | https://www.chromatic.com/ | April 9, 2026 |
| v0 by Vercel | v0 | https://v0.dev/ | April 9, 2026 |

---

## Appendix D: Key Terminology

| Term | Definition |
|------|-----------|
| **RSC** | React Server Components — components that run only on the server, never shipped to client |
| **Server Actions** | `"use server"` functions for server-side mutations, replacing API routes for form submissions |
| **Cache Components** | Next.js 16 `"use cache"` directive for explicit component/output caching |
| **Turbopack** | Rust-based bundler, default in Next.js 16, replaces webpack |
| **CSS-first config** | Tailwind v4 approach: configure themes in CSS `@theme` blocks, not JS config files |
| **Figma MCP Server** | Model Context Protocol server that connects Figma to AI coding agents |
| **Code Connect** | Figma feature linking code components to Figma components for live code snippets in Dev Mode |
| **nuqs** | Type-safe URL search params library for Next.js App Router |
| **proxy.ts** | Next.js 16 replacement for `middleware.ts`, runs on Node.js runtime |
| **React Compiler** | Automatic memoization compiler, stable in Next.js 16 with `reactCompiler: true` |
