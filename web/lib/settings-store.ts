/**
 * Settings Store for Markwritter
 *
 * Zustand store for managing application settings including:
 * - Vault path configuration
 * - LLM model selection
 * - API key secure storage
 * - Theme and language preferences
 *
 * Uses zustand persist middleware for localStorage persistence.
 * API keys are encrypted before storage for security.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// ==================== Types ====================

export type Theme = 'light' | 'dark' | 'system';
export type LLMModel = string;

export interface AppSettings {
  vaultPath: string;
  llmModel: LLMModel;
  apiKey: string;
  theme: Theme;
  language: string;
}

interface SettingsState extends AppSettings {
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
}

interface SettingsActions {
  // Vault path
  setVaultPath: (path: string) => void;

  // LLM model
  setLLMModel: (model: LLMModel) => void;
  getAvailableModels: () => string[];

  // API key (async for encryption)
  setApiKey: (key: string) => Promise<void>;
  clearApiKey: () => void;
  hasApiKey: () => boolean;
  getMaskedApiKey: () => string;
  getDecryptedApiKey: () => Promise<string>;

  // Theme
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;

  // Language
  setLanguage: (language: string) => void;

  // Bulk operations
  updateSettings: (settings: Partial<AppSettings>) => void;
  resetSettings: () => void;
  exportSettings: () => Omit<AppSettings, 'apiKey'>;
  importSettings: (settings: Partial<AppSettings>) => void;

  // Error handling
  setError: (error: string | null) => void;
  clearError: () => void;
}

export type SettingsStore = SettingsState & SettingsActions;

// ==================== Constants ====================

const AVAILABLE_MODELS: string[] = [
  'gpt-4',
  'gpt-4-turbo',
  'gpt-3.5-turbo',
  'claude-3-opus',
  'claude-3-sonnet',
  'claude-3-haiku',
];

const DEFAULT_SETTINGS: AppSettings = {
  vaultPath: '',
  llmModel: 'gpt-4',
  apiKey: '',
  theme: 'system',
  language: 'en',
};

// ==================== Helper Functions ====================

/**
 * Normalize path by removing trailing slashes
 */
function normalizePath(path: string): string {
  if (!path) return '';
  return path.replace(/\/+$/, '');
}

/**
 * Mask API key for display
 * Shows first 3 characters and last 3 characters
 */
function maskApiKey(key: string): string {
  if (!key || key.length < 8) return '';
  return `${key.substring(0, 3)}...${key.substring(key.length - 3)}`;
}

// ==================== Secure Encryption (Web Crypto API) ====================

const ENCRYPTION_KEY_NAME = 'markwritter-encryption-key';
const ENCRYPTION_ALGORITHM = 'AES-GCM';
const KEY_LENGTH = 256;

interface EncryptedData {
  v: 2; // Version for future compatibility
  iv: string; // Base64 encoded IV
  data: string; // Base64 encoded encrypted data
}

// Cache for the encryption key to avoid re-deriving on every operation
let cachedEncryptionKey: CryptoKey | null = null;
let keyDerivationPromise: Promise<CryptoKey | null> | null = null;

/**
 * Clear the cached encryption key (for testing)
 */
export function clearEncryptionKeyCache(): void {
  cachedEncryptionKey = null;
  keyDerivationPromise = null;
}

/**
 * Get or generate the encryption key (cached)
 */
async function getEncryptionKey(): Promise<CryptoKey | null> {
  // Return cached key if available
  if (cachedEncryptionKey) {
    return cachedEncryptionKey;
  }

  // If already deriving, wait for it
  if (keyDerivationPromise) {
    return keyDerivationPromise;
  }

  keyDerivationPromise = (async () => {
    try {
      // Try to get existing key material from localStorage
      let keyMaterial = localStorage.getItem(ENCRYPTION_KEY_NAME);

      if (!keyMaterial) {
        // Generate new key material
        const randomBytes = new Uint8Array(32);
        crypto.getRandomValues(randomBytes);
        keyMaterial = Array.from(randomBytes, (b) => b.toString(16).padStart(2, '0')).join('');
        localStorage.setItem(ENCRYPTION_KEY_NAME, keyMaterial);
      }

      // Convert key material to CryptoKey
      const encoder = new TextEncoder();
      const keyData = encoder.encode(keyMaterial);

      const baseKey = await crypto.subtle.importKey('RAW', keyData, 'PBKDF2', false, [
        'deriveBits',
        'deriveKey',
      ]);

      // Derive actual encryption key using PBKDF2
      const salt = encoder.encode('markwritter-salt');
      const derivedKey = await crypto.subtle.deriveKey(
        {
          name: 'PBKDF2',
          salt: salt,
          iterations: 100000,
          hash: 'SHA-256',
        },
        baseKey,
        { name: ENCRYPTION_ALGORITHM, length: KEY_LENGTH },
        false,
        ['encrypt', 'decrypt']
      );

      cachedEncryptionKey = derivedKey;
      return derivedKey;
    } catch (error) {
      console.error('Failed to get encryption key:', error);
      return null;
    } finally {
      keyDerivationPromise = null;
    }
  })();

  return keyDerivationPromise;
}

