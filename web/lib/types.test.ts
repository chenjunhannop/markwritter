/**
 * Type definitions tests for Markwritter
 *
 * These tests verify the type definitions match the backend API models.
 */

import { describe, it, expect } from 'vitest';
import {
  isSkillIntent,
  isChatIntent,
  isErrorEvent,
  isTextDeltaEvent,
  isDoneEvent,
  type Intent,
  type ChatEvent,
} from './types';

describe('Types', () => {
  describe('Message type', () => {
    it('should define a valid user message', () => {
      const message = {
        id: 'msg-1',
        role: 'user' as const,
        content: 'Hello, world!',
        timestamp: Date.now(),
      };

      expect(message.id).toBe('msg-1');
      expect(message.role).toBe('user');
      expect(message.content).toBe('Hello, world!');
      expect(message.timestamp).toBeTypeOf('number');
    });

    it('should define a valid assistant message', () => {
      const message = {
        id: 'msg-2',
        role: 'assistant' as const,
        content: 'Hello! How can I help you?',
        timestamp: Date.now(),
      };

      expect(message.role).toBe('assistant');
    });
  });

  describe('Skill type', () => {
    it('should define a valid skill with required fields', () => {
      const skill = {
        name: 'example-skill',
        description: 'An example skill',
        version: '1.0.0',
      };

      expect(skill.name).toBe('example-skill');
      expect(skill.description).toBe('An example skill');
      expect(skill.version).toBe('1.0.0');
    });

    it('should define a skill with inputs', () => {
      const skill = {
        name: 'skill-with-inputs',
        description: 'A skill with inputs',
        version: '2.0.0',
        inputs: [
          { name: 'param1', type: 'string', description: 'First param', required: true },
          { name: 'param2', type: 'number', description: 'Second param', required: false },
        ],
        output: { type: 'string', description: 'Output description' },
      };

      expect(skill.inputs).toHaveLength(2);
      expect(skill.inputs?.[0].name).toBe('param1');
      expect(skill.inputs?.[1].required).toBe(false);
    });
  });

  describe('ChatEvent type', () => {
    it('should define a thinking event', () => {
      const event = {
        type: 'thinking' as const,
        content: '',
      };

      expect(event.type).toBe('thinking');
    });

    it('should define a text_delta event', () => {
      const event = {
        type: 'text_delta' as const,
        content: 'Hello',
      };

      expect(event.type).toBe('text_delta');
      expect(event.content).toBe('Hello');
    });

    it('should define a done event', () => {
      const event = {
        type: 'done' as const,
        content: '',
      };

      expect(event.type).toBe('done');
    });

    it('should define an error event', () => {
      const event = {
        type: 'error' as const,
        content: 'Something went wrong',
      };

      expect(event.type).toBe('error');
      expect(event.content).toBe('Something went wrong');
    });
  });

  describe('Session type', () => {
    it('should define a valid session', () => {
      const session = {
        id: 'session-1',
        title: 'Test Session',
        messages: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };

      expect(session.id).toBe('session-1');
      expect(session.title).toBe('Test Session');
      expect(session.messages).toEqual([]);
    });

    it('should define a session with messages', () => {
      const session = {
        id: 'session-2',
        title: 'Session with messages',
        messages: [
          { id: 'msg-1', role: 'user' as const, content: 'Hi', timestamp: 1000 },
          { id: 'msg-2', role: 'assistant' as const, content: 'Hello!', timestamp: 1001 },
        ],
        createdAt: 1000,
        updatedAt: 1001,
      };

      expect(session.messages).toHaveLength(2);
    });
  });

  describe('Intent type', () => {
    it('should define a skill execution intent', () => {
      const intent = {
        type: 'skill' as const,
        skillName: 'example-skill',
        params: { param1: 'value1' },
        confidence: 0.95,
      };

      expect(intent.type).toBe('skill');
      expect(intent.skillName).toBe('example-skill');
      expect(intent.confidence).toBe(0.95);
    });

    it('should define a chat intent', () => {
      const intent = {
        type: 'chat' as const,
        message: 'Hello, how are you?',
        confidence: 0.9,
      };

      expect(intent.type).toBe('chat');
      expect(intent.message).toBe('Hello, how are you?');
    });
  });

  describe('Type Guards', () => {
    describe('isSkillIntent', () => {
      it('should return true for skill intent', () => {
        const intent: Intent = {
          type: 'skill',
          skillName: 'test-skill',
          params: {},
          confidence: 0.9,
        };
        expect(isSkillIntent(intent)).toBe(true);
      });

      it('should return false for chat intent', () => {
        const intent: Intent = {
          type: 'chat',
          message: 'Hello',
          confidence: 0.8,
        };
        expect(isSkillIntent(intent)).toBe(false);
      });
    });

    describe('isChatIntent', () => {
      it('should return true for chat intent', () => {
        const intent: Intent = {
          type: 'chat',
          message: 'Hello',
          confidence: 0.8,
        };
        expect(isChatIntent(intent)).toBe(true);
      });

      it('should return false for skill intent', () => {
        const intent: Intent = {
          type: 'skill',
          skillName: 'test-skill',
          params: {},
          confidence: 0.9,
        };
        expect(isChatIntent(intent)).toBe(false);
      });
    });

    describe('isErrorEvent', () => {
      it('should return true for error event', () => {
        const event: ChatEvent = { type: 'error', content: 'Error message' };
        expect(isErrorEvent(event)).toBe(true);
      });

      it('should return false for non-error events', () => {
        const events: ChatEvent[] = [
          { type: 'thinking', content: '' },
          { type: 'text_delta', content: 'Hello' },
          { type: 'done', content: '' },
        ];
        events.forEach((event) => {
          expect(isErrorEvent(event)).toBe(false);
        });
      });
    });

    describe('isTextDeltaEvent', () => {
      it('should return true for text_delta event', () => {
        const event: ChatEvent = { type: 'text_delta', content: 'Hello' };
        expect(isTextDeltaEvent(event)).toBe(true);
      });

      it('should return false for non-text_delta events', () => {
        const events: ChatEvent[] = [
          { type: 'thinking', content: '' },
          { type: 'error', content: 'Error' },
          { type: 'done', content: '' },
        ];
        events.forEach((event) => {
          expect(isTextDeltaEvent(event)).toBe(false);
        });
      });
    });

    describe('isDoneEvent', () => {
      it('should return true for done event', () => {
        const event: ChatEvent = { type: 'done', content: '' };
        expect(isDoneEvent(event)).toBe(true);
      });

      it('should return false for non-done events', () => {
        const events: ChatEvent[] = [
          { type: 'thinking', content: '' },
          { type: 'text_delta', content: 'Hello' },
          { type: 'error', content: 'Error' },
        ];
        events.forEach((event) => {
          expect(isDoneEvent(event)).toBe(false);
        });
      });
    });
  });
});