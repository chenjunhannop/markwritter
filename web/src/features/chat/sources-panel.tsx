import { ChevronRight, FileText, Folder, FolderOpen, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { TreeNode } from "./chat-api";
import { useChatStore } from "./chat-store";

interface TreeItemProps {
  node: TreeNode;
  selectedPaths: Set<string>;
  onToggle: (path: string) => void;
  depth: number;
}

function TreeItem({ node, selectedPaths, onToggle, depth }: TreeItemProps) {
  const [expanded, setExpanded] = useState(depth < 1);
  const isFolder = node.type === "folder";
  const isChecked = selectedPaths.has(node.path);

  const allDescendantPaths = isFolder ? collectPaths(node) : [node.path];
  const allChecked =
    isFolder && allDescendantPaths.every((p) => selectedPaths.has(p));
  const someChecked =
    isFolder &&
    !allChecked &&
    allDescendantPaths.some((p) => selectedPaths.has(p));

  function collectPaths(n: TreeNode): string[] {
    if (n.type === "file") return [n.path];
    return (n.children ?? []).flatMap(collectPaths);
  }

  function handleToggle() {
    if (isFolder) {
      if (allChecked) {
        allDescendantPaths.forEach((p) => {
          if (selectedPaths.has(p)) onToggle(p);
        });
      } else {
        allDescendantPaths.forEach((p) => {
          if (!selectedPaths.has(p)) onToggle(p);
        });
      }
    } else {
      onToggle(node.path);
    }
  }

  return (
    <div>
      <div
        className={cn(
          "flex items-center gap-1.5 rounded-sm px-2 py-1 text-sm hover:bg-accent/50",
          depth > 0 && "ml-4",
        )}
      >
        {isFolder && (
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={() => setExpanded(!expanded)}
            className="h-4 w-4 shrink-0"
          >
            <ChevronRight
              className={cn(
                "h-3 w-3 transition-transform",
                expanded && "rotate-90",
              )}
            />
          </Button>
        )}
        {!isFolder && <span className="w-4" />}

        <Checkbox
          checked={
            isFolder
              ? allChecked
                ? true
                : someChecked
                  ? "indeterminate"
                  : false
              : isChecked
          }
          onCheckedChange={handleToggle}
        />

        {isFolder ? (
          expanded ? (
            <FolderOpen className="h-4 w-4 shrink-0 text-muted-foreground" />
          ) : (
            <Folder className="h-4 w-4 shrink-0 text-muted-foreground" />
          )
        ) : (
          <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
        )}

        <span className="truncate text-xs">{node.name}</span>
      </div>

      {isFolder && expanded && (
        <div>
          {(node.children ?? []).map((child) => (
            <TreeItem
              key={child.path}
              node={child}
              selectedPaths={selectedPaths}
              onToggle={onToggle}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface SourcesPanelProps {
  open: boolean;
  onClose: () => void;
}

export function SourcesPanel({ open, onClose }: SourcesPanelProps) {
  const activeSessionId = useChatStore((s) => s.activeSessionId);
  const sessions = useChatStore((s) => s.sessions);
  const setActiveSessionSources = useChatStore(
    (s) => s.setActiveSessionSources,
  );
  const session = sessions.find((s) => s.id === activeSessionId);
  const [localSelection, setLocalSelection] = useState<Set<string>>(
    () => new Set(session?.selectedSources ?? []),
  );

  const handleToggle = (path: string) => {
    setLocalSelection((prev) => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const handleConfirm = () => {
    setActiveSessionSources(Array.from(localSelection));
    onClose();
  };

  const handleClear = () => {
    setLocalSelection(new Set());
    setActiveSessionSources([]);
  };

  if (!open) return null;

  return (
    <div className="flex h-full w-64 flex-col border-l bg-background">
      <div className="flex items-center justify-between border-b p-3">
        <span className="text-sm font-semibold">Sources</span>
        <Button type="button" variant="ghost" size="icon-sm" onClick={onClose}>
          <X className="h-4 w-4" />
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-2">
          <SourcesTree selectedPaths={localSelection} onToggle={handleToggle} />
        </div>
      </ScrollArea>

      <div className="flex items-center gap-2 border-t p-3">
        <span className="flex-1 text-xs text-muted-foreground">
          {localSelection.size} selected
        </span>
        <Button type="button" variant="ghost" size="sm" onClick={handleClear}>
          Clear
        </Button>
        <Button type="button" size="sm" onClick={handleConfirm}>
          Done
        </Button>
      </div>
    </div>
  );
}

function SourcesTree({
  selectedPaths,
  onToggle,
}: {
  selectedPaths: Set<string>;
  onToggle: (path: string) => void;
}) {
  return (
    <div className="space-y-0.5">
      <p className="px-2 py-1 text-xs text-muted-foreground">
        Select files to use as context for the chat.
      </p>
      <StaticTreeItems selectedPaths={selectedPaths} onToggle={onToggle} />
    </div>
  );
}

function StaticTreeItems({
  selectedPaths,
  onToggle,
}: {
  selectedPaths: Set<string>;
  onToggle: (path: string) => void;
}) {
  const files: TreeNode[] = [
    {
      name: "notes",
      path: "notes",
      type: "folder",
      children: [
        {
          name: "chapter-1.md",
          path: "notes/chapter-1.md",
          type: "file",
        },
        {
          name: "chapter-2.md",
          path: "notes/chapter-2.md",
          type: "file",
        },
        {
          name: "ideas",
          path: "notes/ideas",
          type: "folder",
          children: [
            {
              name: "brainstorm.md",
              path: "notes/ideas/brainstorm.md",
              type: "file",
            },
          ],
        },
      ],
    },
  ];

  return (
    <>
      {files.map((node) => (
        <TreeItem
          key={node.path}
          node={node}
          selectedPaths={selectedPaths}
          onToggle={onToggle}
          depth={0}
        />
      ))}
    </>
  );
}
