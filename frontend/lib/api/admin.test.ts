import { afterEach, describe, expect, it, vi } from "vitest";
import {
  completeMatch,
  createAdminMatch,
  rescoreMatch,
  syncTournament,
  updateMatchKickoff,
  updateMatchStatus,
  updateMatchTeams,
} from "@/lib/api/admin";

describe("admin API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it("calls the documented provider sync endpoint", async () => {
    const fetchMock = stubFetch({ errors: [] });

    await syncTournament("token", "tournament-1", { year: 2026 });

    expectRequest(fetchMock, {
      body: { year: 2026 },
      method: "POST",
      path: "/api/v1/admin/tournaments/tournament-1/sync",
    });
  });

  it("calls the documented match creation endpoint without bracket-link fields", async () => {
    const fetchMock = stubFetch({ id: "match-1" });

    await createAdminMatch("token", "tournament-1", {
      bracket_position: 3,
      scheduled_at: "2026-07-01T19:00:00.000Z",
      stage: "round_of_16",
    });

    expectRequest(fetchMock, {
      body: {
        bracket_position: 3,
        scheduled_at: "2026-07-01T19:00:00.000Z",
        stage: "round_of_16",
      },
      method: "POST",
      path: "/api/v1/admin/tournaments/tournament-1/matches",
    });
  });

  it("calls kickoff, team, status, completion, and rescore endpoints as documented", async () => {
    const fetchMock = stubFetch({ id: "match-1" });

    await updateMatchKickoff("token", "match-1", {
      scheduled_at: "2026-07-01T19:00:00.000Z",
    });
    await updateMatchTeams("token", "match-1", {
      away_team_id: null,
      home_team_id: "team-1",
    });
    await updateMatchStatus("token", "match-1", {
      status: "in_progress",
    });
    await completeMatch("token", "match-1", {
      away_score: 1,
      home_score: 1,
      winner_team_id: "team-1",
    });
    await rescoreMatch("token", "match-1");

    expectRequest(fetchMock, {
      body: { scheduled_at: "2026-07-01T19:00:00.000Z" },
      call: 0,
      method: "PATCH",
      path: "/api/v1/admin/matches/match-1/kickoff",
    });
    expectRequest(fetchMock, {
      body: { away_team_id: null, home_team_id: "team-1" },
      call: 1,
      method: "PATCH",
      path: "/api/v1/admin/matches/match-1/teams",
    });
    expectRequest(fetchMock, {
      body: { status: "in_progress" },
      call: 2,
      method: "PATCH",
      path: "/api/v1/admin/matches/match-1/status",
    });
    expectRequest(fetchMock, {
      body: { away_score: 1, home_score: 1, winner_team_id: "team-1" },
      call: 3,
      method: "PATCH",
      path: "/api/v1/admin/matches/match-1",
    });
    expectRequest(fetchMock, {
      call: 4,
      method: "POST",
      path: "/api/v1/admin/matches/match-1/rescore",
    });
  });
});

function stubFetch(payload: unknown) {
  const fetchMock = vi.fn().mockImplementation(() =>
    Promise.resolve(new Response(JSON.stringify(payload), {
      headers: { "content-type": "application/json" },
      status: 200,
    })),
  );
  vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "https://api.example.com");
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

function expectRequest(
  fetchMock: ReturnType<typeof vi.fn>,
  expected: {
    body?: unknown;
    call?: number;
    method: string;
    path: string;
  },
) {
  const call = expected.call ?? 0;
  const [url, init] = fetchMock.mock.calls[call] as [URL, RequestInit];
  expect(url.pathname).toBe(expected.path);
  expect(init.method).toBe(expected.method);
  expect(new Headers(init.headers).get("authorization")).toBe("Bearer token");
  if ("body" in expected) {
    expect(init.body).toBe(JSON.stringify(expected.body));
  }
}
