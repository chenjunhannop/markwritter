export type LogLevel = "DEBUG" | "INFO" | "WARNING" | "ERROR";

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  source?: string;
}

export interface LogsResponse {
  logs: LogEntry[];
}
