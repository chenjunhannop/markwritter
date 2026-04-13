import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Loader2, Save, Sparkles } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { AIAssistPanel } from "./ai-assist-panel";
import { getNoteContent, saveNote } from "./record-api";

type SaveStatus = "idle" | "dirty" | "saving" | "saved";

interface NoteEditorProps {
  filePath: string | null;
}

export function NoteEditor({ filePath }: NoteEditorProps) {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [selectedText, setSelectedText] = useState<string | null>(null);
  const [showAI, setShowAI] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const isExternalUpdate = useRef(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["noteContent", filePath],
    queryFn: () => getNoteContent(filePath as string),
    enabled: filePath !== null,
  });

  useEffect(() => {
    if (data) {
      isExternalUpdate.current = true;
      setTitle(data.title);
      setContent(data.content);
      setSaveStatus("saved");
    }
  }, [data]);

  useEffect(() => {
    if (!filePath) {
      setTitle("");
      setContent("");
      setSaveStatus("idle");
    }
  }, [filePath]);

  const saveMutation = useMutation({
    mutationFn: () =>
      saveNote({
        path: filePath as string,
        content,
        title: title || undefined,
      }),
    onSuccess: () => {
      setSaveStatus("saved");
      queryClient.invalidateQueries({ queryKey: ["fileTree"] });
    },
  });

  const handleContentChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      if (isExternalUpdate.current) {
        isExternalUpdate.current = false;
        return;
      }
      setContent(e.target.value);
      setSaveStatus("dirty");
    },
    [],
  );

  const handleTitleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setTitle(e.target.value);
      setSaveStatus("dirty");
    },
    [],
  );

  const handleSave = useCallback(() => {
    if (filePath && saveStatus === "dirty") {
      setSaveStatus("saving");
      saveMutation.mutate();
    }
  }, [filePath, saveStatus, saveMutation]);

  const handleAppend = useCallback((text: string) => {
    setContent((prev) => prev + text);
    setSaveStatus("dirty");
  }, []);

  const handleReplace = useCallback((text: string) => {
    setContent(text);
    setSaveStatus("dirty");
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "s") {
        e.preventDefault();
        handleSave();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave]);

  const handleTextSelect = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    const sel = textarea.value.substring(
      textarea.selectionStart,
      textarea.selectionEnd,
    );
    setSelectedText(sel.length > 0 ? sel : null);
  }, []);

  if (!filePath) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        <p>Select a file from the tree to start editing</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        Loading note...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-muted-foreground">
        <p className="text-destructive">Failed to load note</p>
        <p className="text-sm">{error.message}</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 border-b px-4 py-2">
        <Input
          value={title}
          onChange={handleTitleChange}
          placeholder="Note title"
          className="h-8 flex-1 border-none shadow-none focus-visible:ring-0"
        />
        <div className="flex items-center gap-2">
          <span
            className={
              saveStatus === "saved"
                ? "text-xs text-status-success"
                : saveStatus === "saving"
                  ? "text-xs text-muted-foreground"
                  : saveStatus === "dirty"
                    ? "text-xs text-status-warning"
                    : "text-xs text-muted-foreground"
            }
          >
            {saveStatus === "saved" && "Saved"}
            {saveStatus === "saving" && "Saving..."}
            {saveStatus === "dirty" && "Unsaved"}
            {saveStatus === "idle" && ""}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleSave}
            disabled={saveStatus !== "dirty"}
          >
            <Save className="mr-1 h-3 w-3" />
            Save
          </Button>
          <Button
            variant={showAI ? "default" : "outline"}
            size="sm"
            onClick={() => setShowAI(!showAI)}
          >
            <Sparkles className="mr-1 h-3 w-3" />
            AI
          </Button>
        </div>
      </div>

      <div className="flex flex-1 min-h-0">
        <div className="flex-1 min-w-0">
          <Textarea
            ref={textareaRef}
            value={content}
            onChange={handleContentChange}
            onSelect={handleTextSelect}
            onMouseUp={handleTextSelect}
            placeholder="Start writing..."
            className="h-full resize-none rounded-none border-none shadow-none focus-visible:ring-0 font-mono text-sm"
          />
        </div>

        {showAI && (
          <div className="w-72 shrink-0 border-l p-3 overflow-auto">
            <AIAssistPanel
              content={content}
              selectedText={selectedText}
              onAppend={handleAppend}
              onReplace={handleReplace}
            />
          </div>
        )}
      </div>
    </div>
  );
}
