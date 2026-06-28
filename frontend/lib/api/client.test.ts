import { afterEach, describe, expect, it, vi } from "vitest";
import { apiRequest, ApiError } from "@/lib/api/client";

describe("apiRequest", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it("normalizes documented backend error payloads", async () => {
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.example.com");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "prediction_locked",
              message: "Predictions are closed for this match.",
              details: {},
            },
          }),
          { status: 409, statusText: "Conflict" },
        ),
      ),
    );

    await expect(apiRequest("/api/v1/pools")).rejects.toMatchObject({
      code: "prediction_locked",
      message: "Predictions are closed for this match.",
      status: 409,
    } satisfies Partial<ApiError>);
  });

  it("sends bearer tokens and JSON request bodies", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ id: "pool-1" }), {
        headers: { "content-type": "application/json" },
        status: 200,
      }),
    );
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.example.com");
    vi.stubGlobal("fetch", fetchMock);

    await apiRequest("/api/v1/pools", {
      accessToken: "access-token",
      body: { name: "Office Pool" },
      method: "POST",
    });

    const [, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect(init.method).toBe("POST");
    expect(init.body).toBe(JSON.stringify({ name: "Office Pool" }));
    expect(new Headers(init.headers).get("authorization")).toBe(
      "Bearer access-token",
    );
  });
});