/**
 * Encrypt API key using Web Crypto API (AES-GCM)
 * Returns a string prefixed with 'v2:' for version identification
 */
async function encryptApiKey(key: string): Promise<string> {
  if (!key) return '';

  try {
    const encryptionKey = await getEncryptionKey();
    if (!encryptionKey) {
      // Fallback to base64 if Web Crypto is not available
      console.warn('Web Crypto API not available, using fallback encoding');
      return `enc:${btoa(key)}`;
    }

    const encoder = new TextEncoder();
    const data = encoder.encode(key);

    // Generate random IV
    const iv = crypto.getRandomValues(new Uint8Array(12));

    // Encrypt
    const encrypted = await crypto.subtle.encrypt(
      {
        name: ENCRYPTION_ALGORITHM,
        iv: iv,
      },
      encryptionKey,
      data
    );

    // Create encrypted data object
    const encryptedData: EncryptedData = {
      v: 2,
      iv: Array.from(iv, (b) => b.toString(16).padStart(2, '0')).join(''),
      data: Array.from(new Uint8Array(encrypted), (b) => b.toString(16).padStart(2, '0')).join(''),
    };

    return `v2:${btoa(JSON.stringify(encryptedData))}`;
  } catch (error) {
    console.error('Encryption failed:', error);
    // Fallback to base64
    return `enc:${btoa(key)}`;
  }
}

/**
 * Decrypt API key using Web Crypto API (AES-GCM)
 */
async function decryptApiKey(encrypted: string): Promise<string> {
  if (!encrypted) return '';

  // Handle old base64 format for backwards compatibility
  if (encrypted.startsWith('enc:')) {
    try {
      return atob(encrypted.substring(4));
    } catch {
      return '';
    }
  }

  // Handle new encrypted format
  if (encrypted.startsWith('v2:')) {
    try {
      const encryptionKey = await getEncryptionKey();
      if (!encryptionKey) {
        console.warn('Web Crypto API not available for decryption');
        return '';
      }

      const encryptedData: EncryptedData = JSON.parse(atob(encrypted.substring(3)));

      // Convert hex strings back to Uint8Array
      const iv = new Uint8Array(
        encryptedData.iv.match(/.{1,2}/g)?.map((byte) => parseInt(byte, 16)) || []
      );
      const data = new Uint8Array(
        encryptedData.data.match(/.{1,2}/g)?.map((byte) => parseInt(byte, 16)) || []
      );

      // Decrypt
      const decrypted = await crypto.subtle.decrypt(
        {
          name: ENCRYPTION_ALGORITHM,
          iv: iv,
        },
        encryptionKey,
        data
      );

      const decoder = new TextDecoder();
      return decoder.decode(decrypted);
    } catch (error) {
      console.error('Decryption failed:', error);
      return '';
    }
  }

  // Unknown format, return as-is (should not happen)
  return encrypted;
}

// ==================== Sync wrappers for storage ====================

/**
 * Synchronous wrapper for encryption (for zustand persist compatibility)
 * Uses cached key and falls back to base64 if key not available
 */
function encryptApiKeySync(key: string): string {
  if (!key) return '';

  // If we have a cached key, we can try to encrypt synchronously
  // But Web Crypto is async, so we need a different approach
  // For now, use a marker and encrypt async later
  // This is a known limitation - we'll handle it via the action layer

  // Store with pending marker - will be encrypted on next read
  return `pending:${btoa(key)}`;
}

/**
 * Process pending encryptions asynchronously
 */
async function processPendingEncryption(key: string): Promise<string> {
  if (key.startsWith('pending:')) {
    const decoded = atob(key.substring(8));
    return encryptApiKey(decoded);
  }
  return key;
}

/**
 * Initialize encryption key on module load
 */
async function initializeEncryption(): Promise<void> {
  await getEncryptionKey();
}

// Initialize encryption key when module loads
if (typeof window !== 'undefined') {
  initializeEncryption().catch(console.error);
}

