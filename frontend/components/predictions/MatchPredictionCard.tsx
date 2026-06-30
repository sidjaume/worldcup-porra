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
  const homeTeamName = teamName(match.home_team);
  const awayTeamName = teamName(match.away_team);
  const canEdit = match.status === "scheduled" && (!prediction || prediction.status === "editable");

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
          <p className="text-right font-semibold">{homeTeamName}</p>
          <p className="rounded-md bg-slate-100 px-3 py-2 text-sm font-bold">
            {scoreLine(match)}
          </p>
          <p className="font-semibold">{awayTeamName}</p>
        </div>
        {prediction ? (
          <p className="text-sm text-slate-600">
            Your pick: {prediction.predicted_home_goals} - {prediction.predicted_away_goals}
            {prediction.predicted_winner_team_id
              ? `, ${predictionWinnerName(match, prediction)} advances`
              : ""}
            {prediction.score ? `, ${prediction.score.points} pts` : ""}
          </p>
        ) : null}
        {canEdit ? (
          <PredictionForm
            awayTeamName={awayTeamName}
            awayTeamId={match.away_team?.id ?? null}
            homeTeamName={homeTeamName}
            homeTeamId={match.home_team?.id ?? null}
            matchId={match.id}
            poolId={poolId}
            prediction={prediction}
          />
        ) : (
          <p className="rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-600">
            {readOnlyMessage(match, prediction)}
          </p>
        )}
      </div>
    </Card>
  );
}

function predictionWinnerName(match: Match, prediction: Prediction): string {
  if (prediction.predicted_winner_team_id === match.home_team?.id) {
    return teamName(match.home_team);
  }
  if (prediction.predicted_winner_team_id === match.away_team?.id) {
    return teamName(match.away_team);
  }
  return "Selected team";
}

function readOnlyMessage(match: Match, prediction?: Prediction): string {
  if (match.status === "locked") {
    return "Predictions are closed because this match is locked.";
  }
  if (match.status === "in_progress") {
    return "Predictions are closed while this match is in progress.";
  }
  if (prediction?.status === "locked") {
    return "Your prediction is locked for this match.";
  }
  if (prediction?.status === "scored") {
    return "This prediction has been scored.";
  }
  if (match.status === "completed") {
    return "Predictions are read-only after the match is completed.";
  }
  if (match.status === "cancelled") {
    return "Predictions are closed because this match was cancelled.";
  }
  return "Predictions are read-only for this match.";
}
