import { stageLabel, teamName } from "@/lib/format";
import type { Match, MatchStatus } from "@/types/api";

const FRESHNESS_WINDOW_MINUTES = 30;

export function latestSyncDate(matches: Match[]): Date | null {
  const dates = matches
    .map((match) => {
      if (!match.provider_last_synced_at) {
        return null;
      }
      const date = new Date(match.provider_last_synced_at);
      return Number.isNaN(date.getTime()) ? null : date;
    })
    .filter((date): date is Date => date !== null);

  if (!dates.length) {
    return null;
  }
  return new Date(Math.max(...dates.map((date) => date.getTime())));
}

export function syncStatus(
  latestProviderSyncAt: Date | null,
): "Fresh" | "Not synced" | "Stale" {
  if (!latestProviderSyncAt) {
    return "Not synced";
  }
  return isStale(latestProviderSyncAt) ? "Stale" : "Fresh";
}

export function isStale(date: Date): boolean {
  const ageMs = Date.now() - date.getTime();
  return ageMs > FRESHNESS_WINDOW_MINUTES * 60 * 1000;
}

export type SourceFilter = "all" | "manual" | "not_synced" | "provider";

export function filterMatches(
  matches: Match[],
  statusFilter: "all" | MatchStatus,
  sourceFilter: SourceFilter,
  query: string,
): Match[] {
  const normalizedQuery = query.trim().toLowerCase();

  return matches.filter((match) => {
    if (statusFilter !== "all" && match.status !== statusFilter) {
      return false;
    }
    if (sourceFilter === "manual" && !match.admin_override) {
      return false;
    }
    if (sourceFilter === "not_synced" && match.provider_last_synced_at) {
      return false;
    }
    if (
      sourceFilter === "provider" &&
      (match.admin_override || !match.provider_last_synced_at)
    ) {
      return false;
    }
    if (!normalizedQuery) {
      return true;
    }
    const haystack = [
      teamName(match.home_team),
      teamName(match.away_team),
      `#${match.bracket_position}`,
      String(match.bracket_position),
      stageLabel(match.stage),
    ]
      .join(" ")
      .toLowerCase();
    return haystack.includes(normalizedQuery);
  });
}

