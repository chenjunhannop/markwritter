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
  addMessage: (role: MessageRole, content: string) => void;
  updateMessage: (sessionId: string, messageId: string, content: string) => void;

  // Source actions
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

      addMessage: (role, content) => {
        const state = get();
        if (!state.currentSessionId) return;

        const message: Message = {
          id: crypto.randomUUID(),
          role,
          content,
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

      toggleSource: (path) => {
        set((state) => {
          const has = state.selectedSources.includes(path);
          return {
            selectedSources: has
              ? state.selectedSources.filter((p) => p !== path)
              : [...state.selectedSources, path],
          };
        });
      },

      addSources: (paths) => {
        set((state) => {
          const existing = new Set(state.selectedSources);
          const newPaths = paths.filter((p) => !existing.has(p));
          return { selectedSources: [...state.selectedSources, ...newPaths] };
        });
      },

      removeSources: (paths) => {
        const removeSet = new Set(paths);
        set((state) => ({
          selectedSources: state.selectedSources.filter((p) => !removeSet.has(p)),
        }));
      },

      clearSources: () => {
        set({ selectedSources: [] });
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

export type NavItem = 'chat' | 'skills' | 'explore' | 'query' | 'record' | 'logs' | 'settings';
export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';

interface UIState {
  sidebarCollapsed: boolean;
  activeNav: NavItem;
  connectionStatus: ConnectionStatus;
  leftPanelCollapsed: boolean;
  rightPanelCollapsed: boolean;
  drawerOpen: boolean;

  // Sidebar actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;

  // Navigation actions
  setActiveNav: (nav: NavItem) => void;

  // Connection actions
  setConnectionStatus: (status: ConnectionStatus) => void;

  // Panel actions
  toggleLeftPanel: () => void;
  setLeftPanelCollapsed: (collapsed: boolean) => void;
  toggleRightPanel: () => void;
  setRightPanelCollapsed: (collapsed: boolean) => void;
  setDrawerOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      activeNav: 'chat',
      connectionStatus: 'connected',
      leftPanelCollapsed: false,
      rightPanelCollapsed: false,
      drawerOpen: false,

      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
      },

      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed });
      },

      setActiveNav: (nav) => {
        set({ activeNav: nav });
      },

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

      setDrawerOpen: (open) => {
        set({ drawerOpen: open });
      },
    }),
    {
      name: 'ui-storage',
    }
  )
);