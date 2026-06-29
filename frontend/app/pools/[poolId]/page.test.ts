import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./page.tsx", import.meta.url), "utf8");

describe("PoolDetailPage", () => {
  it("uses the session user to hide owner-only controls from non-owners", () => {
    expect(source).toContain("const isOwner = pool.owner_user_id === session.user.id;");
    expect(source).toContain("isOwner ? (");
    expect(source).toContain("<InviteCodeForm poolId={poolId} />");
    expect(source).toContain("<PoolSettingsForm pool={pool} />");
  });
});
