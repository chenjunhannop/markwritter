/**
 * Sources Store for Markwritter
 *
 * Manages file tree UI state (expand/collapse, search filter).
 * Not persisted -- tree data is fetched from API on mount.
 */

import { create } from 'zustand';
import { getFileTree } from './notes-api';
import type { TreeNode } from './types';

interface SourcesState {
  tree: TreeNode[];
  expandedFolders: Set<string>;
  searchQuery: string;
  isLoading: boolean;
  error: string | null;

  loadTree: () => Promise<void>;
  toggleFolder: (path: string) => void;
  setSearchQuery: (query: string) => void;
  expandAll: () => void;
  collapseAll: () => void;
}

/**
 * Get all directory paths in a tree recursively.
 */
function collectDirectoryPaths(nodes: TreeNode[]): string[] {
  const paths: string[] = [];
  for (const node of nodes) {
    if (node.type === 'directory') {
      paths.push(node.path);
      if (node.children) {
        paths.push(...collectDirectoryPaths(node.children));
      }
    }
  }
  return paths;
}

export const useSourcesStore = create<SourcesState>()((set, get) => ({
  tree: [],
  expandedFolders: new Set<string>(),
  searchQuery: '',
  isLoading: false,
  error: null,

  loadTree: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await getFileTree();
      set({ tree: response.tree, isLoading: false });
    } catch (e) {
      const error = e instanceof Error ? e.message : 'Failed to load file tree';
      set({ error, isLoading: false });
    }
  },

  toggleFolder: (path) => {
    set((state) => {
      const next = new Set(state.expandedFolders);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return { expandedFolders: next };
    });
  },

  setSearchQuery: (query) => {
    set({ searchQuery: query });
  },

  expandAll: () => {
    const { tree } = get();
    const allDirs = collectDirectoryPaths(tree);
    set({ expandedFolders: new Set(allDirs) });
  },

  collapseAll: () => {
    set({ expandedFolders: new Set() });
  },
}));
