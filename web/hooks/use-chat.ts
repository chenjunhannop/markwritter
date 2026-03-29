/**
 * useChat Hook for Markwritter
 *
 * Encapsulates chat logic including:
 * - Message sending
 * - SSE stream processing
 * - StreamBuffer integration for typewriter effect
 * - Error handling and retry
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { sendMessage as apiSendMessage } from '@/lib/api';
import { processSSEStream } from '@/lib/sse';
import { useChatStore } from '@/lib/store';
import { StreamBuffer, type StreamBufferCallbacks } from '@/lib/stream-buffer';
import type { ChatEvent, Message } from '@/lib/types';

/**
 * Hook return type
 */
interface UseChatReturn {
  /** Current streaming response text */
  currentResponse: string;
  /** Whether currently streaming */
  isStreaming: boolean;
  /** Whether thinking/processing */
  isThinking: boolean;
  /** Current error message */
  error: string | null;
  /** Messages in current session */
  messages: Message[];
  /** Send a message */
  sendMessage: (content: string) => Promise<void>;
  /** Stop current streaming */
  stopStreaming: () => void;
  /** Retry last failed message */
  retry: () => Promise<void>;
  /** Clear error state */
  clearError: () => void;
}

/**
 * useChat Hook
 *
 * Manages chat state and interactions with the backend API.
 */
