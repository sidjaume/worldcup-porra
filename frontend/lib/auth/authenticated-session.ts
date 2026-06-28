import { ApiError } from "@/lib/api/client";
import { refreshSession } from "@/lib/api/auth";
import { clearSession, getSession, setSession } from "@/lib/auth/session";
import type { AuthTokenResponse } from "@/types/api";
import type { Session } from "@/lib/auth/session";

export class AuthenticationRequiredError extends Error {
  constructor(message = "Authentication is required.") {
    super(message);
    this.name = "AuthenticationRequiredError";
  }
}

export async function getAuthenticatedSession(): Promise<Session> {
  const session = await getSession();
  if (!session) {
    throw new AuthenticationRequiredError();
  }
  return session;
}

export async function withAuthenticatedSession<T>(
  operation: (accessToken: string) => Promise<T>,
): Promise<T> {
  const session = await getAuthenticatedSession();

  try {
    return await operation(session.accessToken);
  } catch (error) {
    if (!isUnauthorized(error)) {
      throw error;
    }
  }

  let tokens: AuthTokenResponse;
  try {
    tokens = await refreshSession(session.refreshToken);
  } catch (error) {
    if (isUnauthorized(error)) {
      await clearSession();
      throw new AuthenticationRequiredError("Session expired.");
    }
    throw error;
  }

  await setSession(tokens, session.user ?? undefined);

  try {
    return await operation(tokens.access_token);
  } catch (error) {
    if (isUnauthorized(error)) {
      await clearSession();
      throw new AuthenticationRequiredError("Session expired.");
    }
    throw error;
  }
}

export function isUnauthorized(error: unknown): boolean {
  return error instanceof ApiError && error.status === 401;
}
