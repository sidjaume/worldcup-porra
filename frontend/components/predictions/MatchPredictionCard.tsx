import { Calendar, Lock, Target } from "lucide-react";
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
    <article className="overflow-hidden rounded-lg border border-line bg-paper shadow-soft transition hover:border-grass/40">
      <div className="flex items-center justify-between gap-3 border-b border-line bg-slate-50/80 px-4 py-2">
        <span className="truncate text-xs font-semibold uppercase tracking-wide text-slate-500">
          {stageLabel(match.stage)}
        </span>
        <div className="flex shrink-0 items-center gap-2">
          <Calendar aria-hidden="true" size={12} className="text-slate-500" />
          <span className="text-xs font-medium text-slate-500">
            {formatDateTime(match.scheduled_at)}
          </span>
        </div>
      </div>

      <div className="grid gap-4 px-4 py-5">
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
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] sm:items-center">
          <TeamBlock team={match.home_team} align="right" />
          <MatchScore match={match} />
          <TeamBlock team={match.away_team} align="left" />
        </div>
        {prediction ? (
          <PredictionSummary match={match} prediction={prediction} />
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
          <p className="inline-flex items-center gap-2 rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-slate-600">
            <Lock aria-hidden="true" size={14} />
            {readOnlyMessage(match, prediction)}
          </p>
        )}
      </div>
    </article>
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
    <div className={`flex min-w-0 flex-col items-center gap-2 text-center sm:flex-row ${direction}`}>
      {flag ? (
        <span
          aria-label={`${name} flag`}
          className="size-11 shrink-0 rounded-md border border-line bg-white bg-cover bg-center shadow-sm"
          role="img"
          style={{ backgroundImage: `url(${flag})` }}
        />
      ) : (
        <span className="grid size-11 shrink-0 place-items-center rounded-md border border-line bg-white text-xs font-bold uppercase text-slate-600 shadow-sm">
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
      <span className="text-3xl font-black leading-none">{scoreLine(match)}</span>
      {isFinal ? (
        <span className="mt-1 text-[0.65rem] font-bold uppercase">Final</span>
      ) : null}
      {match.status === "scheduled" ? (
        <span className="mt-1 text-[0.65rem] font-bold uppercase text-slate-500">VS</span>
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

function PredictionSummary({
  match,
  prediction,
}: {
  match: Match;
  prediction: Prediction;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-line bg-slate-50 px-3 py-2 text-sm">
      <span className="inline-flex items-center gap-2 font-medium text-slate-600">
        <Target aria-hidden="true" size={14} />
        Your pick
      </span>
      <span className="font-mono text-base font-black text-ink">
        {prediction.predicted_home_goals} - {prediction.predicted_away_goals}
      </span>
      {prediction.predicted_winner_team_id ? (
        <span className="text-xs font-medium text-slate-500">
          {predictionWinnerName(match, prediction)} advances
        </span>
      ) : null}
      {prediction.score ? (
        <span className="rounded-md border border-grass/25 bg-mint px-2 py-1 text-xs font-bold text-grass">
          {prediction.score.points} pts
        </span>
      ) : null}
    </div>
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
