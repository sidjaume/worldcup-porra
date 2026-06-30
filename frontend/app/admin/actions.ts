"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import {
  completeMatch,
  createAdminMatch,
  rescoreMatch,
  syncTournament,
  updateMatchKickoff,
  updateMatchStatus,
  updateMatchTeams,
} from "@/lib/api/admin";
import { ApiError } from "@/lib/api/client";
import { STAGES } from "@/lib/format";
import {
  AuthenticationRequiredError,
  withAuthenticatedSession,
} from "@/lib/auth/authenticated-session";
import type { OperationalMatchStatus, SyncResult, TournamentStage } from "@/types/api";

export type AdminActionState = {
  accessDenied?: boolean;
  error?: string;
  ok?: boolean;
  message?: string;
  syncResult?: SyncResult;
};

export async function syncTournamentAction(
  _state: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  const tournamentId = readString(formData, "tournament_id");
  const year = Number(formData.get("year"));

  if (!tournamentId || !Number.isInteger(year)) {
    return { error: "Tournament and year are required." };
  }
  if (!formData.get("confirm_sync")) {
    return { error: "Confirm provider sync before running it." };
  }

  try {
    const syncResult = await withAuthenticatedSession((accessToken) =>
      syncTournament(accessToken, tournamentId, { year }),
    );
    revalidatePath(`/admin/tournaments/${tournamentId}`);
    return {
      message: syncResult.errors.length
        ? "Sync completed with errors."
        : "Sync completed.",
      ok: true,
      syncResult,
    };
  } catch (error) {
    return toActionError(error);
  }
}

export async function createMatchAction(
  _state: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  const tournamentId = readString(formData, "tournament_id");
  const stage = readStage(formData);
  const bracketPosition = Number(formData.get("bracket_position"));
  const scheduledAt = readIsoDate(formData, "scheduled_at_iso");
  const homeTeamId = readNullableString(formData, "home_team_id");
  const awayTeamId = readNullableString(formData, "away_team_id");

  if (!tournamentId || !stage || !Number.isInteger(bracketPosition) || !scheduledAt) {
    return { error: "Stage, bracket position, and kickoff are required." };
  }
  if (bracketPosition < 1) {
    return { error: "Bracket position must be greater than zero." };
  }
  if (homeTeamId && awayTeamId && homeTeamId === awayTeamId) {
    return { error: "Home and away teams must be different." };
  }
  if (!formData.get("confirm_create")) {
    return { error: "Confirm match creation before saving." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      createAdminMatch(accessToken, tournamentId, {
        away_team_id: awayTeamId,
        bracket_position: bracketPosition,
        home_team_id: homeTeamId,
        scheduled_at: scheduledAt,
        stage,
      }),
    );
    revalidatePath(`/admin/tournaments/${tournamentId}`);
    return { message: "Match created.", ok: true };
  } catch (error) {
    return toActionError(error);
  }
}

export async function updateKickoffAction(
  _state: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  const tournamentId = readString(formData, "tournament_id");
  const matchId = readString(formData, "match_id");
  const scheduledAt = readIsoDate(formData, "scheduled_at_iso");

  if (!tournamentId || !matchId || !scheduledAt) {
    return { error: "New kickoff date and time are required." };
  }
  if (!formData.get("confirm_kickoff")) {
    return { error: "Confirm the kickoff correction before saving." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      updateMatchKickoff(accessToken, matchId, { scheduled_at: scheduledAt }),
    );
    revalidatePath(`/admin/tournaments/${tournamentId}`);
    return {
      message: "Kickoff updated. This match is now marked as a manual override.",
      ok: true,
    };
  } catch (error) {
    return toActionError(error);
  }
}

export async function updateMatchTeamsAction(
  _state: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  const tournamentId = readString(formData, "tournament_id");
  const matchId = readString(formData, "match_id");
  const homeTeamId = readNullableString(formData, "home_team_id");
  const awayTeamId = readNullableString(formData, "away_team_id");

  if (!tournamentId || !matchId) {
    return { error: "Match is required for team correction." };
  }
  if (homeTeamId && awayTeamId && homeTeamId === awayTeamId) {
    return { error: "Home and away teams must be different." };
  }
  if (!formData.get("confirm_teams")) {
    return { error: "Confirm the team correction before saving." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      updateMatchTeams(accessToken, matchId, {
        away_team_id: awayTeamId,
        home_team_id: homeTeamId,
      }),
    );
    revalidatePath(`/admin/tournaments/${tournamentId}`);
    return {
      message: "Teams updated. This match is now marked as a manual override.",
      ok: true,
    };
  } catch (error) {
    return toActionError(error);
  }
}

