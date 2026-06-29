import { NextRequest, NextResponse } from "next/server";
import { exchangeAuthCode } from "@/lib/api/auth";
import { setSession } from "@/lib/auth/session";
import { getFrontendBaseUrl } from "@/lib/config";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");

  if (!code) {
    return frontendRedirect("/?auth_error=missing_code");
  }

  try {
    const payload = await exchangeAuthCode(code);
    await setSession(payload, payload.user);
    return frontendRedirect("/pools");
  } catch {
    return frontendRedirect("/?auth_error=exchange_failed");
  }
}

function frontendRedirect(path: string): NextResponse {
  return NextResponse.redirect(new URL(path, getFrontendBaseUrl()));
}
