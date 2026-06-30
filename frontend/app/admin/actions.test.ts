import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./actions.ts", import.meta.url), "utf8");

describe("admin server actions", () => {
  it("keeps validation limited to frontend-safe checks", () => {
    expect(source).toContain("Home and away teams must be different.");
    expect(source).toContain("Choose a supported non-completed status.");
    expect(source).toContain("End-of-play goals cannot be negative.");
    expect(source).toContain("Choose the advancing winner from this match.");
    expect(source).not.toContain("scorePrediction");
    expect(source).not.toContain("advance");
  });

  it("calls the documented team and status correction clients", () => {
    expect(source).toContain("updateMatchTeams(accessToken, matchId");
    expect(source).toContain("home_team_id: homeTeamId");
    expect(source).toContain("away_team_id: awayTeamId");
    expect(source).toContain("updateMatchStatus(accessToken, matchId, { status })");
    expect(source).toContain('value === "scheduled"');
    expect(source).toContain('value === "locked"');
    expect(source).toContain('value === "in_progress"');
    expect(source).toContain('value === "cancelled"');
    expect(source).not.toContain('value === "completed"');
  });

  it("handles access denied from admin endpoints", () => {
    expect(source).toContain("error.status === 403");
    expect(source).toContain("Admin access is required.");
  });

  it("requires explicit confirmation before mutating admin operations", () => {
    expect(source).toContain('formData.get("confirm_sync")');
    expect(source).toContain('formData.get("confirm_create")');
    expect(source).toContain('formData.get("confirm_teams")');
    expect(source).toContain('formData.get("confirm_status")');
    expect(source).toContain('formData.get("confirm_kickoff")');
    expect(source).toContain('formData.get("confirm_result")');
    expect(source).toContain('formData.get("confirm_rescore")');
  });
});
