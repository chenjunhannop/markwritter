export interface GraphNode {
  id: string;
  label: string;
  type: "person" | "topic" | "concept" | "note";
  data?: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type?: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface NodeDetails {
  node: GraphNode;
  connections: {
    incoming: GraphEdge[];
    outgoing: GraphEdge[];
  };
  relatedNodes: GraphNode[];
}
