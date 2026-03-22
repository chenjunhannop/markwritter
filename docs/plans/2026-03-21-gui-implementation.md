# Markwritter GUI 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 Markwritter 框架添加 Web GUI 界面，包括 Chat UI、Skill Manager 和日志监控功能。

**Architecture:** 前后端分离架构 - FastAPI 后端 API 层 + Next.js 14 前端，通过 SSE 实现流式通信，保持核心层不变。

**Tech Stack:** FastAPI, Pydantic, Next.js 14, Tailwind CSS, Zustand, SSE, Docker

---

## Task 1: 创建 FastAPI 应用骨架

**Files:**
- Create: `api/__init__.py`
- Create: `api/main.py`
- Create: `api/routers/__init__.py`
- Create: `api/models/__init__.py`
- Create: `api/services/__init__.py`

**Step 1: 创建 api 目录结构**

```bash
mkdir -p api/routers api/models api/services
touch api/__init__.py api/routers/__init__.py api/models/__init__.py api/services/__init__.py
```

**Step 2: 编写 FastAPI 主应用**

Create `api/main.py`:

```python
"""FastAPI application entry point for Markwritter API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import chat, skills, logs

app = FastAPI(
    title="Markwritter API",
    description="Agent orchestration framework API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills.router)
app.include_router(chat.router)
app.include_router(logs.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
```

**Step 3: 验证应用可启动**

Run: `uvicorn api.main:app --reload`
Expected: 应用启动在 http://localhost:8000

**Step 4: Commit**

```bash
git add api/
git commit -m "feat: add FastAPI application skeleton"
```

---

## Task 2: 实现 Framework 桥接服务

**Files:**
- Create: `api/services/framework_bridge.py`
- Test: `tests/test_framework_bridge.py`

**Step 1: 编写失败测试**

Create `tests/test_framework_bridge.py`:

```python
"""Tests for framework bridge service."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from api.services.framework_bridge import get_framework, reset_framework


class TestFrameworkBridge:
    """Test framework bridge service."""

    def setup_method(self):
        """Reset framework before each test."""
        reset_framework()

    def teardown_method(self):
        """Reset framework after each test."""
        reset_framework()

    def test_get_framework_returns_framework_instance(self):
        """Test that get_framework returns a Framework instance."""
        with patch("api.services.framework_bridge.SkillRegistry") as mock_registry:
            mock_registry.return_value = MagicMock()
            framework = get_framework()
            assert framework is not None

    def test_get_framework_returns_singleton(self):
        """Test that get_framework returns the same instance."""
        with patch("api.services.framework_bridge.SkillRegistry") as mock_registry:
            mock_registry.return_value = MagicMock()
            framework1 = get_framework()
            framework2 = get_framework()
            assert framework1 is framework2

    def test_reset_framework_clears_instance(self):
        """Test that reset_framework clears the cached instance."""
        with patch("api.services.framework_bridge.SkillRegistry") as mock_registry:
            mock_registry.return_value = MagicMock()
            framework1 = get_framework()
            reset_framework()
            framework2 = get_framework()
            # Different instances after reset
            assert framework1 is not framework2
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/test_framework_bridge.py -v`
Expected: FAIL - module not found

**Step 3: 实现最小代码**

Create `api/services/framework_bridge.py`:

```python
"""Framework bridge service - connects API layer to core Framework."""

from pathlib import Path
from typing import Optional

from markwritter.core import Framework
from markwritter.registry import SkillRegistry

_framework_instance: Optional[Framework] = None


def get_framework() -> Framework:
    """Get or create Framework singleton instance."""
    global _framework_instance
    if _framework_instance is None:
        skills_dir = Path("./skills").resolve()
        registry = SkillRegistry(skills_dir)
        _framework_instance = Framework(registry)
    return _framework_instance


def reset_framework() -> None:
    """Reset framework instance (mainly for testing)."""
    global _framework_instance
    _framework_instance = None
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_framework_bridge.py -v`
Expected: PASS - 3 tests

**Step 5: Commit**

```bash
git add api/services/framework_bridge.py tests/test_framework_bridge.py
git commit -m "feat: add framework bridge service with tests"
```

---

## Task 3: 实现 Skills API 端点

**Files:**
- Create: `api/routers/skills.py`
- Create: `api/models/skill.py`
- Test: `tests/test_skills_api.py`

**Step 1: 编写 API 模型**

Create `api/models/skill.py`:

