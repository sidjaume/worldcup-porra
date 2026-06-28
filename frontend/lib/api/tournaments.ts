import { apiRequest } from "@/lib/api/client";
import type { ID, Match, Team, Tournament, TournamentStage } from "@/types/api";

export function listTournaments(accessToken: string): Promise<Tournament[]> {
  return apiRequest<Tournament[]>("/api/v1/tournaments", { accessToken });
}

export function listTeams(accessToken: string, tournamentId: ID): Promise<Team[]> {
  return apiRequest<Team[]>(`/api/v1/tournaments/${tournamentId}/teams`, {
    accessToken,
  });
}

export function listMatches(
  accessToken: string,
  tournamentId: ID,
  stage?: TournamentStage,
): Promise<Match[]> {
  return apiRequest<Match[]>(`/api/v1/tournaments/${tournamentId}/matches`, {
    accessToken,
    params: { stage },
  });
}
