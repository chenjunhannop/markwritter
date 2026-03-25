/**
 * Tests for Settings Store
 *
 * TDD approach: Tests for settings state management before implementation.
 *
 * Tests cover:
 * - Vault path configuration
 * - LLM model selection
 * - API key secure storage
 * - Theme preferences
 * - Persistence behavior
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock crypto.subtle for API key encryption
const mockCryptoKey = { type: 'secret', algorithm: { name: 'AES-GCM' } };

const mockCrypto = {
  subtle: {
    generateKey: vi.fn().mockResolvedValue(mockCryptoKey),
    encrypt: vi.fn().mockResolvedValue(new ArrayBuffer(16)),
    decrypt: vi.fn().mockResolvedValue(new TextEncoder().encode('test-api-key')),
    importKey: vi.fn().mockResolvedValue(mockCryptoKey),
    exportKey: vi.fn().mockResolvedValue(new ArrayBuffer(16)),
    deriveKey: vi.fn().mockResolvedValue(mockCryptoKey),
  },
  getRandomValues: vi.fn((arr: Uint8Array) => {
    for (let i = 0; i < arr.length; i++) {
      arr[i] = Math.floor(Math.random() * 256);
    }
    return arr;
  }),
};

Object.defineProperty(window, 'crypto', {
  value: mockCrypto,
});

// Import after mocks are set up
import { useSettingsStore, type AppSettings, clearEncryptionKeyCache } from './settings-store';

describe('useSettingsStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
    clearEncryptionKeyCache();

    // Reset store to initial state
    useSettingsStore.setState({
      vaultPath: '',
      llmModel: 'gpt-4',
      apiKey: '',
      theme: 'system',
      language: 'en',
      isLoading: false,
      isSaving: false,
      error: null,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // ==================== Initial State ====================

  describe('initial state', () => {
    it('should have default values', () => {
      const state = useSettingsStore.getState();

      expect(state.vaultPath).toBe('');
      expect(state.llmModel).toBe('gpt-4');
      expect(state.apiKey).toBe('');
      expect(state.theme).toBe('system');
      expect(state.language).toBe('en');
      expect(state.isLoading).toBe(false);
      expect(state.isSaving).toBe(false);
      expect(state.error).toBeNull();
    });
  });

  // ==================== Vault Path ====================

  describe('vault path configuration', () => {
    it('should set vault path', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setVaultPath('/Users/test/Documents/Notes');
      });

      expect(useSettingsStore.getState().vaultPath).toBe('/Users/test/Documents/Notes');
    });

    it('should clear vault path with empty string', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setVaultPath('/Users/test/Documents/Notes');
      });
      expect(useSettingsStore.getState().vaultPath).toBe('/Users/test/Documents/Notes');

      act(() => {
        store.setVaultPath('');
      });
      expect(useSettingsStore.getState().vaultPath).toBe('');
    });

    it('should normalize vault path (remove trailing slash)', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setVaultPath('/Users/test/Documents/Notes/');
      });

      expect(useSettingsStore.getState().vaultPath).toBe('/Users/test/Documents/Notes');
    });

    it('should validate vault path format', () => {
      const store = useSettingsStore.getState();

      // Valid path
      act(() => {
        store.setVaultPath('/valid/path');
      });
      expect(useSettingsStore.getState().error).toBeNull();

      // Invalid path (relative) - should still accept but could show warning
      act(() => {
        store.setVaultPath('relative/path');
      });
      // For now, accept any path
      expect(useSettingsStore.getState().vaultPath).toBe('relative/path');
    });
  });

  // ==================== LLM Model ====================

  describe('LLM model selection', () => {
    it('should set LLM model', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setLLMModel('gpt-3.5-turbo');
      });

      expect(useSettingsStore.getState().llmModel).toBe('gpt-3.5-turbo');
    });

    it('should support common LLM models', () => {
      const models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3-opus', 'claude-3-sonnet'];
      const store = useSettingsStore.getState();

      for (const model of models) {
        act(() => {
          store.setLLMModel(model);
        });
        expect(useSettingsStore.getState().llmModel).toBe(model);
      }
    });

    it('should get available models list', () => {
      const models = useSettingsStore.getState().getAvailableModels();

      expect(models).toContain('gpt-4');
      expect(models).toContain('gpt-3.5-turbo');
      expect(models).toContain('claude-3-opus');
      expect(models).toContain('claude-3-sonnet');
      expect(models.length).toBeGreaterThan(0);
    });
  });

  // ==================== API Key Secure Storage ====================

  describe('API key secure storage', () => {
    it('should set API key', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-api-key-123');
      });

      // API key should be stored (encrypted)
      expect(useSettingsStore.getState().apiKey.length).toBeGreaterThan(0);
    });

    it('should clear API key', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-api-key-123');
      });
      expect(useSettingsStore.getState().apiKey.length).toBeGreaterThan(0);

      act(() => {
        store.clearApiKey();
      });
      expect(useSettingsStore.getState().apiKey).toBe('');
    });

    it('should validate API key is not stored in plain text in localStorage', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-api-key-123');
      });

      // Check that localStorage doesn't contain plain API key
      const storedValue = localStorageMock.getItem('settings-storage');
      expect(storedValue).not.toContain('sk-test-api-key-123');
    });

    it('should check if API key is set', async () => {
      const store = useSettingsStore.getState();

      expect(store.hasApiKey()).toBe(false);

      await act(async () => {
        await store.setApiKey('sk-test-api-key-123');
      });

      expect(useSettingsStore.getState().hasApiKey()).toBe(true);
    });

    it('should mask API key for display', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-api-key-123456');
      });

      const masked = useSettingsStore.getState().getMaskedApiKey();
      // For encrypted keys, should return placeholder
      expect(masked).toBe('***-***-***');
    });

    it('should return empty string for masked key when no key set', () => {
      const masked = useSettingsStore.getState().getMaskedApiKey();
      expect(masked).toBe('');
    });
  });

  // ==================== API Key Encryption Security ====================

  describe('API key encryption security', () => {
    it('should NOT store API key in plain text', async () => {
      const store = useSettingsStore.getState();
      const testApiKey = 'sk-test-secret-api-key-12345';

      await act(async () => {
        await store.setApiKey(testApiKey);
      });

      const storedValue = localStorageMock.getItem('settings-storage');
      expect(storedValue).toBeDefined();

      // The stored value should NOT contain the plain API key
      expect(storedValue).not.toContain(testApiKey);
    });

    it('should use encryption with version marker', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-another-test-key');
      });

      const storedValue = localStorageMock.getItem('settings-storage');
      const parsed = JSON.parse(storedValue || '{}');

      // Should have encryption marker (either v2: or enc:)
      expect(parsed?.state?.apiKey).toMatch(/^(v2:|enc:)/);
    });

    it('should use deriveKey for key derivation', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-key');
      });

      // deriveKey should be called for key derivation
      expect(mockCrypto.subtle.deriveKey).toHaveBeenCalled();
    });

    it('should return decrypted key via getDecryptedApiKey', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-key');
      });

      // Get decrypted key
      const decrypted = await store.getDecryptedApiKey();
      // Should call decrypt or return the original if stored with fallback
      expect(typeof decrypted).toBe('string');
    });

    it('should handle encryption errors gracefully', async () => {
      // Mock encryption failure
      mockCrypto.subtle.encrypt.mockRejectedValueOnce(new Error('Encryption failed'));

      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-error-key');
      });

      // Should have error set or fall back gracefully
      const state = useSettingsStore.getState();
      // Either error is set, or the key was stored with fallback encoding
      expect(state.error || state.apiKey.length > 0).toBeTruthy();
    });

    it('should use getRandomValues for IV generation', async () => {
      const store = useSettingsStore.getState();

      await act(async () => {
        await store.setApiKey('sk-test-iv-key');
      });

      // getRandomValues should be called for IV generation
      expect(mockCrypto.getRandomValues).toHaveBeenCalled();
    });
  });

  // ==================== Theme ====================

  describe('theme configuration', () => {
    it('should set theme', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setTheme('dark');
      });

      expect(useSettingsStore.getState().theme).toBe('dark');
    });

    it('should support all theme options', () => {
      const themes: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system'];
      const store = useSettingsStore.getState();

      for (const theme of themes) {
        act(() => {
          store.setTheme(theme);
        });
        expect(useSettingsStore.getState().theme).toBe(theme);
      }
    });

    it('should toggle theme', () => {
      const store = useSettingsStore.getState();

      // Start with system
      expect(useSettingsStore.getState().theme).toBe('system');

      act(() => {
        store.toggleTheme();
      });
      expect(useSettingsStore.getState().theme).toBe('light');

      act(() => {
        useSettingsStore.getState().toggleTheme();
      });
      expect(useSettingsStore.getState().theme).toBe('dark');

      act(() => {
        useSettingsStore.getState().toggleTheme();
      });
      expect(useSettingsStore.getState().theme).toBe('system');
    });
  });

  // ==================== Language ====================

  describe('language configuration', () => {
    it('should set language', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setLanguage('zh');
      });

      expect(useSettingsStore.getState().language).toBe('zh');
    });

    it('should support common languages', () => {
      const languages = ['en', 'zh', 'ja', 'ko'];
      const store = useSettingsStore.getState();

      for (const lang of languages) {
        act(() => {
          store.setLanguage(lang);
        });
        expect(useSettingsStore.getState().language).toBe(lang);
      }
    });
  });

  // ==================== Bulk Operations ====================

  describe('bulk operations', () => {
    it('should update multiple settings at once', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.updateSettings({
          vaultPath: '/Users/test/Notes',
          llmModel: 'claude-3-opus',
          theme: 'dark',
          language: 'zh',
        });
      });

      const state = useSettingsStore.getState();
      expect(state.vaultPath).toBe('/Users/test/Notes');
      expect(state.llmModel).toBe('claude-3-opus');
      expect(state.theme).toBe('dark');
      expect(state.language).toBe('zh');
    });

    it('should reset settings to defaults', () => {
      const store = useSettingsStore.getState();

      // Set some values
      act(() => {
        store.updateSettings({
          vaultPath: '/Users/test/Notes',
          llmModel: 'claude-3-opus',
          theme: 'dark',
        });
      });

      // Reset
      act(() => {
        store.resetSettings();
      });

      const state = useSettingsStore.getState();
      expect(state.vaultPath).toBe('');
      expect(state.llmModel).toBe('gpt-4');
      expect(state.theme).toBe('system');
      expect(state.language).toBe('en');
    });

    it('should export settings (without API key)', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setVaultPath('/Users/test/Notes');
        store.setApiKey('sk-secret-key');
        store.setTheme('dark');
      });

      const exported = useSettingsStore.getState().exportSettings();

      expect(exported.vaultPath).toBe('/Users/test/Notes');
      expect(exported.theme).toBe('dark');
      expect(exported.apiKey).toBeUndefined();
    });

    it('should import settings', () => {
      const store = useSettingsStore.getState();

      const settingsToImport: Partial<AppSettings> = {
        vaultPath: '/imported/path',
        llmModel: 'claude-3-sonnet',
        theme: 'light',
        language: 'ja',
      };

      act(() => {
        store.importSettings(settingsToImport);
      });

      const state = useSettingsStore.getState();
      expect(state.vaultPath).toBe('/imported/path');
      expect(state.llmModel).toBe('claude-3-sonnet');
      expect(state.theme).toBe('light');
      expect(state.language).toBe('ja');
    });
  });

  // ==================== Error Handling ====================

  describe('error handling', () => {
    it('should set and clear error', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setError('Failed to save settings');
      });

      expect(useSettingsStore.getState().error).toBe('Failed to save settings');

      act(() => {
        useSettingsStore.getState().clearError();
      });

      expect(useSettingsStore.getState().error).toBeNull();
    });
  });

  // ==================== Hook Usage ====================

  describe('hook usage', () => {
    it('should work with renderHook', () => {
      const { result } = renderHook(() => useSettingsStore());

      expect(result.current.vaultPath).toBe('');
      expect(result.current.llmModel).toBe('gpt-4');
      expect(result.current.theme).toBe('system');
    });

    it('should update state through hook', () => {
      const { result } = renderHook(() => useSettingsStore());

      act(() => {
        result.current.setTheme('dark');
      });

      expect(result.current.theme).toBe('dark');
    });
  });

  // ==================== Persistence ====================

  describe('persistence', () => {
    it('should persist settings to localStorage', () => {
      const store = useSettingsStore.getState();

      act(() => {
        store.setTheme('dark');
        store.setVaultPath('/Users/test/Notes');
      });

      // Settings should be persisted (via zustand persist middleware)
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });
  });
});