"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, ClipboardList, LayoutDashboard } from "lucide-react";

const links = [
  { icon: LayoutDashboard, label: "Overview", path: "" },
  { icon: ClipboardList, label: "Predictions", path: "/predictions" },
  { icon: BarChart3, label: "Rankings", path: "/rankings" },
];

export function PoolSubnav({ poolId, poolName }: { poolId: string; poolName: string }) {
  const pathname = usePathname();
  const basePath = `/pools/${poolId}`;

  return (
    <div className="grid gap-3 rounded-lg border border-line bg-white p-3 shadow-soft">
      <div className="min-w-0">
        <p className="text-xs font-semibold uppercase tracking-wide text-grass">Current pool</p>
        <p className="truncate text-sm font-semibold text-ink">{poolName}</p>
      </div>
      <nav aria-label={`${poolName} navigation`} className="flex gap-2 overflow-x-auto">
        {links.map((link) => {
          const href = `${basePath}${link.path}`;
          const isActive = pathname === href;
          const Icon = link.icon;

          return (
            <Link
              aria-current={isActive ? "page" : undefined}
              className={`inline-flex min-h-10 items-center gap-2 whitespace-nowrap rounded-md border px-3 py-2 text-sm font-semibold transition ${
                isActive
                  ? "border-grass bg-grass text-white"
                  : "border-line bg-white text-ink hover:bg-mint hover:text-grass"
              }`}
              href={href}
              key={href}
            >
              <Icon aria-hidden="true" size={16} />
              {link.label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
