export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface AppSettings {
  theme?: "light" | "dark" | "system";
  language?: string;
  vault_path?: string;
  api_url?: string;
  llm_model?: string;
  api_key_set?: boolean;
  [key: string]: unknown;
}

export interface SettingsUpdateResponse {
  success: boolean;
  settings: AppSettings;
}
