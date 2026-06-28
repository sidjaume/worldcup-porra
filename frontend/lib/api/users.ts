import { apiRequest } from "@/lib/api/client";
import type { User } from "@/types/api";

export function getCurrentUser(accessToken: string): Promise<User> {
  return apiRequest<User>("/api/v1/users/me", { accessToken });
}

export function updateCurrentUser(
  accessToken: string,
  displayName: string,
): Promise<User> {
  return apiRequest<User>("/api/v1/users/me", {
    accessToken,
    body: { display_name: displayName },
    method: "PATCH",
  });
}
