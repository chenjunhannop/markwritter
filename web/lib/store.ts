/**
 * Zustand Stores for Markwritter
 *
 * State management for chat, skills, and UI.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Skill, Session, Message, MessageRole } from './types';
import { getSkills, executeSkill } from './api';

// ==================== Chat Store ====================

interface ChatState {
  sessions: Session[];
  currentSessionId: string | null;
  isStreaming: boolean;
  selectedSources: string[];

  // Session actions
  createSession: (title?: string) => string;
  selectSession: (id: string) => void;
  deleteSession: (id: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;

  // Message actions
  addMessage: (
    role: MessageRole,
    content: string,
    options?: { citations?: Message['citations'] }
  ) => void;
  updateMessage: (sessionId: string, messageId: string, content: string) => void;

  // Source actions
  setSelectedSources: (paths: string[]) => void;
  toggleSource: (path: string) => void;
  addSources: (paths: string[]) => void;
  removeSources: (paths: string[]) => void;
  clearSources: () => void;

  // State actions
  setStreaming: (streaming: boolean) => void;
  getCurrentSession: () => Session | null;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      sessions: [],
      currentSessionId: null,
      isStreaming: false,
      selectedSources: [],

      createSession: (title = 'New Chat') => {
        const id = crypto.randomUUID();
        const now = Date.now();
        const { selectedSources } = get();
        const newSession: Session = {
          id,
          title,
          messages: [],
          selectedSources: [...selectedSources],
          createdAt: now,
          updatedAt: now,
        };

        set((state) => ({
          sessions: [...state.sessions, newSession],
          currentSessionId: id,
        }));

        return id;
      },

      selectSession: (id) => {
        set((state) => {
          const session = state.sessions.find((s) => s.id === id);
          if (session) {
            return {
              currentSessionId: id,
              selectedSources: session.selectedSources,
            };
          }
          return { currentSessionId: id };
        });
      },

      deleteSession: (id) => {
        set((state) => {
          const sessions = state.sessions.filter((s) => s.id !== id);
          const currentSessionId =
            state.currentSessionId === id ? null : state.currentSessionId;
          return { sessions, currentSessionId };
        });
      },

      updateSessionTitle: (sessionId, title) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? { ...session, title, updatedAt: Date.now() }
              : session
          ),
        }));
      },

      addMessage: (role, content, options) => {
        const state = get();
        if (!state.currentSessionId) return;

        const message: Message = {
          id: crypto.randomUUID(),
          role,
          content,
          citations: options?.citations,
          timestamp: Date.now(),
        };

        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  messages: [...session.messages, message],
                  updatedAt: Date.now(),
                }
              : session
          ),
        }));
      },

      updateMessage: (sessionId, messageId, content) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId
              ? {
                  ...session,
                  messages: session.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, content } : msg
                  ),
                  updatedAt: Date.now(),
                }
              : session
          ),
        }));
      },

      setSelectedSources: (paths) => {
        set((state) => {
          const nextSelectedSources = [...paths];
          return {
            selectedSources: nextSelectedSources,
            sessions: state.sessions.map((session) =>
              session.id === state.currentSessionId
                ? {
                    ...session,
                    selectedSources: nextSelectedSources,
                    updatedAt: Date.now(),
                  }
                : session
            ),
          };
        });
      },

      toggleSource: (path) => {
        set((state) => {
          const has = state.selectedSources.includes(path);
          const nextSelectedSources = has
            ? state.selectedSources.filter((p) => p !== path)
            : [...state.selectedSources, path];
          return {
            selectedSources: nextSelectedSources,
            sessions: state.sessions.map((session) =>
              session.id === state.currentSessionId
                ? {
                    ...session,
                    selectedSources: nextSelectedSources,
                    updatedAt: Date.now(),
                  }
                : session
            ),
          };
        });
      },

      addSources: (paths) => {
        set((state) => {
          const existing = new Set(state.selectedSources);
          const newPaths = paths.filter((p) => !existing.has(p));
          const nextSelectedSources = [...state.selectedSources, ...newPaths];
          return {
            selectedSources: nextSelectedSources,
            sessions: state.sessions.map((session) =>
              session.id === state.currentSessionId
                ? {
                    ...session,
                    selectedSources: nextSelectedSources,
                    updatedAt: Date.now(),
                  }
                : session
            ),
          };
        });
      },

      removeSources: (paths) => {
        const removeSet = new Set(paths);
        set((state) => ({
          selectedSources: state.selectedSources.filter((p) => !removeSet.has(p)),
          sessions: state.sessions.map((session) =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  selectedSources: session.selectedSources.filter((p) => !removeSet.has(p)),
                  updatedAt: Date.now(),
                }
              : session
          ),
        }));
      },

      clearSources: () => {
        set((state) => ({
          selectedSources: [],
          sessions: state.sessions.map((session) =>
            session.id === state.currentSessionId
              ? {
                  ...session,
                  selectedSources: [],
                  updatedAt: Date.now(),
                }
              : session
          ),
        }));
      },

      setStreaming: (streaming) => {
        set({ isStreaming: streaming });
      },

      getCurrentSession: () => {
        const state = get();
        if (!state.currentSessionId) return null;
        return state.sessions.find((s) => s.id === state.currentSessionId) || null;
      },
    }),
    {
      name: 'chat-storage-v2',
      merge: (persisted, current) => {
        const persistedState = persisted as Record<string, unknown>;
        const currentSessions = (persistedState.sessions ?? current.sessions) as Session[];
        const migratedSessions = currentSessions.map((session) => ({
          ...session,
          selectedSources: session.selectedSources ?? [],
        }));
        return {
          ...current,
          ...persistedState,
          sessions: migratedSessions,
          selectedSources:
            migratedSessions.find((session) => session.id === persistedState.currentSessionId)
              ?.selectedSources ?? (persistedState.selectedSources as string[] | undefined) ?? [],
        };
      },
    }
  )
);

// ==================== Skill Store ====================

interface SkillState {
  skills: Skill[];
  selectedSkill: Skill | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  loadSkills: () => Promise<void>;
  selectSkill: (name: string) => void;
  clearSelection: () => void;
  executeSelectedSkill: (params: Record<string, unknown>) => Promise<string | null>;
}

export const useSkillStore = create<SkillState>()((set, get) => ({
  skills: [],
  selectedSkill: null,
  isLoading: false,
  error: null,

  loadSkills: async () => {
    set({ isLoading: true, error: null });
    try {
      const skills = await getSkills();
      set({ skills, isLoading: false });
    } catch (e) {
      const error = e instanceof Error ? e.message : 'Failed to load skills';
      set({ error, isLoading: false });
    }
  },

  selectSkill: (name) => {
    const state = get();
    const skill = state.skills.find((s) => s.name === name) || null;
    set({ selectedSkill: skill });
  },

  clearSelection: () => {
    set({ selectedSkill: null });
  },

  executeSelectedSkill: async (params) => {
    const state = get();
    if (!state.selectedSkill) {
      set({ error: 'No skill selected' });
      return null;
    }

    set({ isLoading: true, error: null });
    try {
      const result = await executeSkill(state.selectedSkill.name, params);
      set({ isLoading: false });
      return result.success ? result.output : null;
    } catch (e) {
      const error = e instanceof Error ? e.message : 'Failed to execute skill';
      set({ error, isLoading: false });
      return null;
    }
  },
}));

// ==================== UI Store ====================

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';

interface UIState {
  connectionStatus: ConnectionStatus;
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;

  setConnectionStatus: (status: ConnectionStatus) => void;

  toggleLeftPanel: () => void;
  setLeftPanelCollapsed: (collapsed: boolean) => void;
  toggleRightPanel: () => void;
  setRightPanelCollapsed: (collapsed: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      connectionStatus: 'connected',
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,

      setConnectionStatus: (status) => {
        set({ connectionStatus: status });
      },

      toggleLeftPanel: () => {
        set((state) => ({ leftPanelCollapsed: !state.leftPanelCollapsed }));
      },

      setLeftPanelCollapsed: (collapsed) => {
        set({ leftPanelCollapsed: collapsed });
      },

      toggleRightPanel: () => {
        set((state) => ({ rightPanelCollapsed: !state.rightPanelCollapsed }));
      },

      setRightPanelCollapsed: (collapsed) => {
        set({ rightPanelCollapsed: collapsed });
      },
    }),
    {
      name: 'ui-storage',
      merge: (persisted, current) => {
        const persistedState = persisted as Record<string, unknown>;
        return {
          ...current,
          connectionStatus: (persistedState.connectionStatus as ConnectionStatus) ?? current.connectionStatus,
          leftPanelCollapsed: (persistedState.leftPanelCollapsed as boolean) ?? current.leftPanelCollapsed,
          rightPanelCollapsed: (persistedState.rightPanelCollapsed as boolean) ?? current.rightPanelCollapsed,
        };
      },
    }
  )
);
