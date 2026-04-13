import { Navigate, Route, Routes } from "react-router-dom";
import { Toaster } from "sonner";
import { ChatPage } from "@/features/chat/chat-page";
import { ExplorePage } from "@/features/explore/explore-page";
import { LogsPage } from "@/features/logs/logs-page";
import { QueryPage } from "@/features/query/query-page";
import { RecordPage } from "@/features/record/record-page";
import { SettingsPage } from "@/features/settings/settings-page";
import { SkillsPage } from "@/features/skills/skills-page";
import { AppLayout } from "@/layout/app-layout";

export function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/skills" element={<SkillsPage />} />
        <Route path="/explore" element={<ExplorePage />} />
        <Route path="/query" element={<QueryPage />} />
        <Route path="/record" element={<RecordPage />} />
        <Route path="/logs" element={<LogsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/" element={<Navigate to="/chat" replace />} />
      </Routes>
      <Toaster />
    </AppLayout>
  );
}
