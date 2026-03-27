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
  createNote,
  updateNote,
  getNote,
  deleteNote as deleteNoteApi,
  aiContinueStream,
  aiRewrite,
  aiPolish,
  classifyNote,
  suggestTags,
  suggestFolder,
  type NoteResponse,
  type ClassifyResponse,
  type FolderSuggestionResponse,
} from './record-api';
import { processSSEStream } from './sse';

// ==================== Helpers ====================

/**
 * Slugify a title into a safe file path.
 * Lowercase, replace spaces with dashes, remove special chars.
 */
function slugify(title: string): string {
  return title
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Build metadata object from store state for the Notes API.
 */
function buildMetadata(
  title: string,
  folderId: string | null,
  aliases: string[]
): Record<string, unknown> {
  const metadata: Record<string, unknown> = {};

  if (title) {
    metadata.title = title;
  }
  if (folderId) {
    metadata.folder = folderId;
  }
  if (aliases.length > 0) {
    metadata.aliases = aliases;
  }

  return metadata;
}

/**
 * Extract fields from NoteResponse metadata.
 */
function extractMetadataFields(
  metadata: Record<string, unknown>
): { folderId: string | null; aliases: string[] } {
  return {
    folderId: (metadata.folder as string) ?? null,
    aliases: Array.isArray(metadata.aliases)
      ? (metadata.aliases as string[])
      : [],
  };
}

// ==================== Types ====================

interface RecordState {
  // Current record data
  currentRecord: NoteResponse | null;
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
  setCurrentRecord: (record: NoteResponse | null) => void;
  saveRecord: () => Promise<void>;
  clearRecord: () => void;
  deleteRecord: () => Promise<void>;

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
      const { folderId, aliases } = extractMetadataFields(record.metadata);
      set({
        currentRecord: record,
        content: record.content,
        title: record.title ?? '',
        tags: record.tags,
        aliases,
        folderId,
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
      const metadata = buildMetadata(state.title, state.folderId, state.aliases);

      if (state.currentRecord) {
        // Update existing note
        await updateNote(state.currentRecord.path, {
          content: state.content,
          metadata,
        });

        // Fetch the updated note to get latest data
        const updated = await getNote(state.currentRecord.path);

        set({
          currentRecord: updated,
          isSaving: false,
        });
      } else {
        // Create new note
        const notePath = slugify(state.title || 'untitled') + '.md';
        const folderPrefix = state.folderId ? `${state.folderId}/` : '';

        await createNote({
          path: `${folderPrefix}${notePath}`,
          content: state.content,
          metadata,
        });

        // Fetch the created note to get full NoteResponse
        const created = await getNote(`${folderPrefix}${notePath}`);

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

  deleteRecord: async () => {
    const state = get();
    const path = state.currentRecord?.path;

    if (!path) {
      return;
    }

    try {
      await deleteNoteApi(path);
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
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Delete failed';
      set({ saveError: message });
    }
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
      const result = await aiRewrite(state.content);

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
      const result = await aiPolish(state.content);

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
      state.folderId !== ((state.currentRecord.metadata.folder as string) ?? null)
    );
  });
}
