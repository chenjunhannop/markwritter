import { ChatContainer } from "@/components/chat/ChatContainer";

export default function Home() {
  return (
    <main className="h-screen flex flex-col">
      <header className="border-b p-4">
        <h1 className="text-xl font-bold">Markwritter</h1>
        <p className="text-sm text-gray-500">Agent Orchestration Framework</p>
      </header>
      <ChatContainer />
    </main>
  );
}