import { apiRequest } from "@/lib/api/client";
import { getBrowserApiBaseUrl, getFrontendBaseUrl } from "@/lib/config";
import type { AuthExchangeResponse, AuthTokenResponse } from "@/types/api";

export function googleLoginUrl(): string {
  const url = new URL(`${getBrowserApiBaseUrl()}/api/v1/auth/google/start`);
  url.searchParams.set("redirect_uri", `${getFrontendBaseUrl()}/auth/callback`);
  return url.toString();
}

export function exchangeAuthCode(code: string): Promise<AuthExchangeResponse> {
  return apiRequest<AuthExchangeResponse>("/api/v1/auth/exchange", {
    body: { code },
    method: "POST",
  });
}

export function refreshSession(refreshToken: string): Promise<AuthTokenResponse> {
  return apiRequest<AuthTokenResponse>("/api/v1/auth/refresh", {
    body: { refresh_token: refreshToken },
    method: "POST",
  });
}

export function logout(refreshToken: string): Promise<void> {
  return apiRequest<void>("/api/v1/auth/logout", {
    body: { refresh_token: refreshToken },
    method: "POST",
  });
}
