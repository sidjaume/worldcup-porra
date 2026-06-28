import { apiRequest } from "@/lib/api/client";
import type {
  ID,
  Prediction,
  PredictionWriteResponse,
  TournamentStage,
  VisiblePrediction,
} from "@/types/api";

export function listPredictions(
  accessToken: string,
  poolId: ID,
  filters: { matchId?: ID; stage?: TournamentStage } = {},
): Promise<Prediction[]> {
  return apiRequest<Prediction[]>(`/api/v1/pools/${poolId}/predictions`, {
    accessToken,
    params: {
      match_id: filters.matchId,
      stage: filters.stage,
    },
  });
}

export function submitPrediction(
  accessToken: string,
  poolId: ID,
  matchId: ID,
  predictedHomeGoals: number,
  predictedAwayGoals: number,
): Promise<PredictionWriteResponse> {
  return apiRequest<PredictionWriteResponse>(
    `/api/v1/pools/${poolId}/matches/${matchId}/prediction`,
    {
      accessToken,
      body: {
        predicted_home_goals: predictedHomeGoals,
        predicted_away_goals: predictedAwayGoals,
      },
      method: "PUT",
    },
  );
}

export function listVisiblePredictions(
  accessToken: string,
  poolId: ID,
  matchId: ID,
): Promise<VisiblePrediction[]> {
  return apiRequest<VisiblePrediction[]>(
    `/api/v1/pools/${poolId}/matches/${matchId}/predictions`,
    { accessToken },
  );
}
