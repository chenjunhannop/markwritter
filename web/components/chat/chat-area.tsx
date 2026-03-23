/**
 * ChatArea Component for Markwritter
 *
 * Main chat interface that combines:
 * - Message list (ChatSession)
 * - Message input
 * - Streaming indicators
 * - Error handling
 */

'use client';

import { Bot, AlertCircle, RefreshCw, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { useChat } from '@/hooks/use-chat';
import { ChatSession } from './chat-session';
import { MessageInput } from './message-input';

interface ChatAreaProps {
  /** Additional class names */
  className?: string;
}

/**
 * Empty state component
 */
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8">
      <Bot className="h-16 w-16 mb-4 opacity-50" />
      <h3 className="text-lg font-medium mb-2">No messages yet</h3>
      <p className="text-sm text-center">
        Start a conversation by typing a message below.
      </p>
    </div>
  );
}

/**
 * Thinking indicator component
 */
function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 p-4 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span className="text-sm">Thinking...</span>
    </div>
  );
}

/**
 * Error alert component
 */
function ErrorAlert({
  message,
  onRetry,
  onDismiss,
}: {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}) {
  return (
    <Alert variant="destructive" className="m-4">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription className="flex items-center justify-between">
        <span>{message}</span>
        <div className="flex gap-2">
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
              className="ml-2"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          )}
          {onDismiss && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
            >
              <X className="h-3 w-3" />
              <span className="sr-only">Dismiss</span>
            </Button>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
}

export function ChatArea({ className }: ChatAreaProps) {
  const {
    messages,
    currentResponse,
    isStreaming,
    isThinking,
    error,
    sendMessage,
    stopStreaming,
    retry,
    clearError,
  } = useChat();

  const hasMessages = messages.length > 0;
  const showStreamingContent = isStreaming && currentResponse;

  return (
    <main
      className={cn('flex flex-col h-full bg-background', className)}
      role="main"
      aria-label="Chat"
    >
      {/* Error Alert */}
      {error && (
        <ErrorAlert
          message={error}
          onRetry={retry}
          onDismiss={clearError}
        />
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {!hasMessages && !isStreaming ? (
          <EmptyState />
        ) : (
          <ChatSession
            messages={messages}
            isStreaming={isStreaming}
            streamingContent={currentResponse}
            className="flex-1"
          />
        )}

        {/* Thinking Indicator */}
        {isThinking && <ThinkingIndicator />}

        {/* Live region for accessibility */}
        {showStreamingContent && (
          <div role="status" aria-live="polite" className="sr-only">
            {currentResponse}
          </div>
        )}
      </div>

      {/* Input Area */}
      <MessageInput
        onSubmit={sendMessage}
        onStop={stopStreaming}
        isStreaming={isStreaming}
        maxLength={4000}
        autoFocus
      />
    </main>
  );
}