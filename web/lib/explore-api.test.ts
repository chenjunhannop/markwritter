/**
 * Tests for Explore API functions
 *
 * TDD approach: These tests define the expected behavior before implementation.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  getKnowledgeGraph,
  getNodeGraph,
  getRelatedNotes,
  ApiError,
} from './explore-api';
import type { GraphData, NodeGraphData, RelatedNote } from './explore-api';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

// API base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

describe('Explore API', () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // ==========================================================================
  // getKnowledgeGraph Tests
  // ==========================================================================

  describe('getKnowledgeGraph', () => {
    it('should fetch full graph data', async () => {
      const mockGraphData: GraphData = {
        nodes: [
          {
            id: 'note1.md',
            title: 'Note 1',
            path: 'note1.md',
            tags: ['python'],
            connections_count: 2,
          },
          {
            id: 'note2.md',
            title: 'Note 2',
            path: 'note2.md',
            tags: [],
            connections_count: 1,
          },
        ],
        edges: [
          {
            source: 'note1.md',
            target: 'note2.md',
            type: 'wikilink',
            weight: 1.0,
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockGraphData),
      });

      const result = await getKnowledgeGraph();

      expect(mockFetch).toHaveBeenCalledWith(`${API_BASE}/api/v1/explore/graph`, {
        method: 'GET',
      });
      expect(result).toEqual(mockGraphData);
    });

    it('should return empty graph when vault is empty', async () => {
      const emptyGraph: GraphData = {
        nodes: [],
        edges: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(emptyGraph),
      });

      const result = await getKnowledgeGraph();

      expect(result.nodes).toEqual([]);
      expect(result.edges).toEqual([]);
    });

    it('should throw ApiError on failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        text: () => Promise.resolve('Vault not configured'),
      });

      await expect(getKnowledgeGraph()).rejects.toThrow(ApiError);
    });

    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(getKnowledgeGraph()).rejects.toThrow('Network error');
    });
  });

  // ==========================================================================
  // getNodeGraph Tests
  // ==========================================================================

  describe('getNodeGraph', () => {
    it('should fetch node graph data', async () => {
      const mockNodeData: NodeGraphData = {
        node: {
          id: 'note1.md',
          title: 'Note 1',
          path: 'note1.md',
          tags: ['python', 'testing'],
          connections_count: 3,
        },
        edges: [
          {
            source: 'note1.md',
            target: 'note2.md',
            type: 'wikilink',
            weight: 1.0,
          },
          {
            source: 'note3.md',
            target: 'note1.md',
            type: 'wikilink',
            weight: 1.0,
          },
        ],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockNodeData),
      });

      const result = await getNodeGraph('note1.md');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/v1/explore/graph/note1.md`,
        {
          method: 'GET',
        }
      );
      expect(result).toEqual(mockNodeData);
    });

    it('should handle paths with subdirectories', async () => {
      const mockNodeData: NodeGraphData = {
        node: {
          id: 'projects/project-1.md',
          title: 'Project 1',
          path: 'projects/project-1.md',
          tags: [],
          connections_count: 1,
        },
        edges: [],
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockNodeData),
      });

      const result = await getNodeGraph('projects/project-1.md');

      // Path is URL encoded
      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/v1/explore/graph/projects%2Fproject-1.md`,
        {
          method: 'GET',
        }
      );
      expect(result.node.id).toBe('projects/project-1.md');
    });

    it('should throw ApiError for non-existent node', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Note not found: nonexistent.md'),
      });

      try {
        await getNodeGraph('nonexistent.md');
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(404);
      }
    });
  });

  // ==========================================================================
  // getRelatedNotes Tests
  // ==========================================================================

  describe('getRelatedNotes', () => {
    it('should fetch related notes with default depth', async () => {
      const mockRelatedNotes: RelatedNote[] = [
        {
          path: 'note2.md',
          title: 'Note 2',
          tags: ['reference'],
        },
        {
          path: 'note3.md',
          title: 'Note 3',
          tags: [],
        },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRelatedNotes),
      });

      const result = await getRelatedNotes('note1.md');

      expect(mockFetch).toHaveBeenCalledWith(
        `${API_BASE}/api/v1/explore/related/note1.md?depth=1`,
        {
          method: 'GET',
        }
      );
      expect(result).toEqual(mockRelatedNotes);
    });

    it('should fetch related notes with custom depth', async () => {
      const mockRelatedNotes: RelatedNote[] = [
        { path: 'note2.md', title: 'Note 2', tags: [] },
        { path: 'note3.md', title: 'Note 3', tags: [] },
        { path: 'note4.md', title: 'Note 4', tags: [] },
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRelatedNotes),
      });

      const result = await getRelatedNotes('note1.md', 2);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('depth=2'),
        expect.any(Object)
      );
      expect(result).toHaveLength(3);
    });

    it('should return empty array for isolated note', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      });

      const result = await getRelatedNotes('isolated.md');

      expect(result).toEqual([]);
    });

    it('should throw ApiError for non-existent note', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: () => Promise.resolve('Note not found'),
      });

      await expect(getRelatedNotes('nonexistent.md')).rejects.toThrow(ApiError);
    });

    it('should validate depth parameter bounds', async () => {
      // This test ensures the API is called with valid depth
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      });

      // Depth should be clamped between 1 and 10
      await getRelatedNotes('note1.md', 0); // Should use 1
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('depth=1'),
        expect.any(Object)
      );

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      });

      await getRelatedNotes('note1.md', 100); // Should use 10
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('depth=10'),
        expect.any(Object)
      );
    });
  });

  // ==========================================================================
  // Error Handling Tests
  // ==========================================================================

  describe('Error Handling', () => {
    it('should handle 503 Service Unavailable', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Service Unavailable',
        text: () => Promise.resolve('Vault not configured'),
      });

      try {
        await getKnowledgeGraph();
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(503);
      }
    });

    it('should handle 500 Internal Server Error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: () => Promise.resolve('Unexpected error'),
      });

      try {
        await getKnowledgeGraph();
        expect.fail('Should have thrown');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect((error as ApiError).status).toBe(500);
      }
    });
  });
});