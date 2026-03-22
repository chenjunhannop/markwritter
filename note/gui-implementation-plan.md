# Markwritter GUI 实施计划

> 文档版本：1.0
> 创建日期：2026-03-21
> 预估总工时：44-55 小时

---

## 一、需求重述

### 1.1 项目背景

Markwritter 是一个轻量级的 Agent 编排框架，核心功能包括：
- **Parser**：解析用户意图，识别需要调用的 Skill
- **Registry**：管理所有可用的 Skills（从 YAML 定义加载）
- **Executor**：创建 Subagent 执行 Skill 脚本

当前仅有 Typer CLI 命令行界面，用户需要添加 GUI/Web 界面以提升交互体验。

### 1.2 核心需求

| 需求项 | 描述 |
|--------|------|
| Chat UI | 对话式交互界面，支持流式文本展示 |
| Skill Manager | Skill 的 CRUD 管理界面 |
| 日志监控 | 实时日志流展示 |
| 可扩展性 | 架构清晰，支持后续功能迭代 |

### 1.3 设计原则

- **核心层不变**：保持 Markwritter 现有架构
- **前后端分离**：FastAPI 后端 + Next.js 前端
- **流式优先**：使用 SSE 实现实时响应
- **模块化设计**：各层独立，便于扩展

---

## 二、架构设计

### 2.1 整体架构图

```
+---------------------------------------------------------+
|                    前端层 (Next.js)                      |
|  +-------------------+  +--------------------------+    |
|  | Chat UI           |  | Skill Manager Dashboard  |    |
|  | - 流式文本展示     |  | - Skill 列表/详情         |    |
|  | - 输入框          |  | - YAML 编辑器            |    |
|  | - 消息历史        |  | - 创建/编辑/删除         |    |
|  +-------------------+  +--------------------------+    |
|  +-------------------+                                  |
|  | Logs Monitor      |                                  |
|  | - SSE 实时日志    |                                  |
|  | - 日志级别过滤    |                                  |
|  +-------------------+                                  |
+---------------------------------------------------------+
                          | HTTP / SSE
+---------------------------------------------------------+
|              API 层 (FastAPI - Python)                   |
|  +-------------------+  +--------------------------+    |
|  | POST /api/chat    |  | GET /api/skills          |    |
|  | - SSE 流式响应    |  | POST /api/skills         |    |
|  | - 意图解析        |  | PUT /api/skills/{name}   |    |
|  | - Skill 执行      |  | DELETE /api/skills/{name}|    |
|  +-------------------+  +--------------------------+    |
|  +-------------------+                                  |
|  | GET /api/logs/stream                                 |
|  | - SSE 日志流                                          |
|  +-------------------+                                  |
+---------------------------------------------------------+
                          |
+---------------------------------------------------------+
|          核心层 (Markwritter - 保持不变)                 |
|  +----------+  +----------+  +------------------+        |
|  | Parser   |  | Registry |  | Executor         |        |
|  +----------+  +----------+  +------------------+        |
+---------------------------------------------------------+
                          | subprocess
+---------------------------------------------------------+
|          Skill 层 (YAML 定义 + 执行脚本)                 |
+---------------------------------------------------------+
```

### 2.2 技术栈选型

| 层级 | 技术 | 版本 | 理由 |
|------|------|------|------|
| 前端框架 | Next.js | 14.x | App Router、RSC 支持 |
| UI 组件 | Shadcn/UI | latest | 基于 Radix UI、可定制 |
| 样式 | Tailwind CSS | 3.x | 原子化 CSS |
| 状态管理 | Zustand | 4.x | 轻量、支持持久化 |
| 后端框架 | FastAPI | 0.100+ | 异步、自动文档、Pydantic 集成 |
| 流式传输 | SSE | - | 单向流、兼容性好 |
| 进程通信 | asyncio.subprocess | - | 已有实现 |

### 2.3 目录结构设计

