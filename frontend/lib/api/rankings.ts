import { apiRequest } from "@/lib/api/client";
import type { ID, RankingRow } from "@/types/api";

export function getRankings(
  accessToken: string,
  poolId: ID,
): Promise<RankingRow[]> {
  return apiRequest<RankingRow[]>(`/api/v1/pools/${poolId}/rankings`, {
    accessToken,
  });
}
