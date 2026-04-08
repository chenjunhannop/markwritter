'use client';

import { Suspense } from 'react';
import { AppShell } from '@/components/apple';
import { FloatingPanel } from '@/components/apple';
import { NoteForm } from '@/components/record/note-form';
import { QuickRecord } from '@/components/record/quick-record';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { FileEdit, Zap } from 'lucide-react';

function RecordContent() {
  return (
    <div className="py-4">
      <Tabs defaultValue="quick" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2 mb-6">
          <TabsTrigger value="quick" className="gap-2">
            <Zap className="h-4 w-4" />
            Quick Record
          </TabsTrigger>
          <TabsTrigger value="editor" className="gap-2">
            <FileEdit className="h-4 w-4" />
            Full Editor
          </TabsTrigger>
        </TabsList>

        <TabsContent value="quick">
          <FloatingPanel>
            <div className="p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Record</h3>
              <QuickRecord redirectAfterSave={false} />
            </div>
          </FloatingPanel>
        </TabsContent>

        <TabsContent value="editor">
          <FloatingPanel>
            <NoteForm />
          </FloatingPanel>
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function RecordPage() {
  return (
    <Suspense fallback={<div className="p-4">Loading...</div>}>
      <AppShell title="Capture & Compose" statusBadge="Drafting">
        <RecordContent />
      </AppShell>
    </Suspense>
  );
}