```
markwritter/
├── markwritter/              # 核心层（保持不变）
│   ├── core.py
│   ├── parser.py
│   ├── registry.py
│   ├── executor.py
│   ├── models.py
│   ├── llm_client.py
│   ├── config.py
│   ├── logger.py
│   └── cli.py                # CLI 入口（保留）
│
├── api/                      # 新增：FastAPI 后端
│   ├── __init__.py
│   ├── main.py               # FastAPI 应用入口
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py           # /api/chat 端点
│   │   ├── skills.py         # /api/skills 端点
│   │   └── logs.py           # /api/logs 端点
│   ├── models/               # API 请求/响应模型
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── skill.py
│   └── services/             # 业务逻辑封装
│       ├── __init__.py
│       └── framework_bridge.py  # 桥接核心层
│
├── web/                      # 新增：Next.js 前端
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx          # 首页（Chat UI）
│   │   └── skills/
│   │       └── page.tsx      # Skill 列表
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageList.tsx
│   │   │   └── InputBar.tsx
│   │   └── skills/
│   │       └── SkillCard.tsx
│   ├── lib/
│   │   ├── api.ts            # API 客户端
│   │   └── sse.ts            # SSE 工具函数
│   └── package.json
│
├── skills/                   # Skill 定义（保持不变）
├── tests/
├── docker-compose.yml        # 新增：容器编排
├── Dockerfile.api            # 新增：后端镜像
├── Dockerfile.web            # 新增：前端镜像
└── pyproject.toml
```

---

## 三、实施阶段

### Phase 1: FastAPI 后端 API 层

**目标**：创建 RESTful API 层，暴露核心功能

**预估时间**：8-10 小时

**复杂度**：中

#### Step 1.1: 创建 FastAPI 应用骨架

**文件**：`api/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

**产出物**：
- 可启动的 FastAPI 应用
- CORS 配置
- 健康检查端点

#### Step 1.2: 实现 Skills API

**文件**：`api/routers/skills.py`

```python
from fastapi import APIRouter, HTTPException
from typing import List
from pathlib import Path
from markwritter.registry import SkillRegistry
from markwritter.models import SkillDefinition
from api.models.skill import SkillResponse, SkillCreateRequest

router = APIRouter(prefix="/api/skills", tags=["skills"])

def get_registry() -> SkillRegistry:
    skills_dir = Path("./skills").resolve()
    return SkillRegistry(skills_dir)

@router.get("/", response_model=List[SkillResponse])
async def list_skills():
    """列出所有可用的 Skills"""
    registry = get_registry()
    return registry.list_all()

@router.get("/{skill_name}", response_model=SkillResponse)
async def get_skill(skill_name: str):
    """获取单个 Skill 详情"""
    registry = get_registry()
    skill = registry.get(skill_name)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.post("/{skill_name}/run")
async def run_skill(skill_name: str, params: dict = None):
    """执行指定的 Skill"""
    # 异步执行 + SSE 响应
    pass
```

**产出物**：
- `GET /api/skills` - 列出所有 Skills
- `GET /api/skills/{name}` - 获取 Skill 详情
- `POST /api/skills/{name}/run` - 执行 Skill

#### Step 1.3: 实现 Chat API（SSE 流式）

**文件**：`api/routers/chat.py`

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from markwritter.core import Framework
from markwritter.registry import SkillRegistry
from api.models.chat import ChatRequest
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/")
async def chat(request: ChatRequest):
    """处理用户输入，返回 SSE 流式响应"""

    async def event_generator():
        framework = get_framework()

        # 发送思考状态
        yield f"data: {json.dumps({'type': 'thinking'})}\n\n"

        # 处理用户输入
        result = framework.process_input(request.message)

        # 流式发送文本
        for char in result:
            yield f"data: {json.dumps({'type': 'text_delta', 'content': char})}\n\n"

        # 发送完成事件
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

**产出物**：
- `POST /api/chat` - SSE 流式聊天端点

#### Step 1.4: 实现日志流 API

**文件**：`api/routers/logs.py`

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import queue

router = APIRouter(prefix="/api/logs", tags=["logs"])

# 日志队列（用于跨线程通信）
log_queue = queue.Queue()

@router.get("/stream")
async def stream_logs():
    """SSE 流式日志输出"""

    async def log_generator():
        while True:
            try:
                log_entry = log_queue.get(timeout=1.0)
                yield f"data: {log_entry}\n\n"
            except queue.Empty:
                # 发送心跳
                yield ": heartbeat\n\n"

    return StreamingResponse(
        log_generator(),
        media_type="text/event-stream",
    )
```

