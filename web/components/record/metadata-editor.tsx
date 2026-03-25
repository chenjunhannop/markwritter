'use client';

/**
 * Metadata Editor Component
 *
 * Editor for note metadata: title, tags, aliases.
 */

import { useRecordStore } from '@/lib/record-store';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState, useCallback, type KeyboardEvent } from 'react';

interface MetadataEditorProps {
  className?: string;
}

export function MetadataEditor({ className }: MetadataEditorProps) {
  const title = useRecordStore((state) => state.title);
  const tags = useRecordStore((state) => state.tags);
  const aliases = useRecordStore((state) => state.aliases);

  const setTitle = useRecordStore((state) => state.setTitle);
  const addTag = useRecordStore((state) => state.addTag);
  const removeTag = useRecordStore((state) => state.removeTag);
  const setAliases = useRecordStore((state) => state.setAliases);

  const [newTag, setNewTag] = useState('');
  const [newAlias, setNewAlias] = useState('');

  const handleAddTag = useCallback(() => {
    const trimmed = newTag.trim();
    if (trimmed) {
      addTag(trimmed);
      setNewTag('');
    }
  }, [newTag, addTag]);

  const handleTagKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleAddTag();
      }
    },
    [handleAddTag]
  );

  const handleAddAlias = useCallback(() => {
    const trimmed = newAlias.trim();
    if (trimmed && !aliases.includes(trimmed)) {
      setAliases([...aliases, trimmed]);
      setNewAlias('');
    }
  }, [newAlias, aliases, setAliases]);

  const handleAliasKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleAddAlias();
      }
    },
    [handleAddAlias]
  );

  const handleRemoveAlias = useCallback(
    (alias: string) => {
      setAliases(aliases.filter((a) => a !== alias));
    },
    [aliases, setAliases]
  );

  return (
    <div className={cn('space-y-4', className)}>
      <div className="space-y-2">
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Note title"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="tags">Tags</Label>
        <div className="flex flex-wrap gap-2 mb-2">
          {tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="gap-1">
              #{tag}
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-1 hover:text-destructive"
                aria-label={`Remove tag ${tag}`}
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
        <div className="flex gap-2">
          <Input
            id="tags"
            value={newTag}
            onChange={(e) => setNewTag(e.target.value)}
            onKeyDown={handleTagKeyDown}
            placeholder="Add tag"
            className="flex-1"
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={handleAddTag}
            disabled={!newTag.trim()}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="aliases">Aliases</Label>
        <div className="flex flex-wrap gap-2 mb-2">
          {aliases.map((alias) => (
            <Badge key={alias} variant="outline" className="gap-1">
              {alias}
              <button
                type="button"
                onClick={() => handleRemoveAlias(alias)}
                className="ml-1 hover:text-destructive"
                aria-label={`Remove alias ${alias}`}
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
        <div className="flex gap-2">
          <Input
            id="aliases"
            value={newAlias}
            onChange={(e) => setNewAlias(e.target.value)}
            onKeyDown={handleAliasKeyDown}
            placeholder="Add alias"
            className="flex-1"
          />
          <Button
            type="button"
            variant="outline"
            size="icon"
            onClick={handleAddAlias}
            disabled={!newAlias.trim()}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}