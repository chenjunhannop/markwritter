"use client";

import { useEffect, useRef } from "react";
import { Bot, User } from "lucide-react";

import type { Message } from "@/lib/store";

interface MessageListProps {
  messages: Message[];
  currentResponse: string;
  isStreaming: boolean;
}

export function MessageList({
  messages,
  currentResponse,
  isStreaming,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentResponse]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      {isStreaming && currentResponse && (
        <MessageItem
          message={{
            id: "streaming",
            role: "assistant",
            content: currentResponse,
            timestamp: Date.now(),
          }}
          isStreaming
        />
      )}
      <div ref={scrollRef} />
    </div>
  );
}

function MessageItem({
  message,
  isStreaming,
}: {
  message: Message;
  isStreaming?: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? "bg-blue-500" : "bg-gray-500"
        }`}
      >
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-white" />
        )}
      </div>
      <div
        className={`max-w-[80%] px-4 py-2 rounded-lg ${
          isUser ? "bg-blue-500 text-white" : "bg-gray-100"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {isStreaming && (
          <span className="inline-block w-2 h-4 ml-1 bg-gray-400 animate-pulse" />
        )}
      </div>
    </div>
  );
}