export type MessageRole = "user" | "assistant";

export type ChatEventType =
  | "thinking"
  | "text_delta"
  | "sources"
  | "citation"
  | "done"
  | "error";

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  citations?: Citation[];
  timestamp: number;
}

export interface Citation {
  file_path: string;
  page_num: number;
  paragraph_idx: number;
  text_snippet: string;
}

export interface StreamSource {
  id: string;
  title: string;
  content: string;
  score?: number;
  [key: string]: unknown;
}

export interface ChatEvent {
  type: ChatEventType;
  content: string;
  sources?: StreamSource[];
  citation?: Citation;
}

export interface Session {
  id: string;
  title: string;
  messages: Message[];
  selectedSources: string[];
  createdAt: number;
  updatedAt: number;
}

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequestBody {
  message: string;
  session_id: string;
  sources?: string[];
  conversation_history?: ConversationMessage[];
}

export type Intent = SkillIntent | ChatIntent;

export interface SkillIntent {
  type: "skill";
  skillName: string;
  params: Record<string, unknown>;
  confidence: number;
}

export interface ChatIntent {
  type: "chat";
  message: string;
  confidence: number;
}
