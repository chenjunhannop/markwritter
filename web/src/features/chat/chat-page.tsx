import { useState } from "react";
import { ChatArea } from "./chat-area";
import { useChatStore } from "./chat-store";
import { SessionList } from "./session-list";
import { SourcesPanel } from "./sources-panel";

export function ChatPage() {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const createSession = useChatStore((s) => s.createSession);

  const handleNewChat = () => {
    createSession();
    setSourcesOpen(false);
  };

  return (
    <div className="flex h-full">
      <SessionList />

      <div className="flex flex-1 min-w-0">
        <ChatArea
          onToggleSources={() => setSourcesOpen(!sourcesOpen)}
          sourcesOpen={sourcesOpen}
          onNewChat={handleNewChat}
        />

        {activeSessionId && (
          <SourcesPanel
            open={sourcesOpen}
            onClose={() => setSourcesOpen(false)}
          />
        )}
      </div>
    </div>
  );
}
