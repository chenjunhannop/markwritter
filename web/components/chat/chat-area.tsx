/**
 * ChatArea Component for Markwritter
 *
 * Main chat interface that combines:
 * - Panel header with session controls
 * - Message list (ChatSession)
 * - Message input with source context
 * - Streaming indicators
 * - Error handling
 */

'use client';

import { useEffect } from 'react';
import { MessageSquare, AlertCircle, RefreshCw, X, Loader2, Plus, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { useChat } from '@/hooks/use-chat';
import { useChatStore } from '@/lib/store';
import { ChatSession } from './chat-session';
import { MessageInput } from './message-input';
import { FloatingEmptyCard } from '@/components/apple/empty-state';
import { ActionPill } from '@/components/apple/action-pill';

interface ChatAreaProps {
  className?: string;
}

function EmptyState({ onAction }: { onAction?: (action: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center h-full p-6">
      <FloatingEmptyCard
        icon={MessageSquare}
        title="Start a conversation"
        description="Pull in notes from the left, ask naturally, and keep your tools available without the center collapsing into whitespace."
        actions={
          <>
            <ActionPill label="Summarize Source" onClick={() => onAction?.('summarize')} />
            <ActionPill label="Compare Notes" onClick={() => onAction?.('compare')} />
            <ActionPill label="Draft Reply" onClick={() => onAction?.('draft')} />
          </>
        }
      />
    </div>
  );
}

function ThinkingIndicator() {
  return (
    <div className="flex items-center gap-2 px-4 py-2 text-muted-foreground">
      <Loader2 className="h-4 w-4 animate-spin" />
      <span className="text-sm">Thinking...</span>
    </div>
  );
}

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
    <Alert variant="destructive" className="mx-4">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription className="flex items-center justify-between">
        <span className="text-sm">{message}</span>
        <div className="flex gap-2">
          {onRetry && (
            <Button
              variant="outline"
              size="sm"
              onClick={onRetry}
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Retry
            </Button>
          )}
          {onDismiss && (
            <Button variant="ghost" size="sm" onClick={onDismiss}>
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

  const selectedSources = useChatStore((s) => s.selectedSources);
  const currentSessionId = useChatStore((s) => s.currentSessionId);
  const createSession = useChatStore((s) => s.createSession);
  const clearSources = useChatStore((s) => s.clearSources);

  // Auto-create session on first load
  useEffect(() => {
    if (!currentSessionId) {
      createSession();
    }
  }, [currentSessionId, createSession]);

  const hasMessages = messages.length > 0;
  const showStreamingContent = isStreaming && currentResponse;
  const sourceCount = selectedSources.length;

  const handleNewChat = () => {
    createSession();
  };

  return (
    <div
      className={cn('flex h-full flex-col bg-transparent', className)}
      role="main"
      aria-label="Chat"
    >
      {/* Panel Header */}
      <div className="flex h-[42px] shrink-0 items-center gap-2 border-b border-[var(--panel-border)] px-3">
        <span className="text-[13px] font-semibold">Chat</span>
        {sourceCount > 0 && (
          <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
            {sourceCount} source{sourceCount !== 1 ? 's' : ''}
          </Badge>
        )}
        <div className="flex-1" />
        <Button
          variant="ghost"
          size="icon"
          onClick={handleNewChat}
          className="h-7 w-7"
          title="New chat"
        >
          <Plus className="h-4 w-4" />
        </Button>
      </div>

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
          <EmptyState onAction={(action) => {
            const actionPrompts: Record<string, string> = {
              summarize: 'Summarize the selected sources',
              compare: 'Compare the selected notes',
              draft: 'Draft a reply based on the context',
            };
            if (actionPrompts[action]) sendMessage(actionPrompts[action]);
          }} />
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
      <div className="border-t border-[var(--panel-border)] p-3">
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <MessageInput
              onSubmit={sendMessage}
              onStop={stopStreaming}
              isStreaming={isStreaming}
              maxLength={4000}
              autoFocus
              selectedSourceCount={sourceCount}
              onClearSources={clearSources}
              className="border-0 p-0"
            />
          </div>
        </div>

        {/* Source Context Indicator */}
        {sourceCount > 0 && (
          <div className="flex items-center gap-1.5 pt-1.5">
            <FileText className="h-3 w-3 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">
              {sourceCount} source{sourceCount > 1 ? 's' : ''} selected
            </span>
            <button
              onClick={clearSources}
              className="text-xs text-muted-foreground underline-offset-2 hover:text-foreground"
            >
              Clear
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
