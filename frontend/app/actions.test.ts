import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./actions.ts", import.meta.url), "utf8");
const createPoolActionSource = source.slice(
  source.indexOf("export async function createPoolAction"),
  source.indexOf("export async function joinPoolAction"),
);
const updatePoolActionSource = source.slice(
  source.indexOf("export async function updatePoolAction"),
  source.indexOf("function toActionError"),
);

describe("createPoolAction", () => {
  it("returns the initial invite code from the create pool response", () => {
    expect(createPoolActionSource).toContain("inviteCode: pool.invite_code");
    expect(createPoolActionSource).toContain("poolId: pool.id");
    expect(createPoolActionSource).not.toContain("redirect(");
  });
});

describe("updatePoolAction", () => {
  it("does not deactivate pools from the settings form", () => {
    expect(updatePoolActionSource).toContain("updatePool(accessToken, poolId, { name })");
    expect(updatePoolActionSource).not.toContain("formData.get(\"is_active\")");
  });
});

describe("submitPredictionAction", () => {
  it("passes tied advancing winners and clears non-tied winner ids", () => {
    expect(source).toContain('readNullableString(formData, "predicted_winner_team_id")');
    expect(source).toContain("homeGoals === awayGoals ? predictedWinnerTeamId : null");
    expect(source).toContain("Choose the team you expect to advance.");
  });

  it("keeps backend validation errors on the existing action error path", () => {
    expect(source).toContain("if (error instanceof ApiError)");
    expect(source).toContain("return { error: error.message };");
  });
});
