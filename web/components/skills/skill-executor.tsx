/**
 * SkillExecutor Component
 *
 * Displays execution results or errors with copy functionality.
 */

import { useState, useCallback } from 'react';
import { Copy, Check, AlertCircle } from 'lucide-react';

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';

interface SkillExecutorProps {
  /** Execution result string */
  result: string | null;
  /** Error message if execution failed */
  error: string | null;
  /** Custom class name */
  className?: string;
}

/**
 * SkillExecutor displays execution results or errors.
 */
export function SkillExecutor({ result, error, className }: SkillExecutorProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    if (!result) return;

    try {
      await navigator.clipboard.writeText(result);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available, copy failed silently
      // User can manually select and copy the text
    }
  }, [result]);

  // Don't render if no result or error
  if (!result && !error) {
    return null;
  }

  // Error state
  if (error) {
    return (
      <Card className={cn('border-destructive', className)} data-testid="skill-executor">
        <CardHeader>
          <CardTitle className="text-destructive flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive" role="alert">
            <AlertDescription className="whitespace-pre-wrap">
              {error}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Success state with result
  return (
    <Card className={className} data-testid="skill-executor">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Result</CardTitle>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            aria-label={copied ? 'Copied' : 'Copy result'}
          >
            {copied ? (
              <>
                <Check className="h-4 w-4 mr-1" />
                Copied
              </>
            ) : (
              <>
                <Copy className="h-4 w-4 mr-1" />
                Copy
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div
          data-testid="execution-result"
          className="bg-muted rounded-md p-4 text-sm font-mono overflow-auto max-h-96 whitespace-pre-wrap"
        >
          {result}
        </div>
      </CardContent>
    </Card>
  );
}