import { Router } from "express";
import { z } from "zod";
import { authMiddleware, type AuthenticatedRequest } from "../middleware/auth.js";
import { pool } from "../db/index.js";
import { getUserSummary, registerDevice } from "../services/demoRepository.js";
import { buildFcmPayload } from "../services/notificationService.js";

export const notificationsRouter = Router();

const tokenSchema = z.object({
  token: z.string().min(10),
  platform: z.enum(["ios", "android"])
});

notificationsRouter.use(authMiddleware);

notificationsRouter.post("/device-token", async (request: AuthenticatedRequest, response, next) => {
  try {
    const payload = tokenSchema.parse(request.body);
    const record = await registerDevice({
      userId: request.auth!.userId,
      token: payload.token,
      platform: payload.platform
    });
    response.status(201).json(record);
  } catch (error) {
    next(error);
  }
});

notificationsRouter.get("/preview", async (request: AuthenticatedRequest, response, next) => {
  try {
    const summary = await getUserSummary(request.auth!.userId);
    const tokenResult = await pool.query(
      "select token from device_tokens where user_id = $1 order by last_seen_at desc limit 1",
      [request.auth!.userId]
    );
    const token = tokenResult.rows[0]?.token ?? "demo-device-token";
    response.json({
      reminderAt: summary?.stats.recommendedReminder,
      preview: buildFcmPayload(
        token,
        "Keep the streak alive",
        `A quick check-in keeps ${summary?.stats.streak ?? 0} day momentum moving.`,
        { type: "habit_reminder", userId: request.auth!.userId }
      )
    });
  } catch (error) {
    next(error);
  }
});
