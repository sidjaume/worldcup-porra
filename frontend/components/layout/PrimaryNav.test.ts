import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./PrimaryNav.tsx", import.meta.url), "utf8");

describe("PrimaryNav", () => {
  it("supports mobile active page context", () => {
    expect(source).toContain('aria-label="Primary"');
    expect(source).toContain('aria-current={isActive ? "page" : undefined}');
    expect(source).toContain("pathname.startsWith");
  });
});
