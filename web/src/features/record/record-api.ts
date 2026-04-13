import { apiFetch } from "@/lib/api-client";
import type {
  AIContinueResponse,
  AIRewriteWithDiffResponse,
  FileTreeResponse,
  Note,
  NoteContentResponse,
  NoteFormInput,
  SaveNoteRequest,
} from "@/types/record";

export function getFileTree(): Promise<FileTreeResponse> {
  return apiFetch<FileTreeResponse>("/api/v1/notes/tree");
}

export function getNoteContent(path: string): Promise<NoteContentResponse> {
  return apiFetch<NoteContentResponse>(
    `/api/v1/notes/content?path=${encodeURIComponent(path)}`,
  );
}

export function saveNote(data: SaveNoteRequest): Promise<{ success: boolean }> {
  return apiFetch<{ success: boolean }>("/api/v1/notes/content", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function createQuickNote(data: NoteFormInput): Promise<Note> {
  return apiFetch<Note>("/api/v1/record", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function aiContinue(
  content: string,
  context?: string,
): Promise<AIContinueResponse> {
  return apiFetch<AIContinueResponse>("/api/v1/record/ai-assist/continue", {
    method: "POST",
    body: JSON.stringify({ content, context }),
  });
}

export function aiRewriteWithDiff(
  content: string,
  context?: string,
): Promise<AIRewriteWithDiffResponse> {
  return apiFetch<AIRewriteWithDiffResponse>(
    "/api/v1/record/ai-assist/rewrite/diff",
    {
      method: "POST",
      body: JSON.stringify({ content, context }),
    },
  );
}

export function aiPolishWithDiff(
  content: string,
  context?: string,
): Promise<AIRewriteWithDiffResponse> {
  return apiFetch<AIRewriteWithDiffResponse>(
    "/api/v1/record/ai-assist/polish/diff",
    {
      method: "POST",
      body: JSON.stringify({ content, context }),
    },
  );
}

export function trackTelemetry(data: {
  action_type: string;
  text_length: number;
  duration_ms: number;
  accepted: boolean;
}): Promise<void> {
  return apiFetch<void>("/api/v1/record/ai-assist/telemetry", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
