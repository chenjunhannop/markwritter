import { useState } from "react";
import { BaseLayout } from "@/components/layouts/base-layout";
import { ChatArea } from "@/features/chat/chat-area";
import { useChatStore } from "@/features/chat/chat-store";
import { SessionList } from "@/features/chat/session-list";
import { SourcesPanel } from "@/features/chat/sources-panel";

export default function ChatPage() {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const createSession = useChatStore((s) => s.createSession);

  const handleNewChat = () => {
    createSession();
    setSourcesOpen(false);
  };

  return (
    <BaseLayout>
      <div className="flex h-[calc(100vh-var(--header-height)-4rem)]">
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
    </BaseLayout>
  );
}
