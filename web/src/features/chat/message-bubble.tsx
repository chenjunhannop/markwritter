import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import type { Message } from "@/types/chat";
import { CitationBadge } from "./citation-badge";

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex w-full gap-3",
        isUser ? "justify-end" : "justify-start",
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-lg px-4 py-2.5 text-sm leading-relaxed",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground",
          isStreaming && !isUser && "animate-pulse",
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm max-w-none dark:prose-invert prose-p:my-1 prose-pre:my-2 prose-pre:rounded-md prose-pre:bg-background prose-code:text-xs prose-headings:my-2">
            {message.content ? (
              <Markdown remarkPlugins={[remarkGfm]}>{message.content}</Markdown>
            ) : (
              <span className="text-muted-foreground">...</span>
            )}
          </div>
        )}
      </div>

      {!isUser && message.citations && message.citations.length > 0 && (
        <div className="flex max-w-[80%] flex-wrap gap-1">
          {message.citations.map((citation, i) => (
            <CitationBadge
              key={`${citation.file_path}-${citation.page_num}-${citation.paragraph_idx}`}
              citation={citation}
              index={i}
            />
          ))}
        </div>
      )}
    </div>
  );
}