```python
"""Skill API models."""

from typing import Any, Optional

from pydantic import BaseModel

from markwritter.models import SkillDefinition


class SkillResponse(BaseModel):
    """Response model for skill."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    inputs: list[dict[str, Any]] = []
    output: dict[str, str] = {}

    @classmethod
    def from_definition(cls, skill: SkillDefinition) -> "SkillResponse":
        """Create response from SkillDefinition."""
        return cls(
            name=skill.name,
            description=skill.description,
            version=skill.version,
            inputs=[i.model_dump() for i in skill.inputs],
            output=skill.output.model_dump(),
        )


class SkillRunRequest(BaseModel):
    """Request model for running a skill."""

    params: dict[str, Any] = {}


class SkillRunResponse(BaseModel):
    """Response model for skill execution."""

    success: bool
    output: str = ""
    error: str = ""
```

**Step 2: 编写失败测试**

Create `tests/test_skills_api.py`:

```python
"""Tests for Skills API."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


class TestSkillsAPI:
    """Test Skills API endpoints."""

    def test_list_skills_returns_list(self):
        """Test GET /api/skills returns a list."""
        response = client.get("/api/skills")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_skill_not_found(self):
        """Test GET /api/skills/{name} with non-existent skill."""
        response = client.get("/api/skills/nonexistent-skill-xyz")
        assert response.status_code == 404
```

**Step 3: 运行测试验证失败**

Run: `pytest tests/test_skills_api.py -v`
Expected: FAIL - router not implemented

**Step 4: 实现 Skills 路由**

Create `api/routers/skills.py`:

```python
"""Skills API router."""

from fastapi import APIRouter, HTTPException

from api.models.skill import SkillResponse
from api.services.framework_bridge import get_framework

router = APIRouter(prefix="/api/skills", tags=["skills"])


@router.get("/", response_model=list[SkillResponse])
async def list_skills():
    """List all available skills."""
    framework = get_framework()
    skills = framework.registry.list_all()
    return [SkillResponse.from_definition(s) for s in skills]


@router.get("/{skill_name}", response_model=SkillResponse)
async def get_skill(skill_name: str):
    """Get a specific skill by name."""
    framework = get_framework()
    skill = framework.registry.get(skill_name)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return SkillResponse.from_definition(skill)
```

**Step 5: 运行测试验证通过**

Run: `pytest tests/test_skills_api.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add api/routers/skills.py api/models/skill.py tests/test_skills_api.py
git commit -m "feat: add Skills API endpoints with tests"
```

---

## Task 4: 实现 Chat API (SSE 流式)

**Files:**
- Create: `api/routers/chat.py`
- Create: `api/models/chat.py`
- Test: `tests/test_chat_api.py`

**Step 1: 编写 Chat 模型**

Create `api/models/chat.py`:

```python
"""Chat API models."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Request model for chat."""

    message: str


class ChatEvent(BaseModel):
    """SSE event model for chat stream."""

    type: str  # thinking, text_delta, done, error
    content: str = ""
```

**Step 2: 编写失败测试**

Create `tests/test_chat_api.py`:

```python
"""Tests for Chat API."""

import pytest
from fastapi.testclient import TestClient
import json

from api.main import app


client = TestClient(app)


class TestChatAPI:
    """Test Chat API endpoints."""

    def test_chat_returns_sse_stream(self):
        """Test POST /api/chat returns SSE stream."""
        response = client.post(
            "/api/chat",
            json={"message": "hello"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    def test_chat_stream_contains_events(self):
        """Test that chat stream contains expected events."""
        response = client.post(
            "/api/chat",
            json={"message": "hello"},
        )
        # Read the stream
        content = response.text
        # Should contain SSE data lines
        assert "data:" in content or content == ""
```

**Step 3: 实现 Chat 路由**

Create `api/routers/chat.py`:

```python
"""Chat API router with SSE streaming."""

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.models.chat import ChatRequest, ChatEvent
from api.services.framework_bridge import get_framework

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/")
async def chat(request: ChatRequest):
    """Handle chat message and return SSE stream."""

    async def event_generator():
        framework = get_framework()

        # Send thinking status
        yield f"data: {json.dumps({'type': 'thinking'})}\n\n"

        try:
            # Process input through framework
            result = framework.process_input(request.message)

            # Stream the response character by character
            for char in result:
                event = ChatEvent(type="text_delta", content=char)
                yield f"data: {event.model_dump_json()}\n\n"

            # Send done event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            # Send error event
            event = ChatEvent(type="error", content=str(e))
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/test_chat_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add api/routers/chat.py api/models/chat.py tests/test_chat_api.py
git commit -m "feat: add Chat API with SSE streaming"
```

