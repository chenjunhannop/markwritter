import { apiFetch } from "@/lib/api-client";
import type { GraphData, NodeDetails } from "@/types/explore";

export async function getGraph(): Promise<GraphData> {
  return apiFetch<GraphData>("/api/v1/explore/graph");
}

export async function searchGraph(query: string): Promise<GraphData> {
  return apiFetch<GraphData>(
    `/api/v1/explore/graph/search?q=${encodeURIComponent(query)}`,
  );
}

export async function getNodeDetail(nodeId: string): Promise<NodeDetails> {
  return apiFetch<NodeDetails>(
    `/api/v1/explore/graph/detail?node_id=${encodeURIComponent(nodeId)}`,
  );
}

export async function getGraphStats(): Promise<{
  total_nodes: number;
  total_edges: number;
  node_types: Record<string, number>;
}> {
  return apiFetch<{
    total_nodes: number;
    total_edges: number;
    node_types: Record<string, number>;
  }>("/api/v1/explore/stats");
}
