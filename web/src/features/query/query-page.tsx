import { useMutation } from "@tanstack/react-query";
import { AlertCircle, FileText, Loader2, Search, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import type { SearchResult } from "@/types/query";
import { searchNotes } from "./query-api";

const SEARCH_MODES = [
  { value: "hybrid", label: "Hybrid" },
  { value: "keyword", label: "Keyword" },
  { value: "semantic", label: "Semantic" },
] as const;

export function QueryPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<string>("hybrid");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (q: string) => searchNotes(q, mode, 20),
    onSuccess: (data) => {
      setResults(data.results);
    },
    onError: () => {
      toast.error("Search failed. Please try again.");
    },
  });

  const handleSearch = () => {
    const trimmed = query.trim();
    if (!trimmed) return;
    mutation.mutate(trimmed);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    setExpandedId(null);
  };

  const hasSearched = mutation.isIdle ? results.length > 0 : mutation.isSuccess;
  const isEmpty = hasSearched && results.length === 0;

  return (
    <div className="flex h-full flex-col gap-4 p-4 md:p-6">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search your notes..."
            className="pl-9 pr-9"
          />
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <Select value={mode} onValueChange={setMode}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SEARCH_MODES.map((m) => (
              <SelectItem key={m.value} value={m.value}>
                {m.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          onClick={handleSearch}
          disabled={mutation.isPending || !query.trim()}
        >
          {mutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Search className="h-4 w-4" />
          )}
          Search
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {mutation.isPending && (
          <div className="space-y-3">
            <div className="rounded-xl border p-4 space-y-2">
              <Skeleton className="h-5 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
            <div className="rounded-xl border p-4 space-y-2">
              <Skeleton className="h-5 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
            <div className="rounded-xl border p-4 space-y-2">
              <Skeleton className="h-5 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
            <div className="rounded-xl border p-4 space-y-2">
              <Skeleton className="h-5 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-2/3" />
            </div>
          </div>
        )}

        {mutation.isError && (
          <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
            <AlertCircle className="h-10 w-10 text-destructive" />
            <p className="text-sm text-muted-foreground">
              Something went wrong. Please try again.
            </p>
            <Button variant="outline" onClick={handleSearch}>
              Retry
            </Button>
          </div>
        )}

        {!mutation.isPending && !mutation.isError && !hasSearched && (
          <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
            <Search className="h-10 w-10 text-muted-foreground" />
            <p className="text-muted-foreground">Search your notes...</p>
          </div>
        )}

        {isEmpty && (
          <div className="flex flex-col items-center justify-center gap-3 py-20 text-center">
            <FileText className="h-10 w-10 text-muted-foreground" />
            <p className="text-muted-foreground">No results found</p>
          </div>
        )}

        {hasSearched && results.length > 0 && (
          <div className="space-y-3">
            {results.map((result) => {
              const isExpanded = expandedId === result.id;
              return (
                <Card
                  key={result.id}
                  className="cursor-pointer transition-colors hover:bg-accent/50"
                  onClick={() => setExpandedId(isExpanded ? null : result.id)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-base">
                        {result.title}
                      </CardTitle>
                      <Badge variant="secondary" className="shrink-0">
                        {result.score.toFixed(2)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p
                      className={
                        isExpanded
                          ? "text-sm text-muted-foreground whitespace-pre-wrap"
                          : "text-sm text-muted-foreground line-clamp-2"
                      }
                    >
                      {result.content}
                    </p>
                    {Array.isArray(result.metadata?.tags) && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {(result.metadata.tags as string[]).map(
                          (tag: string) => (
                            <Badge
                              key={tag}
                              variant="outline"
                              className="text-xs"
                            >
                              {tag}
                            </Badge>
                          ),
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
