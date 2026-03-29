'use client';

/**
 * VaultPathBar - Pinned-to-bottom vault path display/config.
 * Shows truncated path, click opens Dialog to change.
 */

import { useState } from 'react';
import { FolderOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { useSettingsStore } from '@/lib/settings-store';
import { useSourcesStore } from '@/lib/sources-store';
import { updateSettings } from '@/lib/api';

export function VaultPathBar() {
  const vaultPath = useSettingsStore((s) => s.vaultPath);
  const setVaultPath = useSettingsStore((s) => s.setVaultPath);
  const loadTree = useSourcesStore((s) => s.loadTree);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [inputPath, setInputPath] = useState(vaultPath);
  const [saving, setSaving] = useState(false);

  const displayPath = vaultPath
    ? vaultPath.replace(/^\/Users\/[^/]+/, '~')
    : 'Not configured';

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateSettings({ vault_path: inputPath });
      setVaultPath(inputPath);
      await loadTree();
      setDialogOpen(false);
    } catch {
      // Error handling could be improved
    } finally {
      setSaving(false);
    }
  };

  const handleOpen = () => {
    setInputPath(vaultPath);
    setDialogOpen(true);
  };

  return (
    <>
      <button
        onClick={handleOpen}
        className="flex items-center gap-2 border-t px-3 py-2 text-xs text-muted-foreground hover:bg-accent transition-colors"
      >
        <FolderOpen className="h-3.5 w-3.5 shrink-0" />
        <span className="truncate">{displayPath}</span>
      </button>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Vault Path</DialogTitle>
            <DialogDescription>
              Set the root directory of your Obsidian vault.
            </DialogDescription>
          </DialogHeader>
          <Input
            value={inputPath}
            onChange={(e) => setInputPath(e.target.value)}
            placeholder="/Users/you/Documents/MyVault"
            autoFocus
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={saving || !inputPath.trim()}>
              {saving ? 'Saving...' : 'Save'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
