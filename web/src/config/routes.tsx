import { lazy } from "react";
import { Navigate } from "react-router-dom";

// Markwritter pages
const ChatPage = lazy(() => import("@/app/chat/page"));
const SkillsPage = lazy(() => import("@/app/skills/page"));
const ExplorePage = lazy(() => import("@/app/explore/page"));
const QueryPage = lazy(() => import("@/app/query/page"));
const RecordPage = lazy(() => import("@/app/record/page"));
const LogsPage = lazy(() => import("@/app/logs/page"));
const SettingsPage = lazy(() => import("@/app/settings/page"));

// Auth pages (keep from template)
const SignIn = lazy(() => import("@/app/auth/sign-in/page"));

// Error pages (keep from template)
const NotFound = lazy(() => import("@/app/errors/not-found/page"));

export interface RouteConfig {
  path: string;
  element: React.ReactNode;
  children?: RouteConfig[];
}

export const routes: RouteConfig[] = [
  {
    path: "/",
    element: <Navigate to="chat" replace />,
  },
  // Markwritter business routes
  {
    path: "/chat",
    element: <ChatPage />,
  },
  {
    path: "/skills",
    element: <SkillsPage />,
  },
  {
    path: "/explore",
    element: <ExplorePage />,
  },
  {
    path: "/query",
    element: <QueryPage />,
  },
  {
    path: "/record",
    element: <RecordPage />,
  },
  {
    path: "/logs",
    element: <LogsPage />,
  },
  {
    path: "/settings",
    element: <SettingsPage />,
  },
  // Auth routes (keep minimal)
  {
    path: "/auth/sign-in",
    element: <SignIn />,
  },
  // Catch-all 404
  {
    path: "*",
    element: <NotFound />,
  },
];