**产出物**：
- `GET /api/logs/stream` - SSE 日志流

#### Step 1.5: 桥接核心层

**文件**：`api/services/framework_bridge.py`

```python
from markwritter.core import Framework
from markwritter.registry import SkillRegistry
from pathlib import Path

_framework_instance = None

def get_framework() -> Framework:
    global _framework_instance
    if _framework_instance is None:
        skills_dir = Path("./skills").resolve()
        registry = SkillRegistry(skills_dir)
        _framework_instance = Framework(registry)
    return _framework_instance
```

**产出物**：
- 框架实例管理
- 依赖注入支持

---

### Phase 2: Next.js 前端基础

**目标**：搭建前端项目骨架和基础组件

**预估时间**：10-12 小时

**复杂度**：中

#### Step 2.1: 初始化 Next.js 项目

```bash
cd markwritter
npx create-next-app@14 web --typescript --tailwind --eslint --app --src-dir
```

**配置项**：
- TypeScript: Yes
- Tailwind CSS: Yes
- App Router: Yes
- ESLint: Yes

#### Step 2.2: 安装核心依赖

```bash
cd web
npm install zustand @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install lucide-react clsx tailwind-merge
npm install class-variance-authority
```

#### Step 2.3: 配置 Tailwind CSS

**文件**：`web/tailwind.config.ts`

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
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
      },
    },
  },
  plugins: [],
};

export default config;
```

#### Step 2.4: 创建 Zustand 状态管理

**文件**：`web/lib/store.ts`

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Message {
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

interface Skill {
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

#### Step 2.5: 创建 API 客户端

**文件**：`web/lib/api.ts`

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
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error('Failed to run skill');
  return response.json();
}
```

#### Step 2.6: 创建 SSE 工具函数

**文件**：`web/lib/sse.ts`

