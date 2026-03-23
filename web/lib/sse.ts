/**
 * SSE Processing Utility for Markwritter
 *
 * Provides functions for parsing and processing Server-Sent Events (SSE)
 * from the chat API stream.
 */

import type { ChatEvent } from './types';

/**
 * SSE Parser class for incremental parsing of SSE events.
 * Handles chunked data and incomplete events.
 */
export class SSEParser {
  private buffer = '';

  /**
   * Parse a chunk of SSE data and return complete events.
   * Incomplete events are buffered for the next call.
   *
   * @param chunk - Raw text chunk from the stream
   * @returns Array of parsed ChatEvent objects
   */
  parse(chunk: string): ChatEvent[] {
    this.buffer += chunk;
    const events: ChatEvent[] = [];

    // Split on double newline (SSE event delimiter)
    const parts = this.buffer.split('\n\n');

    // Last part may be incomplete, keep it in buffer
    this.buffer = parts.pop() || '';

    for (const part of parts) {
      const event = this.parseEvent(part);
      if (event) {
        events.push(event);
      }
    }

    return events;
  }

  /**
   * Parse a single SSE event string.
   */
  private parseEvent(eventStr: string): ChatEvent | null {
    const lines = eventStr.split('\n');

    for (const line of lines) {
      // Skip comments
      if (line.startsWith(':')) continue;

      // Parse data lines
      if (line.startsWith('data: ')) {
        const dataStr = line.slice(6).trim();

        // Skip empty data
        if (!dataStr) continue;

        try {
          return JSON.parse(dataStr) as ChatEvent;
        } catch {
          // Skip malformed SSE events silently in production
          if (process.env.NODE_ENV === 'development') {
            // eslint-disable-next-line no-console
            console.warn('Failed to parse SSE event:', line);
          }
        }
      }
    }

    return null;
  }

  /**
   * Reset the parser state.
   */
  reset(): void {
    this.buffer = '';
  }
}

/**
 * Process an SSE stream from a Response.
 *
 * @param response - The Response object with a ReadableStream body
 * @param onEvent - Callback for each parsed ChatEvent
 * @param signal - Optional AbortSignal for cancellation
 */
export async function processSSEStream(
  response: Response,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const reader = response.body?.getReader();

  if (!reader) {
    throw new Error('No response body');
  }

  const decoder = new TextDecoder();
  const parser = new SSEParser();

  try {
    while (true) {
      if (signal?.aborted) {
        throw new Error('Aborted');
      }

      const { done, value } = await reader.read();

      if (done) {
        // Process any remaining buffer
        const remaining = (parser as unknown as { buffer: string }).buffer;
        if (remaining) {
          const lines = remaining.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim();
              if (dataStr) {
                try {
                  const event = JSON.parse(dataStr) as ChatEvent;
                  onEvent(event);
                } catch {
                  // Ignore parse errors for incomplete final chunk
                }
              }
            }
          }
        }
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      const events = parser.parse(chunk);

      for (const event of events) {
        if (signal?.aborted) {
          throw new Error('Aborted');
        }
        onEvent(event);
      }
    }
  } finally {
    reader.releaseLock();
  }
}