export function useChat(): UseChatReturn {
  // Store state - use individual selectors to avoid infinite loops
  const addMessage = useChatStore((state) => state.addMessage);
  const updateMessage = useChatStore((state) => state.updateMessage);
  const setStreaming = useChatStore((state) => state.setStreaming);
  const getCurrentSession = useChatStore((state) => state.getCurrentSession);
  const currentSessionId = useChatStore((state) => state.currentSessionId);
  const storeIsStreaming = useChatStore((state) => state.isStreaming);
  const selectedSources = useChatStore((state) => state.selectedSources);
  const updateSessionTitle = useChatStore((state) => state.updateSessionTitle);

  // Local state
  const [currentResponse, setCurrentResponse] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const abortControllerRef = useRef<AbortController | null>(null);
  const lastMessageRef = useRef<string | null>(null);
  const streamBufferRef = useRef<StreamBuffer | null>(null);
  const pendingMessageIdRef = useRef<string | null>(null);
  const accumulatedTextRef = useRef('');

  // Get current session messages
  const session = getCurrentSession();
  const messages = session?.messages ?? [];

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
      streamBufferRef.current?.dispose();
    };
  }, []);

  /**
   * Handle text reveal from StreamBuffer
   */
  const handleTextReveal = useCallback(
    (messageId: string, _partId: string, revealedText: string, isComplete: boolean) => {
      setCurrentResponse(revealedText);

      if (isComplete && pendingMessageIdRef.current === messageId) {
        // Add the complete message to store
        addMessage('assistant', revealedText);
        setCurrentResponse('');
        pendingMessageIdRef.current = null;
      }
    },
    [addMessage]
  );

  /**
   * Handle thinking state from StreamBuffer
   */
  const handleThinking = useCallback((data: { stage: string } | null) => {
    setIsThinking(data !== null);
  }, []);

  /**
   * Handle done event from StreamBuffer
   */
  const handleDone = useCallback(
    (_data: Record<string, unknown>) => {
      setStreaming(false);
      setIsThinking(false);

      // If there's accumulated text that wasn't added yet
      if (accumulatedTextRef.current && pendingMessageIdRef.current) {
        addMessage('assistant', accumulatedTextRef.current);
        setCurrentResponse('');
        accumulatedTextRef.current = '';
        pendingMessageIdRef.current = null;
      }
    },
    [addMessage, setStreaming]
  );

  /**
   * Handle error from StreamBuffer
   */
  const handleError = useCallback(
    (message: string) => {
      setError(message);
      setStreaming(false);
      setIsThinking(false);
    },
    [setStreaming]
  );

  /**
   * Create and configure StreamBuffer
   */
  const createStreamBuffer = useCallback(() => {
    if (streamBufferRef.current) {
      streamBufferRef.current.dispose();
    }

    const callbacks: StreamBufferCallbacks = {
      onTextReveal: handleTextReveal,
      onThinking: handleThinking,
      onDone: handleDone,
      onError: handleError,
    };

    streamBufferRef.current = new StreamBuffer(callbacks, {
      tickMs: 30,
      charsPerTick: 1,
    });

    return streamBufferRef.current;
  }, [handleTextReveal, handleThinking, handleDone, handleError]);

  /**
   * Send a message
   */
  const sendMessageInternal = useCallback(
    async (content: string): Promise<void> => {
      // Validation
      const trimmed = content.trim();
      if (!trimmed) return;
      if (storeIsStreaming) return;
      if (!currentSessionId) return;

      // Reset state
      setError(null);
      lastMessageRef.current = trimmed;
      accumulatedTextRef.current = '';

      // Add user message
      addMessage('user', trimmed);

      // Auto-title session on first user message
      const session = getCurrentSession();
      if (session && session.messages.length === 0) {
        const autoTitle = trimmed.length > 50 ? trimmed.slice(0, 50) + '...' : trimmed;
        updateSessionTitle(session.id, autoTitle);
      }

      setStreaming(true);
      setIsThinking(false);

      // Create abort controller
      abortControllerRef.current = new AbortController();

      // Create stream buffer for typewriter effect
      const buffer = createStreamBuffer();
      const messageId = crypto.randomUUID();
      pendingMessageIdRef.current = messageId;

      try {
        // Build conversation history from session messages
        const currentMessages = useChatStore.getState().getCurrentSession()?.messages ?? [];
        const conversationHistory = currentMessages.map((m) => ({
          role: m.role as 'user' | 'assistant',
          content: m.content,
        }));

        const response = await apiSendMessage(trimmed, {
          sources: selectedSources.length > 0 ? selectedSources : undefined,
          conversationHistory: conversationHistory.length > 0 ? conversationHistory : undefined,
          signal: abortControllerRef.current.signal,
        });

        // Start the buffer tick loop BEFORE processing SSE stream
        // This ensures text is revealed progressively (typewriter effect)
        // rather than all at once after buffering
        buffer.start();

        // Process SSE stream
        await processSSEStream(response, (event: ChatEvent) => {
          switch (event.type) {
            case 'thinking':
              buffer.pushThinking({ stage: event.content || 'processing' });
              break;

            case 'text_delta':
              if (event.content) {
                buffer.pushText(messageId, event.content);
                accumulatedTextRef.current += event.content;
              }
              break;

            case 'done':
              buffer.sealText(messageId);
              buffer.pushDone();
              break;

            case 'error':
              buffer.pushError(event.content || 'Unknown error');
              break;
          }
        });

        // Wait for buffer to drain (all text revealed)
        await buffer.waitUntilDrained();
      } catch (err) {
        // Don't set error if aborted
        if (err instanceof Error && err.message === 'Aborted') {
          setStreaming(false);
          return;
        }

        const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
        setError(errorMessage);
        setStreaming(false);
        buffer.dispose();
      }
    },
    [
      storeIsStreaming,
      currentSessionId,
      addMessage,
      setStreaming,
      createStreamBuffer,
      selectedSources,
      getCurrentSession,
      updateSessionTitle,
    ]
  );

  /**
   * Stop current streaming
   */
  const stopStreaming = useCallback(() => {
    abortControllerRef.current?.abort();
    streamBufferRef.current?.dispose();
    setStreaming(false);
    setIsThinking(false);
    setCurrentResponse('');
  }, [setStreaming]);

  /**
   * Retry last failed message
   */
  const retry = useCallback(async (): Promise<void> => {
    if (!lastMessageRef.current) return;

    setError(null);
    await sendMessageInternal(lastMessageRef.current);
  }, [sendMessageInternal]);

  /**
   * Clear error state
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Send message wrapper
   */
  const sendMessage = useCallback(
    async (content: string): Promise<void> => {
      await sendMessageInternal(content);
    },
    [sendMessageInternal]
  );

  return {
    currentResponse,
    isStreaming: storeIsStreaming,
    isThinking,
    error,
    messages,
    sendMessage,
    stopStreaming,
    retry,
    clearError,
  };
}