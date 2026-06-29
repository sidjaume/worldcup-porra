import { NextRequest, NextResponse } from "next/server";
import { refreshSession } from "@/lib/api/auth";
import { clearSession, getSession, setSession } from "@/lib/auth/session";
import { getFrontendBaseUrl } from "@/lib/config";

export async function GET(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return frontendRedirect("/");
  }

  try {
    const tokens = await refreshSession(session.refreshToken);
    await setSession(tokens, session.user ?? undefined);
    return frontendRedirect(safeNextPath(request));
  } catch {
    await clearSession();
    return frontendRedirect("/");
  }
}

function frontendRedirect(path: string): NextResponse {
  return NextResponse.redirect(new URL(path, getFrontendBaseUrl()));
}

function safeNextPath(request: NextRequest): string {
  const next = request.nextUrl.searchParams.get("next");
  if (next && next.startsWith("/") && !next.startsWith("//")) {
    return next;
  }
  return "/pools";
}