---

## Task 5: 实现日志流 API

**Files:**
- Create: `api/routers/logs.py`
- Test: `tests/test_logs_api.py`

**Step 1: 编写失败测试**

Create `tests/test_logs_api.py`:

```python
"""Tests for Logs API."""

import pytest
from fastapi.testclient import TestClient

from api.main import app


client = TestClient(app)


class TestLogsAPI:
    """Test Logs API endpoints."""

    def test_logs_stream_returns_sse(self):
        """Test GET /api/logs/stream returns SSE stream."""
        response = client.get("/api/logs/stream")
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
```

**Step 2: 实现日志路由**

Create `api/routers/logs.py`:

```python
"""Logs API router with SSE streaming."""

import asyncio
import queue
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/logs", tags=["logs"])

# Global log queue for cross-thread communication
log_queue: queue.Queue = queue.Queue()


def add_log_entry(entry: str) -> None:
    """Add a log entry to the stream queue."""
    log_queue.put(entry)


@router.get("/stream")
async def stream_logs():
    """Stream logs via SSE."""

    async def log_generator():
        while True:
            try:
                # Non-blocking get with timeout
                log_entry = log_queue.get(timeout=1.0)
                yield f"data: {log_entry}\n\n"
            except queue.Empty:
                # Send heartbeat to keep connection alive
                yield ": heartbeat\n\n"
            except asyncio.CancelledError:
                break

    return StreamingResponse(
        log_generator(),
        media_type="text/event-stream",
    )
```

**Step 3: 运行测试验证通过**

Run: `pytest tests/test_logs_api.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add api/routers/logs.py tests/test_logs_api.py
git commit -m "feat: add Logs API with SSE streaming"
```

---

## Task 6: 初始化 Next.js 前端项目

**Files:**
- Create: `web/` 目录结构

**Step 1: 创建 Next.js 项目**

```bash
npx create-next-app@14 web --typescript --tailwind --eslint --app --src-dir=false --import-alias="@/*"
```

选择选项：
- TypeScript: Yes
- Tailwind CSS: Yes
- App Router: Yes
- ESLint: Yes

**Step 2: 安装核心依赖**

```bash
cd web
npm install zustand lucide-react clsx tailwind-merge class-variance-authority
```

**Step 3: 配置 Tailwind CSS**

Update `web/tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
    },
  },
  plugins: [],
};

export default config;
```

**Step 4: Commit**

```bash
git add web/
git commit -m "feat: initialize Next.js frontend project"
```

---

## Task 7: 创建前端状态管理

**Files:**
- Create: `web/lib/store.ts`
- Create: `web/lib/api.ts`
- Create: `web/lib/sse.ts`

**Step 1: 创建 Zustand Store**

Create `web/lib/store.ts`:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// Chat state
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setStreaming: (streaming: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      isStreaming: false,
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
      setStreaming: (streaming) => set({ isStreaming: streaming }),
      clearMessages: () => set({ messages: [] }),
    }),
    { name: 'chat-storage' }
  )
);

// Skill state
export interface Skill {
  name: string;
  description: string;
  version: string;
}

interface SkillState {
  skills: Skill[];
  selectedSkill: Skill | null;
  setSkills: (skills: Skill[]) => void;
  selectSkill: (skill: Skill | null) => void;
}

export const useSkillStore = create<SkillState>()((set) => ({
  skills: [],
  selectedSkill: null,
  setSkills: (skills) => set({ skills }),
  selectSkill: (skill) => set({ selectedSkill: skill }),
}));
```

**Step 2: 创建 API 客户端**

Create `web/lib/api.ts`:

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchSkills() {
  const response = await fetch(`${API_BASE}/api/skills`);
  if (!response.ok) throw new Error('Failed to fetch skills');
  return response.json();
}

export async function fetchSkill(name: string) {
  const response = await fetch(`${API_BASE}/api/skills/${name}`);
  if (!response.ok) throw new Error('Failed to fetch skill');
  return response.json();
}

export async function runSkill(name: string, params: Record<string, unknown>) {
  const response = await fetch(`${API_BASE}/api/skills/${name}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ params }),
  });
  if (!response.ok) throw new Error('Failed to run skill');
  return response.json();
}
```

**Step 3: 创建 SSE 工具函数**

Create `web/lib/sse.ts`:

```typescript
export interface SSEEvent {
  type: string;
  content?: string;
}

