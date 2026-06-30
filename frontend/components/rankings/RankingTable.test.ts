import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./RankingTable.tsx", import.meta.url), "utf8");

describe("RankingTable", () => {
  it("uses mobile cards and clear ranking labels", () => {
    expect(source).toContain("lg:hidden");
    expect(source).toContain("lg:block");
    expect(source).toContain("Exact scores");
    expect(source).toContain("Correct winners");
    expect(source).toContain("Predictions");
  });
});
