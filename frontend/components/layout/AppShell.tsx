import Image from "next/image";
import Link from "next/link";
import type { ReactNode } from "react";
import { PrimaryNav } from "@/components/layout/PrimaryNav";
import { UserMenu } from "@/components/auth/UserMenu";
import type { User } from "@/types/api";

export function AppShell({
  children,
  user,
}: {
  children: ReactNode;
  user: User | null;
}) {
  return (
    <div className="min-h-screen bg-canvas">
      <header className="sticky top-0 z-50 border-b border-line bg-paper/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link className="flex min-w-0 items-center gap-3 font-bold" href="/">
            <Image
              alt="FIFA World Cup 2026"
              className="h-10 w-auto shrink-0 object-contain"
              height={2784}
              priority
              src="/fifa-world-cup-2026-logo.png"
              width={1800}
            />
            <span className="min-w-0">
              <span className="block truncate text-lg font-black uppercase leading-none">
                Mundial 2026
              </span>
              <span className="mt-0.5 block truncate text-xs font-semibold uppercase text-slate-500">
                Porra knockout
              </span>
            </span>
          </Link>
          <div className="hidden md:block">
            <PrimaryNav />
          </div>
          <UserMenu user={user} />
        </div>
        <div className="border-t border-line bg-paper/80 px-4 py-2 md:hidden">
          <div className="mx-auto max-w-5xl">
            <PrimaryNav />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6 sm:px-6">{children}</main>
    </div>
  );
}
