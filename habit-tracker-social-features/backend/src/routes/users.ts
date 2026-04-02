import { Router } from "express";
import { authMiddleware, type AuthenticatedRequest } from "../middleware/auth.js";
import { getFriends, getUserSummary } from "../services/demoRepository.js";

export const usersRouter = Router();

usersRouter.use(authMiddleware);

usersRouter.get("/me", async (request: AuthenticatedRequest, response, next) => {
  try {
    const summary = await getUserSummary(request.auth!.userId);
    if (!summary) {
      response.status(404).json({ error: "Profile not found" });
      return;
    }
    response.json(summary);
  } catch (error) {
    next(error);
  }
});

usersRouter.get("/me/friends", async (request: AuthenticatedRequest, response, next) => {
  try {
    response.json({ items: await getFriends(request.auth!.userId) });
  } catch (error) {
    next(error);
  }
});
