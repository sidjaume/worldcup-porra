import { NextResponse } from "next/server";
import { logout } from "@/lib/api/auth";
import { clearSession, getSession } from "@/lib/auth/session";
import { getFrontendBaseUrl } from "@/lib/config";

export async function POST() {
  const session = await getSession();
  if (session) {
    try {
      await logout(session.refreshToken);
    } catch {
      // Session cleanup should still happen if the backend session is already gone.
    }
  }
  await clearSession();
  return NextResponse.redirect(new URL("/", getFrontendBaseUrl()), { status: 303 });
}
