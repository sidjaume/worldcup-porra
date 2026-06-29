import { afterEach, describe, expect, it, vi } from "vitest";
import { googleLoginUrl } from "@/lib/api/auth";

describe("googleLoginUrl", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("uses the browser-visible API base URL", () => {
    vi.stubEnv("API_BASE_URL", "http://backend:8000");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000");
    vi.stubEnv("FRONTEND_BASE_URL", "http://localhost:3000");

    const url = new URL(googleLoginUrl());

    expect(url.origin).toBe("http://localhost:8000");
    expect(url.pathname).toBe("/api/v1/auth/google/start");
    expect(url.searchParams.get("redirect_uri")).toBe(
      "http://localhost:3000/auth/callback",
    );
  });
});
