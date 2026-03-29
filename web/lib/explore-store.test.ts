/**
 * Tests for Explore Store
 *
 * TDD approach: These tests define the expected behavior before implementation.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useExploreStore } from './explore-store';
import { ApiError } from './api';
import type { GraphData, GraphNode, GraphEdge, RelatedNote } from './explore-api';
import * as exploreApi from './explore-api';

// Mock the API module
vi.mock('./explore-api', () => ({
  getKnowledgeGraph: vi.fn(),
  getNodeGraph: vi.fn(),
  getRelatedNotes: vi.fn(),
  ApiError: class ApiError extends Error {
    status: number;
    constructor(status: number, message: string) {
      super(message);
      this.status = status;
    }
  },
}));

describe('Explore Store', () => {
  beforeEach(() => {
    // Reset store state before each test
    useExploreStore.setState({
      graphData: null,
      selectedNode: null,
      relatedNotes: [],
      isLoading: false,
      error: null,
    });
    vi.clearAllMocks();
  });

  // ==========================================================================
  // Initial State Tests
  // ==========================================================================

  describe('Initial State', () => {
    it('should have correct initial state', () => {
      const state = useExploreStore.getState();

      expect(state.graphData).toBeNull();
      expect(state.selectedNode).toBeNull();
      expect(state.relatedNotes).toEqual([]);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  // ==========================================================================
  // fetchGraph Tests
  // ==========================================================================

  describe('fetchGraph', () => {
    it('should fetch and store graph data', async () => {
      const mockGraphData: GraphData = {
        nodes: [
          {
            id: 'note1.md',
            title: 'Note 1',
            path: 'note1.md',
            tags: [],
            connections_count: 1,
          },
        ],
        edges: [],
      };

      vi.mocked(exploreApi.getKnowledgeGraph).mockResolvedValueOnce(mockGraphData);

      const { fetchGraph } = useExploreStore.getState();
      await fetchGraph();

      const state = useExploreStore.getState();
      expect(state.graphData).toEqual(mockGraphData);
      expect(state.isLoading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should set loading state during fetch', async () => {
      vi.mocked(exploreApi.getKnowledgeGraph).mockImplementationOnce(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      const { fetchGraph } = useExploreStore.getState();
      const promise = fetchGraph();

      // Check loading state immediately after starting
      expect(useExploreStore.getState().isLoading).toBe(true);

      await promise;

      expect(useExploreStore.getState().isLoading).toBe(false);
    });

    it('should handle fetch errors', async () => {
      const error = new ApiError(503, 'Vault not configured');
      vi.mocked(exploreApi.getKnowledgeGraph).mockRejectedValueOnce(error);

      const { fetchGraph } = useExploreStore.getState();
      await fetchGraph();

      const state = useExploreStore.getState();
      expect(state.error).toBe('Vault not configured');
      expect(state.isLoading).toBe(false);
      expect(state.graphData).toBeNull();
    });

    it('should clear previous error on new fetch', async () => {
      // Set an initial error
      useExploreStore.setState({ error: 'Previous error' });

      const mockGraphData: GraphData = { nodes: [], edges: [] };
      vi.mocked(exploreApi.getKnowledgeGraph).mockResolvedValueOnce(mockGraphData);

      const { fetchGraph } = useExploreStore.getState();
      await fetchGraph();

      expect(useExploreStore.getState().error).toBeNull();
    });
  });

  // ==========================================================================
  // selectNode Tests
  // ==========================================================================

  describe('selectNode', () => {
    it('should fetch node graph data and update state', async () => {
      const mockNodeData = {
        node: {
          id: 'note1.md',
          title: 'Note 1',
          path: 'note1.md',
          tags: [],
          connections_count: 2,
        },
        edges: [
          {
            source: 'note1.md',
            target: 'note2.md',
            type: 'wikilink',
            weight: 1.0,
          },
        ],
      };

      vi.mocked(exploreApi.getNodeGraph).mockResolvedValueOnce(mockNodeData);

      const { selectNode } = useExploreStore.getState();
      await selectNode('note1.md');

      const state = useExploreStore.getState();
      expect(state.selectedNode).toEqual(mockNodeData.node);
      expect(state.isLoading).toBe(false);
    });

    it('should handle node not found error', async () => {
      const error = new ApiError(404, 'Note not found');
      vi.mocked(exploreApi.getNodeGraph).mockRejectedValueOnce(error);

      const { selectNode } = useExploreStore.getState();
      await selectNode('nonexistent.md');

      const state = useExploreStore.getState();
      expect(state.error).toBe('Note not found');
      expect(state.selectedNode).toBeNull();
    });

    it('should clear selection when path is null', async () => {
      // First set a selected node
      const mockNodeData = {
        node: {
          id: 'note1.md',
          title: 'Note 1',
          path: 'note1.md',
          tags: [],
          connections_count: 1,
        },
        edges: [],
      };
      vi.mocked(exploreApi.getNodeGraph).mockResolvedValueOnce(mockNodeData);

      const { selectNode } = useExploreStore.getState();
      await selectNode('note1.md');
      expect(useExploreStore.getState().selectedNode).not.toBeNull();

      // Clear selection
      await selectNode(null);
      expect(useExploreStore.getState().selectedNode).toBeNull();
    });
  });

  // ==========================================================================
  // fetchRelatedNotes Tests
  // ==========================================================================

  describe('fetchRelatedNotes', () => {
    it('should fetch and store related notes', async () => {
      const mockRelatedNotes: RelatedNote[] = [
        { path: 'note2.md', title: 'Note 2', tags: [] },
        { path: 'note3.md', title: 'Note 3', tags: ['important'] },
      ];

      vi.mocked(exploreApi.getRelatedNotes).mockResolvedValueOnce(mockRelatedNotes);

      const { fetchRelatedNotes } = useExploreStore.getState();
      await fetchRelatedNotes('note1.md');

      const state = useExploreStore.getState();
      expect(state.relatedNotes).toEqual(mockRelatedNotes);
      expect(state.isLoading).toBe(false);
    });

    it('should pass depth parameter to API', async () => {
      vi.mocked(exploreApi.getRelatedNotes).mockResolvedValueOnce([]);

      const { fetchRelatedNotes } = useExploreStore.getState();
      await fetchRelatedNotes('note1.md', 2);

      expect(exploreApi.getRelatedNotes).toHaveBeenCalledWith('note1.md', 2);
    });

    it('should use default depth of 1', async () => {
      vi.mocked(exploreApi.getRelatedNotes).mockResolvedValueOnce([]);

      const { fetchRelatedNotes } = useExploreStore.getState();
      await fetchRelatedNotes('note1.md');

      expect(exploreApi.getRelatedNotes).toHaveBeenCalledWith('note1.md', 1);
    });

    it('should handle fetch errors', async () => {
      const error = new ApiError(404, 'Note not found');
      vi.mocked(exploreApi.getRelatedNotes).mockRejectedValueOnce(error);

      const { fetchRelatedNotes } = useExploreStore.getState();
      await fetchRelatedNotes('nonexistent.md');

      const state = useExploreStore.getState();
      expect(state.error).toBe('Note not found');
      expect(state.relatedNotes).toEqual([]);
    });
  });

  // ==========================================================================
  // clearSelection Tests
  // ==========================================================================

  describe('clearSelection', () => {
    it('should clear selected node and related notes', () => {
      // Set some state
      useExploreStore.setState({
        selectedNode: {
          id: 'note1.md',
          title: 'Note 1',
          path: 'note1.md',
          tags: [],
          connections_count: 1,
        },
        relatedNotes: [{ path: 'note2.md', title: 'Note 2', tags: [] }],
      });

      const { clearSelection } = useExploreStore.getState();
      clearSelection();

      const state = useExploreStore.getState();
      expect(state.selectedNode).toBeNull();
      expect(state.relatedNotes).toEqual([]);
    });
  });

  // ==========================================================================
  // clearError Tests
  // ==========================================================================

  describe('clearError', () => {
    it('should clear error state', () => {
      useExploreStore.setState({ error: 'Some error' });

      const { clearError } = useExploreStore.getState();
      clearError();

      expect(useExploreStore.getState().error).toBeNull();
    });
  });

  // ==========================================================================
  // Computed/Derived Data Tests
  // ==========================================================================

  describe('Computed Data', () => {
    it('should provide node lookup by ID', () => {
      const mockGraphData: GraphData = {
        nodes: [
          { id: 'note1.md', title: 'Note 1', path: 'note1.md', tags: [], connections_count: 1 },
          { id: 'note2.md', title: 'Note 2', path: 'note2.md', tags: [], connections_count: 2 },
        ],
        edges: [],
      };

      useExploreStore.setState({ graphData: mockGraphData });

      const { getNodeById } = useExploreStore.getState();
      const node = getNodeById('note1.md');

      expect(node?.title).toBe('Note 1');
    });

    it('should return undefined for non-existent node', () => {
      const mockGraphData: GraphData = {
        nodes: [{ id: 'note1.md', title: 'Note 1', path: 'note1.md', tags: [], connections_count: 1 }],
        edges: [],
      };

      useExploreStore.setState({ graphData: mockGraphData });

      const { getNodeById } = useExploreStore.getState();
      const node = getNodeById('nonexistent.md');

      expect(node).toBeUndefined();
    });

    it('should handle null graphData in getNodeById', () => {
      useExploreStore.setState({ graphData: null });

      const { getNodeById } = useExploreStore.getState();
      const node = getNodeById('note1.md');

      expect(node).toBeUndefined();
    });
  });
});