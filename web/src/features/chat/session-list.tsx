import { MessageSquarePlus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useChatStore } from "./chat-store";

export function SessionList() {
  const sessions = useChatStore((s) => s.sessions);
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const createSession = useChatStore((s) => s.createSession);
  const setActiveSession = useChatStore((s) => s.setActiveSession);
  const deleteSession = useChatStore((s) => s.deleteSession);

  return (
    <div className="flex h-full w-52 flex-col border-r bg-muted/30">
      <div className="flex items-center justify-between p-3">
        <span className="text-sm font-semibold">Chats</span>
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          onClick={() => createSession()}
        >
          <MessageSquarePlus className="h-4 w-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-2">
        {sessions.length === 0 && (
          <p className="px-2 py-4 text-center text-xs text-muted-foreground">
            No conversations yet
          </p>
        )}
        {sessions.map((session) => (
          <Button
            type="button"
            key={session.id}
            variant="ghost"
            className={`group w-full justify-start gap-2 px-2 py-2 text-sm ${
              session.id === activeSessionId
                ? "bg-accent text-accent-foreground"
                : "text-muted-foreground hover:bg-accent/50 hover:text-accent-foreground"
            }`}
            onClick={() => setActiveSession(session.id)}
          >
            <span className="flex-1 truncate">{session.title}</span>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              onClick={(e) => {
                e.stopPropagation();
                deleteSession(session.id);
              }}
              className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100 hover:bg-destructive/10 hover:text-destructive"
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          </Button>
        ))}
      </div>

      {sessions.length > 0 && (
        <div className="border-t px-3 py-2">
          <p className="text-[10px] text-muted-foreground">
            {sessions.length} conversation{sessions.length !== 1 ? "s" : ""}
          </p>
        </div>
      )}
    </div>
  );
}
