/**
 * Settings Panel Components
 *
 * Components for managing application settings including:
 * - Vault path configuration
 * - LLM model selection and API key
 * - Theme and language preferences
 */

'use client';

import React, { useEffect, useState } from 'react';
import {
  useSettingsStore,
  type Theme,
} from '@/lib/settings-store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Eye, EyeOff, Trash2, FolderOpen } from 'lucide-react';

// ==================== Vault Config ====================

interface VaultConfigProps {
  className?: string;
}

export function VaultConfig({ className }: VaultConfigProps) {
  const { vaultPath, setVaultPath } = useSettingsStore();
  const [localPath, setLocalPath] = useState(vaultPath);

  const handleBrowse = async () => {
    try {
      // Check if File System Access API is available
      if ('showDirectoryPicker' in window) {
        const dirHandle = await (window as unknown as { showDirectoryPicker: () => Promise<{ name: string }> }).showDirectoryPicker();
        const path = dirHandle.name;
        setVaultPath(path);
        setLocalPath(path);
      } else {
        // Fallback: prompt user to enter path manually
        const path = prompt('Enter vault path:');
        if (path) {
          setVaultPath(path);
          setLocalPath(path);
        }
      }
    } catch (error) {
      // User cancelled or error occurred
      if (error instanceof Error && error.name !== 'AbortError') {
        console.error('Failed to select directory:', error);
      }
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPath = e.target.value;
    setLocalPath(newPath);
    setVaultPath(newPath);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Vault Path</CardTitle>
        <CardDescription>
          Select your Obsidian vault directory
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2">
          <Input
            value={localPath}
            onChange={handleInputChange}
            placeholder="Select a vault directory"
            className="flex-1"
          />
          <Button
            variant="outline"
            onClick={handleBrowse}
            aria-label="Browse for vault directory"
          >
            <FolderOpen className="h-4 w-4 mr-2" />
            Browse
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== LLM Config ====================

interface LLMConfigProps {
  className?: string;
}

export function LLMConfig({ className }: LLMConfigProps) {
  const {
    llmModel,
    apiKey,
    setLLMModel,
    setApiKey,
    clearApiKey,
    hasApiKey,
    getMaskedApiKey,
    getAvailableModels,
  } = useSettingsStore();

  const [showKey, setShowKey] = useState(false);
  const [keyInput, setKeyInput] = useState('');

  const models = getAvailableModels();

  const handleModelChange = (value: string) => {
    setLLMModel(value);
  };

  const handleKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newKey = e.target.value;
    setKeyInput(newKey);
    setApiKey(newKey);
  };

  const handleClearKey = () => {
    clearApiKey();
    setKeyInput('');
  };

  const toggleKeyVisibility = () => {
    setShowKey(!showKey);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>LLM Configuration</CardTitle>
        <CardDescription>
          Configure your language model and API key
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Model Selection */}
        <div className="space-y-2">
          <Label htmlFor="model-select">Model</Label>
          <Select value={llmModel} onValueChange={handleModelChange}>
            <SelectTrigger id="model-select">
              <SelectValue placeholder="Select a model" />
            </SelectTrigger>
            <SelectContent>
              {models.map((model) => (
                <SelectItem key={model} value={model}>
                  {model}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* API Key Input */}
        <div className="space-y-2">
          <Label htmlFor="api-key">API Key</Label>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                id="api-key"
                type={showKey ? 'text' : 'password'}
                value={hasApiKey() && !keyInput ? getMaskedApiKey() : keyInput}
                onChange={handleKeyChange}
                placeholder="Enter your API key"
                className="pr-20"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={toggleKeyVisibility}
                  aria-label={showKey ? 'Hide API key' : 'Show API key'}
                >
                  {showKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
                {hasApiKey() && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={handleClearKey}
                    aria-label="Clear API key"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </div>
          {hasApiKey() && (
            <p className="text-sm text-muted-foreground">
              API key configured: {getMaskedApiKey()}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== General Config ====================

interface GeneralConfigProps {
  className?: string;
}

const LANGUAGES = [
  { value: 'en', label: 'English' },
  { value: 'zh', label: 'Chinese' },
  { value: 'ja', label: 'Japanese' },
  { value: 'ko', label: 'Korean' },
  { value: 'es', label: 'Spanish' },
  { value: 'fr', label: 'French' },
  { value: 'de', label: 'German' },
];

const THEMES: Array<{ value: Theme; label: string }> = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
];

export function GeneralConfig({ className }: GeneralConfigProps) {
  const { theme, language, setTheme, setLanguage, resetSettings } =
    useSettingsStore();
  const [showResetDialog, setShowResetDialog] = useState(false);

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
  };

  const handleLanguageChange = (value: string) => {
    setLanguage(value);
  };

  const handleReset = () => {
    resetSettings();
    setShowResetDialog(false);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>General Settings</CardTitle>
        <CardDescription>
          Customize your application preferences
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Theme Selection */}
        <div className="space-y-2">
          <Label>Theme</Label>
          <div className="flex gap-2">
            {THEMES.map((t) => (
              <Button
                key={t.value}
                variant={theme === t.value ? 'default' : 'outline'}
                onClick={() => handleThemeChange(t.value)}
                aria-pressed={theme === t.value}
              >
                {t.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Language Selection */}
        <div className="space-y-2">
          <Label htmlFor="language-select">Language</Label>
          <Select value={language} onValueChange={handleLanguageChange}>
            <SelectTrigger id="language-select">
              <SelectValue placeholder="Select a language" />
            </SelectTrigger>
            <SelectContent>
              {LANGUAGES.map((lang) => (
                <SelectItem key={lang.value} value={lang.value}>
                  {lang.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Reset Button */}
        <div className="pt-4">
          <Dialog open={showResetDialog} onOpenChange={setShowResetDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">Reset to Defaults</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Reset Settings?</DialogTitle>
                <DialogDescription>
                  Are you sure you want to reset all settings to their default
                  values? This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setShowResetDialog(false)}
                >
                  Cancel
                </Button>
                <Button variant="destructive" onClick={handleReset}>
                  Reset
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== Settings Panel ====================

interface SettingsPanelProps {
  className?: string;
}

export function SettingsPanel({ className }: SettingsPanelProps) {
  const { error, clearError, isLoading, fetchSettings } = useSettingsStore();

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  return (
    <div className={className}>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      {/* Loading State */}
      {isLoading && (
        <div className="space-y-6 animate-pulse">
          <div className="h-32 rounded-lg bg-muted" />
          <div className="h-48 rounded-lg bg-muted" />
          <div className="h-32 rounded-lg bg-muted" />
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-destructive/10 text-destructive px-4 py-3 rounded-md mb-4 flex items-center justify-between">
          <span>{error}</span>
          <Button variant="ghost" size="sm" onClick={clearError}>
            Dismiss
          </Button>
        </div>
      )}

      {!isLoading && (
        <div className="space-y-6">
          {/* Vault Configuration */}
          <section>
            <VaultConfig />
          </section>

          {/* LLM Configuration */}
          <section>
            <LLMConfig />
          </section>

          {/* General Settings */}
          <section>
            <GeneralConfig />
          </section>
        </div>
      )}
    </div>
  );
}

export default SettingsPanel;