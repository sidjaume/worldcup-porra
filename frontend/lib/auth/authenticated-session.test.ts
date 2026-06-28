import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "@/lib/api/client";
import {
  AuthenticationRequiredError,
  withAuthenticatedSession,
} from "@/lib/auth/authenticated-session";
import { refreshSession } from "@/lib/api/auth";
import { clearSession, getSession, setSession } from "@/lib/auth/session";

vi.mock("@/lib/api/auth", () => ({
  refreshSession: vi.fn(),
}));

vi.mock("@/lib/auth/session", () => ({
  clearSession: vi.fn(),
  getSession: vi.fn(),
  setSession: vi.fn(),
}));

const getSessionMock = vi.mocked(getSession);
const refreshSessionMock = vi.mocked(refreshSession);
const setSessionMock = vi.mocked(setSession);
const clearSessionMock = vi.mocked(clearSession);

describe("withAuthenticatedSession", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    getSessionMock.mockResolvedValue({
      accessToken: "old-access",
      refreshToken: "refresh-token",
      user: null,
    });
  });

  it("uses the existing access token when the request succeeds", async () => {
    const operation = vi.fn().mockResolvedValue("ok");

    await expect(withAuthenticatedSession(operation)).resolves.toBe("ok");

    expect(operation).toHaveBeenCalledOnce();
    expect(operation).toHaveBeenCalledWith("old-access");
    expect(refreshSessionMock).not.toHaveBeenCalled();
  });

  it("refreshes tokens and retries once after a 401", async () => {
    const operation = vi
      .fn()
      .mockRejectedValueOnce(new ApiError("Expired", 401, "unauthorized"))
      .mockResolvedValueOnce("ok");
    refreshSessionMock.mockResolvedValue({
      access_token: "new-access",
      expires_in: 900,
      refresh_token: "new-refresh",
      token_type: "bearer",
    });

    await expect(withAuthenticatedSession(operation)).resolves.toBe("ok");

    expect(refreshSessionMock).toHaveBeenCalledWith("refresh-token");
    expect(setSessionMock).toHaveBeenCalledWith(
      {
        access_token: "new-access",
        expires_in: 900,
        refresh_token: "new-refresh",
        token_type: "bearer",
      },
      undefined,
    );
    expect(operation).toHaveBeenNthCalledWith(2, "new-access");
  });

  it("clears the session when refresh fails", async () => {
    const operation = vi
      .fn()
      .mockRejectedValue(new ApiError("Expired", 401, "unauthorized"));
    refreshSessionMock.mockRejectedValue(
      new ApiError("Invalid refresh token", 401, "unauthorized"),
    );

    await expect(withAuthenticatedSession(operation)).rejects.toBeInstanceOf(
      AuthenticationRequiredError,
    );

    expect(clearSessionMock).toHaveBeenCalledOnce();
  });
});
