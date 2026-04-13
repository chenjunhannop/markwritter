const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export class ApiClientError extends Error {
  public readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}

export async function createApiError(
  response: Response,
): Promise<ApiClientError> {
  let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
  try {
    const body = await response.text();
    if (body) {
      errorMessage = `${response.status}: ${body}`;
    }
  } catch {
    // Ignore parsing errors
  }
  return new ApiClientError(response.status, errorMessage);
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw await createApiError(response);
  }

  return response.json();
}

export { API_BASE };
