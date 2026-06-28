import type { Match, Prediction, TournamentStage } from "@/types/api";

export const STAGES: { label: string; value: TournamentStage }[] = [
  { label: "Round of 32", value: "round_of_32" },
  { label: "Round of 16", value: "round_of_16" },
  { label: "Quarter-finals", value: "quarter_final" },
  { label: "Semi-finals", value: "semi_final" },
  { label: "Final", value: "final" },
];

export function stageLabel(stage: TournamentStage): string {
  return STAGES.find((item) => item.value === stage)?.label ?? stage;
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function teamName(team: Match["home_team"]): string {
  return team?.name ?? "TBD";
}

export function scoreLine(match: Match): string {
  if (match.home_score === null || match.away_score === null) {
    return "vs";
  }
  return `${match.home_score} - ${match.away_score}`;
}

export function predictionsByMatch(predictions: Prediction[]): Map<string, Prediction> {
  return new Map(predictions.map((prediction) => [prediction.match_id, prediction]));
}
