/**
 * Record Store for Markwritter
 *
 * Zustand store for managing record state including:
 * - Current record being edited
 * - Content, title, tags, aliases
 * - AI assistance state (streaming)
 * - Classification suggestions
 */

import { create } from 'zustand';
import {
  createRecord,
  updateRecord,
  aiContinueStream,
  aiRewrite,
  aiPolish,
  classifyNote,
  suggestTags,
  suggestFolder,
  type RecordResponse,
  type ClassifyResponse,
  type FolderSuggestionResponse,
} from './record-api';
import { processSSEStream } from './sse';

// ==================== Types ====================

interface RecordState {
  // Current record data
  currentRecord: RecordResponse | null;
  content: string;
  title: string;
  tags: string[];
  aliases: string[];
  folderId: string | null;

  // Save state
  isSaving: boolean;
  saveError: string | null;

  // AI streaming state
  isStreaming: boolean;
  streamError: string | null;
  abortController: AbortController | null;

  // Classification state
  isClassifying: boolean;
  classificationResult: ClassifyResponse | null;
  tagSuggestions: string[];
  folderSuggestion: FolderSuggestionResponse | null;

  // Content actions
  setContent: (content: string) => void;
  setTitle: (title: string) => void;
  setTags: (tags: string[]) => void;
  addTag: (tag: string) => void;
  removeTag: (tag: string) => void;
  setAliases: (aliases: string[]) => void;
  setFolderId: (folderId: string | null) => void;

  // Record actions
  setCurrentRecord: (record: RecordResponse | null) => void;
  saveRecord: () => Promise<void>;
  clearRecord: () => void;

  // AI assistance actions
  aiContinue: () => Promise<void>;
  aiRewrite: () => Promise<void>;
  aiPolish: () => Promise<void>;
  cancelStream: () => void;

  // Classification actions
  classify: () => Promise<void>;
  fetchTagSuggestions: () => Promise<void>;
  fetchFolderSuggestion: () => Promise<void>;
  setClassificationResult: (result: ClassifyResponse | null) => void;
  acceptSuggestedTags: () => void;
  acceptSuggestedFolder: () => void;

  // Internal actions
  setIsStreaming: (streaming: boolean) => void;
  setAbortController: (controller: AbortController | null) => void;
}

// ==================== Store ====================