```typescript
export interface SSEEvent {
  type: string;
  data?: unknown;
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

---

### Phase 3: Chat UI 核心功能

**目标**：实现流式聊天界面

**预估时间**：12-15 小时

**复杂度**：高

#### Step 3.1: 创建 ChatContainer 组件

**文件**：`web/components/chat/ChatContainer.tsx`

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

  const handleSubmit = useCallback(async (input: string) => {
    if (isStreaming) return;

    // 添加用户消息
    addMessage({ role: 'user', content: input });
    setStreaming(true);
    setCurrentResponse('');

    abortControllerRef.current = new AbortController();

    try {
      await streamChat(
        input,
        (event) => {
          switch (event.type) {
            case 'text_delta':
              setCurrentResponse((prev) => prev + (event as { content: string }).content);
              break;
            case 'done':
              addMessage({ role: 'assistant', content: currentResponse });
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
  }, [isStreaming, currentResponse, addMessage, setStreaming]);

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

#### Step 3.2: 创建 MessageList 组件

**文件**：`web/components/chat/MessageList.tsx`

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

export function MessageList({ messages, currentResponse, isStreaming }: MessageListProps) {
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

function MessageItem({ message, isStreaming }: { message: Message; isStreaming?: boolean }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-500' : 'bg-gray-500'
        }`}
      >
        {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
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

#### Step 3.3: 创建 InputBar 组件

**文件**：`web/components/chat/InputBar.tsx`

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

#### Step 3.4: 创建首页

**文件**：`web/app/page.tsx`

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

---

### Phase 4: Skill Manager Dashboard

**目标**：实现 Skill 管理界面

**预估时间**：8-10 小时

**复杂度**：中

#### Step 4.1: 创建 Skill 列表页

**文件**：`web/app/skills/page.tsx`

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

  useEffect(() => {
    fetchSkills()
      .then(setSkills)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="p-8 text-center">Loading...</div>;
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
    </main>
  );
}
```

#### Step 4.2: 创建 SkillCard 组件

**文件**：`web/components/skills/SkillCard.tsx`

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
        <span className="text-xs bg-gray-100 px-2 py-1 rounded">{skill.version}</span>
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

#### Step 4.3: 创建 Skill 详情页

**文件**：`web/app/skills/[name]/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { fetchSkill, runSkill } from '@/lib/api';
import type { Skill } from '@/lib/store';

export default function SkillDetailPage() {
  const params = useParams();
  const [skill, setSkill] = useState<Skill | null>(null);
  const [params_value, setParamsValue] = useState<Record<string, string>>({});
  const [result, setResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (params.name) {
      fetchSkill(params.name as string).then(setSkill);
    }
  }, [params.name]);

  const handleRun = async () => {
    if (!skill) return;
    setLoading(true);
    try {
      const res = await runSkill(skill.name, params_value);
      setResult(JSON.stringify(res, null, 2));
    } catch (error) {
      setResult('Error: ' + (error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (!skill) return <div className="p-8">Loading...</div>;

  return (
    <main className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">{skill.name}</h1>
      <p className="text-gray-500 mb-6">{skill.description}</p>

      {/* 参数输入 */}
      <div className="mb-6">
        <h2 className="font-semibold mb-2">Parameters</h2>
        {/* 根据 skill.inputs 动态生成表单 */}
        <textarea
          value={JSON.stringify(params_value, null, 2)}
          onChange={(e) => setParamsValue(JSON.parse(e.target.value))}
          className="w-full border rounded p-2 font-mono text-sm"
          rows={4}
        />
      </div>

      <button
        onClick={handleRun}
        disabled={loading}
        className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      >
        {loading ? 'Running...' : 'Run Skill'}
      </button>

      {result && (
        <div className="mt-6">
          <h2 className="font-semibold mb-2">Result</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-x-auto">{result}</pre>
        </div>
      )}
    </main>
  );
}
```

---

### Phase 5: 日志监控与部署

**目标**：实现日志流监控和容器化部署

**预估时间**：6-8 小时

**复杂度**：低

#### Step 5.1: 创建日志流组件

**文件**：`web/components/logs/LogStream.tsx`

```typescript
'use client';

import { useEffect, useState, useRef } from 'react';
import { parseSSEStream } from '@/lib/sse';

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export function LogStream() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const eventSource = new EventSource(`${API_BASE}/api/logs/stream`);

    eventSource.onmessage = (event) => {
      try {
        const log = JSON.parse(event.data);
        setLogs((prev) => [...prev.slice(-100), log]); // 保留最近 100 条
      } catch {
        // 忽略心跳
      }
    };

    return () => eventSource.close();
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
      <div className="p-4 border-b flex gap-2">
        {['all', 'DEBUG', 'INFO', 'WARNING', 'ERROR'].map((level) => (
          <button
            key={level}
            onClick={() => setFilter(level)}
            className={`px-3 py-1 rounded ${
              filter === level ? 'bg-blue-500 text-white' : 'bg-gray-100'
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
            <span className={`mx-2 ${levelColors[log.level] || ''}`}>[{log.level}]</span>
            <span>{log.message}</span>
          </div>
        ))}
        <div ref={scrollRef} />
      </div>
    </div>
  );
}
```

#### Step 5.2: 创建 Dockerfile

**文件**：`Dockerfile.api`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY markwritter/ ./markwritter/
COPY api/ ./api/
COPY skills/ ./skills/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**文件**：`Dockerfile.web`

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

#### Step 5.3: 创建 docker-compose.yml

**文件**：`docker-compose.yml`

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

---

## 四、依赖关系图

```
Phase 1 (FastAPI 后端)
    |
    v
Phase 2 (Next.js 基础) -----> Phase 4 (Skill Manager)
    |                              |
    v                              |
Phase 3 (Chat UI) <---------------+
    |
    v
Phase 5 (部署)
```

**关键依赖：**
- Phase 2 依赖 Phase 1（需要 API 端点）
- Phase 3 依赖 Phase 2（需要基础组件）
- Phase 4 依赖 Phase 2（需要基础组件）
- Phase 5 依赖 Phase 1-4（需要完整功能）

---

## 五、风险评估

### 5.1 技术风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| SSE 连接不稳定 | 中 | 高 | 实现自动重连、心跳检测 |
| 异步执行状态管理复杂 | 中 | 中 | 使用 asyncio.Queue 进行解耦 |
| 前后端类型不一致 | 低 | 中 | 使用 OpenAPI 生成 TypeScript 类型 |
| 跨域请求问题 | 低 | 低 | 正确配置 CORS |

### 5.2 架构风险

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| 核心层 API 变更 | 低 | 高 | 使用适配器模式隔离变更 |
| 状态同步复杂 | 中 | 中 | 使用 Zustand + SSE 保持一致性 |
| 长时间运行的任务 | 中 | 中 | 实现任务队列和状态轮询 |

---

## 六、技术选型说明

### 6.1 为什么选择 FastAPI 而非 Flask？

| 对比项 | FastAPI | Flask |
|--------|---------|-------|
| 异步支持 | 原生支持 | 需要扩展 |
| 类型验证 | Pydantic 自动 | 手动实现 |
| API 文档 | 自动生成 | 需要扩展 |
| 性能 | 更高 | 一般 |
| 学习曲线 | 中等 | 较低 |

**结论**：FastAPI 与 Markwritter 已使用的 Pydantic 高度兼容，且原生支持异步。

### 6.2 为什么选择 SSE 而非 WebSocket？

| 对比项 | SSE | WebSocket |
|--------|-----|-----------|
| 方向 | 单向（服务器->客户端） | 双向 |
| 复杂度 | 简单 | 复杂 |
| 自动重连 | 原生支持 | 需手动实现 |
| 适用场景 | 实时推送 | 双向通信 |

**结论**：Markwritter 的 Chat 和日志场景主要是服务器推送，SSE 更简单可靠。

### 6.3 为什么选择 Zustand 而非 Redux？

| 对比项 | Zustand | Redux |
|--------|---------|-------|
| 代码量 | 少 | 多 |
| 学习曲线 | 低 | 高 |
| 性能 | 更好 | 一般 |
| DevTools | 支持 | 更完善 |

**结论**：Markwritter 状态相对简单，Zustand 足够且更轻量。

---

## 七、成功标准

### 7.1 功能验收

- [ ] 用户可以通过 Chat UI 与 Markwritter 交互
- [ ] Chat 响应支持流式文本展示
- [ ] 用户可以在 Skill Manager 中查看所有 Skills
- [ ] 用户可以在 Skill Manager 中执行指定 Skill
- [ ] 日志监控页面可以实时显示系统日志
- [ ] 所有 API 端点返回正确的响应格式

### 7.2 质量验收

- [ ] 后端单元测试覆盖率 >= 80%
- [ ] 前端组件有对应的 Storybook stories
- [ ] E2E 测试覆盖核心用户流程
- [ ] 无控制台错误或警告
- [ ] 响应时间 < 2s（非流式）

### 7.3 部署验收

- [ ] Docker Compose 可以一键启动完整应用
- [ ] API 文档可通过 `/docs` 访问
- [ ] 开发环境与生产环境配置分离

---

## 八、后续扩展建议

### 8.1 短期（1-2 周）

- 实现会话历史持久化（IndexedDB）
- 添加 Skill 创建向导
- 支持多语言界面

### 8.2 中期（1-2 月）

- 实现 Skill 版本管理
- 添加用户认证
- 支持 WebSocket 双向通信

### 8.3 长期（3-6 月）

- 实现多租户支持
- 添加 Skill 市场
- 支持自定义 Agent 配置

---

## 附录：参考项目

- **openMAIC**: Next.js 14 + LangGraph + Vercel AI SDK
- **worldmonitor**: Next.js + Tauri 桌面应用

---

**文档版本**: 1.0
**创建日期**: 2026-03-21
**预估总工时**: 44-55 小时
