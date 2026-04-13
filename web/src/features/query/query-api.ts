import { apiFetch } from "@/lib/api-client";
import type { SearchResponse } from "@/types/query";

export async function searchNotes(
  query: string,
  mode?: string,
  limit?: number,
): Promise<SearchResponse> {
  return apiFetch<SearchResponse>("/api/v1/query/search", {
    method: "POST",
    body: JSON.stringify({ query, mode, limit }),
  });
}
