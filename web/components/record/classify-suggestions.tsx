'use client';

/**
 * Classify Suggestions Component
 *
 * Displays AI-generated classification suggestions (tags and folder).
 */

import { useRecordStore } from '@/lib/record-store';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, Tag, Folder, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ClassifySuggestionsProps {
  className?: string;
}

export function ClassifySuggestions({ className }: ClassifySuggestionsProps) {
  const content = useRecordStore((state) => state.content);
  const isClassifying = useRecordStore((state) => state.isClassifying);
  const classificationResult = useRecordStore((state) => state.classificationResult);
  const tagSuggestions = useRecordStore((state) => state.tagSuggestions);
  const folderSuggestion = useRecordStore((state) => state.folderSuggestion);

  const classify = useRecordStore((state) => state.classify);
  const addTag = useRecordStore((state) => state.addTag);
  const setFolderId = useRecordStore((state) => state.setFolderId);

  const hasContent = content.trim().length > 0;

  const handleAcceptTag = (tag: string) => {
    addTag(tag);
  };

  const handleAcceptFolder = () => {
    if (folderSuggestion?.folder) {
      setFolderId(folderSuggestion.folder);
    }
  };

  const suggestedTags = classificationResult?.suggested_tags ?? tagSuggestions;
  const suggestedFolder = classificationResult?.suggested_folder ?? folderSuggestion?.folder;

  const hasSuggestions = suggestedTags.length > 0 || suggestedFolder;

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Sparkles className="h-4 w-4" />
            Classification
          </span>
          {isClassifying && <Loader2 className="h-4 w-4 animate-spin" />}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {!hasSuggestions && !isClassifying && (
          <div className="flex flex-col items-center gap-2 py-4">
            <p className="text-sm text-muted-foreground text-center">
              Get AI-powered suggestions for tags and folder
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={classify}
              disabled={!hasContent || isClassifying}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Suggest
            </Button>
          </div>
        )}

        {suggestedTags.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Tag className="h-4 w-4" />
              Suggested tags
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestedTags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="cursor-pointer hover:bg-secondary/80"
                  onClick={() => handleAcceptTag(tag)}
                >
                  +{tag}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {suggestedFolder && (
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Folder className="h-4 w-4" />
              Suggested folder
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{suggestedFolder}</Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleAcceptFolder}
              >
                Accept
              </Button>
            </div>
          </div>
        )}

        {hasSuggestions && (
          <Button
            variant="ghost"
            size="sm"
            onClick={classify}
            disabled={!hasContent || isClassifying}
            className="w-full"
          >
            {isClassifying ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Re-analyze
              </>
            )}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}