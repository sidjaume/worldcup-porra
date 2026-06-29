import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./actions.ts", import.meta.url), "utf8");
const createPoolActionSource = source.slice(
  source.indexOf("export async function createPoolAction"),
  source.indexOf("export async function joinPoolAction"),
);

describe("createPoolAction", () => {
  it("returns the initial invite code from the create pool response", () => {
    expect(createPoolActionSource).toContain("inviteCode: pool.invite_code");
    expect(createPoolActionSource).toContain("poolId: pool.id");
    expect(createPoolActionSource).not.toContain("redirect(");
  });
});
