/**
 * Explore API Client for Markwritter
 *
 * Provides functions for knowledge graph operations.
 */

// API base URL from environment variable
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Custom error class for API errors.
 * Contains HTTP status code and response body.
 */
export class ApiError extends Error {
  public readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

/**
 * Create an ApiError from a failed Response.
 */
async function createApiError(response: Response): Promise<ApiError> {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  try {
    const body = await response.text();
    if (body) {
      errorMessage = `${response.status}: ${body}`;
    }
  } catch {
    // Ignore parsing errors
  }
  return new ApiError(response.status, errorMessage);
}

// ==================== Types ====================

/**
 * Graph node representing a note
 */
export interface GraphNode {
  /** Unique node identifier (note path) */
  id: string;
  /** Note title */
  title: string;
  /** Note path */
  path: string;
  /** Tags associated with the note */
  tags: string[];
  /** Number of connections (incoming + outgoing) */
  connections_count: number;
}

/**
 * Graph edge representing a link between notes
 */
export interface GraphEdge {
  /** Source note path */
  source: string;
  /** Target note path */
  target: string;
  /** Link type (wikilink, backlink, etc.) */
  type: string;
  /** Edge weight */
  weight: number;
}

/**
 * Complete graph data structure
 */
export interface GraphData {
  /** All nodes in the graph */
  nodes: GraphNode[];
  /** All edges in the graph */
  edges: GraphEdge[];
}

/**
 * Node graph data including the node and its edges
 */
export interface NodeGraphData {
  /** The node */
  node: GraphNode;
  /** Edges connected to this node (both incoming and outgoing) */
  edges: GraphEdge[];
}

/**
 * Related note metadata
 */
export interface RelatedNote {
  /** Note path */
  path: string;
  /** Note title */
  title: string | null;
  /** Tags associated with the note */
  tags: string[];
}

// ==================== API Functions ====================

/**
 * Get the complete knowledge graph.
 *
 * @returns GraphData with all nodes and edges
 * @throws ApiError if the request fails
 */
export async function getKnowledgeGraph(): Promise<GraphData> {
  const response = await fetch(`${API_BASE}/api/v1/explore/graph`, {
    method: 'GET',
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Get graph data for a specific node.
 *
 * @param notePath - The path to the note
 * @returns NodeGraphData with the node and its edges
 * @throws ApiError if the request fails
 */
export async function getNodeGraph(notePath: string): Promise<NodeGraphData> {
  const encodedPath = encodeURIComponent(notePath);
  const response = await fetch(
    `${API_BASE}/api/v1/explore/graph/${encodedPath}`,
    {
      method: 'GET',
    }
  );

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

/**
 * Find notes related to the specified note.
 *
 * @param notePath - The path to the note
 * @param depth - Traversal depth (1-10, default 1)
 * @returns Array of related notes
 * @throws ApiError if the request fails
 */
export async function getRelatedNotes(
  notePath: string,
  depth: number = 1
): Promise<RelatedNote[]> {
  // Clamp depth to valid range
  const clampedDepth = Math.max(1, Math.min(10, depth));
  const encodedPath = encodeURIComponent(notePath);

  const response = await fetch(
    `${API_BASE}/api/v1/explore/related/${encodedPath}?depth=${clampedDepth}`,
    {
      method: 'GET',
    }
  );

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}