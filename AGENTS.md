# Markwritter

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vite SPA + React + react-router-dom v7 |
| UI | Radix UI + Tailwind CSS |
| State | Zustand |
| Build/Lint | pnpm, biome (NOT eslint) |
| Test (FE) | vitest (NOT jest) |
| Backend | Python FastAPI + LangGraph + LiteLLM |
| Test (BE) | pytest |
| Lint/Format (BE) | ruff + black |

## Commands

```bash
# Frontend
pnpm dev                  # dev server (web/)
pnpm test                 # vitest
pnpm exec biome check .   # lint + format

# Backend
uvicorn markwritter.api.app:get_app --factory --reload
pytest tests/ -v
ruff check markwritter/ tests/
black markwritter/ tests/
```

## Architecture

- `markwritter/` — Python backend (core, parser, registry, executor, llm_client, api/)
- `web/src/` — Vite SPA frontend (components, pages, hooks, lib)
- `skills/` — Agent skill definitions
- `config.yaml` — LLM and app configuration

## Skill Routing

When a request matches an available skill, invoke it via the Skill tool first.

| Pattern | Skill |
|---------|-------|
| Planning, requirements, breakdown | `delivery-planning` |
| Code review, second opinion | `codex-second-review` |
| Skill creation/migration | `skill-authoring` |
| Orchestration, ambiguous requests | `main-agent-orchestration` |
| Frontend implementation | `frontend-implementation-core` |
| Debug, reproduce | `debug-reproduction` |

Available skills are in `~/.config/opencode/skills/`. Only route to skills that exist.

## Frontend Constraints (IMPORTANT)

**This project does NOT use Next.js.**

- Do NOT use App Router, Server Components, Server Actions, or `'use client'` directives.
- Routing uses `react-router-dom` (`BrowserRouter` + `Routes`), NOT Next.js file-system routing.
- Pages are standard React components under `web/src/`, NOT `app/` directory.
- Fetch data via FastAPI REST endpoints, NOT server-side functions.
- The `nextjs-app-router` skill is NOT applicable to this project; ignore its suggestions.

## Backend Constraints

- FastAPI routes go in `markwritter/api/routes/`.
- Business logic in `markwritter/api/services/`.
- Pydantic models in `markwritter/api/models/`.
- LLM calls go through `LiteLLM`; do not import `openai` directly.
