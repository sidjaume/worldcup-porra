import { LogIn } from "lucide-react";
import { googleLoginUrl } from "@/lib/api/auth";

export function LoginButton() {
  return (
    <a
      className="inline-flex min-h-11 items-center justify-center gap-2 rounded-md border border-grass bg-grass px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#286b43]"
      href={googleLoginUrl()}
    >
      <LogIn aria-hidden="true" size={18} />
      Sign in with Google
    </a>
  );
}
