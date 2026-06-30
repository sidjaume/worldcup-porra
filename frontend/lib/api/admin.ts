import { apiRequest } from "@/lib/api/client";
import type {
  CompleteMatchRequest,
  CreateMatchRequest,
  ID,
  Match,
  SyncResult,
  SyncTournamentRequest,
  UpdateKickoffRequest,
  UpdateMatchStatusRequest,
  UpdateMatchTeamsRequest,
} from "@/types/api";

export function syncTournament(
  accessToken: string,
  tournamentId: ID,
  request: SyncTournamentRequest,
): Promise<SyncResult> {
  return apiRequest<SyncResult>(`/api/v1/admin/tournaments/${tournamentId}/sync`, {
    accessToken,
    body: request,
    method: "POST",
  });
}

export function createAdminMatch(
  accessToken: string,
  tournamentId: ID,
  request: CreateMatchRequest,
): Promise<Match> {
  return apiRequest<Match>(`/api/v1/admin/tournaments/${tournamentId}/matches`, {
    accessToken,
    body: request,
    method: "POST",
  });
}

export function updateMatchKickoff(
  accessToken: string,
  matchId: ID,
  request: UpdateKickoffRequest,
): Promise<Match> {
  return apiRequest<Match>(`/api/v1/admin/matches/${matchId}/kickoff`, {
    accessToken,
    body: request,
    method: "PATCH",
  });
}

export function updateMatchTeams(
  accessToken: string,
  matchId: ID,
  request: UpdateMatchTeamsRequest,
): Promise<Match> {
  return apiRequest<Match>(`/api/v1/admin/matches/${matchId}/teams`, {
    accessToken,
    body: request,
    method: "PATCH",
  });
}

export function updateMatchStatus(
  accessToken: string,
  matchId: ID,
  request: UpdateMatchStatusRequest,
): Promise<Match> {
  return apiRequest<Match>(`/api/v1/admin/matches/${matchId}/status`, {
    accessToken,
    body: request,
    method: "PATCH",
  });
}

export function completeMatch(
  accessToken: string,
  matchId: ID,
  request: CompleteMatchRequest,
): Promise<Match> {
  return apiRequest<Match>(`/api/v1/admin/matches/${matchId}`, {
    accessToken,
    body: request,
    method: "PATCH",
  });
}

export function rescoreMatch(accessToken: string, matchId: ID): Promise<Match> {
  return apiRequest<Match>(`/api/v1/admin/matches/${matchId}/rescore`, {
    accessToken,
    method: "POST",
  });
}
