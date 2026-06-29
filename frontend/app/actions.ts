"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { ApiError } from "@/lib/api/client";
import { createPool, joinPool, rotateInviteCode, updatePool } from "@/lib/api/pools";
import { submitPrediction } from "@/lib/api/predictions";
import { updateCurrentUser } from "@/lib/api/users";
import {
  AuthenticationRequiredError,
  withAuthenticatedSession,
} from "@/lib/auth/authenticated-session";

type ActionState = {
  error?: string;
  inviteCode?: string;
  ok?: boolean;
  poolId?: string;
};

export async function createPoolAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const name = String(formData.get("name") ?? "").trim();
  const tournamentId = String(formData.get("tournament_id") ?? "");

  if (!name || !tournamentId) {
    return { error: "Pool name and tournament are required." };
  }

  try {
    const pool = await withAuthenticatedSession((accessToken) =>
      createPool(accessToken, name, tournamentId),
    );
    revalidatePath("/");
    revalidatePath("/pools");
    return { inviteCode: pool.invite_code, ok: true, poolId: pool.id };
  } catch (error) {
    return toActionError(error);
  }
}

export async function joinPoolAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const inviteCode = String(formData.get("invite_code") ?? "").trim();

  if (!inviteCode) {
    return { error: "Invite code is required." };
  }

  let poolId: string;
  try {
    const pool = await withAuthenticatedSession((accessToken) =>
      joinPool(accessToken, inviteCode),
    );
    poolId = pool.pool_id;
    revalidatePath("/");
    revalidatePath("/pools");
  } catch (error) {
    return toActionError(error);
  }
  redirect(`/pools/${poolId}`);
}

export async function submitPredictionAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const poolId = String(formData.get("pool_id") ?? "");
  const matchId = String(formData.get("match_id") ?? "");
  const homeGoals = Number(formData.get("predicted_home_goals"));
  const awayGoals = Number(formData.get("predicted_away_goals"));

  if (!poolId || !matchId || !Number.isInteger(homeGoals) || !Number.isInteger(awayGoals)) {
    return { error: "Enter whole-number scores for both teams." };
  }
  if (homeGoals < 0 || awayGoals < 0) {
    return { error: "Scores cannot be negative." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      submitPrediction(accessToken, poolId, matchId, homeGoals, awayGoals),
    );
    revalidatePath(`/pools/${poolId}`);
    revalidatePath(`/pools/${poolId}/predictions`);
    return { ok: true };
  } catch (error) {
    return toActionError(error);
  }
}

export async function updateProfileAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const displayName = String(formData.get("display_name") ?? "").trim();

  if (!displayName) {
    return { error: "Display name is required." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      updateCurrentUser(accessToken, displayName),
    );
    revalidatePath("/profile");
    return { ok: true };
  } catch (error) {
    return toActionError(error);
  }
}

export async function rotateInviteCodeAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const poolId = String(formData.get("pool_id") ?? "");

  try {
    const payload = await withAuthenticatedSession((accessToken) =>
      rotateInviteCode(accessToken, poolId),
    );
    return { inviteCode: payload.invite_code, ok: true };
  } catch (error) {
    return toActionError(error);
  }
}

export async function updatePoolAction(
  _state: ActionState,
  formData: FormData,
): Promise<ActionState> {
  const poolId = String(formData.get("pool_id") ?? "");
  const name = String(formData.get("name") ?? "").trim();
  const isActive = formData.get("is_active") === "on";

  if (!poolId || !name) {
    return { error: "Pool name is required." };
  }

  try {
    await withAuthenticatedSession((accessToken) =>
      updatePool(accessToken, poolId, { is_active: isActive, name }),
    );
    revalidatePath(`/pools/${poolId}`);
    return { ok: true };
  } catch (error) {
    return toActionError(error);
  }
}

function toActionError(error: unknown): ActionState {
  if (error instanceof AuthenticationRequiredError) {
    redirect("/");
  }
  if (error instanceof ApiError) {
    return { error: error.message };
  }
  throw error;
}
