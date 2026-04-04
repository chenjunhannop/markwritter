'use client';

/**
 * AI Assist Panel Component
 *
 * A panel for AI assistance with continue, rewrite, and polish buttons.
 * WRT-005-V1: Added diff preview support for rewrite/polish operations.
 */

import { useRecordStore } from '@/lib/record-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Wand2, RefreshCw, Sparkles, Square, CheckCircle, XCircle, Undo2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { DiffPreview } from './diff-preview';

interface AIAssistPanelProps {
  className?: string;
}

export function AIAssistPanel({ className }: AIAssistPanelProps) {
  const currentRecord = useRecordStore((state) => state.currentRecord);
  const content = useRecordStore((state) => state.content);
  const isStreaming = useRecordStore((state) => state.isStreaming);
  const streamError = useRecordStore((state) => state.streamError);

  // WRT-005-V1: Diff preview state
  const showDiffPreview = useRecordStore((state) => state.showDiffPreview);
  const diffResult = useRecordStore((state) => state.diffResult);
  const baseContent = useRecordStore((state) => state.baseContent);
  const generatedContent = useRecordStore((state) => state.generatedContent);

  const aiContinue = useRecordStore((state) => state.aiContinue);
  const aiRewrite = useRecordStore((state) => state.aiRewrite);
  const aiPolish = useRecordStore((state) => state.aiPolish);
  // WRT-005-V1: Diff-based actions
  const aiRewriteWithDiff = useRecordStore((state) => state.aiRewriteWithDiff);
  const aiPolishWithDiff = useRecordStore((state) => state.aiPolishWithDiff);
  const acceptDiff = useRecordStore((state) => state.acceptDiff);
  const rejectDiff = useRecordStore((state) => state.rejectDiff);
  const undoLastAccept = useRecordStore((state) => state.undoLastAccept);
  const canUndo = useRecordStore((state) => state.canUndo);
  const cancelStream = useRecordStore((state) => state.cancelStream);

  const hasContent = content.trim().length > 0;

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Wand2 className="h-4 w-4" />
          AI Assistant
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {streamError && (
          <div className="p-2 text-sm text-destructive bg-destructive/10 rounded-md">
            {streamError}
          </div>
        )}

        {/* WRT-005-V1: Diff Preview */}
        {showDiffPreview && baseContent && generatedContent && (
          <DiffPreview
            original={baseContent}
            modified={generatedContent}
            onAccept={acceptDiff}
            onReject={rejectDiff}
          />
        )}

        {/* WRT-005-V1: Undo Button (shown after accept, within 30s) */}
        {canUndo && (
          <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-md">
            <div className="text-xs text-yellow-700 dark:text-yellow-300 flex items-center gap-2">
              <Undo2 className="h-4 w-4" />
              已接受 AI 修改，可在 30 秒内撤销
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={undoLastAccept}
              className="flex items-center gap-2"
            >
              <Undo2 className="h-4 w-4" />
              撤销
            </Button>
          </div>
        )}

        <div className="flex flex-wrap gap-2">
          {isStreaming ? (
            <Button
              variant="destructive"
              size="sm"
              onClick={cancelStream}
              className="flex items-center gap-2"
            >
              <Square className="h-4 w-4" />
              Cancel
            </Button>
          ) : showDiffPreview ? (
            // Show waiting message during diff preview
            <div className="text-xs text-muted-foreground flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              请审查修改并接受或拒绝
            </div>
          ) : (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={aiContinue}
                disabled={!hasContent}
                className="flex items-center gap-2"
              >
                <Wand2 className="h-4 w-4" />
                Continue
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => aiRewriteWithDiff('formal')}
                disabled={!hasContent}
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Rewrite
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={aiPolishWithDiff}
                disabled={!hasContent}
                className="flex items-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                Polish
              </Button>
            </>
          )}
        </div>

        {!hasContent && (
          <p className="text-xs text-muted-foreground">
            输入内容以启用 AI 辅助功能。
          </p>
        )}
      </CardContent>
    </Card>
  );
}
