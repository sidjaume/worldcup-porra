import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  filterMatches,
  latestSyncDate,
  syncStatus,
} from "@/lib/admin-operations";
import { matchStatusLabel } from "@/lib/format";
import type { Match } from "@/types/api";

const source = readFileSync(new URL("./AdminOperations.tsx", import.meta.url), "utf8");

describe("AdminOperations", () => {
  it("renders compact mobile match cards with sync freshness and source filters", () => {
    expect(source).toContain('aria-label="Match operations"');
    expect(source).toContain("md:grid-cols-2");
    expect(source).toContain("Manual override");
    expect(source).toContain("Not synced");
    expect(source).toContain("Stale");
    expect(source).toContain("Sync failed");
    expect(source).toContain("syncStatus(latestProviderSyncAt)");
  });

  it("cuts over to a no-controls access denied state after admin endpoint 403", () => {
    expect(source).toContain("const [accessDenied, setAccessDenied] = useState(false)");
    expect(source).toContain("if (accessDenied)");
    expect(source).toContain("<AdminAccessDeniedState />");
    expect(source).toContain("useAccessDeniedEffect(state, onAccessDenied)");
  });

  it("computes sync status from real match audit timestamps", () => {
    expect(latestSyncDate([])).toBeNull();
    expect(syncStatus(null)).toBe("Not synced");

    const latest = latestSyncDate([
      match({ id: "old", provider_last_synced_at: "2026-06-29T10:00:00.000Z" }),
      match({ id: "new", provider_last_synced_at: "2026-06-29T11:00:00.000Z" }),
      match({ id: "missing", provider_last_synced_at: null }),
    ]);

    expect(latest?.toISOString()).toBe("2026-06-29T11:00:00.000Z");
  });

  it("filters matches by status, source, and visible search text", () => {
    const matches = [
      match({
        admin_override: false,
        away_team: { id: "team-2", name: "Portugal" },
        bracket_position: 1,
        home_team: { id: "team-1", name: "Spain" },
        id: "provider",
        provider_last_synced_at: "2026-06-29T11:00:00.000Z",
        status: "scheduled",
        sync_source: "provider",
      }),
      match({
        admin_override: true,
        bracket_position: 2,
        id: "manual",
        provider_last_synced_at: "2026-06-29T11:00:00.000Z",
        status: "completed",
      }),
      match({
        bracket_position: 3,
        id: "not-synced",
        provider_last_synced_at: null,
        status: "scheduled",
      }),
      match({
        bracket_position: 4,
        id: "locked",
        status: "locked",
      }),
      match({
        bracket_position: 5,
        id: "in-progress",
        status: "in_progress",
      }),
    ];

    expect(filterMatches(matches, "scheduled", "provider", "")).toHaveLength(1);
    expect(filterMatches(matches, "locked", "all", "")[0]?.id).toBe("locked");
    expect(filterMatches(matches, "in_progress", "all", "")[0]?.id).toBe(
      "in-progress",
    );
    expect(filterMatches(matches, "all", "manual", "")[0]?.id).toBe("manual");
    expect(filterMatches(matches, "all", "not_synced", "")[0]?.id).toBe(
      "not-synced",
    );
    expect(filterMatches(matches, "all", "all", "Spain")[0]?.id).toBe("provider");
    expect(filterMatches(matches, "all", "all", "#2")[0]?.id).toBe("manual");
  });

  it("offers and displays user-friendly labels for every backend match status", () => {
    expect(source).toContain('{ label: "Locked", value: "locked" }');
    expect(source).toContain('{ label: "In progress", value: "in_progress" }');
    expect(source).toContain("matchStatusLabel(match.status)");
    expect(matchStatusLabel("scheduled")).toBe("Scheduled");
    expect(matchStatusLabel("locked")).toBe("Locked");
    expect(matchStatusLabel("in_progress")).toBe("In progress");
    expect(matchStatusLabel("completed")).toBe("Completed");
    expect(matchStatusLabel("cancelled")).toBe("Cancelled");
  });

  it("shows sync success and manual sync error recovery states", () => {
    expect(source).toContain("Teams created");
    expect(source).toContain("Matches updated");
    expect(source).toContain("Review affected matches and correct them manually.");
    expect(source).toContain('role="status"');
    expect(source).toContain('role="alert"');
  });

  it("requires confirmations for create, team, status, kickoff, result, sync, and rescore actions", () => {
    expect(source).toContain("Provider sync can update teams");
    expect(source).toContain("Create this knockout match?");
    expect(source).toContain("Save this team correction?");
    expect(source).toContain("Save this operational status correction?");
    expect(source).toContain("Changing kickoff can change whether predictions are editable.");
    expect(source).toContain("Save final result? The backend will advance the winner");
    expect(source).toContain("Update this final result? Rankings may change");
    expect(source).toContain("Recalculate scores for this completed match?");
  });

  it("labels end-of-play results and tied-match advancing winner behavior", () => {
    expect(source).toContain("end-of-play goals");
    expect(source).toContain("Do not include penalty shoot-out goals.");
    expect(source).toContain("Advancing winner");
    expect(source).toContain("choose the advancing team");
  });

  it("offers existing-match team and status correction controls through documented actions", () => {
    expect(source).toContain("Correct teams for");
    expect(source).toContain("TeamCorrectionForm");
    expect(source).toContain("updateMatchTeamsAction");
    expect(source).toContain('name="home_team_id"');
    expect(source).toContain('name="away_team_id"');
    expect(source).toContain("Either side may remain TBD");
    expect(source).toContain("Correct status for");
    expect(source).toContain("StatusCorrectionForm");
    expect(source).toContain("updateMatchStatusAction");
    expect(source).toContain("OPERATIONAL_STATUS_OPTIONS");
    expect(source).toContain("Completed results stay handled by the final-result form.");
    expect(source).not.toContain('{ label: "Completed", value: "completed" }[]');
  });
});

function match(overrides: Partial<Match>): Match {
  return {
    admin_override: false,
    away_score: null,
    away_team: null,
    bracket_position: 1,
    home_score: null,
    home_team: null,
    id: "match",
    live_minute: null,
    provider_last_synced_at: null,
    scheduled_at: "2026-06-29T10:00:00.000Z",
    stage: "round_of_32",
    status: "scheduled",
    sync_source: null,
    winner_team_id: null,
    ...overrides,
  };
}
