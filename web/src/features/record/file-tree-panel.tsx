import { useQuery } from "@tanstack/react-query";
import {
  ChevronDown,
  ChevronRight,
  FileText,
  Folder,
  FolderOpen,
  PanelLeftClose,
  PanelLeftOpen,
} from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { TreeNode } from "@/types/record";
import { getFileTree } from "./record-api";

interface FileTreePanelProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
  selectedPath: string | null;
  onSelectFile: (path: string) => void;
}

function TreeItem({
  node,
  depth,
  selectedPath,
  onSelectFile,
}: {
  node: TreeNode;
  depth: number;
  selectedPath: string | null;
  onSelectFile: (path: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const isDir = node.type === "directory";
  const isSelected = node.path === selectedPath;

  if (isDir) {
    return (
      <div>
        <button
          type="button"
          onClick={() => setOpen(!open)}
          className={cn(
            "flex w-full items-center gap-1.5 rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground",
          )}
          style={{ paddingLeft: `${depth * 12 + 8}px` }}
        >
          {open ? (
            <ChevronDown className="h-3.5 w-3.5 shrink-0" />
          ) : (
            <ChevronRight className="h-3.5 w-3.5 shrink-0" />
          )}
          {open ? (
            <FolderOpen className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
          ) : (
            <Folder className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
          )}
          <span className="truncate">{node.name}</span>
          {node.file_count != null && (
            <span className="ml-auto text-xs text-muted-foreground">
              {node.file_count}
            </span>
          )}
        </button>
        {open && node.children && (
          <div>
            {node.children.map((child) => (
              <TreeItem
                key={child.path}
                node={child}
                depth={depth + 1}
                selectedPath={selectedPath}
                onSelectFile={onSelectFile}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={() => onSelectFile(node.path)}
      className={cn(
        "flex w-full items-center gap-1.5 rounded-sm px-2 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground",
        isSelected && "bg-accent text-accent-foreground font-medium",
      )}
      style={{ paddingLeft: `${depth * 12 + 8}px` }}
    >
      <FileText className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
      <span className="truncate">{node.name}</span>
    </button>
  );
}

export function FileTreePanel({
  collapsed,
  onToggleCollapse,
  selectedPath,
  onSelectFile,
}: FileTreePanelProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["fileTree"],
    queryFn: getFileTree,
  });

  if (collapsed) {
    return (
      <div className="flex flex-col items-center border-r py-2">
        <Button variant="ghost" size="icon" onClick={onToggleCollapse}>
          <PanelLeftOpen className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className="flex w-64 shrink-0 flex-col border-r">
      <div className="flex items-center justify-between px-3 py-2">
        <span className="text-sm font-medium">Files</span>
        <Button variant="ghost" size="icon" onClick={onToggleCollapse}>
          <PanelLeftClose className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="px-1 pb-2">
          {isLoading && (
            <div className="px-2 py-4 text-center text-xs text-muted-foreground">
              Loading...
            </div>
          )}
          {error && (
            <div className="px-2 py-4 text-center text-xs text-destructive">
              Failed to load files
            </div>
          )}
          {data?.tree.map((node) => (
            <TreeItem
              key={node.path}
              node={node}
              depth={0}
              selectedPath={selectedPath}
              onSelectFile={onSelectFile}
            />
          ))}
          {!isLoading && !error && data?.tree.length === 0 && (
            <div className="px-2 py-4 text-center text-xs text-muted-foreground">
              No files found
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