export const useRecordStore = create<RecordState>()((set, get) => ({
  // Initial state
  currentRecord: null,
  content: '',
  title: '',
  tags: [],
  aliases: [],
  folderId: null,

  isSaving: false,
  saveError: null,

  isStreaming: false,
  streamError: null,
  abortController: null,

  isClassifying: false,
  classificationResult: null,
  tagSuggestions: [],
  folderSuggestion: null,

  // Content actions
  setContent: (content) => {
    set({
      content,
      // Clear classification when content changes
      classificationResult: null,
    });
  },

  setTitle: (title) => {
    set({ title });
  },

  setTags: (tags) => {
    set({ tags });
  },

  addTag: (tag) => {
    set((state) => {
      if (state.tags.includes(tag)) {
        return state;
      }
      return { tags: [...state.tags, tag] };
    });
  },

  removeTag: (tag) => {
    set((state) => ({
      tags: state.tags.filter((t) => t !== tag),
    }));
  },

  setAliases: (aliases) => {
    set({ aliases });
  },

  setFolderId: (folderId) => {
    set({ folderId });
  },

  // Record actions
  setCurrentRecord: (record) => {
    if (record) {
      set({
        currentRecord: record,
        content: record.content,
        title: record.title ?? '',
        tags: record.tags,
        aliases: record.aliases,
        folderId: record.folder_id,
      });
    } else {
      set({
        currentRecord: null,
        content: '',
        title: '',
        tags: [],
        aliases: [],
        folderId: null,
      });
    }
  },

  saveRecord: async () => {
    const state = get();

    set({ isSaving: true, saveError: null });

    try {
      if (state.currentRecord) {
        // Update existing record
        const updated = await updateRecord({
          id: state.currentRecord.id,
          title: state.title || null,
          content: state.content,
          tags: state.tags,
          aliases: state.aliases,
          folder_id: state.folderId,
        });

        set({
          currentRecord: updated,
          isSaving: false,
        });
      } else {
        // Create new record
        const created = await createRecord({
          content: state.content,
          title: state.title || null,
          tags: state.tags,
          aliases: state.aliases,
          folder_id: state.folderId,
        });

        set({
          currentRecord: created,
          isSaving: false,
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Save failed';
      set({
        saveError: message,
        isSaving: false,
      });
    }
  },

  clearRecord: () => {
    set({
      currentRecord: null,
      content: '',
      title: '',
      tags: [],
      aliases: [],
      folderId: null,
      saveError: null,
      streamError: null,
      classificationResult: null,
      tagSuggestions: [],
      folderSuggestion: null,
    });
  },

  // AI assistance actions
  aiContinue: async () => {
    const state = get();

    if (!state.currentRecord) {
      return;
    }

    // Cancel any existing stream
    const existingController = state.abortController;
    if (existingController) {
      existingController.abort();
    }

    const controller = new AbortController();

    set({
      isStreaming: true,
      streamError: null,
      abortController: controller,
    });

    try {
      const response = await aiContinueStream(
        state.currentRecord.id,
        state.content,
        controller.signal
      );

      await processSSEStream(
        response,
        (event) => {
          if (controller.signal.aborted) return;

          const currentState = get();

          // Handle AI stream events
          if (event.type === 'text_delta') {
            set({
              content: currentState.content + event.content,
            });
          } else if (event.type === 'error') {
            set({
              streamError: event.content,
              isStreaming: false,
            });
          } else if (event.type === 'done') {
            set({
              isStreaming: false,
            });
          }
        },
        controller.signal
      );
    } catch (error) {
      if (error instanceof Error && error.message === 'Aborted') {
        return;
      }

      const message = error instanceof Error ? error.message : 'Stream failed';
      set({
        streamError: message,
        isStreaming: false,
      });
    } finally {
      set({
        isStreaming: false,
        abortController: null,
      });
    }
  },

  aiRewrite: async () => {
    const state = get();

    if (!state.currentRecord) {
      return;
    }

    set({ isStreaming: true, streamError: null });

    try {
      const result = await aiRewrite(state.currentRecord.id, state.content);

      set({
        content: result.rewritten,
        isStreaming: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Rewrite failed';
      set({
        streamError: message,
        isStreaming: false,
      });
    }
  },

  aiPolish: async () => {
    const state = get();

    if (!state.currentRecord) {
      return;
    }

    set({ isStreaming: true, streamError: null });

    try {
      const result = await aiPolish(state.currentRecord.id, state.content);

      set({
        content: result.polished,
        isStreaming: false,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Polish failed';
      set({
        streamError: message,
        isStreaming: false,
      });
    }
  },

  cancelStream: () => {
    const controller = get().abortController;
    if (controller) {
      controller.abort();
    }

    set({
      isStreaming: false,
      abortController: null,
    });
  },

  // Classification actions
  classify: async () => {
    const state = get();

    if (!state.content.trim()) {
      return;
    }

    set({ isClassifying: true });

    try {
      const result = await classifyNote(state.content);

      set({
        classificationResult: result,
        isClassifying: false,
      });
    } catch {
      set({
        isClassifying: false,
      });
    }
  },

  fetchTagSuggestions: async () => {
    const state = get();

    if (!state.content.trim()) {
      return;
    }

    try {
      const result = await suggestTags(state.content);

      set({ tagSuggestions: result.tags });
    } catch {
      set({ tagSuggestions: [] });
    }
  },

  fetchFolderSuggestion: async () => {
    const state = get();

    if (!state.content.trim()) {
      return;
    }

    try {
      const result = await suggestFolder(state.content);

      set({ folderSuggestion: result });
    } catch {
      set({ folderSuggestion: null });
    }
  },

  setClassificationResult: (result) => {
    set({ classificationResult: result });
  },

  acceptSuggestedTags: () => {
    const state = get();
    if (state.classificationResult) {
      set({
        tags: [...new Set([...state.tags, ...state.classificationResult.suggested_tags])],
      });
    }
  },

  acceptSuggestedFolder: () => {
    const state = get();
    if (state.classificationResult?.suggested_folder) {
      set({
        folderId: state.classificationResult.suggested_folder,
      });
    }
  },

  // Internal actions
  setIsStreaming: (streaming) => {
    set({ isStreaming: streaming });
  },

  setAbortController: (controller) => {
    set({ abortController: controller });
  },
}));

// ==================== Selector Hooks ====================

/**
 * Selector hook for checking if there is an active record.
 */
export function useHasActiveRecord(): boolean {
  return useRecordStore((state) => state.currentRecord !== null);
}

/**
 * Selector hook for checking if AI is streaming.
 */
export function useIsAIStreaming(): boolean {
  return useRecordStore((state) => state.isStreaming);
}

/**
 * Selector hook for checking if there is content.
 */
export function useHasContent(): boolean {
  return useRecordStore((state) => state.content.length > 0);
}

/**
 * Selector hook for checking if there are unsaved changes.
 */
export function useHasUnsavedChanges(): boolean {
  return useRecordStore((state) => {
    if (!state.currentRecord) {
      return state.content.length > 0 || state.title.length > 0 || state.tags.length > 0;
    }

    return (
      state.content !== state.currentRecord.content ||
      state.title !== (state.currentRecord.title ?? '') ||
      JSON.stringify(state.tags) !== JSON.stringify(state.currentRecord.tags) ||
      state.folderId !== state.currentRecord.folder_id
    );
  });
}