"use client";

import { useCallback, useState } from "react";
import { Send, Square } from "lucide-react";

interface InputBarProps {
  onSubmit: (input: string) => void;
  onStop: () => void;
  isStreaming: boolean;
}

export function InputBar({ onSubmit, onStop, isStreaming }: InputBarProps) {
  const [input, setInput] = useState("");

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    onSubmit(trimmed);
    setInput("");
  }, [input, isStreaming, onSubmit]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="border-t p-4">
      <div className="flex gap-2 items-end">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message... (Enter to send, Shift+Enter for newline)"
          className="flex-1 resize-none border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={1}
          disabled={isStreaming}
        />
        {isStreaming ? (
          <button
            onClick={onStop}
            className="p-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
          >
            <Square size={20} />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="p-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={20} />
          </button>
        )}
      </div>
    </div>
  );
}