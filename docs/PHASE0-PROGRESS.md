# Phase 0: Project Scaffolding - Progress

> Date: April 9, 2026 | Status: **COMPLETE**

## Deliverables Checklist

| # | Deliverable | Status | Notes |
|---|-------------|--------|-------|
| 1 | Initialize Next.js 16.2 project with pnpm | ✅ | Next.js 16.2.3, React 19.2.4, Turbopack |
| 2 | Configure `next.config.ts` (TypeScript config) | ✅ | `reactCompiler: true`, `cacheComponents: true` |
| 3 | Set up Tailwind v4 CSS-first in `globals.css` | ✅ | `@theme` block with oklch colors, dark mode via `.dark` |
| 4 | Install and configure shadcn/ui (New York style) | ✅ | `components.json`, 15 components installed |
| 5 | Set up Biome for linting + formatting | ✅ | `biome.json` with Tailwind directives support |
| 6 | Configure Vitest 4.1 + Testing Library | ✅ | `vitest.config.ts`, jsdom, globals |
| 7 | Configure Playwright for E2E | ✅ | `playwright.config.ts`, smoke test |
| 8 | Set up Storybook 8 with Figma addon | ✅ | `.storybook/` directory, storybook scripts |
| 9 | Create `proxy.ts` template | ✅ | API proxy to FastAPI backend |
| 10 | Create `AGENTS.md` with project conventions | ✅ | Commands, architecture, file conventions |
| 11 | Set up GitHub Actions CI pipeline | ✅ | `.github/workflows/ci.yml` (quality + build + e2e) |
| 12 | Install and configure Figma MCP Server | ✅ | `.cursor/mcp.json` |
| 13 | Create `src/types/` with initial type definitions | ✅ | api.ts, chat.ts, explore.ts, query.ts, record.ts |

## Verification Results

| Check | Result |
|-------|--------|
| `pnpm install` | ✅ Pass (363ms) |
| `pnpm build` | ✅ Pass (Turbopack, 730ms compile) |
| `pnpm test:run` | ✅ Pass (1 test, 513ms) |
| `pnpm biome check src/` | ✅ Pass (27 files, no issues) |
| `pnpm tsc --noEmit` | ✅ Pass (no type errors) |

## Project Structure

```
web-v2/
├── .github/workflows/ci.yml      # CI: lint + typecheck + test + build + e2e
├── .storybook/                    # Storybook config
├── e2e/smoke.spec.ts              # Playwright smoke test
├── src/
│   ├── app/
│   │   ├── globals.css            # Tailwind v4 CSS-first @theme config
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page (placeholder)
│   │   └── page.test.tsx          # Unit test
│   ├── components/ui/             # 15 shadcn/ui components
│   ├── hooks/use-mobile.ts        # Mobile detection hook
│   ├── lib/utils.ts               # cn() utility
│   ├── stores/                    # Zustand stores (empty, Phase 1+)
│   └── types/                     # API type definitions
│       ├── api.ts, chat.ts, explore.ts, query.ts, record.ts
├── test/setup.ts                  # Vitest setup
├── biome.json                     # Biome config (replaces ESLint + Prettier)
├── components.json                # shadcn/ui config
├── next.config.ts                 # Next.js 16 TypeScript config
├── playwright.config.ts           # Playwright config
├── proxy.ts                       # Next.js 16 proxy template
├── vitest.config.ts               # Vitest config
├── tsconfig.json                  # TypeScript config
├── package.json                   # Dependencies
├── pnpm-lock.yaml                 # Lockfile
└── AGENTS.md                      # AI agent instructions
```

## Installed shadcn/ui Components

badge, button, card, command, dialog, dropdown-menu, form, input, label, separator, sheet, sidebar, skeleton, tabs, tooltip

## Dependencies

### Production
- next@16.2.3, react@19.2.4, react-dom@19.2.4
- @tanstack/react-query, zustand, nuqs, react-hook-form, zod
- radix-ui, class-variance-authority, clsx, tailwind-merge
- lucide-react, sonner, react-markdown, remark-gfm, dompurify
- @xyflow/react, cmdk, @hookform/resolvers

### Dev
- @biomejs/biome, vitest, @playwright/test
- tailwindcss, @tailwindcss/postcss, @vitejs/plugin-react
- storybook, @chromatic-com/storybook
- @testing-library/react, @testing-library/jest-dom, @testing-library/user-event
- jsdom, @vitest/coverage-v8, babel-plugin-react-compiler

## Next: Phase 1 - Design System + Layout Shell

Ready to begin. See `docs/frontend-rewrite-plan.md` for Phase 1 deliverables.
