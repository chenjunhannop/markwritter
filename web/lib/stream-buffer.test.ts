/**
 * Tests for StreamBuffer
 *
 * Tests the typewriter effect buffer for SSE text display.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { StreamBuffer } from './stream-buffer';

describe('StreamBuffer', () => {
  let callbacks: {
    onTextReveal: ReturnType<typeof vi.fn>;
    onThinking: ReturnType<typeof vi.fn>;
    onDone: ReturnType<typeof vi.fn>;
    onError: ReturnType<typeof vi.fn>;
  };

  beforeEach(() => {
    vi.useFakeTimers();
    callbacks = {
      onTextReveal: vi.fn(),
      onThinking: vi.fn(),
      onDone: vi.fn(),
      onError: vi.fn(),
    };
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('constructor', () => {
    it('should create a buffer with default options', () => {
      const buffer = new StreamBuffer(callbacks);
      expect(buffer.paused).toBe(false);
      expect(buffer.disposed).toBe(false);
    });

    it('should accept custom tick and charsPerTick options', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 50,
        charsPerTick: 2,
      });
      expect(buffer).toBeDefined();
    });
  });

  describe('pushText and tick', () => {
    it('should reveal text character by character', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 1,
      });

      buffer.pushText('msg-1', 'ABC');
      buffer.start();

      // First tick: reveals 'A'
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'A', false);

      // Second tick: reveals 'AB'
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'AB', false);

      // Third tick: reveals 'ABC' - still not complete (not sealed)
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'ABC', false);

      buffer.dispose();
    });

    it('should reveal multiple chars per tick', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 2,
      });

      buffer.pushText('msg-1', 'ABCDEF');
      buffer.start();

      // First tick: reveals 'AB'
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'AB', false);

      // Second tick: reveals 'ABCD'
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'ABCD', false);

      // Third tick: reveals 'ABCDEF'
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'ABCDEF', false);

      buffer.dispose();
    });

    it('should mark text as complete when sealed', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 3,
      });

      buffer.pushText('msg-1', 'ABC');
      buffer.sealText('msg-1');
      buffer.start();

      // One tick reveals all and marks complete
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'ABC', true);

      buffer.dispose();
    });

    it('should append text to existing unsealed item', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 1,
      });

      buffer.pushText('msg-1', 'A');
      buffer.pushText('msg-1', 'B');
      buffer.pushText('msg-1', 'C');
      buffer.sealText('msg-1');
      buffer.start();

      // Should process as single item 'ABC'
      vi.advanceTimersByTime(90);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'ABC', true);

      buffer.dispose();
    });

    it('should create new text item for different message', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 3,
      });

      buffer.pushText('msg-1', 'ABC');
      buffer.sealText('msg-1');
      buffer.pushText('msg-2', 'XYZ');
      buffer.sealText('msg-2');
      buffer.start();

      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'ABC', true);

      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-2', 'p1', 'XYZ', true);

      buffer.dispose();
    });
  });

  describe('pushThinking', () => {
    it('should call onThinking callback', () => {
      const buffer = new StreamBuffer(callbacks, { tickMs: 30 });
      buffer.pushThinking({ stage: 'analyzing' });
      buffer.start();

      vi.advanceTimersByTime(30);
      expect(callbacks.onThinking).toHaveBeenCalledWith({ stage: 'analyzing' });

      buffer.dispose();
    });
  });

  describe('pushDone', () => {
    it('should call onDone callback and stop timer', () => {
      const buffer = new StreamBuffer(callbacks, { tickMs: 30 });
      buffer.pushDone({});
      buffer.start();

      vi.advanceTimersByTime(30);
      expect(callbacks.onDone).toHaveBeenCalled();

      // Timer should be stopped after done
      vi.advanceTimersByTime(100);
      expect(callbacks.onDone).toHaveBeenCalledTimes(1);

      buffer.dispose();
    });
  });

  describe('pushError', () => {
    it('should call onError callback', () => {
      const buffer = new StreamBuffer(callbacks, { tickMs: 30 });
      buffer.pushError('Something went wrong');
      buffer.start();

      vi.advanceTimersByTime(30);
      expect(callbacks.onError).toHaveBeenCalledWith('Something went wrong');

      buffer.dispose();
    });
  });

  describe('pause and resume', () => {
    it('should pause and resume text reveal', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 1,
      });

      buffer.pushText('msg-1', 'ABC');
      buffer.sealText('msg-1');
      buffer.start();

      // First tick: 'A'
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledTimes(1);

      // Pause
      buffer.pause();
      expect(buffer.paused).toBe(true);

      // Ticks during pause do nothing
      vi.advanceTimersByTime(90);
      expect(callbacks.onTextReveal).toHaveBeenCalledTimes(1);

      // Resume
      buffer.resume();
      expect(buffer.paused).toBe(false);

      // Continue revealing
      vi.advanceTimersByTime(30);
      expect(callbacks.onTextReveal).toHaveBeenCalledTimes(2);

      buffer.dispose();
    });
  });

  describe('flush', () => {
    it('should instantly reveal all content', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 1,
      });

      buffer.pushText('msg-1', 'ABCDEF');
      buffer.sealText('msg-1');
      buffer.pushDone({});

      // Flush instantly reveals everything
      buffer.flush();

      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'ABCDEF', true);
      expect(callbacks.onDone).toHaveBeenCalled();

      buffer.dispose();
    });
  });

  describe('dispose', () => {
    it('should stop timer and mark as disposed', () => {
      const buffer = new StreamBuffer(callbacks, { tickMs: 30 });
      buffer.start();
      buffer.dispose();

      expect(buffer.disposed).toBe(true);

      // No more callbacks after dispose
      vi.advanceTimersByTime(100);
      expect(callbacks.onTextReveal).not.toHaveBeenCalled();
    });

    it('should ignore pushes after dispose', () => {
      const buffer = new StreamBuffer(callbacks, { tickMs: 30 });
      buffer.dispose();

      buffer.pushText('msg-1', 'ABC');
      buffer.start();

      vi.advanceTimersByTime(100);
      expect(callbacks.onTextReveal).not.toHaveBeenCalled();
    });
  });

  describe('waitUntilDrained', () => {
    it('should resolve when done event is processed', async () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 5,
      });

      buffer.pushText('msg-1', 'ABC');
      buffer.sealText('msg-1');
      buffer.pushDone({});
      buffer.start();

      const drainPromise = buffer.waitUntilDrained();

      // Advance timers to process all events
      vi.advanceTimersByTime(100);

      await expect(drainPromise).resolves.toBeUndefined();
    });

    it('should reject if buffer is disposed before drain', async () => {
      const buffer = new StreamBuffer(callbacks, { tickMs: 30 });
      buffer.start();

      const drainPromise = buffer.waitUntilDrained();
      buffer.dispose();

      await expect(drainPromise).rejects.toThrow('Buffer disposed');
    });
  });

  describe('complex scenarios', () => {
    it('should handle mixed event sequence', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 5,
      });

      buffer.pushThinking({ stage: 'start' });
      buffer.pushText('msg-1', 'Hello');
      buffer.sealText('msg-1');
      buffer.pushDone({});

      buffer.start();

      // Process all events
      vi.advanceTimersByTime(200);

      expect(callbacks.onThinking).toHaveBeenCalled();
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', 'Hello', true);
      expect(callbacks.onDone).toHaveBeenCalled();

      buffer.dispose();
    });

    it('should handle empty text gracefully', () => {
      const buffer = new StreamBuffer(callbacks, {
        tickMs: 30,
        charsPerTick: 1,
      });

      buffer.pushText('msg-1', '');
      buffer.sealText('msg-1');
      buffer.start();

      vi.advanceTimersByTime(30);

      // Empty text should still call onTextReveal with empty string
      expect(callbacks.onTextReveal).toHaveBeenCalledWith('msg-1', 'p0', '', true);

      buffer.dispose();
    });
  });
});