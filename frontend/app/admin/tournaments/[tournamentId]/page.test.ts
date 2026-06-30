import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./page.tsx", import.meta.url), "utf8");
const loadingSource = readFileSync(new URL("./loading.tsx", import.meta.url), "utf8");
const errorSource = readFileSync(new URL("./error.tsx", import.meta.url), "utf8");

describe("AdminTournamentPage", () => {
  it("loads only documented tournament APIs before rendering admin operations", () => {
    expect(source).toContain("listTournaments(session.accessToken)");
    expect(source).toContain("listTeams(session.accessToken, tournamentId)");
    expect(source).toContain("listMatches(session.accessToken, tournamentId, activeStage)");
    expect(source.indexOf("const tournaments = await listTournaments")).toBeLessThan(
      source.indexOf("const [teams, matches] = await Promise.all"),
    );
    expect(source.indexOf("if (!tournament)")).toBeLessThan(
      source.indexOf("const [teams, matches] = await Promise.all"),
    );
    expect(source).not.toContain("is_admin");
    expect(source).not.toContain("role ===");
  });

  it("renders route states for loading, empty, 403, and errors", () => {
    expect(loadingSource).toContain("Loading tournament operations...");
    expect(source).toContain("AdminAccessDeniedState");
    expect(source).toContain("NoTournamentsState");
    expect(errorSource).toContain("RouteErrorState");
  });
});
