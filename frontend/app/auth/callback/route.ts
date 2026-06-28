import { NextRequest, NextResponse } from "next/server";
import { exchangeAuthCode } from "@/lib/api/auth";
import { setSession } from "@/lib/auth/session";

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");

  if (!code) {
    return NextResponse.redirect(new URL("/?auth_error=missing_code", request.url));
  }

  try {
    const payload = await exchangeAuthCode(code);
    await setSession(payload, payload.user);
    return NextResponse.redirect(new URL("/pools", request.url));
  } catch {
    return NextResponse.redirect(new URL("/?auth_error=exchange_failed", request.url));
  }
}
