import { Router } from "express";
import { z } from "zod";
import { authMiddleware, type AuthenticatedRequest } from "../middleware/auth.js";
import { createChallenge, getChallenges, getLeaderboard } from "../services/demoRepository.js";

export const challengesRouter = Router();

const createChallengeSchema = z.object({
  title: z.string().min(3),
  description: z.string().min(3),
  habitCategory: z.string().min(2),
  startsOn: z.string(),
  endsOn: z.string(),
  participantIds: z.array(z.string()).default([])
});

challengesRouter.use(authMiddleware);

challengesRouter.get("/", async (request: AuthenticatedRequest, response, next) => {
  try {
    response.json({ items: await getChallenges(request.auth!.userId) });
  } catch (error) {
    next(error);
  }
});

challengesRouter.post("/", async (request: AuthenticatedRequest, response, next) => {
  try {
    const payload = createChallengeSchema.parse(request.body);
    const challenge = await createChallenge({
      ownerId: request.auth!.userId,
      ...payload
    });
    response.status(201).json(challenge);
  } catch (error) {
    next(error);
  }
});

challengesRouter.get("/:challengeId/leaderboard", async (request, response, next) => {
  try {
    response.json({ items: await getLeaderboard(request.params.challengeId) });
  } catch (error) {
    next(error);
  }
});
