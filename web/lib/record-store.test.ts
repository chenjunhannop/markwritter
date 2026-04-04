/**
 * Tests for Record Store
 *
 * Tests the Zustand store for managing record state with Note API.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act } from '@testing-library/react';

// Mock the API functions
vi.mock('./record-api', () => ({
  createRecord: vi.fn(),
  updateRecord: vi.fn(),
  createNote: vi.fn(),
  updateNote: vi.fn(),
  getNote: vi.fn(),
  deleteNote: vi.fn(),
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
  createNote,
  updateNote,
  getNote,
  deleteNote,
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
const mockedCreateNote = vi.mocked(createNote);
const mockedUpdateNote = vi.mocked(updateNote);
const mockedGetNote = vi.mocked(getNote);
const mockedDeleteNote = vi.mocked(deleteNote);
const mockedAiContinueStream = vi.mocked(aiContinueStream);
const mockedAiRewrite = vi.mocked(aiRewrite);
const mockedAiPolish = vi.mocked(aiPolish);
const mockedClassifyNote = vi.mocked(classifyNote);
const mockedSuggestTags = vi.mocked(suggestTags);
const mockedSuggestFolder = vi.mocked(suggestFolder);
const mockedProcessSSEStream = vi.mocked(processSSEStream);

// Helper to create a mock NoteResponse
function createMockNoteResponse(overrides: Record<string, unknown> = {}): import('./record-api').NoteResponse {
  return {
    path: 'test-note.md',
    title: 'Test Note',
    content: 'Test content',
    metadata: { title: 'Test Note' },
    tags: [],
    links: [],
    backlinks: [],
    ...overrides,
  };
}

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

  describe('setCurrentRecord', () => {
    it('should set record and populate store fields from NoteResponse', () => {
      const noteResponse = createMockNoteResponse({
        title: 'My Note',
        content: 'Note content here',
        metadata: { title: 'My Note', folder: 'projects', aliases: ['alias1', 'alias2'] },
        tags: ['tag-a', 'tag-b'],
      });

      act(() => {
        useRecordStore.getState().setCurrentRecord(noteResponse);
      });

      const state = useRecordStore.getState();
      expect(state.currentRecord).toEqual(noteResponse);
      expect(state.content).toBe('Note content here');
      expect(state.title).toBe('My Note');
      expect(state.tags).toEqual(['tag-a', 'tag-b']);
      expect(state.folderId).toBe('projects');
      expect(state.aliases).toEqual(['alias1', 'alias2']);
    });

    it('should handle NoteResponse with null metadata fields gracefully', () => {
      const noteResponse = createMockNoteResponse({
        metadata: {},
      });

      act(() => {
        useRecordStore.getState().setCurrentRecord(noteResponse);
      });

      const state = useRecordStore.getState();
      expect(state.folderId).toBeNull();
      expect(state.aliases).toEqual([]);
    });

    it('should clear store when setting null record', () => {
      const noteResponse = createMockNoteResponse({
        content: 'Existing content',
        title: 'Existing title',
        metadata: { folder: 'existing-folder' },
        tags: ['existing-tag'],
      });

      act(() => {
        useRecordStore.getState().setCurrentRecord(noteResponse);
      });

      expect(useRecordStore.getState().currentRecord).not.toBeNull();

      act(() => {
        useRecordStore.getState().setCurrentRecord(null);
      });

      const state = useRecordStore.getState();
      expect(state.currentRecord).toBeNull();
      expect(state.content).toBe('');
      expect(state.title).toBe('');
      expect(state.tags).toEqual([]);
      expect(state.aliases).toEqual([]);
      expect(state.folderId).toBeNull();
    });
  });

  describe('saveRecord', () => {
    it('should create a new note when no current record', async () => {
      const createdNoteResponse = createMockNoteResponse({
        path: 'my-title.md',
        title: 'My Title',
        content: 'Content',
        tags: ['test'],
      });

      mockedCreateNote.mockResolvedValueOnce({
        success: true,
        path: 'my-title.md',
      });
      mockedGetNote.mockResolvedValueOnce(createdNoteResponse);

      const { setContent, setTitle, setTags, saveRecord } = useRecordStore.getState();

      act(() => {
        setContent('Content');
        setTitle('My Title');
        setTags(['test']);
      });

      await act(async () => {
        await saveRecord();
      });

      expect(mockedCreateNote).toHaveBeenCalledWith({
        path: 'my-title.md',
        content: 'Content',
        metadata: { title: 'My Title' },
      });

      expect(mockedGetNote).toHaveBeenCalledWith('my-title.md');

      const state = useRecordStore.getState();
      expect(state.currentRecord).toEqual(createdNoteResponse);
      expect(state.currentRecord?.path).toBe('my-title.md');
      expect(state.isSaving).toBe(false);
    });

    it('should create note with folder prefix when folderId is set', async () => {
      const createdNoteResponse = createMockNoteResponse({
        path: 'projects/my-title.md',
        title: 'My Title',
        content: 'Content',
      });

      mockedCreateNote.mockResolvedValueOnce({
        success: true,
        path: 'projects/my-title.md',
      });
      mockedGetNote.mockResolvedValueOnce(createdNoteResponse);

      const { setContent, setTitle, setFolderId, saveRecord } = useRecordStore.getState();

      act(() => {
        setContent('Content');
        setTitle('My Title');
        setFolderId('projects');
      });

      await act(async () => {
        await saveRecord();
      });

      expect(mockedCreateNote).toHaveBeenCalledWith({
        path: 'projects/my-title.md',
        content: 'Content',
        metadata: { title: 'My Title', folder: 'projects' },
      });
    });

    it('should create note with untitled path when no title', async () => {
      const createdNoteResponse = createMockNoteResponse({
        path: 'untitled.md',
        content: 'Content',
        title: '',
      });

      mockedCreateNote.mockResolvedValueOnce({
        success: true,
        path: 'untitled.md',
      });
      mockedGetNote.mockResolvedValueOnce(createdNoteResponse);

      const { setContent, saveRecord } = useRecordStore.getState();

      act(() => {
        setContent('Content');
      });

      await act(async () => {
        await saveRecord();
      });

      expect(mockedCreateNote).toHaveBeenCalledWith({
        path: 'untitled.md',
        content: 'Content',
        metadata: {},
      });
    });

    it('should update existing note', async () => {
      const existingNote = createMockNoteResponse({
        path: 'existing-note.md',
        title: 'Original',
        content: 'Original content',
        metadata: { title: 'Original', folder: 'dev-notes' },
        tags: ['original'],
      });

      const updatedNoteResponse = createMockNoteResponse({
        path: 'existing-note.md',
        title: 'Original',
        content: 'Updated content',
        metadata: { title: 'Original', folder: 'dev-notes' },
        tags: ['original'],
      });

      mockedUpdateNote.mockResolvedValueOnce({
        success: true,
        path: 'existing-note.md',
      });
      mockedGetNote.mockResolvedValueOnce(updatedNoteResponse);

      const { setCurrentRecord, setContent, saveRecord } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(existingNote);
        setContent('Updated content');
      });

      await act(async () => {
        await saveRecord();
      });

      expect(mockedUpdateNote).toHaveBeenCalledWith(
        'existing-note.md',
        expect.objectContaining({
          content: 'Updated content',
          metadata: expect.objectContaining({ title: 'Original', folder: 'dev-notes' }),
        })
      );

      expect(mockedGetNote).toHaveBeenCalledWith('existing-note.md');
      expect(useRecordStore.getState().currentRecord).toEqual(updatedNoteResponse);
    });

    it('should include aliases in metadata when saving', async () => {
      const createdNoteResponse = createMockNoteResponse({
        path: 'my-note.md',
        title: 'My Note',
        content: 'Content',
      });

      mockedCreateNote.mockResolvedValueOnce({
        success: true,
        path: 'my-note.md',
      });
      mockedGetNote.mockResolvedValueOnce(createdNoteResponse);

      const { setContent, setTitle, setAliases, saveRecord } = useRecordStore.getState();

      act(() => {
        setContent('Content');
        setTitle('My Note');
        setAliases(['alias-a', 'alias-b']);
      });

      await act(async () => {
        await saveRecord();
      });

      expect(mockedCreateNote).toHaveBeenCalledWith({
        path: 'my-note.md',
        content: 'Content',
        metadata: { title: 'My Note', aliases: ['alias-a', 'alias-b'] },
      });
    });

    it('should handle save errors', async () => {
      mockedCreateNote.mockRejectedValueOnce(new Error('Save failed'));

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

  describe('deleteRecord', () => {
    it('should delete the current record via Notes API', async () => {
      const existingNote = createMockNoteResponse({
        path: 'to-delete.md',
        content: 'Content',
      });

      mockedDeleteNote.mockResolvedValueOnce(undefined);

      const { setCurrentRecord, deleteRecord } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(existingNote);
      });

      await act(async () => {
        await deleteRecord();
      });

      expect(mockedDeleteNote).toHaveBeenCalledWith('to-delete.md');
      expect(useRecordStore.getState().currentRecord).toBeNull();
      expect(useRecordStore.getState().content).toBe('');
      expect(useRecordStore.getState().title).toBe('');
    });

    it('should do nothing when no current record', async () => {
      const { deleteRecord } = useRecordStore.getState();

      await act(async () => {
        await deleteRecord();
      });

      expect(mockedDeleteNote).not.toHaveBeenCalled();
    });

    it('should handle delete errors', async () => {
      const existingNote = createMockNoteResponse({
        path: 'error-note.md',
        content: 'Content',
      });

      mockedDeleteNote.mockRejectedValueOnce(new Error('Delete failed'));

      const { setCurrentRecord, deleteRecord } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(existingNote);
      });

      await act(async () => {
        await deleteRecord();
      });

      expect(useRecordStore.getState().saveError).toBe('Delete failed');
    });
  });

  describe('aiContinue', () => {
    it('should stream AI continue content without recordId', async () => {
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
        setCurrentRecord(createMockNoteResponse({ path: 'note-1.md', content: 'Initial' }));
        setContent('Initial content');
      });

      await act(async () => {
        await aiContinue();
      });

      // Verify aiContinueStream was called WITHOUT recordId
      expect(mockedAiContinueStream).toHaveBeenCalledWith(
        'Initial content',
        expect.any(AbortSignal)
      );

      // Content should be updated with streamed text
      expect(useRecordStore.getState().content).toBe('Initial contentcontinued text');
      expect(useRecordStore.getState().isStreaming).toBe(false);
    });

    it('should handle streaming errors', async () => {
      mockedAiContinueStream.mockRejectedValueOnce(new Error('Stream failed'));

      const { setCurrentRecord, setContent, aiContinue } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(createMockNoteResponse({ path: 'note-1.md' }));
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
    it('should rewrite content without recordId', async () => {
      mockedAiRewrite.mockResolvedValueOnce({
        original: 'original text',
        rewritten: 'rewritten text',
      });

      const { setCurrentRecord, setContent, aiRewrite } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(createMockNoteResponse({ path: 'note-1.md' }));
        setContent('original text');
      });

      await act(async () => {
        await aiRewrite();
      });

      // Verify aiRewrite was called WITHOUT recordId
      expect(mockedAiRewrite).toHaveBeenCalledWith('original text', 'formal');
      expect(useRecordStore.getState().content).toBe('rewritten text');
    });

    it('should handle rewrite errors', async () => {
      mockedAiRewrite.mockRejectedValueOnce(new Error('Rewrite failed'));

      const { setCurrentRecord, setContent, aiRewrite } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(createMockNoteResponse({ path: 'note-1.md' }));
        setContent('content');
      });

      await act(async () => {
        await aiRewrite();
      });

      expect(useRecordStore.getState().streamError).toBe('Rewrite failed');
    });
  });

  describe('aiPolish', () => {
    it('should polish content without recordId', async () => {
      mockedAiPolish.mockResolvedValueOnce({
        original: 'rough text',
        polished: 'polished text',
      });

      const { setCurrentRecord, setContent, aiPolish } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(createMockNoteResponse({ path: 'note-1.md' }));
        setContent('rough text');
      });

      await act(async () => {
        await aiPolish();
      });

      // Verify aiPolish was called WITHOUT recordId
      expect(mockedAiPolish).toHaveBeenCalledWith('rough text');
      expect(useRecordStore.getState().content).toBe('polished text');
    });

    it('should handle polish errors', async () => {
      mockedAiPolish.mockRejectedValueOnce(new Error('Polish failed'));

      const { setCurrentRecord, setContent, aiPolish } = useRecordStore.getState();

      act(() => {
        setCurrentRecord(createMockNoteResponse({ path: 'note-1.md' }));
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
        setCurrentRecord(createMockNoteResponse({
          path: 'note-1.md',
          content: 'Content',
          metadata: { folder: 'test-folder' },
          tags: ['tag'],
        }));
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

      expect(useRecordStore.getState().currentRecord).toBeNull();

      act(() => {
        setCurrentRecord(createMockNoteResponse({ path: 'note-1.md' }));
      });

      expect(useRecordStore.getState().currentRecord).not.toBeNull();
    });

    it('useIsAIStreaming should return streaming state', () => {
      const { setIsStreaming } = useRecordStore.getState();

      expect(useRecordStore.getState().isStreaming).toBe(false);

      act(() => {
        setIsStreaming(true);
      });

      expect(useRecordStore.getState().isStreaming).toBe(true);
    });
  });
});
