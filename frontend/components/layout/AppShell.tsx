import Link from "next/link";
import type { ReactNode } from "react";
import { Trophy } from "lucide-react";
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
    <div className="min-h-screen">
      <header className="border-b border-line bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link className="flex min-w-0 items-center gap-2 font-bold" href="/">
            <span className="grid size-9 shrink-0 place-items-center rounded-md bg-mint text-grass">
              <Trophy aria-hidden="true" size={20} />
            </span>
            <span className="truncate">World Cup Pool</span>
          </Link>
          <div className="hidden md:block">
            <PrimaryNav />
          </div>
          <UserMenu user={user} />
        </div>
        <div className="border-t border-line px-4 py-2 md:hidden">
          <div className="mx-auto max-w-7xl">
            <PrimaryNav />
          </div>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">{children}</main>
    </div>
  );
}
