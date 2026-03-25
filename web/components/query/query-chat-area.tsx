'use client';

/**
 * QueryChatArea Component
 *
 * Q&A chat interface with:
 * - Streaming answer display
 * - Source references
 * - Question input
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { Send, Square, BookOpen } from 'lucide-react';
import { useQueryStore } from '@/lib/query-store';
import { cn } from '@/lib/utils';

interface QueryChatAreaProps {
  className?: string;
}

export function QueryChatArea({ className }: QueryChatAreaProps) {
  const [question, setQuestion] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Use individual selectors to avoid creating new object references
  const currentQuestion = useQueryStore((state) => state.currentQuestion);
  const answer = useQueryStore((state) => state.answer);
  const sources = useQueryStore((state) => state.sources);
  const isStreaming = useQueryStore((state) => state.isStreaming);
  const streamError = useQueryStore((state) => state.streamError);
  const askStream = useQueryStore((state) => state.askStream);
  const cancelStream = useQueryStore((state) => state.cancelStream);
  const clearAnswer = useQueryStore((state) => state.clearAnswer);

  // Scroll to bottom when answer updates
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [answer]);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (question.trim() && !isStreaming) {
        askStream(question.trim());
        setQuestion('');
      }
    },
    [question, isStreaming, askStream]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit(e);
      }
    },
    [handleSubmit]
  );

  const handleCancel = useCallback(() => {
    cancelStream();
  }, [cancelStream]);

  const handleNewQuestion = useCallback(() => {
    clearAnswer();
    setQuestion('');
    inputRef.current?.focus();
  }, [clearAnswer]);

  return (
    <div className={cn('flex flex-col h-full min-h-[400px]', className)}>
      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto mb-4">
        {/* Empty State */}
        {!currentQuestion && !answer && (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <BookOpen className="w-12 h-12 text-gray-300 dark:text-gray-600 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Ask a Question
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-sm">
              Ask questions about your notes and get AI-powered answers with source
              references.
            </p>
          </div>
        )}

        {/* Question and Answer */}
        {(currentQuestion || answer) && (
          <div className="space-y-4">
            {/* Question */}
            {currentQuestion && (
              <div className="flex justify-end">
                <div className="max-w-[80%] bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-2">
                  {currentQuestion}
                </div>
              </div>
            )}

            {/* Answer */}
            {answer && (
              <div className="flex justify-start">
                <div className="max-w-[80%] bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    {answer}
                    {isStreaming && (
                      <span className="inline-block w-2 h-4 ml-1 bg-gray-400 animate-pulse" />
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Sources */}
            {sources.length > 0 && !isStreaming && (
              <div className="flex justify-start">
                <div className="max-w-[80%]">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sources
                  </h4>
                  <div className="space-y-2">
                    {sources.map((source, index) => (
                      <div
                        key={source.id || index}
                        className="text-sm bg-gray-50 dark:bg-gray-800 rounded-lg p-3 border border-gray-200 dark:border-gray-700"
                      >
                        <div className="font-medium text-gray-900 dark:text-gray-100 mb-1">
                          {source.title || `Source ${index + 1}`}
                        </div>
                        <div className="text-gray-600 dark:text-gray-400 line-clamp-2">
                          {source.content}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Error */}
            {streamError && (
              <div className="flex justify-start">
                <div className="max-w-[80%] bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg px-4 py-3">
                  <p className="text-red-600 dark:text-red-400 text-sm">{streamError}</p>
                </div>
              </div>
            )}

            {/* Actions after streaming */}
            {!isStreaming && answer && (
              <div className="flex justify-start">
                <button
                  onClick={handleNewQuestion}
                  className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Ask another question
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your notes..."
            disabled={isStreaming}
            rows={1}
            className="w-full px-4 py-3 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          />
        </div>

        {isStreaming ? (
          <button
            type="button"
            onClick={handleCancel}
            className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors"
          >
            <Square className="w-5 h-5" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!question.trim()}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        )}
      </form>
    </div>
  );
}