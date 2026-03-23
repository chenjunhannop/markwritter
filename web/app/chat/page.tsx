import { MainLayout } from "@/components/layout";
import { ChatArea } from "@/components/chat/chat-area";

export default function ChatPage() {
  return (
    <MainLayout title="Chat">
      <ChatArea />
    </MainLayout>
  );
}