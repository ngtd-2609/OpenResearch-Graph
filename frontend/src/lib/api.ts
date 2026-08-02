export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const ACCESS_TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
export const SESSION_EVENT = "openresearch:session-change";
let refreshPromise: Promise<string | null> | null = null;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

function storage(): Storage | null {
  return typeof window === "undefined" ? null : window.localStorage;
}

export function accessToken(): string | null {
  return storage()?.getItem(ACCESS_TOKEN_KEY) ?? null;
}

export function hasSession(): boolean {
  return Boolean(accessToken() || storage()?.getItem(REFRESH_TOKEN_KEY));
}

export function saveSession(tokens: Pick<TokenResponse, "access_token" | "refresh_token">): void {
  storage()?.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
  storage()?.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  if (typeof window !== "undefined") window.dispatchEvent(new Event(SESSION_EVENT));
}

export function clearSession(): void {
  storage()?.removeItem(ACCESS_TOKEN_KEY);
  storage()?.removeItem(REFRESH_TOKEN_KEY);
  if (typeof window !== "undefined") window.dispatchEvent(new Event(SESSION_EVENT));
}

function errorMessage(payload: unknown, fallback: string): string {
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item === "object" && item !== null && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : String(item),
        )
        .join("; ");
    }
  }
  return fallback;
}

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = storage()?.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) return null;
  if (!refreshPromise) {
    refreshPromise = fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
      .then(async (response) => {
        if (!response.ok) {
          clearSession();
          return null;
        }
        const tokens = (await response.json()) as TokenResponse;
        saveSession(tokens);
        return tokens.access_token;
      })
      .catch(() => {
        clearSession();
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

async function request<T>(path: string, options: RequestInit, retryOnUnauthorized: boolean): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData) && options.body !== undefined) {
    headers.set("Content-Type", "application/json");
  }
  const token = accessToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });
  if (response.status === 401 && retryOnUnauthorized && !path.startsWith("/auth/")) {
    const refreshedToken = await refreshAccessToken();
    if (refreshedToken) return request<T>(path, options, false);
  }
  if (!response.ok) {
    const payload: unknown = await response.json().catch(() => undefined);
    throw new ApiError(errorMessage(payload, response.statusText || "Request failed"), response.status, payload);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  return request<T>(path, options, true);
}

export async function logout(): Promise<void> {
  const refreshToken = storage()?.getItem(REFRESH_TOKEN_KEY);
  try {
    if (refreshToken) {
      await api("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    }
  } finally {
    clearSession();
  }
}
