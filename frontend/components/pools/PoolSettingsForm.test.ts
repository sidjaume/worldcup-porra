import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./PoolSettingsForm.tsx", import.meta.url), "utf8");

describe("PoolSettingsForm", () => {
  it("does not expose pool activation controls without an inactive-pool management view", () => {
    expect(source).toContain('name="name"');
    expect(source).not.toContain('name="is_active"');
    expect(source).not.toContain("defaultChecked={pool.is_active}");
  });
});
