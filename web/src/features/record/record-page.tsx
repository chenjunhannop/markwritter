import { useState } from "react";
import { FileTreePanel } from "./file-tree-panel";
import { NoteEditor } from "./note-editor";

export function RecordPage() {
  const [treeCollapsed, setTreeCollapsed] = useState(false);
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  return (
    <div className="flex h-full">
      <FileTreePanel
        collapsed={treeCollapsed}
        onToggleCollapse={() => setTreeCollapsed(!treeCollapsed)}
        selectedPath={selectedPath}
        onSelectFile={setSelectedPath}
      />
      <div className="flex-1 min-w-0">
        <NoteEditor filePath={selectedPath} />
      </div>
    </div>
  );
}
