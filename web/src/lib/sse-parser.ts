import type { ChatEvent } from "@/types/chat";

export class SSEParser {
  private buffer = "";

  parse(chunk: string): ChatEvent[] {
    this.buffer += chunk;
    const events: ChatEvent[] = [];
    const parts = this.buffer.split("\n\n");
    this.buffer = parts.pop() || "";

    for (const part of parts) {
      const event = this.parseEvent(part);
      if (event) {
        events.push(event);
      }
    }

    return events;
  }

  private parseEvent(eventStr: string): ChatEvent | null {
    const lines = eventStr.split("\n");

    for (const line of lines) {
      if (line.startsWith(":")) continue;
      if (line.startsWith("data: ")) {
        const dataStr = line.slice(6).trim();
        if (!dataStr) continue;
        try {
          return JSON.parse(dataStr) as ChatEvent;
        } catch {
          // Skip malformed SSE events
        }
      }
    }

    return null;
  }

  reset(): void {
    this.buffer = "";
  }
}

export async function processSSEStream(
  response: Response,
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  const parser = new SSEParser();

  try {
    while (true) {
      if (signal?.aborted) throw new Error("Aborted");

      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      const events = parser.parse(chunk);

      for (const event of events) {
        if (signal?.aborted) throw new Error("Aborted");
        onEvent(event);
      }
    }
  } finally {
    reader.releaseLock();
  }
}
