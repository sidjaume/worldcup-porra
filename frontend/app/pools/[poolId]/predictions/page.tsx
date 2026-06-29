import { AppShell } from "@/components/layout/AppShell";
import { MatchPredictionCard } from "@/components/predictions/MatchPredictionCard";
import { StageTabs } from "@/components/predictions/StageTabs";
import { PoolSubnav } from "@/components/pools/PoolSubnav";
import { getPool } from "@/lib/api/pools";
import { listPredictions } from "@/lib/api/predictions";
import { listMatches } from "@/lib/api/tournaments";
import { predictionsByMatch, STAGES } from "@/lib/format";
import { requireSession } from "@/lib/auth/require-session";
import type { TournamentStage } from "@/types/api";

export default async function PredictionsPage({
  params,
  searchParams,
}: {
  params: Promise<{ poolId: string }>;
  searchParams: Promise<{ stage?: TournamentStage }>;
}) {
  const { poolId } = await params;
  const { stage } = await searchParams;
  const activeStage = STAGES.some((item) => item.value === stage)
    ? stage!
    : "round_of_32";

  const session = await requireSession();
  const pool = await getPool(session.accessToken, poolId);
  const [matches, predictions] = await Promise.all([
    listMatches(session.accessToken, pool.tournament_id, activeStage),
    listPredictions(session.accessToken, poolId, { stage: activeStage }),
  ]);
  const predictionMap = predictionsByMatch(predictions);

  return (
    <AppShell user={session.user}>
      <div className="grid gap-6">
        <header>
          <p className="text-sm font-semibold uppercase tracking-wide text-grass">
            {pool.name}
          </p>
          <h1 className="text-3xl font-bold">Predictions</h1>
          <p className="mt-2 text-slate-600">
            Submit predicted scores before each match locks.
          </p>
        </header>
        <PoolSubnav poolId={poolId} poolName={pool.name} />
        <StageTabs activeStage={activeStage} basePath={`/pools/${poolId}/predictions`} />
        <div className="grid gap-4">
          {matches.length ? (
            matches.map((match) => (
              <MatchPredictionCard
                key={match.id}
                match={match}
                poolId={poolId}
                prediction={predictionMap.get(match.id)}
              />
            ))
          ) : (
            <p className="rounded-lg border border-line bg-white p-5 text-sm text-slate-600">
              No matches are available for this stage yet.
            </p>
          )}
        </div>
      </div>
    </AppShell>
  );
}