export async function* parseSSEStream(
  response: Response
): AsyncGenerator<SSEEvent> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';

    for (const eventStr of events) {
      const line = eventStr.trim();
      if (!line.startsWith('data: ')) continue;

      try {
        const data = JSON.parse(line.slice(6));
        yield data;
      } catch {
        console.warn('Failed to parse SSE event:', line);
      }
    }
  }
}

export async function streamChat(
  message: string,
  onEvent: (event: SSEEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.ok) throw new Error('Chat request failed');

  for await (const event of parseSSEStream(response)) {
    onEvent(event);
  }
}
```

**Step 4: Commit**

```bash
git add web/lib/
git commit -m "feat: add frontend state management and API utilities"
```

---

## Task 8: 实现 Chat UI 组件

**Files:**
- Create: `web/components/chat/ChatContainer.tsx`
- Create: `web/components/chat/MessageList.tsx`
- Create: `web/components/chat/InputBar.tsx`

**Step 1: 创建 ChatContainer**

Create `web/components/chat/ChatContainer.tsx`:

```typescript
'use client';

import { useState, useRef, useCallback } from 'react';
import { MessageList } from './MessageList';
import { InputBar } from './InputBar';
import { useChatStore } from '@/lib/store';
import { streamChat } from '@/lib/sse';

export function ChatContainer() {
  const { messages, addMessage, isStreaming, setStreaming } = useChatStore();
  const [currentResponse, setCurrentResponse] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSubmit = useCallback(
    async (input: string) => {
      if (isStreaming) return;

      addMessage({ role: 'user', content: input });
      setStreaming(true);
      setCurrentResponse('');

      abortControllerRef.current = new AbortController();

      try {
        let accumulatedResponse = '';
        await streamChat(
          input,
          (event) => {
            switch (event.type) {
              case 'text_delta':
                accumulatedResponse += event.content || '';
                setCurrentResponse(accumulatedResponse);
                break;
              case 'done':
                addMessage({ role: 'assistant', content: accumulatedResponse });
                setCurrentResponse('');
                setStreaming(false);
                break;
              case 'error':
                console.error('Chat error:', event);
                setStreaming(false);
                break;
            }
          },
          abortControllerRef.current.signal
        );
      } catch (error) {
        console.error('Stream error:', error);
        setStreaming(false);
      }
    },
    [isStreaming, addMessage, setStreaming]
  );

  const handleStop = useCallback(() => {
    abortControllerRef.current?.abort();
    setStreaming(false);
  }, [setStreaming]);

  return (
    <div className="flex flex-col h-full">
      <MessageList
        messages={messages}
        currentResponse={currentResponse}
        isStreaming={isStreaming}
      />
      <InputBar
        onSubmit={handleSubmit}
        onStop={handleStop}
        isStreaming={isStreaming}
      />
    </div>
  );
}
```

**Step 2: 创建 MessageList**

Create `web/components/chat/MessageList.tsx`:

```typescript
'use client';

import { useEffect, useRef } from 'react';
import type { Message } from '@/lib/store';
import { User, Bot } from 'lucide-react';

interface MessageListProps {
  messages: Message[];
  currentResponse: string;
  isStreaming: boolean;
}

export function MessageList({
  messages,
  currentResponse,
  isStreaming,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentResponse]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      {isStreaming && currentResponse && (
        <MessageItem
          message={{
            id: 'streaming',
            role: 'assistant',
            content: currentResponse,
            timestamp: Date.now(),
          }}
          isStreaming
        />
      )}
      <div ref={scrollRef} />
    </div>
  );
}

function MessageItem({
  message,
  isStreaming,
}: {
  message: Message;
  isStreaming?: boolean;
}) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500' : 'bg-gray-500'
        }`}
      >
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-white" />
        )}
      </div>
      <div
        className={`max-w-[80%] px-4 py-2 rounded-lg ${
          isUser ? 'bg-blue-500 text-white' : 'bg-gray-100'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {isStreaming && (
          <span className="inline-block w-2 h-4 ml-1 bg-gray-400 animate-pulse" />
        )}
      </div>
    </div>
  );
}
```

**Step 3: 创建 InputBar**

Create `web/components/chat/InputBar.tsx`:

```typescript
'use client';

