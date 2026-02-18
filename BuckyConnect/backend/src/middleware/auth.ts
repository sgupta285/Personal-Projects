import { Request, Response, NextFunction } from "express";
import { getUserById } from "../models/database";

// Simple header-based auth for demo purposes
// In production, replace with JWT/OAuth
export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const userId = req.headers["x-user-id"] as string;
  if (!userId) {
    return next(); // Allow unauthenticated for GraphQL playground
  }

  const user = getUserById(userId);
  if (user) {
    (req as any).user = user;
  }
  next();
}

export function requireAuth(req: Request, res: Response, next: NextFunction) {
  if (!(req as any).user) {
    return res.status(401).json({ error: "Authentication required" });
  }
  next();
}
