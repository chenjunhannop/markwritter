# Markwritter Code Map

> **Last Updated:** 2026-03-23
> **Entry Points:** `markwritter/cli.py`, `api/main.py`, `web/app/`

---

## Architecture Overview

```
+-------------------+     +-------------------+     +-------------------+
|   CLI (Typer)     |     |   API (FastAPI)   |     |   Web (Next.js)   |
|   markwritter     |     |   :8000           |     |   :3000           |
+-------------------+     +-------------------+     +-------------------+
          |                        |                        |
          v                        v                        v
+-------------------------------------------------------------------+
|                    Core Framework (markwritter/)                   |
|  +----------+  +----------+  +----------+  +----------+           |
|  |  core    |  |  parser  |  | registry |  | executor |           |
|  +----------+  +----------+  +----------+  +----------+           |
+-------------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------------+
|                         Skills (skills/)                          |
|  +----------+  +----------+  +----------+  +----------+           |
|  |  query   |  |  record  |  | explore  |  |  custom  |           |
|  +----------+  +----------+  +----------+  +----------+           |
+-------------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------------+
|                     External Services                             |
|  +----------+  +----------+  +----------+  +----------+           |
|  |  memU    |  | LangGraph|  | LiteLLM  |  | Obsidian |           |
|  | (memory) |  |  (AI)    |  |  (LLM)   |  |  Vault   |           |
|  +----------+  +----------+  +----------+  +----------+           |
+-------------------------------------------------------------------+
```

---

## Key Modules

### Backend Core (`markwritter/`)

| Module | Purpose | Exports | Dependencies |
|--------|---------|---------|--------------|
| `core.py` | Framework orchestrator | `Framework` | parser, registry, executor, llm_client |
| `parser.py` | Intent parsing | `InputParser`, `Intent` | llm_client |
| `registry.py` | Skill management | `SkillRegistry`, `Skill` | pyyaml |
| `executor.py` | Skill execution | `SkillExecutor`, `ExecutionResult` | subprocess |
| `llm_client.py` | LLM integration | `LLMClient` | litellm |
| `config.py` | Configuration | `get_config()`, `Config` | pyyaml |
| `cli.py` | CLI interface | `main()` | typer |
| `models.py` | Data models | Various Pydantic models | pydantic |
| `logger.py` | Logging utilities | `get_logger()` | logging |

### API Layer (`api/`)

| Module | Purpose | Endpoints |
|--------|---------|-----------|
| `main.py` | FastAPI app | `/docs`, `/redoc` |
| `routers/` | API routes | `/api/query`, `/api/record`, `/api/explore` |
| `models/` | Request/response models | Pydantic models |
| `services/` | Business logic | Service classes |

### Frontend (`web/`)

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `app/` | Next.js pages | `page.tsx`, `layout.tsx` |
| `components/` | React components | UI components |
| `lib/` | Utilities | Helpers, API client |
| `hooks/` | Custom hooks | React hooks |
| `e2e/` | E2E tests | Playwright tests |

### Skills (`skills/`)

| Skill | Purpose | Files |
|-------|---------|-------|
| `hello` | Example skill | `skill.yaml`, `run.py` |

---

## Data Flow

```
User Input
    |
    v
+-------------------+
| Parser            | -- Parse intent, extract skill name and params
+-------------------+
    |
    v
+-------------------+
| Registry          | -- Look up skill definition
+-------------------+
    |
    v
+-------------------+
| Executor          | -- Execute skill as subprocess
+-------------------+
    |
    v
+-------------------+
| Skill Output      | -- Return result to user
+-------------------+
```

---

## Configuration

### config.yaml

```yaml
llm:
  default_model: "gpt-4o-mini"
  api_base: "https://api.openai.com/v1"

skills:
  directory: "skills"

logging:
  level: "INFO"
  file: "logs/markwritter.log"
```

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| typer | >=0.9.0 | CLI framework |
| pydantic | >=2.0.0 | Data validation |
| pyyaml | >=6.0 | YAML parsing |
| litellm | >=1.0.0 | LLM abstraction |
| fastapi | >=0.100.0 | REST API |
| uvicorn | >=0.23.0 | ASGI server |

---

## Related Areas

- [Project Overview](OVERVIEW.md)
- [Transformation Plan](../note/note-app-transformation-plan.md)
- [Framework Design](../note/framework-design.md)