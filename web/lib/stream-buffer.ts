/**
 * StreamBuffer for Markwritter
 *
 * A typewriter effect buffer for SSE text display.
 * Reveals text character-by-character at a configurable rate.
 */

/**
 * Callbacks for StreamBuffer events.
 */
export interface StreamBufferCallbacks {
  /**
   * Called when text is revealed.
   * @param messageId - The message ID
   * @param partId - Unique ID for this text part
   * @param revealedText - Text visible so far
   * @param isComplete - True when fully revealed AND sealed
   */
  onTextReveal(messageId: string, partId: string, revealedText: string, isComplete: boolean): void;

  /**
   * Called when thinking state changes.
   */
  onThinking(data: { stage: string } | null): void;

  /**
   * Called when stream is done.
   */
  onDone(data: Record<string, unknown>): void;

  /**
   * Called when an error occurs.
   */
  onError(message: string): void;
}

/**
 * Options for StreamBuffer configuration.
 */
interface StreamBufferOptions {
  /** Milliseconds between ticks. Default: 30 */
  tickMs?: number;
  /** Characters revealed per tick. Default: 1 */
  charsPerTick?: number;
}

/**
 * Internal buffer item types.
 */
type BufferItem =
  | { kind: 'text'; messageId: string; partId: string; text: string; sealed: boolean }
  | { kind: 'thinking'; stage: string }
  | { kind: 'done'; data: Record<string, unknown> }
  | { kind: 'error'; message: string };

/**
 * StreamBuffer - manages typewriter-style text reveal for SSE streams.
 *
 * Features:
 * - Character-by-character text reveal at configurable rate
 * - Pause/resume support
 * - Instant flush for restoring persisted sessions
 * - Proper cleanup with dispose
 */
export class StreamBuffer {
  // Queue
  private items: BufferItem[] = [];
  private readIndex = 0;
  private charCursor = 0;

  // Control
  private _paused = false;
  private _disposed = false;
  private timer: ReturnType<typeof setInterval> | null = null;

  // Config
  private readonly tickMs: number;
  private readonly charsPerTick: number;
  private readonly cb: StreamBufferCallbacks;
  private partCounter = 0;
  private _drainResolve: (() => void) | null = null;
  private _drainReject: ((err: Error) => void) | null = null;

  constructor(callbacks: StreamBufferCallbacks, options?: StreamBufferOptions) {
    this.cb = callbacks;
    this.tickMs = options?.tickMs ?? 30;
    this.charsPerTick = options?.charsPerTick ?? 1;
  }

  // ─── Push Methods ────────────────────────────────────────────────

  /**
   * Push text for a message.
   * If the last queue item is an unsealed text item for the same messageId,
   * the delta is appended in-place. Otherwise a new text item is created.
   */
  pushText(messageId: string, delta: string): void {
    if (this._disposed) return;

    const last = this.items[this.items.length - 1];
    if (last && last.kind === 'text' && last.messageId === messageId && !last.sealed) {
      last.text += delta;
    } else {
      this.items.push({
        kind: 'text',
        messageId,
        partId: `p${this.partCounter++}`,
        text: delta,
        sealed: false,
      });
    }
  }

  /**
   * Mark the current (last) text item as complete.
   */
  sealText(messageId: string): void {
    if (this._disposed) return;

    for (let i = this.items.length - 1; i >= 0; i--) {
      const item = this.items[i];
      if (item.kind === 'text' && item.messageId === messageId && !item.sealed) {
        item.sealed = true;
        break;
      }
    }
  }

  /**
   * Push a thinking event.
   */
  pushThinking(data: { stage: string }): void {
    if (this._disposed) return;
    this.items.push({ kind: 'thinking', ...data });
  }

  /**
   * Push a done event.
   */
  pushDone(data: Record<string, unknown> = {}): void {
    if (this._disposed) return;
    this.sealLastText();
    this.items.push({ kind: 'done', data });
  }

  /**
   * Push an error event.
   */
  pushError(message: string): void {
    if (this._disposed) return;
    this.items.push({ kind: 'error', message });
  }

  // ─── Control ─────────────────────────────────────────────────────

  /**
   * Start the tick loop. Idempotent.
   */
  start(): void {
    if (this._disposed || this.timer) return;
    this.timer = setInterval(() => this.tick(), this.tickMs);
  }

  /**
   * Instantly pause - tick becomes a no-op.
   */
  pause(): void {
    this._paused = true;
  }

  /**
   * Resume from where we left off.
   */
  resume(): void {
    this._paused = false;
  }

