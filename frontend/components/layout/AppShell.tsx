import Link from "next/link";
import type { ReactNode } from "react";
import { Trophy } from "lucide-react";
import { UserMenu } from "@/components/auth/UserMenu";
import type { User } from "@/types/api";

const navItems = [
  { href: "/pools", label: "Pools" },
  { href: "/profile", label: "Profile" },
];

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
          <Link className="flex items-center gap-2 font-bold" href="/">
            <span className="grid size-9 place-items-center rounded-md bg-mint text-grass">
              <Trophy aria-hidden="true" size={20} />
            </span>
            <span>World Cup Pool</span>
          </Link>
          <nav className="hidden items-center gap-2 md:flex">
            {navItems.map((item) => (
              <Link
                className="rounded-md px-3 py-2 text-sm font-medium text-ink hover:bg-mint"
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            ))}
          </nav>
          <UserMenu user={user} />
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">{children}</main>
    </div>
  );
}
