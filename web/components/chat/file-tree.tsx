'use client';

/**
 * FileTree - Container component for the vault file tree.
 * Renders FileTreeNode for each root node.
 * Handles Shift+click range selection.
 */

import { useRef, useCallback } from 'react';
import { useChatStore } from '@/lib/store';
import { useSourcesStore } from '@/lib/sources-store';
import { FileTreeNode } from './file-tree-node';
import type { TreeNode } from '@/lib/types';

interface FileTreeProps {
  tree: TreeNode[];
}

function collectFilePaths(nodes: TreeNode[]): string[] {
  const paths: string[] = [];
  for (const node of nodes) {
    if (node.type === 'file') {
      paths.push(node.path);
    }
    if (node.children) {
      paths.push(...collectFilePaths(node.children));
    }
  }
  return paths;
}

export function FileTree({ tree }: FileTreeProps) {
  const selectedSources = useChatStore((s) => s.selectedSources);
  const expandedFolders = useSourcesStore((s) => s.expandedFolders);
  const toggleFolder = useSourcesStore((s) => s.toggleFolder);
  const toggleSource = useChatStore((s) => s.toggleSource);

  const lastClickedRef = useRef<string | null>(null);
  const allFilePathsRef = useRef<string[]>([]);

  // Update the flat file path list when tree changes
  if (tree.length > 0 && allFilePathsRef.current.length === 0) {
    allFilePathsRef.current = collectFilePaths(tree);
  }

  const handleToggleSource = useCallback(
    (path: string, e: React.MouseEvent) => {
      if (e.shiftKey && lastClickedRef.current) {
        // Range selection
        const allPaths = allFilePathsRef.current;
        const lastIdx = allPaths.indexOf(lastClickedRef.current);
        const currentIdx = allPaths.indexOf(path);
        if (lastIdx !== -1 && currentIdx !== -1) {
          const [start, end] = [Math.min(lastIdx, currentIdx), Math.max(lastIdx, currentIdx)];
          const rangePaths = allPaths.slice(start, end + 1);
          const currentSet = new Set(selectedSources);

          if (currentSet.has(path)) {
            // Deselect range
            const removeSet = new Set(rangePaths);
            const remaining = selectedSources.filter((p) => !removeSet.has(p));
            if (remaining.length === 0) {
              useChatStore.getState().clearSources();
            } else {
              useChatStore.setState({ selectedSources: remaining });
            }
          } else {
            // Select range
            const newPaths = rangePaths.filter((p) => !currentSet.has(p));
            if (newPaths.length > 0) {
              useChatStore.getState().addSources(newPaths);
            }
          }
          lastClickedRef.current = path;
          return;
        }
      }

      toggleSource(path);
      lastClickedRef.current = path;
    },
    [selectedSources, toggleSource]
  );

  if (tree.length === 0) {
    return (
      <div className="flex items-center justify-center px-4 py-8 text-sm text-muted-foreground">
        No files found
      </div>
    );
  }

  return (
    <div className="flex flex-col overflow-y-auto py-1" role="tree">
      {tree.map((node) => (
        <FileTreeNode
          key={node.path}
          node={node}
          depth={0}
          expandedFolders={expandedFolders}
          selectedSources={selectedSources}
          searchQuery={useSourcesStore.getState().searchQuery}
          onToggleFolder={toggleFolder}
          onToggleSource={handleToggleSource}
        />
      ))}
    </div>
  );
}
