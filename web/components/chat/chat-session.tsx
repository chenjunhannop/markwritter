/**
 * ChatSession Component for Markwritter
 *
 * Renders chat messages with:
 * - User/assistant message styling
 * - Markdown support (using react-markdown for security)
 * - Streaming indicator
 * - Auto-scroll
 */

'use client';

import { useEffect, useRef, memo } from 'react';
import { Bot, User } from 'lucide-react';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';
import type { Message } from '@/lib/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatSessionProps {
  /** Messages to display */
  messages: Message[];
  /** Whether currently streaming */
  isStreaming?: boolean;
  /** Current streaming content */
  streamingContent?: string;
  /** Additional class names */
  className?: string;
}

/**
 * Format relative time
 */
function formatRelativeTime(timestamp: number): string {
  const now = Date.now();
  const diff = now - timestamp;

  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 1) {
    return new Date(timestamp).toLocaleDateString();
  }
  if (days === 1) {
    return '1d ago';
  }
  if (hours > 0) {
    return `${hours}h ago`;
  }
  if (minutes > 0) {
    return `${minutes}m ago`;
  }
  return 'just now';
}

/**
 * Safe markdown renderer using react-markdown
 * Automatically sanitizes HTML and prevents XSS attacks
 */
function renderMarkdown(content: string): React.ReactNode {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        // Style code blocks
        pre: ({ children }) => (
          <pre className="bg-muted p-2 rounded-md my-2 overflow-x-auto text-sm">
            {children}
          </pre>
        ),
        // Style inline code
        code: ({ className, children, ...props }) => {
          // Check if this is inline code (no className) or code block
          const isInline = !className;
          if (isInline) {
            return (
              <code className="bg-muted px-1 py-0.5 rounded text-sm" {...props}>
                {children}
              </code>
            );
          }
          return (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
        // Secure links: open in new tab with security attributes
        a: ({ href, children }) => (
          <a
            href={href}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary underline hover:text-primary/80"
          >
            {children}
          </a>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

/**
 * Single message component
 */
const MessageItem = memo(function MessageItem({
  message,
}: {
  message: Message;
}) {
  const isUser = message.role === 'user';

  return (
    <article
      className={cn(
        'flex gap-3 p-4',
        isUser && 'flex-row-reverse'
      )}
    >
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback
          className={cn(
            isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div
        className={cn(
          'flex flex-col gap-1 max-w-[80%]',
          isUser && 'items-end'
        )}
      >
        <div
          className={cn(
            'rounded-lg px-4 py-2',
            isUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted'
          )}
        >
          <div className="whitespace-pre-wrap break-words">
            {renderMarkdown(message.content)}
          </div>
        </div>
        <span className="text-xs text-muted-foreground">
          {formatRelativeTime(message.timestamp)}
        </span>
      </div>
    </article>
  );
});

/**
 * Streaming indicator component
 */
function StreamingIndicator({ content }: { content: string }) {
  return (
    <article
      className="flex gap-3 p-4"
      role="status"
      aria-live="polite"
    >
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className="bg-muted">
          <Bot className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>

      <div className="flex flex-col gap-1 max-w-[80%]">
        <div className="rounded-lg px-4 py-2 bg-muted">
          <div className="whitespace-pre-wrap break-words">
            {content}
            <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
          </div>
        </div>
      </div>
    </article>
  );
}

/**
 * Empty state component
 */
function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-muted-foreground p-8">
      <Bot className="h-12 w-12 mb-4 opacity-30" />
      <p className="text-lg font-medium mb-1">Start a conversation</p>
      <p className="text-sm text-center max-w-xs">
        Select sources from the left panel or type a message below.
      </p>
    </div>
  );
}

export function ChatSession({
  messages,
  isStreaming = false,
  streamingContent = '',
  className,
}: ChatSessionProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change or streaming content updates
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className={cn('flex flex-col h-full', className)}>
        <EmptyState />
      </div>
    );
  }

  return (
    <ScrollArea className={cn('flex-1', className)}>
      <div className="flex flex-col">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}

        {isStreaming && streamingContent && (
          <StreamingIndicator content={streamingContent} />
        )}

        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}