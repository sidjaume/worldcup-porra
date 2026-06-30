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
  const openMatches = matches.filter((match) => match.status === "scheduled").length;
  const pendingPredictions = matches.filter(
    (match) => match.status === "scheduled" && !predictionMap.has(match.id),
  ).length;

  return (
    <AppShell user={session.user}>
      <div className="mx-auto grid max-w-2xl gap-5">
        <header>
          <p className="text-sm font-semibold uppercase tracking-wide text-grass">
            {pool.name}
          </p>
          <h1 className="text-3xl font-black uppercase leading-none">Partidos</h1>
        </header>
        <PoolSubnav poolId={poolId} poolName={pool.name} />
        <div className="flex gap-6 overflow-x-auto border-y border-line bg-white/60 px-1 py-3">
          {[
            { label: "Abiertos", value: openMatches },
            { label: "Pendientes", value: pendingPredictions },
            { label: "Guardadas", value: predictions.length },
          ].map((item) => (
            <div className="shrink-0" key={item.label}>
              <p className="text-xs font-medium text-slate-500">{item.label}</p>
              <p className="font-mono text-sm font-black text-ink">{item.value}</p>
            </div>
          ))}
        </div>
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
