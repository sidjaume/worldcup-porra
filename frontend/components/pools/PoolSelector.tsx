import Link from "next/link";
import { Users } from "lucide-react";
import type { PoolSummary } from "@/types/api";
import { Card } from "@/components/ui/Card";

export function PoolSelector({ pools }: { pools: PoolSummary[] }) {
  if (pools.length === 0) {
    return (
      <Card>
        <p className="text-sm text-slate-600">You are not in a pool yet.</p>
      </Card>
    );
  }

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {pools.map((pool) => (
        <Link href={`/pools/${pool.id}`} key={pool.id}>
          <Card className="h-full transition hover:border-grass">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="font-semibold">{pool.name}</h3>
                <p className="mt-1 text-sm capitalize text-slate-600">{pool.role}</p>
              </div>
              <span className="inline-flex items-center gap-1 rounded-md bg-mint px-2 py-1 text-sm font-medium text-grass">
                <Users aria-hidden="true" size={15} />
                {pool.participant_count}
              </span>
            </div>
          </Card>
        </Link>
      ))}
    </div>
  );
}
