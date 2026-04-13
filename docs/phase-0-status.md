# Phase 0: Project Scaffolding — Status Report

> Date: April 9, 2026 | Status: **Complete**

---

## Verification Summary

| Check | Status |
|-------|--------|
| `pnpm tsc --noEmit` | PASS |
| `pnpm biome check src/` | PASS — 11 files, 0 issues |
| `pnpm vitest run` | PASS — 1 suite, 1 test |
| `pnpm build` | PASS — Next.js 16.2.3 Turbopack, 743ms compile |

## Installed Versions

| Package | Version |
|---------|---------|
| Next.js | 16.2.3 |
| React | 19.2.4 |
| Tailwind CSS | 4.2.2 (CSS-first, no config file) |
| TypeScript | 5.9.3 |
| Vitest | 4.1.4 |
| Biome | 2.4.10 |
| Storybook | 10.3.5 |

---

## Files Created

### Project Root

| File | Purpose |
|------|---------|
| `Dockerfile.web-v2` | Multi-stage Docker build (deps → builder → runner), Node 22 Alpine |
| `.github/workflows/ci.yml` | 4-job CI pipeline: lint+typecheck → test → build → e2e |
| `.gitignore` (updated) | Added web-v2/ entries to root gitignore |

### web-v2/ Project

#### Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | Project manifest with all deps and scripts |
| `pnpm-lock.yaml` | Lockfile |
| `tsconfig.json` | TypeScript config with `@/` path alias |
| `next.config.ts` | React Compiler + Cache Components enabled |
| `postcss.config.mjs` | Tailwind v4 PostCSS plugin |
| `biome.json` | Biome v2 linting + formatting (replaces ESLint + Prettier) |
| `components.json` | shadcn/ui config (New York style, neutral base, RSC enabled) |
| `vitest.config.ts` | Vitest with jsdom, Testing Library, `@/` alias |
| `playwright.config.ts` | Playwright E2E config (Chromium, auto dev server) |
| `proxy.ts` | Next.js 16 API proxy template |
| `AGENTS.md` | Project conventions and command reference |
| `.gitignore` | Node, Next.js, test, Storybook ignores |

#### Storybook

| File | Purpose |
|------|---------|
| `.storybook/main.ts` | Storybook 10 config with React-Vite framework |
| `.storybook/preview.ts` | Global CSS import and controls config |

#### Source Code

| File | Purpose |
|------|---------|
| `src/app/globals.css` | Tailwind v4 CSS-first with full `@theme` design tokens + dark mode |
| `src/app/layout.tsx` | Root layout |
| `src/app/page.tsx` | Minimal home page (placeholder) |
| `src/lib/utils.ts` | `cn()` utility (clsx + tailwind-merge) |

#### Type Definitions

| File | Contents |
|------|----------|
| `src/types/api.ts` | `ApiResponse<T>`, `ApiError`, `PaginatedResponse<T>` |
| `src/types/chat.ts` | `Message`, `Session`, `ChatEvent`, `Citation`, `StreamSource`, `ChatRequestBody`, `Intent` |
| `src/types/record.ts` | `TreeNode`, `FileTreeResponse`, `SourceReference`, `Note`, `NoteFormInput` |
| `src/types/query.ts` | `SearchResult`, `SearchRequest`, `SearchFilters`, `SearchResponse` |
| `src/types/explore.ts` | `GraphNode`, `GraphEdge`, `GraphData`, `NodeDetails` |
| `src/types/index.ts` | Re-exports all type modules |

#### Testing

| File | Purpose |
|------|---------|
| `test/setup.ts` | Vitest setup with `@testing-library/jest-dom/vitest` |
| `src/app/page.test.tsx` | Smoke test — renders without crashing |
| `e2e/smoke.spec.ts` | Playwright smoke — homepage title check |

#### Directory Structure (empty, ready for Phase 1)

| Directory | Purpose |
|-----------|---------|
| `src/components/ui/` | shadcn/ui auto-generated components |
| `src/hooks/` | Custom React hooks |
| `src/stores/` | Zustand stores (UI state only) |

---

## Notes

1. **React Compiler** — Required adding `babel-plugin-react-compiler` as a dev dependency
2. **Cache Components** — `cacheComponents` moved from `experimental` to top-level in Next.js 16
3. **Storybook** — Installed as v10.3.5 (newer than planned v8). Addon peer warnings are benign
4. **Biome** — Installed as v2.4.10 (newer than planned v1.9). Includes Tailwind CSS directives support
5. **Tailwind v4** — No `tailwind.config.ts` file. All configuration in `src/app/globals.css` `@theme` block
6. **No legacy code** — Every file is fresh. Zero code carried over from `web/`

---

## Phase 1 Readiness

The project is ready for Phase 1 (Design System + Layout Shell):

- [x] Next.js 16.2 with Turbopack builds successfully
- [x] Tailwind v4 CSS-first with placeholder design tokens
- [x] shadcn/ui initialized (New York style, neutral base)
- [x] Biome linting passes
- [x] Vitest + Testing Library configured and passing
- [x] Playwright configured with smoke test
- [x] Storybook configured
- [x] Type definitions ported from `web/lib/types.ts`
- [x] CI pipeline ready (lint → typecheck → test → build → e2e)
- [x] Docker build ready
- [x] `AGENTS.md` with project conventions
