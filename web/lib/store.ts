/**
 * Zustand Stores for Markwritter
 *
 * State management for chat, skills, and settings.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Skill, Session, Message, MessageRole } from './types';
import { getSkills, executeSkill, getSettings, updateSettings } from './api';

// ==================== Chat Store ====================

interface ChatState {
  sessions: Session[];
  currentSessionId: string | null;
  isStreaming: boolean;

  // Session actions
  createSession: (title?: string) => string;
  selectSession: (id: string) => void;
  deleteSession: (id: string) => void;

  // Message actions
  addMessage: (role: MessageRole, content: string) => void;
  updateMessage: (sessionId: string, messageId: string, content: string) => void;

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

      createSession: (title = 'New Chat') => {
        const id = crypto.randomUUID();
        const now = Date.now();
        const newSession: Session = {
          id,
          title,
          messages: [],
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
        set({ currentSessionId: id });
      },

      deleteSession: (id) => {
        set((state) => {
          const sessions = state.sessions.filter((s) => s.id !== id);
          const currentSessionId =
            state.currentSessionId === id ? null : state.currentSessionId;
          return { sessions, currentSessionId };
        });
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
      name: 'chat-storage',
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

export type NavItem = 'chat' | 'skills' | 'logs' | 'settings';
export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error';

interface UIState {
  sidebarCollapsed: boolean;
  activeNav: NavItem;
  connectionStatus: ConnectionStatus;

  // Sidebar actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;

  // Navigation actions
  setActiveNav: (nav: NavItem) => void;

  // Connection actions
  setConnectionStatus: (status: ConnectionStatus) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      activeNav: 'chat',
      connectionStatus: 'connected',

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
    }),
    {
      name: 'ui-storage',
    }
  )
);

// ==================== Settings Store ====================

export interface AppSettings {
  theme: 'light' | 'dark' | 'system';
  language: string;
  [key: string]: unknown;
}

interface SettingsState {
  settings: AppSettings | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  loadSettings: () => Promise<void>;
  updateSettingsAction: (updates: Partial<AppSettings>) => Promise<void>;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      settings: null,
      isLoading: false,
      error: null,

      loadSettings: async () => {
        set({ isLoading: true, error: null });
        try {
          const settings = await getSettings();
          set({ settings: settings as AppSettings, isLoading: false });
        } catch (e) {
          const error = e instanceof Error ? e.message : 'Failed to load settings';
          set({ error, isLoading: false });
        }
      },

      updateSettingsAction: async (updates) => {
        set({ isLoading: true, error: null });
        try {
          const result = await updateSettings(updates);
          set({ settings: result.settings as AppSettings, isLoading: false });
        } catch (e) {
          const error = e instanceof Error ? e.message : 'Failed to update settings';
          set({ error, isLoading: false });
        }
      },

      setTheme: (theme) => {
        set((state) => ({
          settings: {
            theme,
            language: state.settings?.language ?? 'en',
          },
        }));
      },
    }),
    {
      name: 'settings-storage',
    }
  )
);