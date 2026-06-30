import { LogOut, UserCircle } from "lucide-react";
import type { User } from "@/types/api";
import { Button } from "@/components/ui/Button";

export function UserMenu({ user }: { user: User | null }) {
  const name = user?.display_name ?? user?.email ?? "Signed in";
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="flex items-center gap-3">
      <div className="hidden items-center gap-2 sm:flex">
        <span className="grid size-8 place-items-center rounded-full border border-grass/25 bg-mint text-xs font-black text-grass">
          {initials || <UserCircle aria-hidden="true" size={18} />}
        </span>
        <span className="max-w-44 truncate text-sm font-medium">
          {name}
        </span>
      </div>
      <form action="/logout" method="post">
        <Button aria-label="Sign out" type="submit" variant="secondary">
          <LogOut aria-hidden="true" size={16} />
          <span className="hidden sm:inline">Sign out</span>
        </Button>
      </form>
    </div>
  );
}
