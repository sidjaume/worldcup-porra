import { cookies } from "next/headers";
import type { AuthTokenResponse, User } from "@/types/api";

const ACCESS_TOKEN_COOKIE = "wcp_access_token";
const REFRESH_TOKEN_COOKIE = "wcp_refresh_token";
const USER_COOKIE = "wcp_user";

export type Session = {
  accessToken: string;
  refreshToken: string;
  user: User | null;
};

const cookieOptions = {
  httpOnly: true,
  sameSite: "lax" as const,
  secure: process.env.NODE_ENV === "production",
  path: "/",
};

export async function getSession(): Promise<Session | null> {
  const store = await cookies();
  const accessToken = store.get(ACCESS_TOKEN_COOKIE)?.value;
  const refreshToken = store.get(REFRESH_TOKEN_COOKIE)?.value;

  if (!accessToken || !refreshToken) {
    return null;
  }

  return {
    accessToken,
    refreshToken,
    user: parseUserCookie(store.get(USER_COOKIE)?.value),
  };
}

export async function setSession(tokens: AuthTokenResponse, user?: User): Promise<void> {
  const store = await cookies();
  store.set(ACCESS_TOKEN_COOKIE, tokens.access_token, {
    ...cookieOptions,
    maxAge: tokens.expires_in,
  });
  store.set(REFRESH_TOKEN_COOKIE, tokens.refresh_token, {
    ...cookieOptions,
    maxAge: 60 * 60 * 24 * 30,
  });
  if (user) {
    store.set(USER_COOKIE, JSON.stringify(user), {
      ...cookieOptions,
      httpOnly: false,
      maxAge: 60 * 60 * 24 * 30,
    });
  }
}

export async function clearSession(): Promise<void> {
  const store = await cookies();
  store.delete(ACCESS_TOKEN_COOKIE);
  store.delete(REFRESH_TOKEN_COOKIE);
  store.delete(USER_COOKIE);
}

function parseUserCookie(value: string | undefined): User | null {
  if (!value) {
    return null;
  }
  try {
    return JSON.parse(value) as User;
  } catch {
    return null;
  }
}
