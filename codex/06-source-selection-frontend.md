# Task 06: Connect Frontend Source Selection to Backend API

## Priority: P1

## Problem

The frontend has a sources panel with file tree and checkbox selection, but the selected sources are only stored in the frontend Zustand store. The backend never receives them, so RAG retrieval can't filter by selected sources.

## Current State

### Frontend (sources stored locally only)

File: `web/lib/store.ts`:

```typescript
interface ChatState {
  selectedSources: string[];  // Stored in Zustand, never sent to backend
  // ...
}
```

File: `web/components/chat/sources-panel.tsx`:
- Has file tree with checkboxes
- Selection stored via `useChatStore`
- **Never calls backend API to persist**

### Backend (has API but frontend doesn't call it)

File: `markwritter/api/routes/chat.py`:

```python
@router.post("/sources")
async def select_sources(request: SourceSelectionRequest) -> SourceSelectionResponse:
    """Select sources for a chat session."""
    chat_db = await get_chat_db()
    await chat_db.save_session(request.session_id, request.source_paths)
    # ...
```

## What To Build

### Step 1: Add backend API calls to frontend

File: `web/lib/api.ts` - Add source selection functions:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface SourceSelectionRequest {
  session_id: string;
  source_paths: string[];
}

export interface SourceSelectionResponse {
  session_id: string;
  selected_sources: string[];
  count: number;
}

export async function selectSources(
  request: SourceSelectionRequest
): Promise<SourceSelectionResponse> {
  const response = await fetch(`${API_BASE}/api/v1/chat/sources`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Failed to select sources');
  return response.json();
}

export async function getSelectedSources(
  session_id: string
): Promise<SourceSelectionResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/chat/sources?session_id=${encodeURIComponent(session_id)}`
  );
  if (!response.ok) throw new Error('Failed to get sources');
  return response.json();
}

export async function clearSources(
  session_id: string
): Promise<{ success: boolean; session_id: string; message: string }> {
  const response = await fetch(
    `${API_BASE}/api/v1/chat/sources?session_id=${encodeURIComponent(session_id)}`,
    { method: 'DELETE' }
  );
  if (!response.ok) throw new Error('Failed to clear sources');
  return response.json();
}
```

### Step 2: Update sources panel to call API

File: `web/components/chat/sources-panel.tsx`:

```typescript
'use client';

import { useCallback } from 'react';
import { useChatStore } from '@/lib/store';
import { selectSources, getSelectedSources } from '@/lib/api';
import { FileTree } from './file-tree';

export function SourcesPanel() {
  const { selectedSources, setSelectedSources, sessionId } = useChatStore();

  const handleSourceToggle = useCallback(async (path: string, selected: boolean) => {
    const newSources = selected
      ? [...selectedSources, path]
      : selectedSources.filter((s) => s !== path);

    // Update local state optimistically
    setSelectedSources(newSources);

    // Persist to backend
    try {
      await selectSources({
        session_id: sessionId,
        source_paths: newSources,
      });
    } catch (error) {
      console.error('Failed to save sources:', error);
      // Revert on error
      setSelectedSources(selectedSources);
    }
  }, [selectedSources, setSelectedSources, sessionId]);

  // Load sources on mount
  useEffect(() => {
    getSelectedSources(sessionId)
      .then((response) => {
        setSelectedSources(response.selected_sources);
      })
      .catch((error) => {
        console.error('Failed to load sources:', error);
      });
  }, [sessionId, setSelectedSources]);

  return (
    <div className="h-full overflow-auto border-r">
      <div className="p-4 border-b">
        <h2 className="font-semibold mb-2">Sources</h2>
        <p className="text-sm text-gray-500">
          {selectedSources.length} selected
        </p>
      </div>
      <FileTree
        selectedPaths={selectedSources}
        onPathToggle={handleSourceToggle}
      />
    </div>
  );
}
```

### Step 3: Add session ID management

File: `web/lib/store.ts` - Ensure session ID is persisted:

```typescript
interface ChatState {
  sessionId: string;
  selectedSources: string[];
  // ...
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      sessionId: crypto.randomUUID(),  // Generate on init
      selectedSources: [],
      // ...
    }),
    { name: 'chat-storage' }
  )
);
```

### Step 4: Pass sources to chat API

File: `web/lib/api.ts` - Update `sendMessage`:

```typescript
export interface ChatRequestBody {
  message: string;
  session_id: string;
  sources?: string[];  // Already defined, just ensure it's used
  conversation_history?: ConversationMessage[];
}

export async function sendMessage(body: ChatRequestBody): Promise<Response> {
  return fetch(`${API_BASE}/api/v1/chat/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}
```

File: `web/hooks/use-chat.ts` - Pass sources when sending:

```typescript
const handleSubmit = useCallback(async (input: string) => {
  addMessage({ role: 'user', content: input });
  setStreaming(true);

  const abortController = new AbortController();

  try {
    const response = await sendMessage({
      message: input,
      session_id: sessionId,
      sources: selectedSources,  // PASS SOURCES
      conversation_history: messages.map((m) => ({
        role: m.role,
        content: m.content,
      })),
    });

    // ... process SSE stream
  } catch (error) {
    // ...
  }
}, [sessionId, selectedSources, messages]);
```

## Implementation Steps

1. **Add API functions** to `web/lib/api.ts`
2. **Update `SourcesPanel`** to call API on selection change
3. **Load sources on mount** from backend
4. **Pass sources to chat** in `use-chat.ts`
5. **Ensure session ID** is persisted and used consistently

## Files to Modify

- `web/lib/api.ts` - Add source selection API functions
- `web/components/chat/sources-panel.tsx` - Wire up API calls
- `web/hooks/use-chat.ts` - Pass sources to chat
- `web/lib/store.ts` - Verify session ID persistence

## Files to Read First

- `web/lib/api.ts` - Current API client
- `web/components/chat/sources-panel.tsx` - Current panel
- `web/hooks/use-chat.ts` - Current chat hook
- `markwritter/api/routes/chat.py` - Backend source selection endpoints

## Tests

- Test sources are saved to backend on selection
- Test sources are loaded on page refresh
- Test sources are sent with chat requests
- Test error handling when backend is unavailable
