# Frontend-Backend UI Verification Report

**Date:** 2026-03-27
**Scope:** API path matching + UI interaction testing for all 7 frontend pages
**Tools:** Static code analysis + agent-browser (Playwright)

---

## 1. API Path Matching Matrix

### 1.1 Status Summary

| Status | Count | Description |
|--------|-------|-------------|
| MATCH | 12 | Fully compatible (path + method + schema) |
| FIELD_MISMATCH | 5 | Path matches but request body differs |
| MISMATCH | 2 | Path or HTTP method differs |
| MISSING_BACKEND | 2 | Frontend calls non-existent endpoint |
| MISSING_FRONTEND | 22 | Backend endpoint unused by frontend |

### 1.2 Detailed Matching Table

#### Core API (api.ts)

| Function | Method | Frontend Path | Backend Path | Status |
|----------|--------|---------------|--------------|--------|
| `sendMessage()` | POST | `/api/chat/message` | `/api/chat/` | **MISMATCH** |
| `getSkills()` | GET | `/api/skills` | `/api/skills/` | MATCH (deprecated) |
| `getSkill(name)` | GET | `/api/skills/{name}` | `/api/skills/{skill_name}` | MATCH (deprecated) |
| `executeSkill(name, params)` | POST | `/api/skills/{name}/execute` | `/api/skills/{skill_name}/run` | **MISMATCH** |
| `getSettings()` | GET | `/api/settings` | (none) | **MISSING_BACKEND** |
| `updateSettings(settings)` | PUT | `/api/settings` | (none) | **MISSING_BACKEND** |

#### Query API (query-api.ts)

| Function | Method | Path | Status |
|----------|--------|------|--------|
| `keywordSearch()` | POST | `/api/v1/query/search` | MATCH |
| `semanticSearch()` | POST | `/api/v1/query/semantic` | MATCH |
| `hybridSearch()` | POST | `/api/v1/query/hybrid` | MATCH |
| `askQuestion()` | POST | `/api/v1/query/ask` | MATCH |
| `askQuestionStream()` | POST | `/api/v1/query/ask/stream` | MATCH |
| `getSuggestions()` | GET | `/api/v1/query/suggest` | MATCH |

#### Record API (record-api.ts)

| Function | Method | Path | Status |
|----------|--------|------|--------|
| `createRecord()` | POST | `/api/v1/record/create` | **FIELD_MISMATCH** |
| `updateRecord()` | PUT | `/api/v1/record/update` | **FIELD_MISMATCH** |
| `aiContinueStream()` | POST | `/api/v1/record/ai-assist/continue/stream` | **FIELD_MISMATCH** |
| `aiRewrite()` | POST | `/api/v1/record/ai-assist/rewrite` | **FIELD_MISMATCH** |
| `aiPolish()` | POST | `/api/v1/record/ai-assist/polish` | **FIELD_MISMATCH** |
| `classifyNote()` | POST | `/api/v1/record/classify` | MATCH |
| `suggestTags()` | POST | `/api/v1/record/suggest/tags` | MATCH |
| `suggestFolder()` | POST | `/api/v1/record/suggest/folder` | MATCH |

#### Explore API (explore-api.ts)

| Function | Method | Path | Status |
|----------|--------|------|--------|
| `getKnowledgeGraph()` | GET | `/api/v1/explore/graph` | MATCH |
| `getNodeGraph(path)` | GET | `/api/v1/explore/graph/{path}` | MATCH |
| `getRelatedNotes(path, depth)` | GET | `/api/v1/explore/related/{path}` | MATCH |

#### Logs (LogStream.tsx)

| Component | Method | Path | Status |
|-----------|--------|------|--------|
| `LogStream` | GET (SSE) | `/api/logs/stream` | MATCH (deprecated) |

---

## 2. UI Interaction Test Results

### 2.1 Test Environment

- Backend: `http://localhost:8000` (uvicorn, Python 3.10)
- Frontend: `http://localhost:3000` (Next.js dev server)
- Tool: agent-browser (Playwright)

### 2.2 Page-by-Page Results

#### Chat (`/chat`) - PASS (UI) / FAIL (API)

| Check | Result | Detail |
|-------|--------|--------|
| Page renders | PASS | Chat interface with message input and send button |
| Send button disabled when empty | PASS | Button correctly disabled with no content |
| Send button enabled with text | PASS | Button enables after typing |
| Sidebar navigation highlight | PASS | "Chat" button highlighted as active |
| API connectivity | **FAIL** | `sendMessage()` calls wrong path `/api/chat/message` |

#### Skills (`/skills`) - PASS (UI) / FAIL (API)

| Check | Result | Detail |
|-------|--------|--------|
| Skill cards load | PASS | At least one skill card rendered with Run/Edit buttons |
| Search filtering | PASS | Typing in search box filters results, Clear button appears |
| API list endpoint | PASS | `GET /api/skills` returns 200 (deprecated route works) |
| Skill execution | **FAIL** | `executeSkill()` uses wrong suffix `/execute` vs `/run` |

#### Logs (`/logs`) - PASS (UI) / PASS (API)

| Check | Result | Detail |
|-------|--------|--------|
| Log level filters render | PASS | Buttons: all/DEBUG/INFO/WARNING/ERROR |
| SSE connection | PASS | Uses deprecated `/api/logs/stream` which works |
| Sidebar navigation | PASS | "Logs" button highlighted |

#### Settings (`/settings`) - WARN (UI) / FAIL (API)

