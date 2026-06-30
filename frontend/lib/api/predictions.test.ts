import { afterEach, describe, expect, it, vi } from "vitest";
import { submitPrediction } from "@/lib/api/predictions";

describe("prediction API client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.unstubAllEnvs();
  });

  it("sends the advancing winner for tied predictions", async () => {
    const fetchMock = stubFetch({ id: "prediction-1" });

    await submitPrediction("token", "pool-1", "match-1", 1, 1, "team-1");

    expectRequest(fetchMock, {
      body: {
        predicted_away_goals: 1,
        predicted_home_goals: 1,
        predicted_winner_team_id: "team-1",
      },
      method: "PUT",
      path: "/api/v1/pools/pool-1/matches/match-1/prediction",
    });
  });

  it("sends null advancing winner for non-tied predictions", async () => {
    const fetchMock = stubFetch({ id: "prediction-1" });

    await submitPrediction("token", "pool-1", "match-1", 2, 1, null);

    expectRequest(fetchMock, {
      body: {
        predicted_away_goals: 1,
        predicted_home_goals: 2,
        predicted_winner_team_id: null,
      },
      method: "PUT",
      path: "/api/v1/pools/pool-1/matches/match-1/prediction",
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
    body: unknown;
    method: string;
    path: string;
  },
) {
  const [url, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
  expect(url.pathname).toBe(expected.path);
  expect(init.method).toBe(expected.method);
  expect(new Headers(init.headers).get("authorization")).toBe("Bearer token");
  expect(JSON.parse(String(init.body))).toEqual(expected.body);
}
