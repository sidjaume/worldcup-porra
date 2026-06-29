import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./PoolSettingsForm.tsx", import.meta.url), "utf8");

describe("PoolSettingsForm", () => {
  it("uses the explicit backend active state for the checkbox", () => {
    expect(source).toContain("defaultChecked={pool.is_active}");
    expect(source).not.toContain("pool.is_active ?? true");
  });
});
