export interface SSEEvent {
  type: string;
  content?: string;
}

export async function* parseSSEStream(
  response: Response
): AsyncGenerator<SSEEvent> {
  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const eventStr of events) {
      const line = eventStr.trim();
      if (!line.startsWith("data: ")) continue;

      try {
        const data = JSON.parse(line.slice(6));
        yield data;
      } catch {
        console.warn("Failed to parse SSE event:", line);
      }
    }
  }
}

export async function streamChat(
  message: string,
  onEvent: (event: SSEEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const response = await fetch(`${API_BASE}/api/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
    signal,
  });

  if (!response.ok) throw new Error("Chat request failed");

  for await (const event of parseSSEStream(response)) {
    onEvent(event);
  }
}