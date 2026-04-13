import { FileText, Loader2, MessageSquarePlus } from "lucide-react";
import { useEffect, useRef } from "react";
import { EmptyState } from "@/components/shared/empty-state";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useChatStore } from "./chat-store";
import { MessageBubble } from "./message-bubble";
import { MessageInput } from "./message-input";
import { useChatStream } from "./use-chat-stream";

interface ChatAreaProps {
  onToggleSources: () => void;
  sourcesOpen: boolean;
  onNewChat: () => void;
}

export function ChatArea({
  onToggleSources,
  sourcesOpen,
  onNewChat,
}: ChatAreaProps) {
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const sessions = useChatStore((s) => s.sessions);
  const session = sessions.find((s) => s.id === activeSessionId);
  const { sendMessage, isStreaming, isThinking, cancel } = useChatStream();
  const bottomRef = useRef<HTMLDivElement>(null);
  const messages = session?.messages ?? [];
  const sourceCount = session?.selectedSources.length ?? 0;
  const messageLen = messages.length;

  useEffect(() => {
    if (messageLen > 0 || isThinking) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messageLen, isThinking]);

  if (!session) {
    return (
      <div className="flex h-full items-center justify-center">
        <EmptyState
          icon={
            <MessageSquarePlus className="h-6 w-6 text-muted-foreground/50" />
          }
          title="No conversation selected"
          description="Create a new chat to get started"
          action={
            <Button type="button" onClick={onNewChat}>
              New Chat
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div className="flex items-center gap-2 min-w-0">
          <h2 className="truncate text-sm font-semibold">{session.title}</h2>
          {sourceCount > 0 && (
            <Badge
              variant="secondary"
              className="cursor-pointer shrink-0"
              onClick={onToggleSources}
            >
              <FileText className="mr-1 h-3 w-3" />
              {sourceCount} source{sourceCount !== 1 ? "s" : ""}
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-1">
          {!sourcesOpen && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={onToggleSources}
            >
              <FileText className="h-3.5 w-3.5" />
              Sources
            </Button>
          )}
          <Button type="button" variant="ghost" size="sm" onClick={onNewChat}>
            <MessageSquarePlus className="h-3.5 w-3.5" />
            New
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="mx-auto max-w-3xl space-y-4 p-4">
          {messages.length === 0 && (
            <EmptyState
              icon={
                <MessageSquarePlus className="h-8 w-8 text-muted-foreground" />
              }
              title="Start a conversation"
              description="Ask questions about your notes, get summaries, or brainstorm ideas. Select sources to provide context."
            />
          )}

          {messages.map((message, i) => (
            <MessageBubble
              key={message.id}
              message={message}
              isStreaming={
                isStreaming &&
                message.role === "assistant" &&
                i === messages.length - 1
              }
            />
          ))}

          {isThinking && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className={cn("h-4 w-4 animate-spin")} />
              <span>Thinking...</span>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <MessageInput
        onSend={sendMessage}
        onCancel={cancel}
        isStreaming={isStreaming}
      />
    </div>
  );
}
