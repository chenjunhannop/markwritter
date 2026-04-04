'use client';

/**
 * Record Page
 *
 * Main page for creating and editing notes.
 */

import { Suspense } from 'react';
import { MainLayout } from '@/components/layout';
import { NoteForm } from '@/components/record/note-form';
import { QuickRecord } from '@/components/record/quick-record';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileEdit, Zap } from 'lucide-react';

function RecordContent() {
  return (
    <div className="container mx-auto py-6 flex-1 flex flex-col min-h-0">
      <Tabs defaultValue="quick" className="flex-1 flex flex-col">
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

        <TabsContent value="quick" className="flex-1">
          <Card className="max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle>Quick Record</CardTitle>
            </CardHeader>
            <CardContent>
              <QuickRecord redirectAfterSave={false} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="editor" className="flex-1">
          <NoteForm />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function RecordPage() {
  return (
    <Suspense fallback={<div className="p-4">Loading...</div>}>
      <MainLayout title="Record">
        <RecordContent />
      </MainLayout>
    </Suspense>
  );
}