| Check | Result | Detail |
|-------|--------|--------|
| Page renders | PASS | Header + basic settings displayed |
| Theme selector | PASS | Shows "system" theme |
| Language selector | PASS | Shows "en" language |
| Full SettingsPanel | **WARN** | Only basic General Settings shown, missing VaultConfig/LLMConfig |
| API connectivity | **FAIL** | `getSettings()` / `updateSettings()` call non-existent `/api/settings` |

#### Explore (`/explore`) - PASS (UI) / WARN (API)

| Check | Result | Detail |
|-------|--------|--------|
| Page renders | PASS | "Knowledge Graph" heading, Refresh/Load Graph buttons |
| Error handling | PASS | Shows error when vault not configured (503) |
| Graph visualization | WARN | Cannot test without vault configured |
| API path | PASS | Frontend paths match backend exactly |

#### Query (`/query`) - PASS (UI) / PASS (API)

| Check | Result | Detail |
|-------|--------|--------|
| Search mode selector | PASS | Hybrid/Keyword/Semantic options |
| Search input | PASS | Placeholder "Search your notes..." |
| Search button disabled when empty | PASS | Correct behavior |
| Search button enabled with text | PASS | Enables after typing, Clear button appears |
| All 6 API paths | PASS | All query API endpoints fully compatible |

#### Record (`/record`) - PASS (UI) / FAIL (API)

| Check | Result | Detail |
|-------|--------|--------|
| Tab switching | PASS | Quick Record / Full Editor tabs |
| Quick Record input | PASS | Textarea with Save button |
| Save button state | PASS | Disabled when empty, enabled with content |
| Full Editor toolbar | PASS | Bold/Italic/Heading/Quote/List/Link/Code/Code block/Wikilink/Callout |
| AI assist buttons | PASS | Continue/Rewrite/Polish/Suggest (disabled when empty) |
| Note creation | **FAIL** | `createRecord()` body schema incompatible with backend |
| Note update | **FAIL** | `updateRecord()` uses `id` instead of `path` |
| AI continue/rewrite/polish | **FAIL** | Frontend sends `record_id` field not in backend schema |

### 2.3 Cross-Page Navigation

| Check | Result | Detail |
|-------|--------|--------|
| Root `/` redirects to `/chat` | PASS | Chat page renders at root |
| Sidebar navigation | PASS | Chat/Skills/Logs/Settings all accessible via sidebar |
| Direct URL navigation | PASS | All 7 pages load via direct URL |
| Page transitions | PASS | No console errors on navigation |

---

## 3. Issues Summary

### 3.1 Critical (Blocks Functionality)

| # | Component | Issue | Impact |
|---|-----------|-------|--------|
| 1 | Chat | `sendMessage()` path mismatch: `/api/chat/message` vs `/api/chat/` | Chat completely broken |
| 2 | Skills | `executeSkill()` suffix mismatch: `/execute` vs `/run` | Skill execution returns 404 |
| 3 | Settings | No backend `/api/settings` endpoint | Settings cannot load or save |
| 4 | Record | `createRecord()` body schema mismatch (missing `path`, extra fields) | Note creation fails |
| 5 | Record | `updateRecord()` uses `id` instead of `path` | Note update fails |
| 6 | Record | AI assist endpoints receive extra `record_id` field | AI context lost |

### 3.2 Warning (Works but Suboptimal)

| # | Component | Issue | Impact |
|---|-----------|-------|--------|
| 7 | Skills/Logs | Uses deprecated `/api/` prefix instead of `/api/v1/` | Works but should migrate |
| 8 | Settings | Only basic settings UI rendered, missing VaultConfig/LLMConfig | Incomplete settings experience |
| 9 | Explore | Cannot test without vault configuration | UI correct but data-dependent |

### 3.3 Architecture Gaps

| # | Gap | Detail |
|---|-----|--------|
| 10 | Content module unused | 5 endpoints at `/api/v1/content/*` have zero frontend consumers |
| 11 | Notes API unused | 6 endpoints at `/api/v1/notes/*` unused by frontend (uses deprecated record API) |
| 12 | Search duplication | Two search systems (`search.py` vs `query.py`), frontend only uses query.py |
| 13 | Schema divergence | Frontend uses `id`/`title`/`folder_id`, backend uses `path`/`content`/`metadata` |

---

## 4. Fix Recommendations

### Priority 1: Fix Critical API Mismatches

1. **Chat path**: Update frontend `sendMessage()` to call `POST /api/v1/chat/` (or add backend route at `/api/v1/chat/message`)
2. **Skill execution suffix**: Change frontend `executeSkill()` to use `/run` instead of `/execute`
3. **Settings endpoint**: Implement `GET/PUT /api/v1/settings` in the backend, or remove settings UI
4. **Record CRUD schema**: Align frontend body schema with backend - use `path` instead of `id`, include required `path` field in create
5. **AI assist fields**: Either remove `record_id` from frontend or add it to backend schema

### Priority 2: Migrate Deprecated Routes

6. Update `getSkills()`, `getSkill()`, `LogStream` to use `/api/v1/` prefix
7. Migrate record frontend from deprecated `/api/v1/record/create` to `/api/v1/notes`

### Priority 3: Fill Frontend Gaps

8. Build frontend UI for Content module (`/api/v1/content/*`)
9. Migrate frontend record pages to use Notes API (`/api/v1/notes/*`)
10. Integrate full SettingsPanel (VaultConfig + LLMConfig) into Settings page

### Priority 4: Clean Up

11. Remove redundant `search.py` routes if query.py covers all use cases
12. Remove deprecated route registrations once all frontend calls use `/api/v1/`
