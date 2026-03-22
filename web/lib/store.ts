import { create } from "zustand";
import { persist } from "zustand/middleware";

// Chat state
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

interface ChatState {
  messages: Message[];
  isStreaming: boolean;
  addMessage: (message: Omit<Message, "id" | "timestamp">) => void;
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
    { name: "chat-storage" }
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