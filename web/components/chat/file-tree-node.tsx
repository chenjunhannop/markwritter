'use client';

/**
 * FileTreeNode - Recursive tree node for the file tree.
 * Renders differently based on type (directory vs file).
 */

import { memo } from 'react';
import { ChevronRight, Folder, FolderOpen, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { TreeNode } from '@/lib/types';

interface FileTreeNodeProps {
  node: TreeNode;
  depth: number;
  expandedFolders: Set<string>;
  selectedSources: string[];
  searchQuery: string;
  onToggleFolder: (path: string) => void;
  onToggleSource: (path: string, e: React.MouseEvent) => void;
}

function matchesSearch(node: TreeNode, searchQuery: string): boolean {
  if (!searchQuery) return true;
  const q = searchQuery.toLowerCase();
  if (node.name.toLowerCase().includes(q)) return true;
  if (node.type === 'directory' && node.children) {
    return node.children.some((child) => matchesSearch(child, q));
  }
  return false;
}

export const FileTreeNode = memo(function FileTreeNode({
  node,
  depth,
  expandedFolders,
  selectedSources,
  searchQuery,
  onToggleFolder,
  onToggleSource,
}: FileTreeNodeProps) {
  if (!matchesSearch(node, searchQuery)) return null;

  const isExpanded = expandedFolders.has(node.path);
  const isSelected = selectedSources.includes(node.path);
  const isDirectory = node.type === 'directory';

  const handleClick = (e: React.MouseEvent) => {
    if (isDirectory) {
      onToggleFolder(node.path);
    } else {
      onToggleSource(node.path, e);
    }
  };

  return (
    <div>
      <button
        onClick={handleClick}
        className={cn(
          'flex w-full items-center gap-1.5 rounded-sm px-2 py-1 text-sm transition-colors hover:bg-accent',
          isSelected && 'bg-secondary'
        )}
        style={{ paddingLeft: `${depth * 16 + 8}px` }}
      >
        {isDirectory ? (
          <>
            <ChevronRight
              className={cn(
                'h-3.5 w-3.5 shrink-0 text-muted-foreground transition-transform duration-150',
                isExpanded && 'rotate-90'
              )}
            />
            {isExpanded ? (
              <FolderOpen className="h-4 w-4 shrink-0 text-blue-500" />
            ) : (
              <Folder className="h-4 w-4 shrink-0 text-blue-400" />
            )}
          </>
        ) : (
          <span className="w-[14px] shrink-0" />
        )}

        <span className="truncate">{node.name}</span>

        {isDirectory && node.file_count !== undefined && (
          <span className="ml-auto shrink-0 text-xs text-muted-foreground">
            {node.file_count}
          </span>
        )}

        {!isDirectory && (
          <FileText className="ml-auto shrink-0 h-3.5 w-3.5 text-muted-foreground/60" />
        )}
      </button>

      {isDirectory && isExpanded && node.children && (
        <div>
          {node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              depth={depth + 1}
              expandedFolders={expandedFolders}
              selectedSources={selectedSources}
              searchQuery={searchQuery}
              onToggleFolder={onToggleFolder}
              onToggleSource={onToggleSource}
            />
          ))}
        </div>
      )}
    </div>
  );
});
