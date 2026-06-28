import { NextResponse } from "next/server";
import { logout } from "@/lib/api/auth";
import { clearSession, getSession } from "@/lib/auth/session";

export async function POST(request: Request) {
  const session = await getSession();
  if (session) {
    try {
      await logout(session.refreshToken);
    } catch {
      // Session cleanup should still happen if the backend session is already gone.
    }
  }
  await clearSession();
  return NextResponse.redirect(new URL("/", request.url), { status: 303 });
}
