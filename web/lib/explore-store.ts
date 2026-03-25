/**
 * Explore Store for knowledge graph state management
 *
 * Uses Zustand for state management with async actions.
 */

import { create } from 'zustand';
import {
  getKnowledgeGraph,
  getNodeGraph,
  getRelatedNotes,
  ApiError,
  type GraphData,
  type GraphNode,
  type GraphEdge,
  type RelatedNote,
} from './explore-api';

// ==================== Types ====================

/**
 * Node graph data including node and its edges
 */
export interface NodeGraphData {
  node: GraphNode;
  edges: GraphEdge[];
}

/**
 * Explore store state
 */
export interface ExploreState {
  /** Complete graph data */
  graphData: GraphData | null;
  /** Currently selected node */
  selectedNode: GraphNode | null;
  /** Edges for selected node */
  selectedNodeEdges: GraphEdge[];
  /** Related notes for selected node */
  relatedNotes: RelatedNote[];
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
}

/**
 * Explore store actions
 */
export interface ExploreActions {
  /** Fetch the complete knowledge graph */
  fetchGraph: () => Promise<void>;
  /** Select a node and fetch its details */
  selectNode: (path: string | null) => Promise<void>;
  /** Fetch related notes for a node */
  fetchRelatedNotes: (path: string, depth?: number) => Promise<void>;
  /** Clear the current selection */
  clearSelection: () => void;
  /** Clear any error state */
  clearError: () => void;
  /** Get a node by its ID */
  getNodeById: (id: string) => GraphNode | undefined;
}

export type ExploreStore = ExploreState & ExploreActions;

// ==================== Initial State ====================

const initialState: ExploreState = {
  graphData: null,
  selectedNode: null,
  selectedNodeEdges: [],
  relatedNotes: [],
  isLoading: false,
  error: null,
};

// ==================== Store Implementation ====================

export const useExploreStore = create<ExploreStore>((set, get) => ({
  ...initialState,

  fetchGraph: async () => {
    set({ isLoading: true, error: null });

    try {
      const graphData = await getKnowledgeGraph();
      set({ graphData, isLoading: false });
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : 'Failed to fetch graph';
      set({ error: message, isLoading: false });
    }
  },

  selectNode: async (path) => {
    if (path === null) {
      set({ selectedNode: null, selectedNodeEdges: [], relatedNotes: [] });
      return;
    }

    set({ isLoading: true, error: null });

    try {
      const nodeData = await getNodeGraph(path);
      set({
        selectedNode: nodeData.node,
        selectedNodeEdges: nodeData.edges,
        isLoading: false,
      });
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : 'Failed to fetch node';
      set({ error: message, isLoading: false, selectedNode: null });
    }
  },

  fetchRelatedNotes: async (path, depth = 1) => {
    set({ isLoading: true, error: null });

    try {
      const relatedNotes = await getRelatedNotes(path, depth);
      set({ relatedNotes, isLoading: false });
    } catch (error) {
      const message =
        error instanceof ApiError ? error.message : 'Failed to fetch related notes';
      set({ error: message, isLoading: false, relatedNotes: [] });
    }
  },

  clearSelection: () => {
    set({
      selectedNode: null,
      selectedNodeEdges: [],
      relatedNotes: [],
    });
  },

  clearError: () => {
    set({ error: null });
  },

  getNodeById: (id) => {
    const { graphData } = get();
    if (!graphData) return undefined;
    return graphData.nodes.find((node) => node.id === id);
  },
}));