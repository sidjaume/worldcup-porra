import { AppShell } from "@/components/layout/AppShell";
import { InviteCodeForm } from "@/components/pools/InviteCodeForm";
import { ParticipantList } from "@/components/pools/ParticipantList";
import { PoolSubnav } from "@/components/pools/PoolSubnav";
import { PoolSettingsForm } from "@/components/pools/PoolSettingsForm";
import { RankingTable } from "@/components/rankings/RankingTable";
import { Card } from "@/components/ui/Card";
import { getPool, listParticipants } from "@/lib/api/pools";
import { getRankings } from "@/lib/api/rankings";
import { listMatches } from "@/lib/api/tournaments";
import { formatDateTime, stageLabel } from "@/lib/format";
import { requireSession } from "@/lib/auth/require-session";

export default async function PoolDetailPage({
  params,
}: {
  params: Promise<{ poolId: string }>;
}) {
  const { poolId } = await params;
  const session = await requireSession();
  const pool = await getPool(session.accessToken, poolId);
  const [participants, rankings, matches] = await Promise.all([
    listParticipants(session.accessToken, poolId),
    getRankings(session.accessToken, poolId),
    listMatches(session.accessToken, pool.tournament_id),
  ]);

  const nextMatches = matches
    .filter((match) => match.status === "scheduled")
    .sort((a, b) => Date.parse(a.scheduled_at) - Date.parse(b.scheduled_at))
    .slice(0, 4);

  return (
    <AppShell user={session.user}>
      <div className="grid gap-6">
        <header className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-grass">Pool</p>
            <h1 className="text-3xl font-bold">{pool.name}</h1>
            <p className="mt-2 text-slate-600">{pool.participant_count} participants</p>
          </div>
        </header>
        <PoolSubnav poolId={poolId} poolName={pool.name} />

        <div className="grid gap-4 lg:grid-cols-[1.4fr_0.8fr]">
          <Card>
            <h2 className="mb-4 text-lg font-semibold">Next matches</h2>
            <div className="grid gap-3">
              {nextMatches.length ? (
                nextMatches.map((match) => (
                  <div
                    className="rounded-md border border-line px-4 py-3"
                    key={match.id}
                  >
                    <div className="flex flex-wrap justify-between gap-2">
                      <p className="font-semibold">{stageLabel(match.stage)}</p>
                      <p className="text-sm text-slate-600">
                        {formatDateTime(match.scheduled_at)}
                      </p>
                    </div>
                    <p className="mt-1 text-sm text-slate-600">
                      {match.home_team?.name ?? "TBD"} vs {match.away_team?.name ?? "TBD"}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-600">No scheduled matches yet.</p>
              )}
            </div>
          </Card>
          <Card>
            <h2 className="mb-4 text-lg font-semibold">Invite code</h2>
            <InviteCodeForm poolId={poolId} />
          </Card>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <Card>
            <h2 className="mb-4 text-lg font-semibold">Participants</h2>
            <ParticipantList participants={participants} />
          </Card>
          <Card>
            <h2 className="mb-4 text-lg font-semibold">Pool settings</h2>
            <PoolSettingsForm pool={pool} />
          </Card>
        </div>

        <Card>
          <h2 className="mb-4 text-lg font-semibold">Rankings preview</h2>
          <RankingTable rows={rankings.slice(0, 5)} />
        </Card>
      </div>
    </AppShell>
  );
}
