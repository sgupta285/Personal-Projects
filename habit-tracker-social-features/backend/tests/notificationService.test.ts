import { describe, expect, it } from "vitest";
import { buildFcmPayload, recommendReminderTime } from "../src/services/notificationService.js";

describe("recommendReminderTime", () => {
  it("leans toward the hour before historical completion", () => {
    const recommendation = recommendReminderTime({
      completionHistory: [
        { completedAt: "2026-04-01T18:10:00.000Z" },
        { completedAt: "2026-03-31T18:25:00.000Z" },
        { completedAt: "2026-03-30T19:02:00.000Z" }
      ],
      quietWindowStart: "07:00",
      quietWindowEnd: "21:00"
    });

    expect(recommendation).toBe("17:00");
  });

  it("builds an FCM payload", () => {
    const payload = buildFcmPayload("token-1234567890", "Title", "Body", { habitId: "1" });
    expect(payload.notification.title).toBe("Title");
  });
});
