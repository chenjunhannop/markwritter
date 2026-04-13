export interface SearchResult {
  id: string;
  title: string;
  content: string;
  score: number;
  source: string;
  highlights?: string[];
  metadata?: Record<string, unknown>;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  filters?: SearchFilters;
}

export interface SearchFilters {
  sources?: string[];
  dateRange?: {
    start: number;
    end: number;
  };
  tags?: string[];
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
  query: string;
  latency_ms: number;
}
