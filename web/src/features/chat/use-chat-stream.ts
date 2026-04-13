import { useCallback, useRef, useState } from "react";
import { processSSEStream } from "@/lib/sse-parser";
import type { Citation, ConversationMessage, Message } from "@/types/chat";
import { sendMessageStream } from "./chat-api";
import { useChatStore } from "./chat-store";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const addMessage = useChatStore((s) => s.addMessage);
  const updateLastAssistantMessage = useChatStore(
    (s) => s.updateLastAssistantMessage,
  );
  const setSessionTitle = useChatStore((s) => s.setSessionTitle);
  const addCitationToLastAssistantMessage = useChatStore(
    (s) => s.addCitationToLastAssistantMessage,
  );
  const sessions = useChatStore((s) => s.sessions);
  const activeSessionId = useChatStore((s) => s.activeSessionId);

  const cancel = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsStreaming(false);
    setIsThinking(false);
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!activeSessionId || !content.trim()) return;

      setError(null);
      setIsStreaming(true);
      setIsThinking(false);

      const sessionId = activeSessionId;
      const session = sessions.find((s) => s.id === sessionId);
      if (!session) return;

      const userMessage: Message = {
        id: generateId(),
        role: "user",
        content: content.trim(),
        timestamp: Date.now(),
      };

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: "",
        timestamp: Date.now(),
      };

      addMessage(sessionId, userMessage);
      addMessage(sessionId, assistantMessage);

      if (session.messages.length === 0) {
        setSessionTitle(sessionId, content.trim().slice(0, 50));
      }

      const conversationHistory: ConversationMessage[] = session.messages.map(
        (m) => ({ role: m.role, content: m.content }),
      );

      const abortController = new AbortController();
      abortRef.current = abortController;

      let accumulated = "";

      try {
        const response = await sendMessageStream(
          {
            message: content.trim(),
            session_id: sessionId,
            sources:
              session.selectedSources.length > 0
                ? session.selectedSources
                : undefined,
            conversation_history:
              conversationHistory.length > 0 ? conversationHistory : undefined,
          },
          abortController.signal,
        );

        await processSSEStream(
          response,
          (event) => {
            switch (event.type) {
              case "thinking":
                setIsThinking(true);
                break;
              case "text_delta":
                setIsThinking(false);
                accumulated += event.content;
                updateLastAssistantMessage(sessionId, accumulated);
                break;
              case "citation":
                if (event.citation) {
                  addCitationToLastAssistantMessage(
                    sessionId,
                    event.citation as Citation,
                  );
                }
                break;
              case "done":
                break;
              case "error":
                setError(event.content);
                break;
            }
          },
          abortController.signal,
        );
      } catch (err) {
        if (err instanceof Error && err.message === "Aborted") {
          if (accumulated) {
            updateLastAssistantMessage(
              sessionId,
              `${accumulated}\n\n*[Cancelled]*`,
            );
          } else {
            updateLastAssistantMessage(sessionId, "*[Cancelled]*");
          }
        } else {
          const msg = err instanceof Error ? err.message : "Unknown error";
          setError(msg);
          if (!accumulated) {
            updateLastAssistantMessage(sessionId, `*Error: ${msg}*`);
          }
        }
      } finally {
        setIsStreaming(false);
        setIsThinking(false);
        abortRef.current = null;
      }
    },
    [
      activeSessionId,
      sessions,
      addMessage,
      updateLastAssistantMessage,
      setSessionTitle,
      addCitationToLastAssistantMessage,
    ],
  );

  return { sendMessage, isStreaming, isThinking, error, cancel };
}
