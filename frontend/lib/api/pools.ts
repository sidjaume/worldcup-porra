import { apiRequest } from "@/lib/api/client";
import type {
  CreatePoolResponse,
  ID,
  InviteCodeResponse,
  JoinPoolResponse,
  Participant,
  PoolDetail,
  PoolSummary,
} from "@/types/api";

export function listPools(accessToken: string): Promise<PoolSummary[]> {
  return apiRequest<PoolSummary[]>("/api/v1/pools", { accessToken });
}

export function getPool(accessToken: string, poolId: ID): Promise<PoolDetail> {
  return apiRequest<PoolDetail>(`/api/v1/pools/${poolId}`, { accessToken });
}

export function createPool(
  accessToken: string,
  name: string,
  tournamentId: ID,
): Promise<CreatePoolResponse> {
  return apiRequest<CreatePoolResponse>("/api/v1/pools", {
    accessToken,
    body: { name, tournament_id: tournamentId },
    method: "POST",
  });
}

export function updatePool(
  accessToken: string,
  poolId: ID,
  values: { is_active?: boolean; name?: string },
): Promise<Pick<PoolDetail, "id" | "is_active" | "name">> {
  return apiRequest<Pick<PoolDetail, "id" | "is_active" | "name">>(
    `/api/v1/pools/${poolId}`,
    {
      accessToken,
      body: values,
      method: "PATCH",
    },
  );
}

export function joinPool(
  accessToken: string,
  inviteCode: string,
): Promise<JoinPoolResponse> {
  return apiRequest<JoinPoolResponse>("/api/v1/pools/join", {
    accessToken,
    body: { invite_code: inviteCode },
    method: "POST",
  });
}

export function listParticipants(
  accessToken: string,
  poolId: ID,
): Promise<Participant[]> {
  return apiRequest<Participant[]>(`/api/v1/pools/${poolId}/participants`, {
    accessToken,
  });
}

export function removeParticipant(
  accessToken: string,
  poolId: ID,
  userId: ID,
): Promise<void> {
  return apiRequest<void>(`/api/v1/pools/${poolId}/participants/${userId}`, {
    accessToken,
    method: "DELETE",
  });
}

export function rotateInviteCode(
  accessToken: string,
  poolId: ID,
): Promise<InviteCodeResponse> {
  return apiRequest<InviteCodeResponse>(
    `/api/v1/pools/${poolId}/invite-code/rotate`,
    {
      accessToken,
      method: "POST",
    },
  );
}
