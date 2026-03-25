'use client';

/**
 * AI Assist Panel Component
 *
 * A panel for AI assistance with continue, rewrite, and polish buttons.
 */

import { useRecordStore } from '@/lib/record-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Wand2, RefreshCw, Sparkles, Square } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AIAssistPanelProps {
  className?: string;
}

export function AIAssistPanel({ className }: AIAssistPanelProps) {
  const currentRecord = useRecordStore((state) => state.currentRecord);
  const content = useRecordStore((state) => state.content);
  const isStreaming = useRecordStore((state) => state.isStreaming);
  const streamError = useRecordStore((state) => state.streamError);

  const aiContinue = useRecordStore((state) => state.aiContinue);
  const aiRewrite = useRecordStore((state) => state.aiRewrite);
  const aiPolish = useRecordStore((state) => state.aiPolish);
  const cancelStream = useRecordStore((state) => state.cancelStream);

  const hasRecord = currentRecord !== null;
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
          ) : (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={aiContinue}
                disabled={!hasRecord}
                className="flex items-center gap-2"
              >
                <Wand2 className="h-4 w-4" />
                Continue
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={aiRewrite}
                disabled={!hasRecord || !hasContent}
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Rewrite
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={aiPolish}
                disabled={!hasRecord || !hasContent}
                className="flex items-center gap-2"
              >
                <Sparkles className="h-4 w-4" />
                Polish
              </Button>
            </>
          )}
        </div>

        {!hasRecord && (
          <p className="text-xs text-muted-foreground">
            Save your note to enable AI assistance.
          </p>
        )}
      </CardContent>
    </Card>
  );
}