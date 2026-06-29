import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./ParticipantList.tsx", import.meta.url), "utf8");

describe("ParticipantList", () => {
  it("uses a mobile-safe card layout", () => {
    expect(source).toContain("md:hidden");
    expect(source).toContain("md:block");
    expect(source).toContain("Joined");
    expect(source).toContain("truncate");
  });
});
