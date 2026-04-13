import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Message, Session } from "@/types/chat";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

interface ChatState {
  sessions: Session[];
  activeSessionId: string | null;
}

interface ChatActions {
  createSession: () => string;
  deleteSession: (id: string) => void;
  setActiveSession: (id: string) => void;
  addMessage: (sessionId: string, message: Message) => void;
  updateLastAssistantMessage: (sessionId: string, content: string) => void;
  setSessionTitle: (sessionId: string, title: string) => void;
  setActiveSessionSources: (sources: string[]) => void;
  addCitationToLastAssistantMessage: (
    sessionId: string,
    citation: Message["citations"] extends (infer T)[] | undefined ? T : never,
  ) => void;
}

export const useChatStore = create<ChatState & ChatActions>()(
  persist(
    (set, get) => ({
      sessions: [],
      activeSessionId: null,

      createSession: () => {
        const id = generateId();
        const now = Date.now();
        const session: Session = {
          id,
          title: "New Chat",
          messages: [],
          selectedSources: [],
          createdAt: now,
          updatedAt: now,
        };
        set((state) => ({
          sessions: [session, ...state.sessions],
          activeSessionId: id,
        }));
        return id;
      },

      deleteSession: (id) => {
        set((state) => {
          const filtered = state.sessions.filter((s) => s.id !== id);
          return {
            sessions: filtered,
            activeSessionId:
              state.activeSessionId === id
                ? (filtered[0]?.id ?? null)
                : state.activeSessionId,
          };
        });
      },

      setActiveSession: (id) => {
        set({ activeSessionId: id });
      },

      addMessage: (sessionId, message) => {
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === sessionId
              ? {
                  ...s,
                  messages: [...s.messages, message],
                  updatedAt: Date.now(),
                }
              : s,
          ),
        }));
      },

      updateLastAssistantMessage: (sessionId, content) => {
        set((state) => ({
          sessions: state.sessions.map((s) => {
            if (s.id !== sessionId) return s;
            const msgs = [...s.messages];
            for (let i = msgs.length - 1; i >= 0; i--) {
              if (msgs[i].role === "assistant") {
                msgs[i] = { ...msgs[i], content };
                break;
              }
            }
            return { ...s, messages: msgs, updatedAt: Date.now() };
          }),
        }));
      },

      setSessionTitle: (sessionId, title) => {
        set((state) => ({
          sessions: state.sessions.map((s) =>
            s.id === sessionId ? { ...s, title } : s,
          ),
        }));
      },

      setActiveSessionSources: (sources) => {
        const { activeSessionId, sessions } = get();
        if (!activeSessionId) return;
        set({
          sessions: sessions.map((s) =>
            s.id === activeSessionId ? { ...s, selectedSources: sources } : s,
          ),
        });
      },

      addCitationToLastAssistantMessage: (sessionId, citation) => {
        set((state) => ({
          sessions: state.sessions.map((s) => {
            if (s.id !== sessionId) return s;
            const msgs = [...s.messages];
            for (let i = msgs.length - 1; i >= 0; i--) {
              if (msgs[i].role === "assistant") {
                const existing = msgs[i].citations ?? [];
                msgs[i] = {
                  ...msgs[i],
                  citations: [...existing, citation],
                };
                break;
              }
            }
            return { ...s, messages: msgs };
          }),
        }));
      },
    }),
    { name: "mw-chat-sessions" },
  ),
);
