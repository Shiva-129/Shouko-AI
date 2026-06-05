import { useUpgradeModal } from "@/lib/hooks/useUpgradeModal";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RequestOptions = {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
};

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    const { createClient } = await import("@/lib/supabase");
    const supabase = createClient();
    if (supabase) {
      const { data } = await supabase.auth.getSession();
      if (data.session?.access_token) {
        return { Authorization: `Bearer ${data.session.access_token}` };
      }
    }
  } catch {
    // Not running in browser or Supabase not configured
  }
  return { Authorization: "Bearer mock-token" };
}

export async function api<T = unknown>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", body, headers = {} } = options;
  const authHeaders = await getAuthHeaders();

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const errorPayload = errorBody?.error || errorBody;
    if (response.status === 429) {
      if (typeof window !== "undefined") {
        useUpgradeModal.getState().open(
          errorPayload.title || "Usage Limit Reached",
          errorPayload.message || "You have hit the monthly usage threshold for your Free account."
        );
      }
      throw new ApiError(
        429,
        errorPayload.code || "USAGE_LIMIT_REACHED",
        errorPayload.message || "Usage limit reached",
        errorPayload.details
      );
    }
    if (response.status === 401) {
      if (typeof window !== "undefined") {
        const { createClient } = await import("@/lib/supabase");
        const supabase = createClient();
        if (supabase) {
          await supabase.auth.signOut();
        }
        window.location.href = "/login";
      }
      throw new ApiError(401, "UNAUTHORIZED", "Session expired");
    }
    throw new ApiError(
      response.status,
      errorPayload.code || "API_ERROR",
      errorPayload.message || `Request failed with status ${response.status}`,
      errorPayload.details
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export const apiClient = {
  get: <T>(path: string) => api<T>(path),
  post: <T>(path: string, body?: unknown) => api<T>(path, { method: "POST", body }),
  put: <T>(path: string, body?: unknown) => api<T>(path, { method: "PUT", body }),
  patch: <T>(path: string, body?: unknown) => api<T>(path, { method: "PATCH", body }),
  delete: <T>(path: string) => api<T>(path, { method: "DELETE" }),
};