import { useState, useCallback, KeyboardEvent } from 'react';
import { Send, Square } from 'lucide-react';

interface InputBarProps {
  onSubmit: (input: string) => void;
  onStop: () => void;
  isStreaming: boolean;
}

export function InputBar({ onSubmit, onStop, isStreaming }: InputBarProps) {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    onSubmit(trimmed);
    setInput('');
  }, [input, isStreaming, onSubmit]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="border-t p-4">
      <div className="flex gap-2 items-end">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
          className="flex-1 resize-none border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={1}
          disabled={isStreaming}
        />
        {isStreaming ? (
          <button
            onClick={onStop}
            className="p-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
          >
            <Square size={20} />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        )}
      </div>
    </div>
  );
}
```

**Step 4: 更新首页**

Update `web/app/page.tsx`:

```typescript
import { ChatContainer } from '@/components/chat/ChatContainer';

export default function Home() {
  return (
    <main className="h-screen flex flex-col">
      <header className="border-b p-4">
        <h1 className="text-xl font-bold">Markwritter</h1>
        <p className="text-sm text-gray-500">Agent Orchestration Framework</p>
      </header>
      <ChatContainer />
    </main>
  );
}
```

**Step 5: Commit**

```bash
git add web/components/chat/ web/app/page.tsx
git commit -m "feat: implement Chat UI components"
```

---

## Task 9: 实现 Skill Manager 页面

**Files:**
- Create: `web/app/skills/page.tsx`
- Create: `web/components/skills/SkillCard.tsx`

**Step 1: 创建 SkillCard 组件**

Create `web/components/skills/SkillCard.tsx`:

```typescript
import Link from 'next/link';
import type { Skill } from '@/lib/store';
import { Play, Edit, Trash2 } from 'lucide-react';

interface SkillCardProps {
  skill: Skill;
}

export function SkillCard({ skill }: SkillCardProps) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold">{skill.name}</h3>
        <span className="text-xs bg-gray-100 px-2 py-1 rounded">
          {skill.version}
        </span>
      </div>
      <p className="text-sm text-gray-500 mb-4">{skill.description}</p>
      <div className="flex gap-2">
        <Link
          href={`/skills/${skill.name}`}
          className="flex-1 flex items-center justify-center gap-1 px-3 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
        >
          <Play size={14} />
          Run
        </Link>
        <Link
          href={`/skills/${skill.name}/edit`}
          className="flex items-center justify-center p-2 border rounded hover:bg-gray-50"
        >
          <Edit size={14} />
        </Link>
        <button className="flex items-center justify-center p-2 border border-red-200 text-red-500 rounded hover:bg-red-50">
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
}
```

**Step 2: 创建 Skill 列表页**

Create `web/app/skills/page.tsx`:

```typescript
'use client';

import { useEffect, useState } from 'react';
import { fetchSkills } from '@/lib/api';
import { SkillCard } from '@/components/skills/SkillCard';
import type { Skill } from '@/lib/store';
import { Plus } from 'lucide-react';
import Link from 'next/link';

export default function SkillsPage() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSkills()
      .then(setSkills)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <main className="p-8">
        <div className="text-center">Loading...</div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="p-8">
        <div className="text-center text-red-500">Error: {error}</div>
      </main>
    );
  }

  return (
    <main className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Skills</h1>
        <Link
          href="/skills/new"
          className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg"
        >
          <Plus size={16} />
          New Skill
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {skills.map((skill) => (
          <SkillCard key={skill.name} skill={skill} />
        ))}
      </div>
      {skills.length === 0 && (
        <div className="text-center text-gray-500 mt-8">
          No skills found. Create your first skill!
        </div>
      )}
    </main>
  );
}
```

**Step 3: Commit**

```bash
git add web/app/skills/ web/components/skills/
git commit -m "feat: implement Skill Manager page"
```

---

## Task 10: 实现日志流监控组件

**Files:**
- Create: `web/components/logs/LogStream.tsx`
- Create: `web/app/logs/page.tsx`

**Step 1: 创建 LogStream 组件**

Create `web/components/logs/LogStream.tsx`:

```typescript
'use client';

