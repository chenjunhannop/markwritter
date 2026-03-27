'use client';

/**
 * Note Form Component
 *
 * Complete note editing form with editor, metadata, and AI assistance.
 */

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { useRecordStore } from '@/lib/record-store';
import { MarkdownEditor } from '@/components/editor/markdown-editor';
import { MetadataEditor } from './metadata-editor';
import { AIAssistPanel } from '@/components/editor/ai-assist-panel';
import { ClassifySuggestions } from './classify-suggestions';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Save, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NoteFormProps {
  className?: string;
}

export function NoteForm({ className }: NoteFormProps) {
  const searchParams = useSearchParams();
  const recordPath = searchParams.get('path');

  const currentRecord = useRecordStore((state) => state.currentRecord);
  const isSaving = useRecordStore((state) => state.isSaving);
  const saveError = useRecordStore((state) => state.saveError);
  const saveRecord = useRecordStore((state) => state.saveRecord);
  const clearRecord = useRecordStore((state) => state.clearRecord);

  // Clear form when no record path
  useEffect(() => {
    if (!recordPath) {
      clearRecord();
    }
  }, [recordPath, clearRecord]);

  const handleSave = async () => {
    await saveRecord();
  };

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <div className="flex items-center justify-between p-4 border-b">
        <h1 className="text-xl font-semibold">
          {currentRecord ? 'Edit Note' : 'New Note'}
        </h1>
        <div className="flex items-center gap-2">
          {saveError && (
            <span className="text-sm text-destructive">{saveError}</span>
          )}
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 p-4 overflow-auto">
          <Tabs defaultValue="editor" className="h-full flex flex-col">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="editor">Editor</TabsTrigger>
              <TabsTrigger value="metadata">Metadata</TabsTrigger>
            </TabsList>

            <TabsContent value="editor" className="flex-1 mt-4">
              <MarkdownEditor className="h-full" minHeight={400} />
            </TabsContent>

            <TabsContent value="metadata" className="flex-1 mt-4">
              <Card>
                <CardContent className="pt-6">
                  <MetadataEditor />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        <div className="w-80 border-l p-4 space-y-4 overflow-auto">
          <AIAssistPanel />
          <ClassifySuggestions />
        </div>
      </div>
    </div>
  );
}