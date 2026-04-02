import { Router } from "express";
import { z } from "zod";
import { authMiddleware, type AuthenticatedRequest } from "../middleware/auth.js";
import { completeHabit, createHabit } from "../services/demoRepository.js";

export const habitsRouter = Router();

const habitSchema = z.object({
  name: z.string().min(2),
  category: z.string().min(2),
  frequency: z.enum(["daily", "weekly"]),
  targetPerPeriod: z.number().int().positive(),
  color: z.string().min(4)
});

const entrySchema = z.object({
  completedAt: z.string().datetime().optional()
});

habitsRouter.use(authMiddleware);

habitsRouter.post("/", async (request: AuthenticatedRequest, response, next) => {
  try {
    const payload = habitSchema.parse(request.body);
    const habit = await createHabit({
      userId: request.auth!.userId,
      ...payload
    });
    response.status(201).json(habit);
  } catch (error) {
    next(error);
  }
});

habitsRouter.post("/:habitId/complete", async (request: AuthenticatedRequest, response, next) => {
  try {
    const payload = entrySchema.parse(request.body ?? {});
    const entry = await completeHabit({
      userId: request.auth!.userId,
      habitId: request.params.habitId,
      completedAt: payload.completedAt ?? new Date().toISOString()
    });
    response.status(201).json(entry);
  } catch (error) {
    next(error);
  }
});
