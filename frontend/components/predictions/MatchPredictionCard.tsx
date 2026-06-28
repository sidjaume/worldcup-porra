import { Card } from "@/components/ui/Card";
import { formatDateTime, scoreLine, stageLabel, teamName } from "@/lib/format";
import type { Match, Prediction } from "@/types/api";
import { PredictionForm } from "@/components/predictions/PredictionForm";

export function MatchPredictionCard({
  match,
  poolId,
  prediction,
}: {
  match: Match;
  poolId: string;
  prediction?: Prediction;
}) {
  const isScheduled = match.status === "scheduled";

  return (
    <Card>
      <div className="grid gap-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="rounded-md bg-mint px-2 py-1 text-xs font-semibold text-grass">
            {stageLabel(match.stage)} #{match.bracket_position}
          </span>
          <span className="text-sm text-slate-600">{formatDateTime(match.scheduled_at)}</span>
        </div>
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
          <p className="text-right font-semibold">{teamName(match.home_team)}</p>
          <p className="rounded-md bg-slate-100 px-3 py-2 text-sm font-bold">
            {scoreLine(match)}
          </p>
          <p className="font-semibold">{teamName(match.away_team)}</p>
        </div>
        {prediction ? (
          <p className="text-sm text-slate-600">
            Your pick: {prediction.predicted_home_goals} - {prediction.predicted_away_goals}
            {prediction.score ? `, ${prediction.score.points} pts` : ""}
          </p>
        ) : null}
        {isScheduled ? (
          <PredictionForm matchId={match.id} poolId={poolId} prediction={prediction} />
        ) : (
          <p className="rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-600">
            Predictions are read-only for this match.
          </p>
        )}
      </div>
    </Card>
  );
}
