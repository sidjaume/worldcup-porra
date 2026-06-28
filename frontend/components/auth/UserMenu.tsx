import { LogOut, UserCircle } from "lucide-react";
import type { User } from "@/types/api";
import { Button } from "@/components/ui/Button";

export function UserMenu({ user }: { user: User | null }) {
  return (
    <div className="flex items-center gap-3">
      <div className="hidden items-center gap-2 sm:flex">
        <UserCircle aria-hidden="true" size={20} />
        <span className="max-w-44 truncate text-sm font-medium">
          {user?.display_name ?? user?.email ?? "Signed in"}
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
