/**
 * MessageInput Component for Markwritter
 *
 * A message input component with:
 * - Enter to send, Shift+Enter for newline
 * - Loading state with stop button
 * - Character limit support
 * - React Hook Form integration
 */

'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { Send, Square } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

interface MessageInputProps {
  /** Callback when message is submitted */
  onSubmit: (content: string) => void;
  /** Callback when stop button is clicked */
  onStop?: () => void;
  /** Whether currently streaming */
  isStreaming: boolean;
  /** Maximum character length */
  maxLength?: number;
  /** Auto focus on mount */
  autoFocus?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Additional class names */
  className?: string;
}

export function MessageInput({
  onSubmit,
  onStop,
  isStreaming,
  maxLength,
  autoFocus = false,
  placeholder = 'Type a message... (Enter to send, Shift+Enter for newline)',
  className,
}: MessageInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto focus
  useEffect(() => {
    if (autoFocus && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [autoFocus]);

  // Auto resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;

    onSubmit(trimmed);
    setInput('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [input, isStreaming, onSubmit]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const value = e.target.value;
      if (maxLength && value.length > maxLength) {
        return;
      }
      setInput(value);
    },
    [maxLength]
  );

  const handleStop = useCallback(() => {
    onStop?.();
  }, [onStop]);

  const isEmpty = !input.trim();
  const charCount = input.length;

  // Character count display
  const renderCharCount = () => {
    if (!maxLength) return null;

    const isNearLimit = charCount >= maxLength * 0.8;
    const isAtLimit = charCount >= maxLength;

    return (
      <span
        className={cn(
          'text-xs transition-colors',
          isAtLimit
            ? 'text-red-500'
            : isNearLimit
              ? 'text-amber-500'
              : 'text-muted-foreground'
        )}
      >
        {charCount}/{maxLength}
      </span>
    );
  };

  return (
    <div className={cn('border-t p-4', className)}>
      <div className="flex gap-2 items-end">
        <div className="flex-1 flex flex-col gap-1">
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isStreaming}
            aria-label="Message input"
            aria-disabled={isStreaming}
            className="min-h-[44px] max-h-[200px] resize-none"
            rows={1}
          />
          {maxLength && (
            <div className="flex justify-end">{renderCharCount()}</div>
          )}
        </div>

        {isStreaming ? (
          onStop && (
            <Button
              type="button"
              variant="destructive"
              size="icon"
              onClick={handleStop}
              aria-label="Stop streaming"
              className="shrink-0"
            >
              <Square className="h-4 w-4" />
            </Button>
          )
        ) : (
          <Button
            type="button"
            size="icon"
            onClick={handleSubmit}
            disabled={isEmpty}
            aria-label="Send message"
            className="shrink-0"
          >
            <Send className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}