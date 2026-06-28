import { AppShell } from "@/components/layout/AppShell";
import { RankingTable } from "@/components/rankings/RankingTable";
import { Card } from "@/components/ui/Card";
import { getPool } from "@/lib/api/pools";
import { getRankings } from "@/lib/api/rankings";
import { requireSession } from "@/lib/auth/require-session";

export default async function RankingsPage({
  params,
}: {
  params: Promise<{ poolId: string }>;
}) {
  const { poolId } = await params;
  const session = await requireSession();
  const [pool, rankings] = await Promise.all([
    getPool(session.accessToken, poolId),
    getRankings(session.accessToken, poolId),
  ]);

  return (
    <AppShell user={session.user}>
      <div className="grid gap-6">
        <header>
          <p className="text-sm font-semibold uppercase tracking-wide text-grass">
            {pool.name}
          </p>
          <h1 className="text-3xl font-bold">Rankings</h1>
          <p className="mt-2 text-slate-600">
            Rankings are read directly from backend-scored predictions.
          </p>
        </header>
        <Card>
          <RankingTable rows={rankings} />
        </Card>
      </div>
    </AppShell>
  );
}