import { useEffect, useState, useRef } from 'react';

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export function LogStream() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const [connected, setConnected] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const API_BASE =
      process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const eventSource = new EventSource(`${API_BASE}/api/logs/stream`);

    eventSource.onopen = () => setConnected(true);
    eventSource.onerror = () => setConnected(false);

    eventSource.onmessage = (event) => {
      try {
        const log = JSON.parse(event.data);
        setLogs((prev) => [...prev.slice(-100), log]); // Keep last 100
      } catch {
        // Ignore heartbeat
      }
    };

    return () => {
      eventSource.close();
      setConnected(false);
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const filteredLogs = logs.filter(
    (log) => filter === 'all' || log.level === filter
  );

  const levelColors: Record<string, string> = {
    DEBUG: 'text-gray-500',
    INFO: 'text-blue-500',
    WARNING: 'text-yellow-500',
    ERROR: 'text-red-500',
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b flex gap-2 items-center">
        <div
          className={`w-2 h-2 rounded-full ${
            connected ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
        <span className="text-sm text-gray-500">
          {connected ? 'Connected' : 'Disconnected'}
        </span>
        <div className="flex-1" />
        {['all', 'DEBUG', 'INFO', 'WARNING', 'ERROR'].map((level) => (
          <button
            key={level}
            onClick={() => setFilter(level)}
            className={`px-3 py-1 rounded text-sm ${
              filter === level
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 hover:bg-gray-200'
            }`}
          >
            {level}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto p-4 font-mono text-sm bg-gray-50">
        {filteredLogs.map((log, i) => (
          <div key={i} className="py-1">
            <span className="text-gray-400">{log.timestamp}</span>
            <span className={`mx-2 ${levelColors[log.level] || ''}`}>
              [{log.level}]
            </span>
            <span>{log.message}</span>
          </div>
        ))}
        <div ref={scrollRef} />
      </div>
    </div>
  );
}
```

**Step 2: 创建日志页面**

Create `web/app/logs/page.tsx`:

```typescript
import { LogStream } from '@/components/logs/LogStream';

export default function LogsPage() {
  return (
    <main className="h-screen flex flex-col">
      <header className="border-b p-4">
        <h1 className="text-xl font-bold">Logs Monitor</h1>
        <p className="text-sm text-gray-500">Real-time system logs</p>
      </header>
      <div className="flex-1">
        <LogStream />
      </div>
    </main>
  );
}
```

**Step 3: Commit**

```bash
git add web/components/logs/ web/app/logs/
git commit -m "feat: implement log streaming monitor"
```

---

## Task 11: 创建 Docker 部署配置

**Files:**
- Create: `Dockerfile.api`
- Create: `Dockerfile.web`
- Create: `docker-compose.yml`

**Step 1: 创建后端 Dockerfile**

Create `Dockerfile.api`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY markwritter/ ./markwritter/
COPY api/ ./api/
COPY skills/ ./skills/
COPY config.yaml .

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 2: 创建前端 Dockerfile**

Create `Dockerfile.web`:

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY web/package*.json ./
RUN npm ci

COPY web/ .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
```

**Step 3: 创建 docker-compose.yml**

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - ./skills:/app/skills
      - ./config.yaml:/app/config.yaml
    environment:
      - DASHSCOPE_API_KEY=${DASHSCOPE_API_KEY}

  web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - api
```

**Step 4: Commit**

```bash
git add Dockerfile.api Dockerfile.web docker-compose.yml
git commit -m "feat: add Docker deployment configuration"
```

---

## Dependencies

```
Task 1 (FastAPI skeleton)
    |
    v
Task 2 (Framework bridge)
    |
    v
Task 3, 4, 5 (API endpoints - can run in parallel)
    |
    v
Task 6 (Next.js init)
    |
    v
Task 7 (Frontend state)
    |
    v
Task 8, 9, 10 (UI components - can run in parallel)
    |
    v
Task 11 (Docker deployment)
```

---

## Risks

| Risk | Level | Mitigation |
|------|-------|------------|
| SSE connection unstable | HIGH | Implement auto-reconnect, heartbeat |
| Framework API changes | MEDIUM | Use adapter pattern in services layer |
| CORS issues | LOW | Configure CORS middleware properly |
| Long-running tasks | MEDIUM | Implement task queue for async execution |

---

## Estimated Complexity

- **Phase 1 (Tasks 1-5)**: 8-10 hours - Backend API layer
- **Phase 2 (Tasks 6-7)**: 4-5 hours - Frontend basics
- **Phase 3 (Tasks 8-10)**: 10-12 hours - UI components
- **Phase 4 (Task 11)**: 2-3 hours - Deployment

**Total**: 24-30 hours

---

**Plan created**: 2026-03-21