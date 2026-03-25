# Markwritter Project Overview

> **Last Updated:** 2026-03-23
> **Version:** 1.0.0-alpha

---

## Product Vision

**Markwritter = Obsidian + memU + AI Agent**

An AI-native knowledge management tool that transforms note-taking from simple storage into intelligent thinking extension.

### Target Users

| User Group | Pain Points | Solution |
|------------|-------------|----------|
| Knowledge Workers | Fragmented information, hard to integrate | AI auto-extracts key info, builds connections |
| Learners | Many study materials, low review efficiency | Intelligent Q&A, knowledge graph-assisted review |
| Researchers | Complex literature management, difficult relation discovery | Auto-summary, semantic search, topic clustering |
| Creators | Low writing efficiency, easy to lose inspiration | Quick capture, AI-assisted expansion |

---

## Architecture Overview

```
+-------------------------------------------------------------------------+
|                              Frontend Layer                              |
|  +-------------+  +-------------+  +----------------------------------+  |
|  | Query UI    |  | Record UI   |  | Explore UI                       |  |
|  | - NL Search |  | - Quick Note|  | - Knowledge Graph Visualization  |  |
|  | - RAG       |  | - AI Assist |  | - Relation Discovery             |  |
|  | - Q&A       |  | - Templates |  | - Topic Clustering               |  |
|  +-------------+  +-------------+  +----------------------------------+  |
+-------------------------------------------------------------------------+
                                    |
                                    | HTTP / SSE / WebSocket
                                    v
+-------------------------------------------------------------------------+
|                              API Layer                                   |
|  +-------------+  +-------------+  +----------------------------------+  |
|  | /api/query  |  | /api/record |  | /api/explore                     |  |
|  | - search    |  | - create    |  | - graph                          |  |
|  | - ask       |  | - update    |  | - relations                      |  |
|  | - suggest   |  | - ai-assist |  | - clusters                       |  |
|  +-------------+  +-------------+  +----------------------------------+  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                           Core Service Layer                             |
|  +-------------------------------------------------------------------+  |
|  |                    Memory Service (memU Integration)              |  |
|  |  Memorize  |  Retrieve  |  CRUD  |  Workflow Engine              |  |
|  +-------------------------------------------------------------------+  |
|  +-------------------------------------------------------------------+  |
|  |                    AI Agent (LangGraph Orchestration)             |  |
|  |  Director  |  Query Agent  |  Record Agent  |  Explore Agent     |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                              Data Layer                                  |
|  +-------------------------------------------------------------------+  |
|  |                   Obsidian Vault (Markdown Files)                 |  |
|  |  Notes  |  Attachments  |  Canvas  |  YAML Frontmatter           |  |
|  +-------------------------------------------------------------------+  |
|  +-------------------------------------------------------------------+  |
|  |                   Vector Store (Vector Index)                     |  |
|  |  Embeddings  |  Index  |  SQLite / PostgreSQL + pgvector         |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

---

## Three Core Modules

### 1. Query Module

**Purpose**: Help users find and understand their notes.

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Natural Language Search | Users describe needs in natural language | LLM intent parsing + RAG |
| Semantic Retrieval | Vector similarity-based retrieval | memU retrieve (RAG mode) |
| Keyword Search | Traditional full-text search | SQLite FTS5 / PostgreSQL |
| Intelligent Q&A | Q&A based on note content | LLM + RAG |
| Search Suggestions | Context-aware suggestions | LLM generation |

### 2. Record Module

**Purpose**: Help users capture and organize information.

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Quick Capture | Simple text input with auto-processing | Markdown editor |
| AI Writing Assist | Continue, rewrite, polish | LLM Agent |
| Template System | Pre-defined templates with variables | YAML templates |
| Web Clipping | Extract content from web pages | defuddle extraction |
| Voice Recording | Voice-to-text capture | ASR service |
| Auto-classification | Automatic content categorization | memU memorize |
| Relation Suggestions | Suggest connections to existing notes | Vector similarity + knowledge graph |

### 3. Explore Module

**Purpose**: Help users discover connections and patterns.

| Feature | Description | Implementation |
|---------|-------------|----------------|
| Knowledge Graph | Visualize note relationships | D3.js / React Flow |
| Relation Discovery | Find hidden connections | Vector similarity + LLM analysis |
| Topic Clustering | Group notes by topic | Vector clustering + LLM naming |
| Timeline | Browse note evolution over time | Time index + visualization |
| Random Walk | Discover unexpected connections | Graph random walk algorithm |

---

## Data Flow

```
User Input (Query/Record)
         |
         v
+------------------------------------------------------------------+
|  Frontend Layer (Next.js App Router)                             |
|  /query   - Query interface                                       |
|  /record  - Record interface                                      |
|  /explore - Explore interface                                     |
|  /notes/* - Note details                                          |
+------------------------------------------------------------------+
         |
         | HTTP/SSE
         v
+------------------------------------------------------------------+
|  API Layer (FastAPI)                                             |
|  POST /api/query    - Handle queries                              |
|  POST /api/record   - Handle records                              |
|  GET  /api/explore  - Get graph data                              |
|  WS   /api/chat     - Real-time conversation                      |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  Service Layer                                                    |
|  Markwritter Core: Parser, Registry, Executor                    |
|  Skills: query-skill, record-skill, explore-skill                |
|  memU: MemoryService, memorize(), retrieve()                     |
|  LangGraph: Director Graph, specialized agents                   |
+------------------------------------------------------------------+
         |
         v
+------------------------------------------------------------------+
|  Data Layer                                                       |
|  Obsidian Vault: Markdown files, attachments, canvas             |
|  Vector Store: SQLite/PostgreSQL + embeddings                    |
+------------------------------------------------------------------+
```

---

## Obsidian Compatibility

Markwritter maintains 100% compatibility with Obsidian:

- **File Format**: Obsidian Flavored Markdown
- **Metadata**: YAML Frontmatter (title, tags, aliases, custom properties)
- **Links**: Wikilinks `[[Note Name]]`
- **Embeds**: `![[embed]]` syntax
- **Callouts**: `> [!type]` syntax
- **Directory Structure**: User's existing folder organization

---

## Implementation Roadmap

### Phase 1: MVP (4 weeks)

- [ ] Python backend framework
- [ ] memU integration
- [ ] Obsidian Vault file operations
- [ ] Keyword + semantic search
- [ ] Basic note editor
- [ ] Auto-classification
- [ ] Next.js frontend

### Phase 2: Core Experience (3 weeks)

- [ ] Intelligent Q&A
- [ ] AI writing assistance
- [ ] Content summarization
- [ ] Knowledge graph basics
- [ ] Relationship discovery

### Phase 3: Enhanced Features (3 weeks)

- [ ] Web clipping
- [ ] Voice recording
- [ ] Multi-vault support
- [ ] Desktop app (Tauri)
- [ ] Performance optimization

### Phase 4: Ecosystem (Ongoing)

- [ ] Plugin system
- [ ] Cloud sync
- [ ] Team collaboration

---

## Related Documentation

- [Transformation Plan](../note/note-app-transformation-plan.md) - Complete product roadmap
- [Framework Design](../note/framework-design.md) - Technical architecture
- [Frontend Modules Plan](../note/frontend-modules-plan.md) - Frontend implementation
- [GUI Implementation Plan](../note/gui-implementation-plan.md) - UI/UX design

---

**Maintainer**: Markwritter Team