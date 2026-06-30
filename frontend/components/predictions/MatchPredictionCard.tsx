import { Card } from "@/components/ui/Card";
import { formatDateTime, scoreLine, stageLabel, teamName, teamShortName } from "@/lib/format";
import type { Match, Prediction, TeamBrief } from "@/types/api";
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
    <Card className="overflow-hidden border-t-4 border-t-sky">
      <div className="grid gap-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="rounded-md bg-mint px-2 py-1 text-xs font-bold uppercase text-grass">
            {stageLabel(match.stage)} #{match.bracket_position}
          </span>
          <div className="flex flex-wrap items-center justify-end gap-2">
            {match.status === "in_progress" ? <LiveBadge minute={match.live_minute} /> : null}
            {match.status === "completed" ? (
              <span className="rounded-md bg-ink px-2 py-1 text-xs font-bold uppercase text-paper">
                Final
              </span>
            ) : null}
            <span className="text-sm text-slate-600">{formatDateTime(match.scheduled_at)}</span>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] sm:items-center">
          <TeamBlock team={match.home_team} align="right" />
          <MatchScore match={match} />
          <TeamBlock team={match.away_team} align="left" />
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

function TeamBlock({
  align,
  team,
}: {
  align: "left" | "right";
  team: TeamBrief | null;
}) {
  const name = teamName(team);
  const fallback = teamShortName(team);
  const flag = team?.flag_url;
  const direction = align === "right" ? "sm:flex-row-reverse sm:text-right" : "";

  return (
    <div className={`flex min-w-0 items-center gap-3 ${direction}`}>
      {flag ? (
        <span
          aria-label={`${name} flag`}
          className="size-9 shrink-0 rounded-md border border-line bg-white bg-cover bg-center"
          role="img"
          style={{ backgroundImage: `url(${flag})` }}
        />
      ) : (
        <span className="grid size-9 shrink-0 place-items-center rounded-md border border-line bg-white text-xs font-bold uppercase text-slate-600">
          {fallback}
        </span>
      )}
      <span className="min-w-0">
        <span className="block truncate text-base font-bold text-ink">{name}</span>
        <span className="block truncate text-xs font-semibold uppercase text-slate-500">
          {fallback}
        </span>
      </span>
    </div>
  );
}

function MatchScore({ match }: { match: Match }) {
  const isFinal = match.status === "completed";
  const isLive = match.status === "in_progress";
  const stateClasses = isLive
    ? "border-grass bg-mint text-grass"
    : isFinal
      ? "border-ink bg-ink text-paper"
      : "border-line bg-white text-ink";

  return (
    <div
      className={`mx-auto grid min-w-20 place-items-center rounded-md border px-4 py-2 text-center shadow-sm ${stateClasses}`}
    >
      <span className="text-xl font-black leading-none">{scoreLine(match)}</span>
      {isFinal ? (
        <span className="mt-1 text-[0.65rem] font-bold uppercase">Final result</span>
      ) : null}
      {match.status === "scheduled" ? (
        <span className="mt-1 text-[0.65rem] font-bold uppercase text-slate-500">
          Scheduled
        </span>
      ) : null}
    </div>
  );
}

function LiveBadge({ minute }: { minute: number | null }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-md bg-grass px-2 py-1 text-xs font-bold uppercase text-white">
      <span aria-hidden="true" className="size-2 rounded-full bg-white" />
      Live{minute !== null ? ` ${minute}'` : ""}
    </span>
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
