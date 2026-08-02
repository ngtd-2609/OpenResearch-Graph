import { afterEach, describe, expect, it, vi } from "vitest";

import { api, clearSession, hasSession, saveSession } from "./api";

afterEach(() => {
  clearSession();
  vi.restoreAllMocks();
});

describe("session helpers", () => {
  it("stores and clears a token pair", () => {
    saveSession({ access_token: "access", refresh_token: "refresh" });
    expect(hasSession()).toBe(true);
    clearSession();
    expect(hasSession()).toBe(false);
  });
});

describe("api", () => {
  it("parses backend detail into a typed error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Forbidden" }), {
          status: 403,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(api("/admin/integrations")).rejects.toEqual(
      expect.objectContaining({ message: "Forbidden", status: 403 }),
    );
  });

  it("adds the access token to authorized requests", async () => {
    saveSession({ access_token: "access", refresh_token: "refresh" });
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await api<{ ok: boolean }>("/health-like");
    const headers = new Headers(fetchMock.mock.calls[0][1]?.headers);
    expect(headers.get("Authorization")).toBe("Bearer access");
  });
});
