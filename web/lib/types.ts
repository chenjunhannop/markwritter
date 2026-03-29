/**
 * Type definitions for Markwritter
 *
 * These types match the backend API models defined in:
 * - markwritter/api/models/skill.py (SkillResponse, SkillRunRequest, SkillRunResponse)
 * - markwritter/api/models/chat.py (ChatRequest, ChatEvent)
 * - markwritter/models.py (SkillDefinition, SkillInput, SkillOutput)
 */

// ==================== Message Types ====================

/**
 * Role of a message sender
 */
export type MessageRole = 'user' | 'assistant';

/**
 * Chat message representation
 */
export interface Message {
  /** Unique message identifier */
  id: string;
  /** Role of the message sender */
  role: MessageRole;
  /** Message content */
  content: string;
  /** Unix timestamp in milliseconds */
  timestamp: number;
}

// ==================== Skill Types ====================

/**
 * Skill input parameter definition
 */
export interface SkillInput {
  /** Parameter name */
  name: string;
  /** Parameter type (string, number, boolean, enum, etc.) */
  type: string;
  /** Parameter description */
  description: string;
  /** Whether the parameter is required */
  required: boolean;
  /** Default value for optional parameters */
  default?: unknown;
  /** Enum values for enum type parameters */
  enum?: string[];
}

/**
 * Skill output definition
 */
export interface SkillOutput {
  /** Output type */
  type: string;
  /** Output description */
  description: string;
}

/**
 * Skill definition from API (matches SkillResponse)
 */
export interface Skill {
  /** Unique skill name */
  name: string;
  /** Skill description */
  description: string;
  /** Skill version */
  version: string;
  /** Input parameters */
  inputs: SkillInput[];
  /** Output definition */
  output: SkillOutput;
}

/**
 * Request to run a skill
 */
export interface SkillRunRequest {
  /** Parameter values for skill execution */
  params: Record<string, unknown>;
}

/**
 * Response from skill execution
 */
export interface SkillRunResponse {
  /** Whether execution succeeded */
  success: boolean;
  /** Output from skill execution */
  output: string;
  /** Error message if execution failed */
  error: string;
}

// ==================== Chat Event Types ====================

/**
 * Type of SSE event from chat stream
 */
export type ChatEventType = 'thinking' | 'text_delta' | 'sources' | 'done' | 'error';

/**
 * Source reference for streaming events
 */
export interface StreamSource {
  id: string;
  title: string;
  content: string;
  score?: number;
  [key: string]: unknown;
}

/**
 * SSE event from chat stream (matches ChatEvent)
 */
export interface ChatEvent {
  /** Event type */
  type: ChatEventType;
  /** Event content (empty for thinking/done, text for text_delta, message for error) */
  content: string;
  /** Source references (for sources event type) */
  sources?: StreamSource[];
}

// ==================== File Tree Types ====================

/**
 * Node in the vault file tree
 */
export interface TreeNode {
  /** Display name (file or directory name) */
  name: string;
  /** Relative path from vault root */
  path: string;
  /** Node type */
  type: 'file' | 'directory';
  /** Number of .md files in directory (recursive, directory only) */
  file_count?: number;
  /** Child nodes (directory only) */
  children?: TreeNode[];
}

/**
 * Response from GET /api/v1/notes/tree
 */
export interface FileTreeResponse {
  tree: TreeNode[];
}

// ==================== Source Reference Types ====================

/**
 * Reference to a source file used in chat context
 */
export interface SourceReference {
  /** Vault-relative file path */
  filePath: string;
  /** File name */
  fileName: string;
  /** Relevant excerpt from the source */
  excerpt?: string;
}

// ==================== Session Types ====================

/**
 * Session for managing conversations
 */
export interface Session {
  /** Unique session identifier */
  id: string;
  /** Session title */
  title: string;
  /** Messages in the session */
  messages: Message[];
  /** Vault-relative paths of selected source files */
  selectedSources: string[];
  /** Creation timestamp (Unix milliseconds) */
  createdAt: number;
  /** Last update timestamp (Unix milliseconds) */
  updatedAt: number;
}

// ==================== Chat Request Types ====================

/**
 * Message in conversation history for multi-turn context
 */
export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
}

/**
 * Request body for POST /api/v1/chat/
 */
export interface ChatRequestBody {
  message: string;
  sources?: string[];
  conversation_history?: ConversationMessage[];
}

// ==================== Intent Types ====================

/**
 * Skill execution intent
 */
export interface SkillIntent {
  /** Intent type discriminator */
  type: 'skill';
  /** Name of the skill to execute */
  skillName: string;
  /** Parameters for skill execution */
  params: Record<string, unknown>;
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * Chat intent (general conversation)
 */
export interface ChatIntent {
  /** Intent type discriminator */
  type: 'chat';
  /** The chat message */
  message: string;
  /** Confidence score (0-1) */
  confidence: number;
}

/**
 * Union type for all intents
 */
export type Intent = SkillIntent | ChatIntent;

// ==================== Type Guards ====================

/**
 * Check if an intent is a skill intent
 */
export function isSkillIntent(intent: Intent): intent is SkillIntent {
  return intent.type === 'skill';
}

/**
 * Check if an intent is a chat intent
 */
export function isChatIntent(intent: Intent): intent is ChatIntent {
  return intent.type === 'chat';
}

/**
 * Check if a chat event is an error
 */
export function isErrorEvent(event: ChatEvent): boolean {
  return event.type === 'error';
}

/**
 * Check if a chat event is a text delta
 */
export function isTextDeltaEvent(event: ChatEvent): boolean {
  return event.type === 'text_delta';
}

/**
 * Check if a chat event is done
 */
export function isDoneEvent(event: ChatEvent): boolean {
  return event.type === 'done';
}