import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./PoolSubnav.tsx", import.meta.url), "utf8");

describe("PoolSubnav", () => {
  it("keeps pool context and active subpage state visible", () => {
    expect(source).toContain("Current pool");
    expect(source).toContain('aria-label={`${poolName} navigation`}');
    expect(source).toContain('aria-current={isActive ? "page" : undefined}');
    expect(source).toContain("overflow-x-auto");
  });
});
