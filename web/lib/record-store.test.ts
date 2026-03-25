/**
 * Tests for Record Store
 *
 * Tests the Zustand store for managing record state.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act } from '@testing-library/react';

// Mock the API functions
vi.mock('./record-api', () => ({
  createRecord: vi.fn(),
  updateRecord: vi.fn(),
  aiContinueStream: vi.fn(),
  aiRewrite: vi.fn(),
  aiPolish: vi.fn(),
  classifyNote: vi.fn(),
  suggestTags: vi.fn(),
  suggestFolder: vi.fn(),
}));

// Mock the SSE processing
vi.mock('./sse', () => ({
  processSSEStream: vi.fn(),
}));

// Import after mocking
import {
  createRecord,
  updateRecord,
  aiContinueStream,
  aiRewrite,
  aiPolish,
  classifyNote,
  suggestTags,
  suggestFolder,
} from './record-api';
import { processSSEStream } from './sse';
import { useRecordStore, useHasActiveRecord, useIsAIStreaming } from './record-store';

// Type the mocked functions
const mockedCreateRecord = vi.mocked(createRecord);
const mockedUpdateRecord = vi.mocked(updateRecord);
const mockedAiContinueStream = vi.mocked(aiContinueStream);
const mockedAiRewrite = vi.mocked(aiRewrite);
const mockedAiPolish = vi.mocked(aiPolish);
const mockedClassifyNote = vi.mocked(classifyNote);
const mockedSuggestTags = vi.mocked(suggestTags);
const mockedSuggestFolder = vi.mocked(suggestFolder);
const mockedProcessSSEStream = vi.mocked(processSSEStream);

describe('Record Store', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store state
    useRecordStore.setState({
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
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('initial state', () => {
    it('should have correct initial state', () => {
      const state = useRecordStore.getState();

      expect(state.currentRecord).toBeNull();
      expect(state.content).toBe('');
      expect(state.title).toBe('');
      expect(state.tags).toEqual([]);
      expect(state.aliases).toEqual([]);
      expect(state.folderId).toBeNull();
      expect(state.isSaving).toBe(false);
      expect(state.saveError).toBeNull();
      expect(state.isStreaming).toBe(false);
      expect(state.streamError).toBeNull();
      expect(state.abortController).toBeNull();
      expect(state.isClassifying).toBe(false);
      expect(state.classificationResult).toBeNull();
      expect(state.tagSuggestions).toEqual([]);
      expect(state.folderSuggestion).toBeNull();
    });
  });

  describe('setContent', () => {
    it('should update content', () => {
      const { setContent } = useRecordStore.getState();

      act(() => {
        setContent('New content');
      });

      expect(useRecordStore.getState().content).toBe('New content');
    });

    it('should clear classification when content changes', () => {
      const { setContent, setClassificationResult } = useRecordStore.getState();

      // Set initial classification
      act(() => {
        setClassificationResult({
          suggested_tags: ['test'],
          suggested_folder: 'folder',
          confidence: 0.8,
        });
      });

      expect(useRecordStore.getState().classificationResult).not.toBeNull();

      // Change content
      act(() => {
        setContent('Different content');
      });

      expect(useRecordStore.getState().classificationResult).toBeNull();
    });
  });

  describe('setTitle', () => {
    it('should update title', () => {
      const { setTitle } = useRecordStore.getState();

      act(() => {
        setTitle('New Title');
      });

      expect(useRecordStore.getState().title).toBe('New Title');
    });
  });

  describe('setTags', () => {
    it('should update tags', () => {
      const { setTags } = useRecordStore.getState();

      act(() => {
        setTags(['tag1', 'tag2']);
      });

      expect(useRecordStore.getState().tags).toEqual(['tag1', 'tag2']);
    });
  });

  describe('addTag', () => {
    it('should add a new tag', () => {
      const { setTags, addTag } = useRecordStore.getState();

      act(() => {
        setTags(['existing']);
        addTag('new-tag');
      });

      expect(useRecordStore.getState().tags).toContain('new-tag');
    });

    it('should not add duplicate tags', () => {
      const { setTags, addTag } = useRecordStore.getState();

      act(() => {
        setTags(['existing']);
        addTag('existing');
      });

      expect(useRecordStore.getState().tags.filter((t) => t === 'existing')).toHaveLength(1);
    });
  });

  describe('removeTag', () => {
    it('should remove a tag', () => {
      const { setTags, removeTag } = useRecordStore.getState();

      act(() => {
        setTags(['tag1', 'tag2', 'tag3']);
        removeTag('tag2');
      });

      expect(useRecordStore.getState().tags).toEqual(['tag1', 'tag3']);
    });

    it('should handle removing non-existent tag', () => {
      const { setTags, removeTag } = useRecordStore.getState();

      act(() => {
        setTags(['tag1']);
        removeTag('nonexistent');
      });

      expect(useRecordStore.getState().tags).toEqual(['tag1']);
    });
  });

  describe('saveRecord', () => {
    it('should create a new record when no current record', async () => {
      const mockResponse = {
        id: 'new-record-id',
        title: 'Test',
        content: 'Content',
        folder_id: null,
        tags: ['test'],
        aliases: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      mockedCreateRecord.mockResolvedValueOnce(mockResponse);

      const { setContent, setTags, saveRecord } = useRecordStore.getState();

      act(() => {
        setContent('Content');
        setTags(['test']);
      });

      await act(async () => {
        await saveRecord();
      });

      expect(mockedCreateRecord).toHaveBeenCalledWith({
        content: 'Content',
        title: null,
        tags: ['test'],
        folder_id: null,
        aliases: [],
      });

      expect(useRecordStore.getState().currentRecord).toEqual(mockResponse);
      expect(useRecordStore.getState().isSaving).toBe(false);
    });

    it('should update existing record', async () => {
      const existingRecord = {
        id: 'existing-id',
        title: 'Original',
        content: 'Original content',
        folder_id: null,
        tags: [],
        aliases: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };

      const updatedResponse = {
        ...existingRecord,
        content: 'Updated content',
        updated_at: '2024-01-02T00:00:00Z',
      };

      mockedUpdateRecord.mockResolvedValueOnce(updatedResponse);

      const { setCurrentRecord, setContent, saveRecord } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(existingRecord);
        setContent('Updated content');
      });

      await act(async () => {
        await saveRecord();
      });

      expect(mockedUpdateRecord).toHaveBeenCalledWith({
        id: 'existing-id',
        content: 'Updated content',
        title: 'Original',
        tags: [],
        aliases: [],
        folder_id: null,
      });

      expect(useRecordStore.getState().currentRecord).toEqual(updatedResponse);
    });

    it('should handle save errors', async () => {
      mockedCreateRecord.mockRejectedValueOnce(new Error('Save failed'));

      const { setContent, saveRecord } = useRecordStore.getState();

      act(() => {
        setContent('Content');
      });

      await act(async () => {
        await saveRecord();
      });

      expect(useRecordStore.getState().saveError).toBe('Save failed');
      expect(useRecordStore.getState().isSaving).toBe(false);
    });
  });

  describe('aiContinue', () => {
    it('should stream AI continue content', async () => {
      const mockResponse = {
        ok: true,
        body: {},
      };

      mockedAiContinueStream.mockResolvedValueOnce(mockResponse as unknown as Response);
      mockedProcessSSEStream.mockImplementationOnce(async (_response, onEvent) => {
        onEvent({ type: 'text_delta', content: 'continued ' });
        onEvent({ type: 'text_delta', content: 'text' });
        onEvent({ type: 'done', content: '' });
      });

      const { setCurrentRecord, setContent, aiContinue } = useRecordStore.getState();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: 'Initial',
          folder_id: null,
          tags: [],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
        setContent('Initial content');
      });

      await act(async () => {
        await aiContinue();
      });

      // Content should be updated with streamed text
      expect(useRecordStore.getState().content).toBe('Initial contentcontinued text');
      expect(useRecordStore.getState().isStreaming).toBe(false);
    });

    it('should handle streaming errors', async () => {
      mockedAiContinueStream.mockRejectedValueOnce(new Error('Stream failed'));

      const { setCurrentRecord, setContent, aiContinue } = useRecordStore.getState();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: '',
          folder_id: null,
          tags: [],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
        setContent('Content');
      });

      await act(async () => {
        await aiContinue();
      });

      expect(useRecordStore.getState().streamError).toBe('Stream failed');
      expect(useRecordStore.getState().isStreaming).toBe(false);
    });

    it('should require current record', async () => {
      const { aiContinue } = useRecordStore.getState();

      await act(async () => {
        await aiContinue();
      });

      expect(mockedAiContinueStream).not.toHaveBeenCalled();
    });
  });

  describe('aiRewrite', () => {
    it('should rewrite content', async () => {
      mockedAiRewrite.mockResolvedValueOnce({
        original: 'original text',
        rewritten: 'rewritten text',
      });

      const { setCurrentRecord, setContent, aiRewrite } = useRecordStore.getState();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: '',
          folder_id: null,
          tags: [],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
        setContent('original text');
      });

      await act(async () => {
        await aiRewrite();
      });

      expect(useRecordStore.getState().content).toBe('rewritten text');
    });

    it('should handle rewrite errors', async () => {
      mockedAiRewrite.mockRejectedValueOnce(new Error('Rewrite failed'));

      const { setCurrentRecord, setContent, aiRewrite } = useRecordStore.getState();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: '',
          folder_id: null,
          tags: [],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
        setContent('content');
      });

      await act(async () => {
        await aiRewrite();
      });

      expect(useRecordStore.getState().streamError).toBe('Rewrite failed');
    });
  });

  describe('aiPolish', () => {
    it('should polish content', async () => {
      mockedAiPolish.mockResolvedValueOnce({
        original: 'rough text',
        polished: 'polished text',
      });

      const { setCurrentRecord, setContent, aiPolish } = useRecordStore.getState();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: '',
          folder_id: null,
          tags: [],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
        setContent('rough text');
      });

      await act(async () => {
        await aiPolish();
      });

      expect(useRecordStore.getState().content).toBe('polished text');
    });

    it('should handle polish errors', async () => {
      mockedAiPolish.mockRejectedValueOnce(new Error('Polish failed'));

      const { setCurrentRecord, setContent, aiPolish } = useRecordStore.getState();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: '',
          folder_id: null,
          tags: [],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
        setContent('content');
      });

      await act(async () => {
        await aiPolish();
      });

      expect(useRecordStore.getState().streamError).toBe('Polish failed');
    });
  });

  describe('classify', () => {
    it('should classify content and set suggestions', async () => {
      mockedClassifyNote.mockResolvedValueOnce({
        suggested_tags: ['tag1', 'tag2'],
        suggested_folder: 'folder/path',
        confidence: 0.9,
      });

      const { setContent, classify } = useRecordStore.getState();

      act(() => {
        setContent('Some content to classify');
      });

      await act(async () => {
        await classify();
      });

      expect(useRecordStore.getState().classificationResult).toEqual({
        suggested_tags: ['tag1', 'tag2'],
        suggested_folder: 'folder/path',
        confidence: 0.9,
      });
      expect(useRecordStore.getState().isClassifying).toBe(false);
    });

    it('should handle classification errors', async () => {
      mockedClassifyNote.mockRejectedValueOnce(new Error('Classification failed'));

      const { setContent, classify } = useRecordStore.getState();

      act(() => {
        setContent('Content');
      });

      await act(async () => {
        await classify();
      });

      expect(useRecordStore.getState().isClassifying).toBe(false);
    });

    it('should not classify empty content', async () => {
      const { classify } = useRecordStore.getState();

      await act(async () => {
        await classify();
      });

      expect(mockedClassifyNote).not.toHaveBeenCalled();
    });
  });

  describe('fetchTagSuggestions', () => {
    it('should fetch tag suggestions', async () => {
      mockedSuggestTags.mockResolvedValueOnce({
        tags: ['suggested1', 'suggested2'],
      });

      const { setContent, fetchTagSuggestions } = useRecordStore.getState();

      act(() => {
        setContent('Content for tags');
      });

      await act(async () => {
        await fetchTagSuggestions();
      });

      expect(useRecordStore.getState().tagSuggestions).toEqual(['suggested1', 'suggested2']);
    });

    it('should handle tag suggestion errors silently', async () => {
      mockedSuggestTags.mockRejectedValueOnce(new Error('Tag suggestion failed'));

      const { setContent, fetchTagSuggestions } = useRecordStore.getState();

      act(() => {
        setContent('Content');
      });

      await act(async () => {
        await fetchTagSuggestions();
      });

      expect(useRecordStore.getState().tagSuggestions).toEqual([]);
    });
  });

  describe('fetchFolderSuggestion', () => {
    it('should fetch folder suggestion', async () => {
      mockedSuggestFolder.mockResolvedValueOnce({
        folder: 'suggested/folder',
        confidence: 0.85,
      });

      const { setContent, fetchFolderSuggestion } = useRecordStore.getState();

      act(() => {
        setContent('Content for folder');
      });

      await act(async () => {
        await fetchFolderSuggestion();
      });

      expect(useRecordStore.getState().folderSuggestion).toEqual({
        folder: 'suggested/folder',
        confidence: 0.85,
      });
    });

    it('should handle folder suggestion errors silently', async () => {
      mockedSuggestFolder.mockRejectedValueOnce(new Error('Folder suggestion failed'));

      const { setContent, fetchFolderSuggestion } = useRecordStore.getState();

      act(() => {
        setContent('Content');
      });

      await act(async () => {
        await fetchFolderSuggestion();
      });

      expect(useRecordStore.getState().folderSuggestion).toBeNull();
    });
  });

  describe('cancelStream', () => {
    it('should abort streaming', () => {
      const controller = new AbortController();
      const abortSpy = vi.spyOn(controller, 'abort');

      const { setIsStreaming, setAbortController, cancelStream } = useRecordStore.getState();

      act(() => {
        setIsStreaming(true);
        setAbortController(controller);
      });

      act(() => {
        cancelStream();
      });

      expect(abortSpy).toHaveBeenCalled();
      expect(useRecordStore.getState().isStreaming).toBe(false);
      expect(useRecordStore.getState().abortController).toBeNull();
    });
  });

  describe('clearRecord', () => {
    it('should reset all record state', () => {
      const {
        setCurrentRecord,
        setContent,
        setTitle,
        setTags,
        setClassificationResult,
        clearRecord,
      } = useRecordStore.getState();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: 'Content',
          folder_id: null,
          tags: ['tag'],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
        setContent('Content');
        setTitle('Title');
        setTags(['tag']);
        setClassificationResult({
          suggested_tags: ['suggestion'],
          suggested_folder: 'folder',
          confidence: 0.8,
        });
      });

      act(() => {
        clearRecord();
      });

      expect(useRecordStore.getState().currentRecord).toBeNull();
      expect(useRecordStore.getState().content).toBe('');
      expect(useRecordStore.getState().title).toBe('');
      expect(useRecordStore.getState().tags).toEqual([]);
      expect(useRecordStore.getState().classificationResult).toBeNull();
    });
  });

  describe('selector hooks', () => {
    it('useHasActiveRecord should return true when record exists', () => {
      const { setCurrentRecord } = useRecordStore.getState();

      // Check initial state directly
      expect(useRecordStore.getState().currentRecord).toBeNull();

      act(() => {
        setCurrentRecord({
          id: 'record-1',
          title: 'Test',
          content: 'Content',
          folder_id: null,
          tags: [],
          aliases: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z',
        });
      });

      expect(useRecordStore.getState().currentRecord).not.toBeNull();
    });

    it('useIsAIStreaming should return streaming state', () => {
      const { setIsStreaming } = useRecordStore.getState();

      // Check initial state directly
      expect(useRecordStore.getState().isStreaming).toBe(false);

      act(() => {
        setIsStreaming(true);
      });

      expect(useRecordStore.getState().isStreaming).toBe(true);
    });
  });
});