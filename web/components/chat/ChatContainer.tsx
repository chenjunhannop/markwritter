"use client";

import { useCallback, useRef, useState } from "react";

import { useChatStore } from "@/lib/store";
import { streamChat } from "@/lib/sse";

import { InputBar } from "./InputBar";
import { MessageList } from "./MessageList";

export function ChatContainer() {
  const { messages, addMessage, isStreaming, setStreaming } = useChatStore();
  const [currentResponse, setCurrentResponse] = useState("");
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSubmit = useCallback(
    async (input: string) => {
      if (isStreaming) return;

      addMessage({ role: "user", content: input });
      setStreaming(true);
      setCurrentResponse("");

      abortControllerRef.current = new AbortController();

      try {
        let accumulatedResponse = "";
        await streamChat(
          input,
          (event) => {
            switch (event.type) {
              case "text_delta":
                accumulatedResponse += event.content || "";
                setCurrentResponse(accumulatedResponse);
                break;
              case "done":
                addMessage({ role: "assistant", content: accumulatedResponse });
                setCurrentResponse("");
                setStreaming(false);
                break;
              case "error":
                console.error("Chat error:", event);
                setStreaming(false);
                break;
            }
          },
          abortControllerRef.current.signal
        );
      } catch (error) {
        console.error("Stream error:", error);
        setStreaming(false);
      }
    },
    [isStreaming, addMessage, setStreaming]
  );

  const handleStop = useCallback(() => {
    abortControllerRef.current?.abort();
    setStreaming(false);
  }, [setStreaming]);

  return (
    <div className="flex flex-col h-full">
      <MessageList
        messages={messages}
        currentResponse={currentResponse}
        isStreaming={isStreaming}
      />
      <InputBar
        onSubmit={handleSubmit}
        onStop={handleStop}
        isStreaming={isStreaming}
      />
    </div>
  );
}