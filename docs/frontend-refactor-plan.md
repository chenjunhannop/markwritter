# Frontend Refactoring Plan

> **Status**: Draft  
> **Date**: 2026-04-09  
> **Scope**: `web/` directory — architecture improvements, no feature changes

---

## Table of Contents

1. [Current Architecture Audit](#1-current-architecture-audit)
2. [Tech Stack Recommendations](#2-tech-stack-recommendations)
3. [Project Structure & Folder Organization](#3-project-structure--folder-organization)
4. [Component Architecture Patterns](#4-component-architecture-patterns)
5. [State Management Strategy](#5-state-management-strategy)
6. [API & Data Fetching Approach](#6-api--data-fetching-approach)
7. [Testing Strategy](#7-testing-strategy)
8. [CI/CD Considerations](#8-cicd-considerations)
9. [Recommended Subagent Workflow](#9-recommended-subagent-workflow)

---

## 1. Current Architecture Audit

### What exists today

| Layer | Current Choice | Files |
|-------|---------------|-------|
| Framework | Next.js 15 App Router, React 19 | `app/` |
| Styling | Tailwind CSS 4 + shadcn/ui (new-york) | `tailwind.config.ts`, `components/ui/` |
| State | Zustand 5 with `persist` middleware | `lib/store.ts`, `lib/*-store.ts` |
| API | Raw `fetch()` calls, 4 separate modules | `lib/api.ts`, `lib/*-api.ts` |
| Streaming | Custom SSE parser + StreamBuffer typewriter | `lib/sse.ts`, `lib/stream-buffer.ts` |
| Unit tests | Vitest 3 + Testing Library | `**/*.test.ts(x)`, 80% coverage threshold |
| E2E tests | Playwright (Chromium, Firefox, WebKit, mobile) | `e2e/*.spec.ts` |
| Validation | Zod + react-hook-form | `package.json` |
| Graph | @xyflow/react | `components/explore/` |

### Identified problems

| # | Problem | Impact | Location |
|---|---------|--------|----------|
| P1 | `store.ts` is 413 lines containing 3 unrelated stores (Chat, Skill, UI) | Hard to navigate, increases bundle coupling | `lib/store.ts` |
| P2 | `API_BASE` constant duplicated in 4 files | Drift risk, config not centralized | `lib/api.ts:16`, `lib/explore-api.ts:10`, `lib/query-api.ts:16`, `lib/record-api.ts:13` |
| P3 | `createApiError()` reimplemented in `api.ts` and 3 domain modules | Maintenance burden, inconsistent error shape | `lib/query-api.ts:132`, `lib/record-api.ts` imports from `api.ts` but others don't |
| P4 | No shared error boundary or loading-skeleton pattern | Inconsistent UX across pages | Components lack error boundaries |
| P5 | Store actions embed API calls directly (e.g., `loadSkills` calls `getSkills()`) | Hard to test stores in isolation, no caching | `lib/store.ts:291-300` |
| P6 | Types split between `lib/types.ts` (shared) and `lib/*-api.ts` (local) | Consumer must know which file to import from | `lib/types.ts` vs `lib/explore-api.ts` |
| P7 | No request deduplication or stale-while-revalidate | Unnecessary duplicate fetches on mount | All API modules |
| P8 | `settings-store.ts` is 641 lines with encryption logic mixed in | Violates single-responsibility | `lib/settings-store.ts` |
| P9 | No path aliases for `components/` subdomains | Deep relative imports (`@/components/chat/...`) work but are verbose | Throughout |
| P10 | E2E tests depend on live dev server | Slow, flaky CI | `playwright.config.ts:86-93` |

---

## 2. Tech Stack Recommendations

### Keep (no migration cost, already good fits)

| Technology | Justification |
|-----------|---------------|
| **Next.js 15 App Router** | RSC support, file-based routing, `generateMetadata`. Already in use. No reason to change. |
| **React 19** | Latest stable. `use()`, `useOptimistic`, improved Suspense. Already integrated. |
| **Zustand 5** | Lightweight, TypeScript-friendly, supports `persist`. Scales well for this app's state complexity. Not worth replacing with Redux/Valtio. |
| **Tailwind CSS 4** | Zero-config in v4, good DX. Already paired with shadcn/ui. |
| **shadcn/ui (new-york)** | Copy-paste components, full ownership. Already set up with `components.json`. |
| **Vitest 3** | Fast, ESM-native, compatible with Testing Library. Already at 80% threshold. |
| **Playwright** | Multi-browser E2E, already configured with mobile projects. |
| **Zod** | Runtime validation, shared between client and (potentially) server. |

### Add (solves identified problems)

| Technology | Solves | Justification |
|-----------|--------|---------------|
| **TanStack Query v5** | P5, P7 | Built-in caching, deduplication, stale-while-revalidate, optimistic updates, and `useMutation`. Removes need for hand-rolled loading/error state in stores. Keeps Zustand for pure client state (UI, sessions). |
| **React Error Boundary** (library or hand-rolled) | P4 | Consistent error UX per route. ~50 lines of code; no need for `react-error-boundary` npm package. |
| **`openapi-typescript`** (code-gen) | P6 | Auto-generate TypeScript types from the FastAPI backend's OpenAPI schema. Single source of truth, eliminates drift between frontend types and backend models. |

### Do NOT add (avoid over-engineering)

| Technology | Why skip |
|-----------|----------|
| **Redux Toolkit** | Zustand already serves this app well. Migration cost with no benefit. |
| **tRPC** | Backend is Python/FastAPI. Adding a Node.js tRPC router just for the frontend would add complexity without sufficient payoff for this app's scale. |
| **Storybook** | Useful but premature. The component library (shadcn/ui) is well-documented; custom components are domain-specific. Add later if team grows. |
| **MSW (Mock Service Worker)** | Current test setup with Vitest mocks is sufficient. Add if E2E test flakiness becomes a recurring problem. |

---

## 3. Project Structure & Folder Organization

### Proposed structure

```
web/
├── app/                          # Next.js App Router (routes only)
│   ├── layout.tsx
│   ├── page.tsx                  # Redirects to /chat
│   ├── chat/page.tsx
│   ├── explore/page.tsx
│   ├── logs/page.tsx
│   ├── query/page.tsx
│   ├── record/page.tsx
│   ├── settings/page.tsx
│   └── skills/page.tsx
│
├── components/
│   ├── ui/                       # shadcn/ui primitives (unchanged)
│   ├── layout/                   # Shell: sidebar, header, main-layout
│   ├── chat/                     # Chat domain components
│   ├── editor/                   # Markdown editor & AI assist
│   ├── explore/                  # Knowledge graph
│   ├── query/                    # Search & Q&A
│   ├── record/                   # Note CRUD
│   ├── settings/                 # Settings panel
│   ├── skills/                   # Skill cards & executor
│   ├── logs/                     # Log stream
│   └── shared/                   # NEW: cross-cutting components
│       ├── error-boundary.tsx
│       ├── loading-skeleton.tsx
│       ├── empty-state.tsx
│       └── confirm-dialog.tsx
│
├── features/                     # NEW: domain modules (colocation)
│   ├── chat/
│   │   ├── api.ts                # Chat-specific API functions
│   │   ├── hooks.ts              # useChat, useChatSession
│   │   ├── stores.ts             # Chat Zustand store (sessions, messages)
│   │   ├── types.ts              # Chat-specific types
│   │   └── utils.ts              # Chat helpers
│   ├── skills/
│   │   ├── api.ts
│   │   ├── hooks.ts
│   │   ├── stores.ts
│   │   └── types.ts
│   ├── explore/
│   │   ├── api.ts
│   │   ├── hooks.ts
│   │   ├── stores.ts
│   │   └── types.ts
│   ├── query/
│   │   ├── api.ts
│   │   ├── hooks.ts
│   │   ├── stores.ts
│   │   └── types.ts
│   ├── record/
│   │   ├── api.ts
│   │   ├── hooks.ts
│   │   ├── stores.ts
│   │   └── types.ts
│   └── settings/
│       ├── api.ts
│       ├── hooks.ts
│       ├── stores.ts
│       ├── crypto.ts             # Extracted encryption logic
│       └── types.ts
│
├── lib/                          # Shared infrastructure
│   ├── api-client.ts             # NEW: centralized fetch wrapper
│   ├── query-client.ts           # NEW: TanStack Query provider config
│   ├── sse.ts                    # SSE parser (unchanged)
│   ├── stream-buffer.ts          # Typewriter (unchanged)
│   ├── nav-config.ts             # Navigation (unchanged)
│   ├── utils.ts                  # cn() (unchanged)
│   └── types/                    # NEW: shared type barrel
│       ├── index.ts              # Re-exports everything
│       ├── common.ts             # Shared types (Nav, Connection)
│       └── generated.ts          # Auto-generated from OpenAPI (future)
│
├── hooks/                        # Shared hooks (cross-domain)
│   ├── use-media-query.ts
│   └── use-debounce.ts
│
├── providers/                    # NEW: React context providers
│   ├── query-provider.tsx        # TanStack QueryClientProvider
│   └── theme-provider.tsx
│
├── e2e/                          # Unchanged structure
├── test/                         # Test setup
└── config files                  # package.json, tsconfig, etc.
```

### Why this structure

1. **`features/` colocation**: Each domain (chat, skills, etc.) keeps its API, hooks, store, and types together. Developers working on "record" don't need to touch `lib/`.

2. **`lib/` becomes infrastructure-only**: Only shared utilities (API client, SSE parser, types). No domain logic.

3. **`components/` stays flat-by-domain**: No nesting beyond one level. The `shared/` folder is the only new addition.

4. **`providers/`**: Separates React context providers from components. Cleaner `layout.tsx`.

5. **Migration is incremental**: Each feature module can be extracted one at a time. No big-bang rewrite.

---

## 4. Component Architecture Patterns

### 4.1 Component categories

```
                    ┌─────────────────────────┐
                    │   Page (app/*/page.tsx)  │   Server Component by default
                    │   - Compose layout       │   'use client' only when needed
                    │   - Fetch data (RSC)     │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │   Layout Component       │   Client Component
                    │   - Sidebar, Header      │   Manages shell state
                    │   - Panel toggles        │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │   Feature Component      │   Client Component
                    │   - ChatArea, SkillList  │   Uses hooks + stores
                    │   - Knows domain state   │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │   Presentational Comp.   │   Client Component
                    │   - FileTreeNode, Badge  │   Props-only, no hooks
                    │   - Highly reusable      │
                    └──────────┬──────────────┘
                               │
                    ┌──────────▼──────────────┐
                    │   UI Primitive           │   shadcn/ui
                    │   - Button, Input, Sheet │   No domain knowledge
                    └─────────────────────────┘
```

### 4.2 Rules

| Rule | Guideline |
|------|-----------|
| **Server by default** | `app/*/page.tsx` files are Server Components unless they need client interactivity. Mark `'use client'` only when necessary. |
| **Data fetching at edges** | Use TanStack Query hooks in feature components, or `fetch()` directly in Server Components for initial data. |
| **Presentational components are pure** | Components like `FileTreeNode`, `CitationBadge`, `StudioCard` receive data via props, no store access. |
| **One store per feature** | Each `features/*/stores.ts` exports one Zustand store. No cross-feature store imports. |
| **Error boundaries per route** | Each `app/*/page.tsx` wraps its content in an `<ErrorBoundary>`. Shared component lives in `components/shared/`. |
| **Loading states via Suspense** | Use Next.js `<Suspense fallback={<LoadingSkeleton />}>` for route-level loading. TanStack Query handles granular loading within components. |

### 4.3 Component file template

```
components/<domain>/<component-name>.tsx     # Component
components/<domain>/<component-name>.test.tsx # Co-located test
```

Each component file:
- Exports a single named component (no default exports)
- Uses `cn()` for conditional classes
- Defines prop types inline or in a local `types.ts`

---

## 5. State Management Strategy

### 5.1 Zustand vs TanStack Query split

```
┌───────────────────────────────────────────────────────┐
│                    State Spectrum                      │
│                                                       │
│  Client-only          │  Server-synced                │
│  (Zustand)            │  (TanStack Query)             │
│                       │                               │
│  • UI toggles         │  • Chat messages              │
│  • Sidebar collapsed  │  • Skills list                │
│  • Panel state        │  • File tree                  │
│  • Navigation         │  • Search results             │
│  • Theme preference   │  • Knowledge graph            │
│  • Session list       │  • Settings (remote)          │
│  • Draft content      │  • Note content               │
│                       │  • Tag suggestions            │
│                       │  • AI rewrite/polish results  │
└───────────────────────────────────────────────────────┘
```

### 5.2 Zustand stores (refactored)

**Current**: 8 stores in flat `lib/`  
**Proposed**: 6 stores, one per `features/*/stores.ts`

| Store | State | Persist? |
|-------|-------|----------|
| `features/chat/stores.ts` → `useChatStore` | Sessions, selected sources, streaming flag | Yes (localStorage) |
| `features/settings/stores.ts` → `useSettingsStore` | Theme, language, API URL (non-sensitive preferences) | Yes (localStorage) |
| `features/record/stores.ts` → `useRecordStore` | Draft content, title, tags, diff/undo state | No |
| `features/explore/stores.ts` → `useExploreStore` | Selected node, graph viewport | No |
| `features/query/stores.ts` → `useQueryStore` | Search mode preference | Partial |
| `components/layout/` → `useUIStore` | Sidebar, panels, nav, drawer | Yes (localStorage) |

**Key changes**:
- Split `store.ts` into `features/chat/stores.ts` (Chat + Source state), `features/skills/stores.ts` (Skills state)
- Keep `useUIStore` in layout since it's UI-shell-specific
- Remove API calls from store actions — stores only hold client state
- Extract encryption logic from `settings-store.ts` into `features/settings/crypto.ts`

### 5.3 TanStack Query (new)

Replace hand-rolled loading/error/caching state in stores with TanStack Query hooks:

```typescript
// features/chat/hooks.ts
export function useChatMessages(sessionId: string) {
  return useQuery({
    queryKey: ['chat', 'messages', sessionId],
    queryFn: () => getChatMessages(sessionId),
    enabled: !!sessionId,
  });
}

export function useSendMessage() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: SendMessageParams) => sendMessageStream(params),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['chat'] });
    },
  });
}
```

**Benefits**:
- Automatic cache invalidation and background refetch
- Deduplication of identical requests across components
- Built-in `isPending`, `isError`, `data` states — no manual tracking
- Optimistic updates for mutations
- `staleTime` and `gcTime` configurable per query

### 5.4 Streaming state

SSE streaming (chat, AI continue, Q&A) stays as-is — these are real-time streams that don't fit TanStack Query's request/response model. Keep:
- `lib/sse.ts` — SSE parser
- `lib/stream-buffer.ts` — typewriter effect
- `features/chat/hooks.ts` → `useChat()` hook manages streaming via `useMutation` + manual SSE processing

---

## 6. API & Data Fetching Approach

### 6.1 Centralized API client

**Replace** 4 separate `fetch()` patterns with one shared client:

```typescript
// lib/api-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
  params?: Record<string, string>;
}

async function apiClient<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, params, ...fetchOptions } = options;

  const url = new URL(`${API_BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }

  const response = await fetch(url.toString(), {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    throw await ApiError.fromResponse(response);
  }

  return response.json();
}

export const api = {
  get: <T>(path: string, params?: Record<string, string>) =>
    apiClient<T>(path, { method: 'GET', params }),

  post: <T>(path: string, body: unknown, signal?: AbortSignal) =>
    apiClient<T>(path, { method: 'POST', body, signal }),

  put: <T>(path: string, body: unknown) =>
    apiClient<T>(path, { method: 'PUT', body }),

  del: <T>(path: string) =>
    apiClient<T>(path, { method: 'DELETE' }),

  stream: (path: string, body: unknown, signal?: AbortSignal) =>
    // Returns raw Response for SSE processing
    fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal,
    }),
};
```

### 6.2 Domain API modules become thin wrappers

```typescript
// features/chat/api.ts
import { api } from '@/lib/api-client';
import type { ChatRequestBody, SourceSelectionResponse } from './types';

export function sendMessage(body: ChatRequestBody, signal?: AbortSignal) {
  return api.stream('/api/v1/chat/', body, signal);
}

export function getSelectedSources(sessionId: string) {
  return api.get<SourceSelectionResponse>('/api/v1/chat/sources', {
    session_id: sessionId,
  });
}
```

### 6.3 Error handling strategy

```
ApiError (lib/api-client.ts)
  ├── status: number
  ├── message: string
  └── toUserMessage(): string     // Friendly message for UI

ErrorBoundary (components/shared/)
  └── Catches render errors, shows fallback

TanStack Query onError
  └── Global handler: toast notification via sonner

Hook-level error state
  └── useMutation's `error` field for inline error display
```

### 6.4 OpenAPI type generation (future)

When backend stabilizes:
1. Add `openapi-typescript` to devDependencies
2. Generate `lib/types/generated.ts` from `http://localhost:8000/openapi.json`
3. Domain `types.ts` files re-export from generated types
4. Add `npm run generate:types` script

---

## 7. Testing Strategy

### 7.1 Testing pyramid

```
          ┌──────────┐
          │  E2E (10) │   Playwright: critical user flows only
          │           │   Chat, Record CRUD, Settings
         ┌┴───────────┴┐
         │ Integration  │   Vitest + Testing Library
         │    (30)      │   Hook + store + API interaction
        ┌┴─────────────┴┐
        │    Unit (60)   │   Vitest: stores, utils, API client
        │                │   Pure functions, type guards
        └────────────────┘
```

### 7.2 Test organization

```
web/
├── features/*/          # Unit tests co-located
│   ├── stores.test.ts   # Store state transitions
│   ├── api.test.ts      # API functions (mocked fetch)
│   └── hooks.test.ts    # Hooks with renderHook
│
├── components/*/        # Integration tests co-located
│   ├── chat-area.test.tsx
│   └── ...
│
├── lib/                 # Infrastructure tests
│   ├── api-client.test.ts
│   ├── sse.test.ts
│   └── stream-buffer.test.ts
│
├── e2e/                 # E2E tests (unchanged)
│   ├── chat.spec.ts
│   ├── record.spec.ts
│   ├── settings.spec.ts
│   └── ...
│
└── test/
    ├── setup.ts         # Global setup (jsdom, mocks)
    └── fixtures/        # Shared test data factories
        ├── chat-fixtures.ts
        ├── record-fixtures.ts
        └── ...
```

### 7.3 Mocking strategy

| Layer | Mock approach |
|-------|--------------|
| API calls | Mock `api` module methods in domain tests. No network calls. |
| TanStack Query | Use `@tanstack/react-query` test utilities (`QueryClientProvider` with `retry: false`). |
| Zustand stores | Reset store between tests via `store.setState(initialState)`. |
| SSE streaming | Mock `processSSEStream` to emit events synchronously. |
| Next.js router | Mock `next/navigation` in page-level tests. |

### 7.4 Coverage targets

| Category | Target | Current |
|----------|--------|---------|
| `lib/` infrastructure | 90% | ~85% |
| `features/*/stores.ts` | 90% | ~80% |
| `features/*/api.ts` | 80% | ~75% |
| `features/*/hooks.ts` | 80% | ~70% |
| `components/**` | 70% (interaction tests) | ~75% |
| Overall | 80% | 80% |

---

## 8. CI/CD Considerations

### 8.1 Pipeline stages

```yaml
# Proposed GitHub Actions pipeline
stages:
  - lint          # ESLint + TypeScript check
  - unit-test     # Vitest with coverage
  - build         # next build (catches type errors)
  - e2e-test      # Playwright (only on PR, not every push)
  - docker-build  # Build Docker image
```

### 8.2 Specific improvements

| Area | Current | Proposed |
|------|---------|----------|
| **Lint** | `next lint` (ESLint) | Add `tsc --noEmit` as separate step for faster type feedback |
| **Unit tests** | `vitest run` locally | Run in CI with `--coverage` and fail if below 80% threshold |
| **E2E tests** | Run against live dev server | Add `@playwright/test` CI mode with `retries: 2`, trace on failure (already configured) |
| **Build** | `next build` in Docker | Run `next build` as CI step before Docker to catch build errors faster |
| **Docker** | Multi-stage (good) | Add `.dockerignore` for `node_modules`, `coverage`, `.next` to reduce build context |
| **Caching** | None | Cache `node_modules` and `.next/cache` in CI for 2-3x faster builds |

### 8.3 Environment management

```
NEXT_PUBLIC_API_URL    → Backend URL (varies by env)
NEXT_PUBLIC_APP_VERSION → From package.json or CI build number
```

No secrets in the frontend bundle. API keys are managed server-side.

---

## 9. Recommended Subagent Workflow

### 9.1 Migration phases (ordered by risk, low → high)

Each phase is a self-contained unit of work that can be completed and verified independently.

```
Phase 1: Foundation        Phase 2: Extract Domains     Phase 3: Data Layer
─────────────────         ─────────────────────         ──────────────────
1A. Centralize API client  2A. Extract chat feature      3A. Add TanStack Query
1B. Create shared types    2B. Extract skills feature    3B. Refactor stores
1C. Error boundary         2C. Extract explore feature   3C. Migrate API calls
1D. Providers folder       2D. Extract query feature     3D. Hook consolidation
                           2E. Extract record feature
                           2F. Extract settings feature
```

### 9.2 Subagent task breakdown

#### Phase 1: Foundation (low risk, no behavior change)

| Task ID | Subagent Type | Description | Verification |
|---------|--------------|-------------|--------------|
| 1A | `refactor-driver` | Create `lib/api-client.ts` with centralized `api` object. Update all 4 API modules to use it. Remove duplicated `API_BASE` and `createApiError`. | `npm run test:run` passes, no behavior change |
| 1B | `refactor-driver` | Move shared types from `lib/types.ts` to `lib/types/`. Create barrel export. Update all imports. | `npm run build` succeeds |
| 1C | `frontend-implementer` | Create `components/shared/error-boundary.tsx`, `loading-skeleton.tsx`, `empty-state.tsx`. Add to each route page. | Visual check in dev |
| 1D | `refactor-driver` | Create `providers/` folder. Move `TooltipProvider`, `Toaster` wrapping to providers. Clean up `app/layout.tsx`. | `npm run build` succeeds |

#### Phase 2: Extract domains (medium risk, structural change)

Each domain extraction follows the same pattern:

1. Create `features/<domain>/` directory
2. Move `<domain>-api.ts` → `features/<domain>/api.ts`
3. Move `<domain>-store.ts` → `features/<domain>/stores.ts`
4. Move domain-specific types → `features/<domain>/types.ts`
5. Move domain hooks → `features/<domain>/hooks.ts`
6. Update all imports across the codebase
7. Run tests

| Task ID | Subagent Type | Description | Verification |
|---------|--------------|-------------|--------------|
| 2A | `refactor-driver` | Extract `chat` feature module. Split `store.ts` chat store into `features/chat/stores.ts`. Update 15+ component imports. | `npm run test:run` + `npm run build` |
| 2B | `refactor-driver` | Extract `skills` feature module. Move skill store from `store.ts`. | Tests + build |
| 2C | `refactor-driver` | Extract `explore` feature module. | Tests + build |
| 2D | `refactor-driver` | Extract `query` feature module. | Tests + build |
| 2E | `refactor-driver` | Extract `record` feature module. Move 791-line store. | Tests + build |
| 2F | `refactor-driver` | Extract `settings` feature module. Split encryption into `crypto.ts`. | Tests + build |
| 2G | `refactor-driver` | Delete empty `lib/store.ts`. Move `useUIStore` to layout. Final cleanup. | Full test suite + build |

#### Phase 3: Data layer (higher risk, behavior refinement)

| Task ID | Subagent Type | Description | Verification |
|---------|--------------|-------------|--------------|
| 3A | `frontend-implementer` | Install TanStack Query. Create `lib/query-client.ts` and `providers/query-provider.tsx`. Add to root layout. | Build succeeds |
| 3B | `frontend-implementer` | For each domain: create TanStack Query hooks in `features/*/hooks.ts` for server data (lists, detail fetches). Keep Zustand for client-only state. | Per-domain tests |
| 3C | `refactor-driver` | Remove server-data from Zustand stores. Stores keep only UI/session/draft state. Simplify store actions. | Tests pass, no visual regressions |
| 3D | `frontend-implementer` | Consolidate streaming hooks. Ensure `useChat`, `useQueryStream`, `useRecordAI` share common streaming patterns. | Integration tests |

### 9.3 After each phase

1. Run `npm run lint && npm run test:run && npm run build`
2. Run `npm run test:e2e` against the most critical flows (chat, record CRUD)
3. Git commit with message like `refactor(web): phase N - description`
4. If tests fail, use `bug-investigator` subagent to diagnose before proceeding

### 9.4 Rollback strategy

Each phase is a single commit. If issues arise:
- `git revert <sha>` to undo a phase
- Re-run tests to confirm rollback is clean
- No database migrations involved — purely frontend structural changes

---

## Appendix A: File count impact

| Metric | Before | After |
|--------|--------|-------|
| Files in `lib/` | 30 | ~10 |
| Files in `features/` | 0 | ~30 |
| Store files | 8 flat | 6 domain-scoped |
| API modules | 4 with duplication | 4 thin + 1 shared client |
| Shared types file | 1 monolithic (294 lines) | Split into domain + shared |

## Appendix B: Dependency additions

```json
{
  "dependencies": {
    "@tanstack/react-query": "^5"
  },
  "devDependencies": {
    "@tanstack/react-query-devtools": "^5",
    "openapi-typescript": "^7"
  }
}
```

Total new runtime dependency: **1** (`@tanstack/react-query`, ~13KB gzipped).

## Appendix C: Risks and mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Import path breakage during Phase 2 | Medium | TypeScript compiler catches all missing imports at build time |
| TanStack Query cache invalidation bugs | Low | Start with aggressive `staleTime: 0`, tune per-query after verification |
| E2E test flakiness after refactor | Low | Run full E2E suite after each phase, not just at the end |
| Bundle size increase from TanStack Query | Very low | ~13KB gzipped; verify with `next build` output |
| Settings encryption migration | Medium | Keep backward-compatible decryption; add migration test |
