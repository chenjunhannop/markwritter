/**
 * Tests for Zustand Stores
 *
 * Tests the state management stores for chat and skills.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock the API module before importing the store
vi.mock('./api', () => ({
  getSkills: vi.fn(),
  executeSkill: vi.fn(),
}));

// Import after mocking
import { useChatStore, useSkillStore, useUIStore } from './store';
import { getSkills, executeSkill } from './api';

// Get mocked functions
const mockedGetSkills = vi.mocked(getSkills);
const mockedExecuteSkill = vi.mocked(executeSkill);

// Reset stores between tests
const resetStores = () => {
  useChatStore.setState({
    sessions: [],
    currentSessionId: null,
    isStreaming: false,
  });
  useSkillStore.setState({
    skills: [],
    selectedSkill: null,
    isLoading: false,
    error: null,
  });
};

describe('useChatStore', () => {
  beforeEach(() => {
    resetStores();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('sessions', () => {
    it('should start with empty sessions', () => {
      const state = useChatStore.getState();
      expect(state.sessions).toEqual([]);
      expect(state.currentSessionId).toBeNull();
    });

    it('should create a new session', () => {
      const store = useChatStore.getState();
      const sessionId = store.createSession('New Chat');

      const state = useChatStore.getState();
      expect(state.sessions).toHaveLength(1);
      expect(state.sessions[0].title).toBe('New Chat');
      expect(state.sessions[0].id).toBe(sessionId);
      expect(state.currentSessionId).toBe(sessionId);
    });

    it('should create session with auto-generated title', () => {
      const store = useChatStore.getState();
      store.createSession();

      const state = useChatStore.getState();
      expect(state.sessions[0].title).toBe('New Chat');
    });

    it('should select a session', () => {
      const store = useChatStore.getState();
      const id1 = store.createSession('Chat 1');
      const id2 = store.createSession('Chat 2');

      store.selectSession(id1);
      expect(useChatStore.getState().currentSessionId).toBe(id1);

      store.selectSession(id2);
      expect(useChatStore.getState().currentSessionId).toBe(id2);
    });

    it('should delete a session', () => {
      const store = useChatStore.getState();
      const id1 = store.createSession('Chat 1');
      const id2 = store.createSession('Chat 2');

      store.deleteSession(id1);

      const state = useChatStore.getState();
      expect(state.sessions).toHaveLength(1);
      expect(state.sessions[0].id).toBe(id2);
    });

    it('should clear currentSessionId when deleting current session', () => {
      const store = useChatStore.getState();
      const id = store.createSession('Chat');

      store.deleteSession(id);

      const state = useChatStore.getState();
      expect(state.currentSessionId).toBeNull();
    });
  });

  describe('messages', () => {
    it('should add a message to current session', () => {
      const store = useChatStore.getState();
      store.createSession('Test');

      store.addMessage('user', 'Hello');

      const state = useChatStore.getState();
      const session = state.sessions[0];
      expect(session.messages).toHaveLength(1);
      expect(session.messages[0].role).toBe('user');
      expect(session.messages[0].content).toBe('Hello');
    });

    it('should not add message if no current session', () => {
      const store = useChatStore.getState();
      store.addMessage('user', 'Hello');

      const state = useChatStore.getState();
      expect(state.sessions).toHaveLength(0);
    });

    it('should update message content', () => {
      const store = useChatStore.getState();
      store.createSession('Test');
      store.addMessage('assistant', 'Hello');

      const sessionId = useChatStore.getState().currentSessionId!;
      const messageId = useChatStore.getState().sessions[0].messages[0].id;

      store.updateMessage(sessionId, messageId, 'Hello World');

      const state = useChatStore.getState();
      expect(state.sessions[0].messages[0].content).toBe('Hello World');
    });

    it('should generate unique message IDs', () => {
      const store = useChatStore.getState();
      store.createSession('Test');
      store.addMessage('user', 'Msg 1');
      store.addMessage('user', 'Msg 2');

      const state = useChatStore.getState();
      const ids = state.sessions[0].messages.map((m) => m.id);
      expect(ids[0]).not.toBe(ids[1]);
    });

    it('should set streaming state', () => {
      const store = useChatStore.getState();
      expect(store.isStreaming).toBe(false);

      store.setStreaming(true);
      expect(useChatStore.getState().isStreaming).toBe(true);

      store.setStreaming(false);
      expect(useChatStore.getState().isStreaming).toBe(false);
    });
  });

  describe('getCurrentSession', () => {
    it('should return current session', () => {
      const store = useChatStore.getState();
      const id = store.createSession('Test');

      const session = store.getCurrentSession();
      expect(session).toBeDefined();
      expect(session?.id).toBe(id);
    });

    it('should return null if no current session', () => {
      const store = useChatStore.getState();
      const session = store.getCurrentSession();
      expect(session).toBeNull();
    });
  });
});

describe('useSkillStore', () => {
  beforeEach(() => {
    resetStores();
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should start with empty skills', () => {
      const state = useSkillStore.getState();
      expect(state.skills).toEqual([]);
      expect(state.selectedSkill).toBeNull();
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  describe('loadSkills', () => {
    it('should load skills and set loading state', async () => {
      const mockSkills = [
        { name: 'skill1', description: 'Skill 1', version: '1.0.0', inputs: [], output: { type: 'string', description: '' } },
        { name: 'skill2', description: 'Skill 2', version: '1.0.0', inputs: [], output: { type: 'string', description: '' } },
      ];

      mockedGetSkills.mockResolvedValue(mockSkills);

      const store = useSkillStore.getState();
      await store.loadSkills();

      const state = useSkillStore.getState();
      expect(state.skills).toEqual(mockSkills);
      expect(state.isLoading).toBe(false);
    });

    it('should handle load errors', async () => {
      mockedGetSkills.mockRejectedValue(new Error('Network error'));

      const store = useSkillStore.getState();
      await store.loadSkills();

      const state = useSkillStore.getState();
      expect(state.error).toBe('Network error');
      expect(state.isLoading).toBe(false);
    });
  });

  describe('selectSkill', () => {
    it('should select a skill', () => {
      const mockSkill = {
        name: 'translate',
        description: 'Translate text',
        version: '1.0.0',
        inputs: [],
        output: { type: 'string', description: '' },
      };

      const store = useSkillStore.getState();
      useSkillStore.setState({ skills: [mockSkill] });

      store.selectSkill('translate');

      expect(useSkillStore.getState().selectedSkill).toEqual(mockSkill);
    });

    it('should clear selection for non-existent skill', () => {
      const store = useSkillStore.getState();
      store.selectSkill('nonexistent');

      expect(useSkillStore.getState().selectedSkill).toBeNull();
    });
  });

  describe('clearSelection', () => {
    it('should clear skill selection', () => {
      const mockSkill = {
        name: 'translate',
        description: 'Translate text',
        version: '1.0.0',
        inputs: [],
        output: { type: 'string', description: '' },
      };

      useSkillStore.setState({ selectedSkill: mockSkill });
      const store = useSkillStore.getState();
      store.clearSelection();

      expect(useSkillStore.getState().selectedSkill).toBeNull();
    });
  });

  describe('executeSelectedSkill', () => {
    it('should execute selected skill and return output', async () => {
      const mockSkill = {
        name: 'translate',
        description: 'Translate text',
        version: '1.0.0',
        inputs: [],
        output: { type: 'string', description: '' },
      };

      useSkillStore.setState({ selectedSkill: mockSkill });
      mockedExecuteSkill.mockResolvedValue({ success: true, output: 'Translated text', error: '' });

      const store = useSkillStore.getState();
      const result = await store.executeSelectedSkill({ text: 'Hello' });

      expect(result).toBe('Translated text');
      expect(mockedExecuteSkill).toHaveBeenCalledWith('translate', { text: 'Hello' });
    });

    it('should return null if no skill selected', async () => {
      const store = useSkillStore.getState();
      const result = await store.executeSelectedSkill({});

      expect(result).toBeNull();
      expect(useSkillStore.getState().error).toBe('No skill selected');
    });
  });
});

// ==================== Phase 2: NavItem type extension ====================

describe('NavItem type extension (Phase 2)', () => {
  it('should allow setActiveNav with explore, query, record', () => {
    const store = useUIStore.getState();

    store.setActiveNav('explore');
    expect(useUIStore.getState().activeNav).toBe('explore');

    store.setActiveNav('query');
    expect(useUIStore.getState().activeNav).toBe('query');

    store.setActiveNav('record');
    expect(useUIStore.getState().activeNav).toBe('record');

    // Reset to default
    store.setActiveNav('chat');
  });
});

