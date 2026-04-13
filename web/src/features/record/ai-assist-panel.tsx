import { Loader2, PenLine, Sparkles, Type } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import type { AIRewriteWithDiffResponse } from "@/types/record";
import { DiffPreview } from "./diff-preview";
import { aiContinue, aiPolishWithDiff, aiRewriteWithDiff } from "./record-api";

interface AIAssistPanelProps {
  content: string;
  selectedText: string | null;
  onAppend: (text: string) => void;
  onReplace: (text: string) => void;
}

export function AIAssistPanel({
  content,
  selectedText,
  onAppend,
  onReplace,
}: AIAssistPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [diffResult, setDiffResult] =
    useState<AIRewriteWithDiffResponse | null>(null);
  const [diffActionType, setDiffActionType] = useState<string>("");
  const [startTime, setStartTime] = useState<number>(0);

  const targetContent = selectedText || content;
  const hasSelection = selectedText !== null && selectedText.length > 0;

  const handleContinue = async () => {
    setLoading(true);
    setError(null);
    setDiffResult(null);
    const start = Date.now();
    setStartTime(start);
    try {
      const result = await aiContinue(content);
      onAppend(result.generated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to continue");
    } finally {
      setLoading(false);
    }
  };

  const handleRewrite = async () => {
    setLoading(true);
    setError(null);
    setDiffResult(null);
    setDiffActionType("rewrite");
    const start = Date.now();
    setStartTime(start);
    try {
      const result = await aiRewriteWithDiff(targetContent);
      setDiffResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to rewrite");
    } finally {
      setLoading(false);
    }
  };

  const handlePolish = async () => {
    setLoading(true);
    setError(null);
    setDiffResult(null);
    setDiffActionType("polish");
    const start = Date.now();
    setStartTime(start);
    try {
      const result = await aiPolishWithDiff(targetContent);
      setDiffResult(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to polish");
    } finally {
      setLoading(false);
    }
  };

  const handleDiffAccept = (modified: string) => {
    if (hasSelection && diffResult && selectedText) {
      const idx = content.indexOf(selectedText);
      const before = content.substring(0, idx);
      const after = content.substring(idx + selectedText.length);
      onReplace(before + modified + after);
    } else {
      onReplace(modified);
    }
    setDiffResult(null);
  };

  const handleDiffReject = () => {
    setDiffResult(null);
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-1.5">
        <Sparkles className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-medium">AI Assist</span>
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleContinue}
          disabled={loading || content.trim().length === 0}
        >
          {loading ? (
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
          ) : (
            <Type className="mr-1 h-3 w-3" />
          )}
          Continue
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRewrite}
          disabled={loading || targetContent.trim().length === 0}
        >
          {loading ? (
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
          ) : (
            <Sparkles className="mr-1 h-3 w-3" />
          )}
          Rewrite
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={handlePolish}
          disabled={loading || targetContent.trim().length === 0}
        >
          {loading ? (
            <Loader2 className="mr-1 h-3 w-3 animate-spin" />
          ) : (
            <PenLine className="mr-1 h-3 w-3" />
          )}
          Polish
        </Button>
      </div>

      {hasSelection && (
        <p className="text-xs text-muted-foreground">
          Applying to selected text ({selectedText.length} chars)
        </p>
      )}

      {loading && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          AI is thinking...
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          <span>{error}</span>
          <Button variant="ghost" size="sm" onClick={() => setError(null)}>
            Dismiss
          </Button>
        </div>
      )}

      {diffResult && (
        <DiffPreview
          delta={diffResult.delta}
          original={diffResult.original}
          modified={diffResult.modified}
          actionType={diffActionType}
          startTime={startTime}
          onAccept={handleDiffAccept}
          onReject={handleDiffReject}
        />
      )}
    </div>
  );
}