// ==================== Store Implementation ====================

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set, get) => ({
      // Initial state
      ...DEFAULT_SETTINGS,
      isLoading: false,
      isSaving: false,
      error: null,

      // Vault path
      setVaultPath: (path) => {
        set({ vaultPath: normalizePath(path), error: null });
      },

      // LLM model
      setLLMModel: (model) => {
        set({ llmModel: model, error: null });
      },

      getAvailableModels: () => {
        return [...AVAILABLE_MODELS];
      },

      // API key - encrypts before storing
      setApiKey: async (key) => {
        if (!key) {
          set({ apiKey: '', error: null });
          return;
        }

        // Store encrypted version directly
        try {
          const encrypted = await encryptApiKey(key);
          // Store the encrypted value directly - storage won't re-encrypt
          set({ apiKey: encrypted, error: null });
        } catch (error) {
          console.error('Failed to encrypt API key:', error);
          set({ error: 'Failed to secure API key' });
        }
      },

      clearApiKey: () => {
        set({ apiKey: '' });
      },

      hasApiKey: () => {
        const state = get();
        // Check if there's any stored value (encrypted or not)
        return state.apiKey.length > 0;
      },

      getMaskedApiKey: () => {
        const state = get();
        // If the key is encrypted, we need to decrypt it first for display
        const storedKey = state.apiKey;
        if (!storedKey) return '';

        // For encrypted keys, we can't show the real value
        // Just return a placeholder indicating it's set
        if (storedKey.startsWith('v2:') || storedKey.startsWith('enc:')) {
          return '***-***-***';
        }
        return maskApiKey(storedKey);
      },

      // Get decrypted API key (for internal use)
      getDecryptedApiKey: async () => {
        const state = get();
        const storedKey = state.apiKey;
        if (!storedKey) return '';

        if (storedKey.startsWith('v2:') || storedKey.startsWith('enc:')) {
          return decryptApiKey(storedKey);
        }
        return storedKey;
      },

      // Theme
      setTheme: (theme) => {
        set({ theme, error: null });
      },

      toggleTheme: () => {
        const themes: Theme[] = ['system', 'light', 'dark'];
        const currentTheme = get().theme;
        const currentIndex = themes.indexOf(currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        set({ theme: themes[nextIndex] });
      },

      // Language
      setLanguage: (language) => {
        set({ language, error: null });
      },

      // Bulk operations
      updateSettings: (settings) => {
        const updates: Partial<AppSettings> = {};

        if (settings.vaultPath !== undefined) {
          updates.vaultPath = normalizePath(settings.vaultPath);
        }
        if (settings.llmModel !== undefined) {
          updates.llmModel = settings.llmModel;
        }
        // Note: apiKey should be set via setApiKey for proper encryption
        if (settings.apiKey !== undefined) {
          console.warn('Use setApiKey for proper encryption');
        }
        if (settings.theme !== undefined) {
          updates.theme = settings.theme;
        }
        if (settings.language !== undefined) {
          updates.language = settings.language;
        }

        set({ ...updates, error: null });
      },

      resetSettings: () => {
        set({ ...DEFAULT_SETTINGS, error: null });
      },

      exportSettings: () => {
        const state = get();
        return {
          vaultPath: state.vaultPath,
          llmModel: state.llmModel,
          theme: state.theme,
          language: state.language,
        };
      },

      importSettings: (settings) => {
        get().updateSettings(settings);
      },

      // Error handling
      setError: (error) => {
        set({ error });
      },

      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'settings-storage',
      // Standard storage - encryption is handled in setApiKey action
      storage: {
        getItem: (name) => {
          const str = localStorage.getItem(name);
          if (!str) return null;
          return JSON.parse(str);
        },
        setItem: (name, value) => {
          localStorage.setItem(name, JSON.stringify(value));
        },
        removeItem: (name) => localStorage.removeItem(name),
      },
    }
  )
);

// ==================== Selector Hooks ====================

/**
 * Selector hook for checking if vault is configured
 */
export function useHasVaultConfigured(): boolean {
  return useSettingsStore((state) => state.vaultPath.length > 0);
}

/**
 * Selector hook for checking if API key is set
 */
export function useHasApiKeySet(): boolean {
  return useSettingsStore((state) => state.apiKey.length > 0);
}

/**
 * Selector hook for getting current theme
 */
export function useCurrentTheme(): Theme {
  return useSettingsStore((state) => state.theme);
}

/**
 * Selector hook for getting available models
 */
export function useAvailableModels(): string[] {
  return useSettingsStore((state) => state.getAvailableModels());
}