export async function updateMatchStatusAction(
  _state: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  const tournamentId = readString(formData, "tournament_id");
  const matchId = readString(formData, "match_id");
  const status = readOperationalStatus(formData);

  if (!tournamentId || !matchId || !status) {
    return { error: "Choose a supported non-completed status." };
  }
  if (!formData.get("confirm_status")) {
    return { error: "Confirm the status correction before saving." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      updateMatchStatus(accessToken, matchId, { status }),
    );
    revalidatePath(`/admin/tournaments/${tournamentId}`);
    return {
      message: "Status updated. This match is now marked as a manual override.",
      ok: true,
    };
  } catch (error) {
    return toActionError(error);
  }
}

export async function completeMatchAction(
  _state: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  const tournamentId = readString(formData, "tournament_id");
  const matchId = readString(formData, "match_id");
  const homeTeamId = readString(formData, "home_team_id");
  const awayTeamId = readString(formData, "away_team_id");
  const winnerTeamId = readString(formData, "winner_team_id");
  const homeScore = Number(formData.get("home_score"));
  const awayScore = Number(formData.get("away_score"));

  if (!tournamentId || !matchId || !homeTeamId || !awayTeamId) {
    return { error: "Match teams are required before saving a result." };
  }
  if (!Number.isInteger(homeScore) || !Number.isInteger(awayScore)) {
    return { error: "Enter whole-number end-of-play goals for both teams." };
  }
  if (homeScore < 0 || awayScore < 0) {
    return { error: "End-of-play goals cannot be negative." };
  }
  if (winnerTeamId !== homeTeamId && winnerTeamId !== awayTeamId) {
    return { error: "Choose the advancing winner from this match." };
  }
  if (!formData.get("confirm_result")) {
    return { error: "Confirm the final result before saving." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      completeMatch(accessToken, matchId, {
        away_score: awayScore,
        home_score: homeScore,
        winner_team_id: winnerTeamId,
      }),
    );
    revalidatePath(`/admin/tournaments/${tournamentId}`);
    return {
      message: "Result saved. Scoring was recalculated for this match.",
      ok: true,
    };
  } catch (error) {
    return toActionError(error);
  }
}

export async function rescoreMatchAction(
  _state: AdminActionState,
  formData: FormData,
): Promise<AdminActionState> {
  const tournamentId = readString(formData, "tournament_id");
  const matchId = readString(formData, "match_id");

  if (!tournamentId || !matchId) {
    return { error: "Match is required for rescoring." };
  }
  if (!formData.get("confirm_rescore")) {
    return { error: "Confirm rescoring before running it." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      rescoreMatch(accessToken, matchId),
    );
    revalidatePath(`/admin/tournaments/${tournamentId}`);
    return { message: "Scores recalculated for this match.", ok: true };
  } catch (error) {
    return toActionError(error);
  }
}

function readString(formData: FormData, name: string): string {
  return String(formData.get(name) ?? "").trim();
}

function readNullableString(formData: FormData, name: string): string | null {
  const value = readString(formData, name);
  return value || null;
}

function readStage(formData: FormData): TournamentStage | null {
  const value = readString(formData, "stage");
  return STAGES.some((stage) => stage.value === value)
    ? (value as TournamentStage)
    : null;
}

function readOperationalStatus(formData: FormData): OperationalMatchStatus | null {
  const value = readString(formData, "status");
  return value === "scheduled" ||
    value === "locked" ||
    value === "in_progress" ||
    value === "cancelled"
    ? value
    : null;
}

function readIsoDate(formData: FormData, name: string): string | null {
  const value = readString(formData, name);
  if (!value) {
    return null;
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date.toISOString();
}

function toActionError(error: unknown): AdminActionState {
  if (error instanceof AuthenticationRequiredError) {
    redirect("/");
  }
  if (error instanceof ApiError) {
    if (error.status === 403) {
      return { accessDenied: true, error: "Admin access is required." };
    }
    return { error: error.message };
  }
  throw error;
}
