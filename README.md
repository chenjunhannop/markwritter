# Markwritter

**AI-Native Knowledge Management Tool**

> Markwritter = Obsidian + memU + AI Agent

An AI-native knowledge management tool that transforms note-taking from simple storage into intelligent thinking extension.

## Overview

Markwritter is an AI-powered intelligent note-taking application built on Obsidian's Markdown file system. It provides three core modules: Query, Record, and Explore.

### Key Features

- **Query Module**: Natural language search, semantic retrieval, intelligent Q&A
- **Record Module**: Quick capture, AI-assisted writing, template system
- **Explore Module**: Knowledge graph, relationship discovery, topic clustering

### Core Value

```
Traditional Note Tools: Store -> Search -> Forget
Markwritter:           Store -> Organize -> Connect -> Utilize
```

| Dimension | Traditional Tools | Markwritter |
|-----------|------------------|-------------|
| **Capture** | Manual input | AI-assisted, voice input, web clipping |
| **Organize** | Manual categorization | Auto-classification, semantic clustering |
| **Retrieve** | Keyword search | Semantic search, natural language Q&A |
| **Connect** | Manual links | Auto-discover relationships, knowledge graph |
| **Utilize** | Copy-paste | AI-generated summaries, intelligent Q&A |

## Architecture

```
markwritter/
├── markwritter/          # Python backend core
│   ├── core.py           # Framework orchestrator
│   ├── parser.py         # Intent parser
│   ├── registry.py       # Skill registry
│   ├── executor.py       # Skill executor
│   ├── llm_client.py     # LLM client (LiteLLM)
│   ├── config.py         # Configuration
│   └── api/              # FastAPI REST API
│       ├── app.py        # API entry point
│       ├── routes/       # API routes
│       ├── models/       # Pydantic models
│       └── services/     # Business logic
├── web/                  # Next.js frontend
│   ├── app/              # App Router pages
│   ├── components/       # React components
│   ├── lib/              # Utilities
│   └── hooks/            # React hooks
├── skills/               # Skill definitions
├── tests/                # Test suite
├── note/                 # Design documentation
└── docs/                 # Project documentation
```

## Tech Stack

| Layer | Technology | Version |
|-------|------------|---------|
| **Frontend** | Next.js | 15.x |
| **UI Library** | Radix UI + Tailwind | 4.x |
| **State Management** | Zustand | 5.x |
| **Backend** | FastAPI | latest |
| **AI Orchestration** | LangGraph | 1.x |
| **Memory Service** | memU | latest |
| **Database** | SQLite / PostgreSQL | - |
| **Vector Search** | pgvector / FAISS | - |
| **Desktop** | Tauri (planned) | 2.x |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- pnpm (recommended)

### Backend Setup

```bash
# Install Python dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Configure LLM (optional, for AI features)
# Edit config.yaml with your LLM settings
```

### Frontend Setup

```bash
cd web

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

### Running the API Server

```bash
# Start FastAPI server
uvicorn markwritter.api.app:get_app --factory --reload

# API will be available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## CLI Usage

```bash
# List available skills
markwritter list-skills

# Interactive chat mode
markwritter chat
```

## Project Status

### ✅ Completed (v0.1.1.0 - 2026-03-30)

- [x] Core framework skeleton
- [x] Registry and Parser
- [x] Executor and subagent execution
- [x] CLI interface
- [x] FastAPI backend
- [x] Next.js frontend foundation
- [x] LiteLLM integration
- [x] **Chat with Sources MVP**
  - [x] LangGraph chat orchestration
  - [x] RAG search with source selection
  - [x] Chat session persistence (SQLite)
  - [x] SSE streaming with citations
  - [x] Vector search cache
  - [x] Path → ContentID resolver
  - [x] Watchdog file watcher

### 🎯 In Progress (Phase 2)

- [ ] AI Writing Assist (continue, rewrite, polish)
- [ ] Content Summarization (single & multi-note)
- [ ] Knowledge Graph Basics (visualization, link suggestions)

### 📋 Planned

- [ ] Web clipping (URL extraction, auto-tagging)
- [ ] Vector search (pgvector/FAISS integration)
- [ ] Voice recording (ASR integration)
- [ ] Desktop app (Tauri)
- [ ] Cloud sync
- [ ] Plugin system

## Development

### Running Tests

```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd web
pnpm test

# E2E tests
pnpm test:e2e
```

### Code Quality

```bash
# Format code
black markwritter/ tests/

# Lint
ruff check markwritter/ tests/
```

## Documentation

### Product & Design
- [Transformation Plan](note/note-app-transformation-plan.md) - Full product roadmap
- [Framework Design](note/framework-design.md) - Architecture details
- [GUI Implementation](note/gui-implementation-plan.md) - Frontend design
- [LiteLLM Integration](note/litellm-integration-plan.md) - LLM configuration

### Figma Design System
- [Figma Design Specification](docs/figma-design-spec.md) - Complete design system specs
- [Figma Wireframes](docs/figma-wireframes.md) - Page layouts and component structures
- [Figma Implementation Guide](docs/figma-implementation-guide.md) - Step-by-step guide

## License

MIT