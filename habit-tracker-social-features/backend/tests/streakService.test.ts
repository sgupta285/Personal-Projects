import { describe, expect, it } from "vitest";
import { badgeForStreak, computeStreak } from "../src/services/streakService.js";

describe("computeStreak", () => {
  it("counts consecutive days including today", () => {
    const streak = computeStreak([
      "2026-04-01T09:00:00.000Z",
      "2026-03-31T09:00:00.000Z",
      "2026-03-30T09:00:00.000Z"
    ], "2026-04-01T12:00:00.000Z");

    expect(streak).toBe(3);
  });

  it("allows the latest completion to be yesterday", () => {
    const streak = computeStreak([
      "2026-03-31T09:00:00.000Z",
      "2026-03-30T09:00:00.000Z"
    ], "2026-04-01T12:00:00.000Z");

    expect(streak).toBe(2);
  });

  it("creates badge milestones", () => {
    expect(badgeForStreak(7)).toContain("Week Warrior");
  });
});
