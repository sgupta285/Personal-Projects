import { describe, expect, it } from "vitest";
import { streakLabel } from "../src/utils/streak";

describe("streakLabel", () => {
  it("returns a stronger label as streaks grow", () => {
    expect(streakLabel(8)).toBe("Strong week");
  });
});
