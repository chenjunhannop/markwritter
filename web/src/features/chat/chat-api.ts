import { API_BASE, apiFetch } from "@/lib/api-client";
import type { ChatRequestBody } from "@/types/chat";

export interface TreeNode {
  name: string;
  path: string;
  type: "file" | "folder";
  children?: TreeNode[];
}

export interface FileTreeResponse {
  tree: TreeNode[];
}

export interface SourceSelectionResponse {
  session_id: string;
  source_paths: string[];
}

export async function sendMessageStream(
  body: ChatRequestBody,
  signal?: AbortSignal,
): Promise<Response> {
  const response = await fetch(`${API_BASE}/api/v1/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text}`);
  }

  return response;
}

export async function selectSources(
  sessionId: string,
  paths: string[],
): Promise<SourceSelectionResponse> {
  return apiFetch<SourceSelectionResponse>("/api/v1/chat/sources", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, source_paths: paths }),
  });
}

export async function getSelectedSources(
  sessionId: string,
): Promise<SourceSelectionResponse> {
  return apiFetch<SourceSelectionResponse>(
    `/api/v1/chat/sources?session_id=${encodeURIComponent(sessionId)}`,
  );
}

export async function clearSelectedSources(sessionId: string): Promise<void> {
  await apiFetch<void>(
    `/api/v1/chat/sources?session_id=${encodeURIComponent(sessionId)}`,
    { method: "DELETE" },
  );
}

export async function getFileTree(): Promise<FileTreeResponse> {
  return apiFetch<FileTreeResponse>("/api/v1/notes/tree");
}
