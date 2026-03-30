# Task 05: Add Citation Event Support in Frontend

## Priority: P1

## Problem

The backend supports citations in the chat graph, but the frontend doesn't render them. The citation event type is missing from the TypeScript types, and there's no UI component to display citations.

## Current State

### Backend (already supports citations)

File: `markwritter/api/models/chat.py`

```python
class ChatEvent(BaseModel):
    type: str  # "thinking", "text_delta", "done", "error", "citation"
    content: Optional[str] = None
    citation: Optional[Citation] = None

class Citation(BaseModel):
    file_path: str
    page_num: int
    paragraph_idx: int
    text_snippet: str
```

### Frontend (missing citation support)

File: `web/lib/types.ts`

```typescript
export type ChatEventType =
  | "thinking"
  | "text_delta"
  | "sources"
  | "done"
  | "error";
// MISSING: "citation"

export interface ChatEvent {
  type: ChatEventType;
  content: string;
  // MISSING: citation field
}
```

## What To Build

### Step 1: Update TypeScript types

File: `web/lib/types.ts`:

```typescript
export type ChatEventType =
  | "thinking"
  | "text_delta"
  | "sources"
  | "citation"  // ADD
  | "done"
  | "error";

export interface Citation {
  file_path: string;
  page_num: number;
  paragraph_idx: number;
  text_snippet: string;
}

export interface ChatEvent {
  type: ChatEventType;
  content: string;
  citation?: Citation;  // ADD
  sources?: StreamSource[];
}
```

### Step 2: Update SSE parser to handle citations

File: `web/lib/sse.ts` - should already work if types are updated.

### Step 3: Create Citation component

File: `web/components/chat/citation-badge.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { Info } from 'lucide-react';

interface CitationBadgeProps {
  number: number;
  citation: Citation;
}

export function CitationBadge({ number, citation }: CitationBadgeProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setShowTooltip(!showTooltip)}
        className="inline-flex items-center justify-center w-5 h-5 text-xs bg-blue-500 text-white rounded hover:bg-blue-600 align-super mx-0.5"
      >
        {number}
      </button>

      {showTooltip && (
        <div className="absolute bottom-full left-0 mb-2 p-3 bg-gray-900 text-white text-sm rounded-lg shadow-lg z-50 w-64">
          <div className="font-semibold mb-1">{citation.file_path}</div>
          {citation.page_num > 0 && (
            <div className="text-gray-300 mb-1">Page {citation.page_num}</div>
          )}
          <div className="text-gray-200 italic border-l-2 border-gray-600 pl-2">
            "{citation.text_snippet}"
          </div>
          <div
            className="absolute bottom-0 left-4 transform translate-y-1/2 -translate-x-1/2"
            style={{
              width: 0,
              height: 0,
              borderLeft: '6px solid transparent',
              borderRight: '6px solid transparent',
              borderTop: '6px solid #1f2937',
            }}
          />
        </div>
      )}
    </div>
  );
}
```

### Step 4: Render citations in chat messages

File: `web/components/chat/chat-session.tsx`:

```typescript
import { CitationBadge } from './citation-badge';

// In the message rendering logic:
function renderMessageContent(content: string, citations?: Citation[]) {
  if (!citations || citations.length === 0) {
    return <p className="whitespace-pre-wrap">{content}</p>;
  }

  // Replace [1], [2], etc. with citation badges
  const parts = content.split(/(\[\d+\])/g);

  return (
    <p className="whitespace-pre-wrap">
      {parts.map((part, i) => {
        const match = part.match(/\[(\d+)\]/);
        if (match) {
          const citationNum = parseInt(match[1], 10);
          const citation = citations[citationNum - 1];
          if (citation) {
            return (
              <CitationBadge
                key={i}
                number={citationNum}
                citation={citation}
              />
            );
          }
        }
        return part;
      })}
    </p>
  );
}
```

### Step 5: Store citations in message

File: `web/lib/store.ts` - Update `useChatStore`:

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];  // ADD
  timestamp: number;
}

// In addMessage:
addMessage: (message) =>
  set((state) => ({
    messages: [
      ...state.messages,
      {
        ...message,
        id: crypto.randomUUID(),
        timestamp: Date.now(),
      },
    ],
  })),
```

### Step 6: Handle citation events in use-chat hook

File: `web/hooks/use-chat.ts`:

```typescript
// In the SSE event handler:
case 'citation':
  const citationData = JSON.parse(event.content);
  setCurrentCitations((prev) => [...prev, citationData]);
  break;
```

## Implementation Steps

1. **Update `web/lib/types.ts`** - Add citation types
2. **Create `web/components/chat/citation-badge.tsx`** - Citation display component
3. **Update `web/components/chat/chat-session.tsx`** - Render citations in messages
4. **Update `web/hooks/use-chat.ts`** - Handle citation events
5. **Update `web/lib/store.ts`** - Store citations with messages

## Files to Modify

- `web/lib/types.ts`
- `web/components/chat/citation-badge.tsx` (new)
- `web/components/chat/chat-session.tsx`
- `web/hooks/use-chat.ts`
- `web/lib/store.ts`

## Files to Read First

- `web/lib/types.ts` - Current types
- `web/hooks/use-chat.ts` - Current chat hook
- `web/components/chat/chat-session.tsx` - Current message rendering

## Tests

Update `web/components/chat/chat-session.test.tsx`:
- Test citation badges render correctly
- Test clicking badge shows tooltip
- Test citation data is preserved
