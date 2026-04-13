export interface TreeNode {
  name: string;
  path: string;
  type: "file" | "directory";
  file_count?: number;
  children?: TreeNode[];
}

export interface FileTreeResponse {
  tree: TreeNode[];
}

export interface SourceReference {
  filePath: string;
  fileName: string;
  excerpt?: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  category?: string;
  createdAt: number;
  updatedAt: number;
}

export interface NoteFormInput {
  title: string;
  content: string;
  tags: string[];
  category?: string;
  sources?: string[];
}

export interface DiffDelta {
  op: "equal" | "insert" | "delete";
  text: string;
}

export interface AIRewriteWithDiffResponse {
  original: string;
  modified: string;
  delta: DiffDelta[];
}

export interface AIContinueResponse {
  generated: string;
}

export interface NoteContentResponse {
  content: string;
  path: string;
  title: string;
}

export interface SaveNoteRequest {
  path: string;
  content: string;
  title?: string;
}
