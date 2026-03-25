'use client';

/**
 * Markdown Editor Component
 *
 * A markdown editor with toolbar supporting:
 * - Basic markdown syntax (bold, italic, heading, link, code)
 * - Obsidian-specific syntax (wikilinks, callouts, tags)
 * - Keyboard shortcuts
 * - Selection-aware formatting
 */

import { useRef, useCallback, type KeyboardEvent, type ChangeEvent } from 'react';
import { useRecordStore } from '@/lib/record-store';
import { EditorToolbar } from './editor-toolbar';
import { cn } from '@/lib/utils';

interface MarkdownEditorProps {
  className?: string;
  placeholder?: string;
  minHeight?: number;
}

export function MarkdownEditor({
  className,
  placeholder = 'Start writing...',
  minHeight = 300,
}: MarkdownEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const content = useRecordStore((state) => state.content);
  const isStreaming = useRecordStore((state) => state.isStreaming);
  const setContent = useRecordStore((state) => state.setContent);

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      setContent(e.target.value);
    },
    [setContent]
  );

  const insertText = useCallback(
    (before: string, after: string = '') => {
      const textarea = textareaRef.current;
      if (!textarea) return;

      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const selectedText = content.substring(start, end);
      const newText =
        content.substring(0, start) +
        before +
        selectedText +
        after +
        content.substring(end);

      setContent(newText);

      // Reset cursor position
      requestAnimationFrame(() => {
        textarea.focus();
        const newCursorPos = start + before.length + selectedText.length;
        textarea.setSelectionRange(newCursorPos, newCursorPos);
      });
    },
    [content, setContent]
  );

  const handleBold = useCallback(() => {
    insertText('**', '**');
  }, [insertText]);

  const handleItalic = useCallback(() => {
    insertText('_', '_');
  }, [insertText]);

  const handleHeading = useCallback(() => {
    insertText('# ', '');
  }, [insertText]);

  const handleLink = useCallback(() => {
    insertText('[', '](url)');
  }, [insertText]);

  const handleCode = useCallback(() => {
    insertText('`', '`');
  }, [insertText]);

  const handleCodeBlock = useCallback(() => {
    insertText('```\n', '\n```');
  }, [insertText]);

  const handleWikilink = useCallback(() => {
    insertText('[[', ']]');
  }, [insertText]);

  const handleCallout = useCallback(
    (type: string = 'note') => {
      insertText(`> [!${type}]\n> `, '');
    },
    [insertText]
  );

  const handleQuote = useCallback(() => {
    insertText('> ', '');
  }, [insertText]);

  const handleList = useCallback(() => {
    insertText('- ', '');
  }, [insertText]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
          case 'b':
            e.preventDefault();
            handleBold();
            break;
          case 'i':
            e.preventDefault();
            handleItalic();
            break;
          case 'k':
            e.preventDefault();
            handleLink();
            break;
        }
      }

      // Handle Tab for code blocks or indentation
      if (e.key === 'Tab') {
        e.preventDefault();
        insertText('  ', '');
      }
    },
    [handleBold, handleItalic, handleLink, insertText]
  );

  return (
    <div className={cn('flex flex-col border rounded-lg', className)}>
      <EditorToolbar
        onBold={handleBold}
        onItalic={handleItalic}
        onHeading={handleHeading}
        onLink={handleLink}
        onCode={handleCode}
        onCodeBlock={handleCodeBlock}
        onWikilink={handleWikilink}
        onCallout={handleCallout}
        onQuote={handleQuote}
        onList={handleList}
        disabled={isStreaming}
      />
      <textarea
        ref={textareaRef}
        value={content}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={isStreaming}
        className={cn(
          'flex-1 w-full p-4 resize-none',
          'bg-transparent outline-none',
          'font-mono text-sm leading-relaxed',
          'placeholder:text-muted-foreground',
          isStreaming && 'opacity-50 cursor-not-allowed'
        )}
        style={{ minHeight }}
      />
    </div>
  );
}