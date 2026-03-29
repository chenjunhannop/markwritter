/**
 * Tests for Settings Panel Components
 *
 * TDD approach: Tests for settings panel components before implementation.
 *
 * Tests cover:
 * - SettingsPanel: Main settings container
 * - VaultConfig: Vault path configuration
 * - LLMConfig: LLM model and API key configuration
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  SettingsPanel,
  VaultConfig,
  LLMConfig,
  GeneralConfig,
} from './settings-panel';

// Mock the settings store
const mockStore = {
  vaultPath: '',
  llmModel: 'gpt-4',
  apiKey: '',
  theme: 'system',
  language: 'en',
  isLoading: false,
  isSaving: false,
  error: null,
  setVaultPath: vi.fn(),
  setLLMModel: vi.fn(),
  setApiKey: vi.fn(),
  clearApiKey: vi.fn(),
  hasApiKey: vi.fn(() => false),
  getMaskedApiKey: vi.fn(() => ''),
  setTheme: vi.fn(),
  toggleTheme: vi.fn(),
  setLanguage: vi.fn(),
  updateSettings: vi.fn(),
  resetSettings: vi.fn(),
  exportSettings: vi.fn(() => ({
    vaultPath: '',
    llmModel: 'gpt-4',
    theme: 'system',
    language: 'en',
  })),
  importSettings: vi.fn(),
  setError: vi.fn(),
  clearError: vi.fn(),
  fetchSettings: vi.fn(),
  syncSettings: vi.fn(),
  getAvailableModels: vi.fn(() => [
    'gpt-4',
    'gpt-3.5-turbo',
    'claude-3-opus',
    'claude-3-sonnet',
  ]),
};

vi.mock('@/lib/settings-store', () => ({
  useSettingsStore: vi.fn((selector) => {
    if (typeof selector === 'function') {
      return selector(mockStore);
    }
    return mockStore;
  }),
}));

// Mock window.showDirectoryPicker for file system access
const mockShowDirectoryPicker = vi.fn();
Object.defineProperty(window, 'showDirectoryPicker', {
  value: mockShowDirectoryPicker,
  writable: true,
});

// Mock pointer capture for Radix UI
Element.prototype.hasPointerCapture = vi.fn(() => false);
Element.prototype.setPointerCapture = vi.fn();
Element.prototype.releasePointerCapture = vi.fn();

// Mock scrollIntoView for Radix UI
Element.prototype.scrollIntoView = vi.fn();

// Import after mocks
import { useSettingsStore } from '@/lib/settings-store';

describe('SettingsPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.vaultPath = '';
    mockStore.llmModel = 'gpt-4';
    mockStore.apiKey = '';
    mockStore.theme = 'system';
    mockStore.language = 'en';
    mockStore.error = null;
  });

  describe('rendering', () => {
    it('should render settings panel with title', () => {
      render(<SettingsPanel />);

      expect(screen.getByRole('heading', { name: 'Settings' })).toBeInTheDocument();
    });

    it('should render all settings sections', () => {
      render(<SettingsPanel />);

      // Use more specific queries to avoid multiple matches
      expect(screen.getByText('Vault Path')).toBeInTheDocument();
      expect(screen.getByLabelText(/model/i)).toBeInTheDocument();
      expect(screen.getByText('General Settings')).toBeInTheDocument();
    });

    it('should display error message when present', () => {
      mockStore.error = 'Failed to save settings';
      render(<SettingsPanel />);

      expect(screen.getByText('Failed to save settings')).toBeInTheDocument();
    });
  });
});

describe('VaultConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.vaultPath = '';
  });

  describe('rendering', () => {
    it('should render vault configuration section', () => {
      render(<VaultConfig />);

      expect(screen.getByText('Vault Path')).toBeInTheDocument();
    });

    it('should display current vault path', () => {
      mockStore.vaultPath = '/Users/test/Notes';
      render(<VaultConfig />);

      expect(screen.getByDisplayValue('/Users/test/Notes')).toBeInTheDocument();
    });

    it('should show placeholder when no vault path set', () => {
      render(<VaultConfig />);

      expect(
        screen.getByPlaceholderText(/select a vault directory/i)
      ).toBeInTheDocument();
    });
  });

  describe('directory picker', () => {
    it('should have a button to select vault directory', () => {
      render(<VaultConfig />);

      expect(
        screen.getByRole('button', { name: /browse/i })
      ).toBeInTheDocument();
    });

    it('should call showDirectoryPicker when browse button clicked', async () => {
      const user = userEvent.setup();
      mockShowDirectoryPicker.mockResolvedValue({
        name: 'Notes',
        path: '/Users/test/Notes',
      });

      render(<VaultConfig />);

      const browseButton = screen.getByRole('button', { name: /browse/i });
      await user.click(browseButton);

      expect(mockShowDirectoryPicker).toHaveBeenCalled();
    });

    it('should update vault path after selection', async () => {
      const user = userEvent.setup();
      mockShowDirectoryPicker.mockResolvedValue({
        name: 'Notes',
        path: '/Users/test/Notes',
      });

      render(<VaultConfig />);

      const browseButton = screen.getByRole('button', { name: /browse/i });
      await user.click(browseButton);

      await waitFor(() => {
        expect(mockStore.setVaultPath).toHaveBeenCalled();
      });
    });

    it('should handle directory picker cancellation', async () => {
      const user = userEvent.setup();
      mockShowDirectoryPicker.mockRejectedValue(new Error('User cancelled'));

      render(<VaultConfig />);

      const browseButton = screen.getByRole('button', { name: /browse/i });
      await user.click(browseButton);

      // Should not throw error
      expect(mockStore.setVaultPath).not.toHaveBeenCalled();
    });
  });

  describe('manual path input', () => {
    it('should allow manual path input', async () => {
      const user = userEvent.setup();
      render(<VaultConfig />);

      const input = screen.getByRole('textbox');
      await user.type(input, '/custom/path');

      expect(mockStore.setVaultPath).toHaveBeenCalled();
    });
  });
});

describe('LLMConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.llmModel = 'gpt-4';
    mockStore.apiKey = '';
  });

  describe('model selection', () => {
    it('should render model selection dropdown', () => {
      render(<LLMConfig />);

      expect(screen.getByLabelText(/model/i)).toBeInTheDocument();
    });

    it('should display current model', () => {
      mockStore.llmModel = 'claude-3-opus';
      render(<LLMConfig />);

      // Check that the model is displayed in the select trigger
      expect(screen.getByText('claude-3-opus')).toBeInTheDocument();
    });

    it('should show available models when dropdown is opened', async () => {
      const user = userEvent.setup();
      render(<LLMConfig />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      // Wait for dropdown to open and check for model options
      await waitFor(() => {
        expect(screen.getByRole('option', { name: /gpt-4/ })).toBeInTheDocument();
      });
    });

    it('should update model on selection', async () => {
      const user = userEvent.setup();
      render(<LLMConfig />);

      const trigger = screen.getByRole('combobox');
      await user.click(trigger);

      await waitFor(async () => {
        const option = screen.getByRole('option', { name: /claude-3-opus/ });
        await user.click(option);
      });

      expect(mockStore.setLLMModel).toHaveBeenCalledWith('claude-3-opus');
    });
  });

  describe('API key input', () => {
    it('should render API key input field', () => {
      render(<LLMConfig />);

      // Use more specific selector
      const input = document.getElementById('api-key');
      expect(input).toBeInTheDocument();
    });

    it('should use password input type for security', () => {
      render(<LLMConfig />);

      const input = document.getElementById('api-key') as HTMLInputElement;
      expect(input.type).toBe('password');
    });

    it('should show masked key when key is set', () => {
      mockStore.apiKey = 'sk-test-api-key-123';
      mockStore.hasApiKey = () => true;
      mockStore.getMaskedApiKey = () => 'sk-...123';

      render(<LLMConfig />);

      expect(screen.getByText(/sk-\.\.\.123/)).toBeInTheDocument();
    });

    it('should update API key on input', async () => {
      const user = userEvent.setup();
      render(<LLMConfig />);

      const input = document.getElementById('api-key') as HTMLInputElement;
      await user.type(input, 's');

      expect(mockStore.setApiKey).toHaveBeenCalled();
    });

    it('should have a clear button for API key when set', () => {
      mockStore.apiKey = 'sk-test-key';
      mockStore.hasApiKey = () => true;

      render(<LLMConfig />);

      expect(
        screen.getByRole('button', { name: /clear api key/i })
      ).toBeInTheDocument();
    });

    it('should clear API key when clear button clicked', async () => {
      const user = userEvent.setup();
      mockStore.apiKey = 'sk-test-key';
      mockStore.hasApiKey = () => true;

      render(<LLMConfig />);

      const clearButton = screen.getByRole('button', { name: /clear api key/i });
      await user.click(clearButton);

      expect(mockStore.clearApiKey).toHaveBeenCalled();
    });

    it('should toggle API key visibility', async () => {
      const user = userEvent.setup();
      mockStore.apiKey = 'sk-test-key';

      render(<LLMConfig />);

      const toggleButton = screen.getByRole('button', { name: /show api key/i });
      const input = document.getElementById('api-key') as HTMLInputElement;

      // Initially hidden
      expect(input.type).toBe('password');

      // Click to show
      await user.click(toggleButton);
      expect(input.type).toBe('text');
    });
  });
});

describe('GeneralConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockStore.theme = 'system';
    mockStore.language = 'en';
  });

  describe('theme selection', () => {
    it('should render theme selection', () => {
      render(<GeneralConfig />);

      expect(screen.getByText('Theme')).toBeInTheDocument();
    });

    it('should show theme options', () => {
      render(<GeneralConfig />);

      expect(screen.getByRole('button', { name: 'Light' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Dark' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'System' })).toBeInTheDocument();
    });

    it('should highlight current theme', () => {
      mockStore.theme = 'dark';
      render(<GeneralConfig />);

      // The dark option should be selected/active
      const darkOption = screen.getByRole('button', { name: 'Dark' });
      expect(darkOption).toHaveAttribute('aria-pressed', 'true');
    });

    it('should update theme on selection', async () => {
      const user = userEvent.setup();
      render(<GeneralConfig />);

      const lightOption = screen.getByRole('button', { name: 'Light' });
      await user.click(lightOption);

      expect(mockStore.setTheme).toHaveBeenCalledWith('light');
    });
  });

  describe('language selection', () => {
    it('should render language selection', () => {
      render(<GeneralConfig />);

      expect(screen.getByText('Language')).toBeInTheDocument();
    });

    it('should show language dropdown', () => {
      render(<GeneralConfig />);

      const select = screen.getByRole('combobox', { name: /language/i });
      expect(select).toBeInTheDocument();
    });

    it('should update language on selection', async () => {
      const user = userEvent.setup();
      render(<GeneralConfig />);

      const trigger = screen.getByRole('combobox', { name: /language/i });
      await user.click(trigger);

      await waitFor(async () => {
        const option = screen.getByRole('option', { name: /chinese/i });
        await user.click(option);
      });

      expect(mockStore.setLanguage).toHaveBeenCalledWith('zh');
    });
  });

  describe('reset button', () => {
    it('should have a reset to defaults button', () => {
      render(<GeneralConfig />);

      expect(
        screen.getByRole('button', { name: /reset to defaults/i })
      ).toBeInTheDocument();
    });

    it('should show confirmation dialog before reset', async () => {
      const user = userEvent.setup();
      render(<GeneralConfig />);

      const resetButton = screen.getByRole('button', { name: /reset to defaults/i });
      await user.click(resetButton);

      // Should show confirmation dialog
      expect(screen.getByText(/reset settings/i)).toBeInTheDocument();
    });

    it('should reset settings on confirmation', async () => {
      const user = userEvent.setup();
      render(<GeneralConfig />);

      const resetButton = screen.getByRole('button', { name: /reset to defaults/i });
      await user.click(resetButton);

      const confirmButton = screen.getByRole('button', { name: /^reset$/i });
      await user.click(confirmButton);

      expect(mockStore.resetSettings).toHaveBeenCalled();
    });
  });
});