import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./CreatePoolForm.tsx", import.meta.url), "utf8");

describe("CreatePoolForm", () => {
  it("shows the initial invite code and pool link after creation", () => {
    expect(source).toContain("state.inviteCode");
    expect(source).toContain('title="Initial invite code"');
    expect(source).toContain("InviteCodeCopyPanel");
    expect(source).toContain("state.poolId");
    expect(source).toContain('href={`/pools/${state.poolId}`}');
  });
});
