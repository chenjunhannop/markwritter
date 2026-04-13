import {
  Boxes,
  FileEdit,
  GitGraph,
  type LucideIcon,
  MessageSquare,
  ScrollText,
  Search,
  Settings,
} from "lucide-react";

export interface NavItemConfig {
  readonly id: string;
  readonly label: string;
  readonly icon: LucideIcon;
  readonly path: string;
}

export const navItems: readonly NavItemConfig[] = [
  { id: "chat", label: "Chat", icon: MessageSquare, path: "/chat" },
  { id: "skills", label: "Skills", icon: Boxes, path: "/skills" },
  { id: "explore", label: "Explore", icon: GitGraph, path: "/explore" },
  { id: "query", label: "Query", icon: Search, path: "/query" },
  { id: "record", label: "Record", icon: FileEdit, path: "/record" },
  { id: "logs", label: "Logs", icon: ScrollText, path: "/logs" },
  { id: "settings", label: "Settings", icon: Settings, path: "/settings" },
] as const;
