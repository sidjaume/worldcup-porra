import { NextRequest, NextResponse } from "next/server";
import { refreshSession } from "@/lib/api/auth";
import { clearSession, getSession, setSession } from "@/lib/auth/session";

export async function GET(request: NextRequest) {
  const session = await getSession();
  if (!session) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  try {
    const tokens = await refreshSession(session.refreshToken);
    await setSession(tokens, session.user ?? undefined);
    return NextResponse.redirect(new URL(safeNextPath(request), request.url));
  } catch {
    await clearSession();
    return NextResponse.redirect(new URL("/", request.url));
  }
}

function safeNextPath(request: NextRequest): string {
  const next = request.nextUrl.searchParams.get("next");
  if (next && next.startsWith("/") && !next.startsWith("//")) {
    return next;
  }
  return "/pools";
}
