/**
 * Tests for SSE Processing Utility
 *
 * Tests the SSE stream parser and event processor.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { processSSEStream, SSEParser } from './sse';
import type { ChatEvent } from './types';

// Helper to create a mock ReadableStream from chunks
function createMockStream(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  let index = 0;

  return new ReadableStream({
    pull(controller) {
      if (index < chunks.length) {
        controller.enqueue(encoder.encode(chunks[index]));
        index++;
      } else {
        controller.close();
      }
    },
  });
}

// Helper to create a Response with a mock body
function createMockResponse(chunks: string[]): Response {
  return {
    ok: true,
    body: createMockStream(chunks),
  } as Response;
}

describe('SSE Processing', () => {
  describe('SSEParser', () => {
    let parser: SSEParser;

    beforeEach(() => {
      parser = new SSEParser();
    });

    it('should parse a single SSE event', () => {
      const chunk = 'data: {"type":"thinking","content":"Processing..."}\n\n';
      const events = parser.parse(chunk);

      expect(events).toHaveLength(1);
      expect(events[0]).toEqual({
        type: 'thinking',
        content: 'Processing...',
      });
    });

    it('should parse multiple SSE events in one chunk', () => {
      const chunk =
        'data: {"type":"text_delta","content":"Hello"}\n\n' +
        'data: {"type":"text_delta","content":" World"}\n\n';
      const events = parser.parse(chunk);

      expect(events).toHaveLength(2);
      expect(events[0]).toEqual({ type: 'text_delta', content: 'Hello' });
      expect(events[1]).toEqual({ type: 'text_delta', content: ' World' });
    });

    it('should handle incomplete events (buffering)', () => {
      // First chunk is incomplete
      const events1 = parser.parse('data: {"type":"text_delta","content":"He');
      expect(events1).toHaveLength(0);

      // Second chunk completes the event
      const events2 = parser.parse('llo"}\n\n');
      expect(events2).toHaveLength(1);
      expect(events2[0]).toEqual({ type: 'text_delta', content: 'Hello' });
    });

    it('should skip non-data lines', () => {
      const chunk =
        ': this is a comment\n' +
        'data: {"type":"done","content":""}\n\n';
      const events = parser.parse(chunk);

      expect(events).toHaveLength(1);
      expect(events[0].type).toBe('done');
    });

    it('should handle empty data lines', () => {
      const chunk = 'data: \n\ndata: {"type":"done","content":""}\n\n';
      const events = parser.parse(chunk);

      expect(events).toHaveLength(1);
      expect(events[0].type).toBe('done');
    });

    it('should parse all event types', () => {
      const events = parser.parse(
        'data: {"type":"thinking","content":"stage1"}\n\n' +
        'data: {"type":"text_delta","content":"text"}\n\n' +
        'data: {"type":"done","content":""}\n\n' +
        'data: {"type":"error","content":"Something went wrong"}\n\n'
      );

      expect(events).toHaveLength(4);
      expect(events[0].type).toBe('thinking');
      expect(events[1].type).toBe('text_delta');
      expect(events[2].type).toBe('done');
      expect(events[3].type).toBe('error');
    });

    it('should handle JSON parse errors gracefully', () => {
      const chunk = 'data: {invalid json}\n\ndata: {"type":"done","content":""}\n\n';
      const events = parser.parse(chunk);

      // Should skip invalid event and continue
      expect(events).toHaveLength(1);
      expect(events[0].type).toBe('done');
    });
  });

  describe('processSSEStream', () => {
    it('should process a complete SSE stream', async () => {
      const chunks = [
        'data: {"type":"thinking","content":""}\n\n',
        'data: {"type":"text_delta","content":"Hello"}\n\n',
        'data: {"type":"text_delta","content":" World"}\n\n',
        'data: {"type":"done","content":""}\n\n',
      ];
      const response = createMockResponse(chunks);
      const events: ChatEvent[] = [];

      await processSSEStream(response, (event) => {
        events.push(event);
      });

      expect(events).toHaveLength(4);
      expect(events[0].type).toBe('thinking');
      expect(events[1].content).toBe('Hello');
      expect(events[2].content).toBe(' World');
      expect(events[3].type).toBe('done');
    });

    it('should call onEvent for each parsed event', async () => {
      const chunks = [
        'data: {"type":"text_delta","content":"A"}\n\n' +
        'data: {"type":"text_delta","content":"B"}\n\n' +
        'data: {"type":"text_delta","content":"C"}\n\n',
      ];
      const response = createMockResponse(chunks);
      const onEvent = vi.fn();

      await processSSEStream(response, onEvent);

      expect(onEvent).toHaveBeenCalledTimes(3);
    });

    it('should throw error if response body is null', async () => {
      const response = { ok: true, body: null } as unknown as Response;

      await expect(processSSEStream(response, vi.fn())).rejects.toThrow('No response body');
    });

    it('should check abort signal before processing events', async () => {
      const controller = new AbortController();
      controller.abort(); // Abort immediately

      const chunks = ['data: {"type":"text_delta","content":"Start"}\n\n'];
      const response = createMockResponse(chunks);

      // Even though stream has data, abort should be checked
      const onEvent = vi.fn();

      // Since we abort before processing, it should throw
      await expect(
        processSSEStream(response, onEvent, controller.signal)
      ).rejects.toThrow('Aborted');
    });

    it('should accumulate text_delta events', async () => {
      const chunks = [
        'data: {"type":"text_delta","content":"The "}\n\n',
        'data: {"type":"text_delta","content":"quick "}\n\n',
        'data: {"type":"text_delta","content":"brown "}\n\n',
        'data: {"type":"text_delta","content":"fox"}\n\n',
        'data: {"type":"done","content":""}\n\n',
      ];
      const response = createMockResponse(chunks);
      const textParts: string[] = [];

      await processSSEStream(response, (event) => {
        if (event.type === 'text_delta') {
          textParts.push(event.content);
        }
      });

      expect(textParts.join('')).toBe('The quick brown fox');
    });

    it('should handle error events', async () => {
      const chunks = [
        'data: {"type":"thinking","content":""}\n\n',
        'data: {"type":"error","content":"Something went wrong"}\n\n',
      ];
      const response = createMockResponse(chunks);
      const events: ChatEvent[] = [];

      await processSSEStream(response, (event) => {
        events.push(event);
      });

      expect(events).toHaveLength(2);
      expect(events[1].type).toBe('error');
      expect(events[1].content).toBe('Something went wrong');
    });

    it('should handle mixed chunk sizes', async () => {
      // Single events split across chunks
      const chunks = [
        'data: {"type":"text_delta","content":"He',
        'llo"}\n\ndata: {"type":"text_delta","content":" ',
        'World"}\n\ndata: {"type":"done","content":""}\n\n',
      ];
      const response = createMockResponse(chunks);
      const events: ChatEvent[] = [];

      await processSSEStream(response, (event) => {
        events.push(event);
      });

      expect(events).toHaveLength(3);
      expect(events[0].content).toBe('Hello');
      expect(events[1].content).toBe(' World');
      expect(events[2].type).toBe('done');
    });
  });
});