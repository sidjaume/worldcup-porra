import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./InviteCodeForm.tsx", import.meta.url), "utf8");

describe("InviteCodeForm", () => {
  it("keeps invite code copy feedback accessible and reusable", () => {
    expect(source).toContain("export function InviteCodeCopyPanel");
    expect(source).toContain('navigator.clipboard.writeText(code)');
    expect(source).toContain('role="status"');
    expect(source).toContain("Copy failed. Select the code and copy it manually.");
  });
});
