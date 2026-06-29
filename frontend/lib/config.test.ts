import { afterEach, describe, expect, it, vi } from "vitest";
import { getApiBaseUrl, getBrowserApiBaseUrl } from "@/lib/config";

describe("frontend config", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("prefers API_BASE_URL for server-side API calls", () => {
    vi.stubEnv("API_BASE_URL", "http://backend:8000/");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/");

    expect(getApiBaseUrl()).toBe("http://backend:8000");
  });

  it("uses NEXT_PUBLIC_API_BASE_URL for browser-visible API URLs", () => {
    vi.stubEnv("API_BASE_URL", "http://backend:8000/");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/");

    expect(getBrowserApiBaseUrl()).toBe("http://localhost:8000");
  });
});