  /**
   * Returns a Promise that resolves when the buffer has processed all items.
   */
  waitUntilDrained(): Promise<void> {
    if (this._disposed) {
      return Promise.reject(new Error('Buffer already disposed'));
    }
    return new Promise<void>((resolve, reject) => {
      this._drainResolve = resolve;
      this._drainReject = reject;
    });
  }

  /**
   * Whether the buffer is paused.
   */
  get paused(): boolean {
    return this._paused;
  }

  /**
   * Whether the buffer is disposed.
   */
  get disposed(): boolean {
    return this._disposed;
  }

  /**
   * Flush: instantly reveal everything remaining.
   * Used when restoring persisted sessions.
   */
  flush(): void {
    if (this._disposed) return;

    while (this.readIndex < this.items.length) {
      const item = this.items[this.readIndex];
      switch (item.kind) {
        case 'text':
          this.cb.onTextReveal(item.messageId, item.partId, item.text, true);
          break;
        case 'thinking':
          this.cb.onThinking({ stage: item.stage });
          break;
        case 'done':
          this.cb.onDone(item.data);
          this._drainResolve?.();
          this._drainResolve = null;
          this._drainReject = null;
          break;
        case 'error':
          this.cb.onError(item.message);
          break;
      }
      this.readIndex++;
      this.charCursor = 0;
    }
  }

  /**
   * Stop tick loop and release resources.
   */
  dispose(): void {
    if (this._disposed) return;
    this._disposed = true;

    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }

    // Reject waiting drain promise
    this._drainReject?.(new Error('Buffer disposed'));
    this._drainResolve = null;
    this._drainReject = null;
  }

  // ─── Internals ───────────────────────────────────────────────────

  /**
   * Seal the last text item in the queue.
   */
  private sealLastText(): void {
    for (let i = this.items.length - 1; i >= 0; i--) {
      const item = this.items[i];
      if (item.kind === 'text' && !item.sealed) {
        item.sealed = true;
        break;
      }
      // Stop searching once we hit a non-text item
      if (item.kind !== 'text') break;
    }
  }

  /**
   * Process one tick - reveal characters and advance through items.
   */
  private tick(): void {
    if (this._paused || this._disposed) return;

    const item = this.items[this.readIndex];
    if (!item) return; // Queue empty or caught up

    switch (item.kind) {
      case 'text': {
        // Advance character cursor
        this.charCursor = Math.min(this.charCursor + this.charsPerTick, item.text.length);
        const revealed = item.text.slice(0, this.charCursor);
        const fullyRevealed = this.charCursor >= item.text.length;
        const isComplete = fullyRevealed && item.sealed;

        this.cb.onTextReveal(item.messageId, item.partId, revealed, isComplete);

        if (isComplete) {
          this.readIndex++;
          this.charCursor = 0;
          this.advanceNonText();
        }
        // If fullyRevealed but !sealed: wait for more SSE deltas
        break;
      }

      case 'thinking':
        this.cb.onThinking({ stage: item.stage });
        this.readIndex++;
        this.charCursor = 0;
        this.advanceNonText();
        break;

      case 'done':
        this.cb.onDone(item.data);
        this.readIndex++;
        this.charCursor = 0;
        // Stop the timer
        if (this.timer) {
          clearInterval(this.timer);
          this.timer = null;
        }
        this._drainResolve?.();
        this._drainResolve = null;
        this._drainReject = null;
        break;

      case 'error':
        this.cb.onError(item.message);
        this.readIndex++;
        this.charCursor = 0;
        // Stop the timer on error
        if (this.timer) {
          clearInterval(this.timer);
          this.timer = null;
        }
        this._drainReject?.(new Error(item.message));
        this._drainResolve = null;
        this._drainReject = null;
        break;
    }
  }

  /**
   * After processing a non-text item, keep advancing through consecutive
   * non-text items in the same tick.
   */
  private advanceNonText(): void {
    while (this.readIndex < this.items.length) {
      const next = this.items[this.readIndex];
      if (next.kind === 'text') break;

      switch (next.kind) {
        case 'thinking':
          this.cb.onThinking({ stage: next.stage });
          break;
        case 'done':
          this.cb.onDone(next.data);
          this.readIndex++;
          this.charCursor = 0;
          if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
          }
          this._drainResolve?.();
          this._drainResolve = null;
          this._drainReject = null;
          return;
        case 'error':
          this.cb.onError(next.message);
          break;
      }
      this.readIndex++;
      this.charCursor = 0;
    }
  }
}