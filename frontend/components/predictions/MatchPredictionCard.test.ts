import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./MatchPredictionCard.tsx", import.meta.url), "utf8");
const formSource = readFileSync(new URL("./PredictionForm.tsx", import.meta.url), "utf8");

describe("MatchPredictionCard", () => {
  it("keeps scheduled matches editable only when the prediction is editable", () => {
    expect(source).toContain(
      'match.status === "scheduled" && (!prediction || prediction.status === "editable")',
    );
  });

  it("shows specific read-only copy for locked and in-progress matches", () => {
    expect(source).toContain('match.status === "locked"');
    expect(source).toContain("Predictions are closed because this match is locked.");
    expect(source).toContain('match.status === "in_progress"');
    expect(source).toContain("Predictions are closed while this match is in progress.");
  });

  it("requires an advancing winner only when entered prediction goals are tied", () => {
    expect(formSource).toContain('name="predicted_winner_team_id"');
    expect(formSource).toContain("homeGoals !== \"\"");
    expect(formSource).toContain("Number(homeGoals) === Number(awayGoals)");
    expect(formSource).toContain("Choose advancing team");
    expect(formSource).toContain("required");
    expect(formSource).toContain('type="hidden" value=""');
  });

  it("passes team ids into the prediction form and displays tied winner picks", () => {
    expect(source).toContain("awayTeamId={match.away_team?.id ?? null}");
    expect(source).toContain("homeTeamId={match.home_team?.id ?? null}");
    expect(source).toContain("predictionWinnerName(match, prediction)");
    expect(source).toContain("advances");
  });
});
