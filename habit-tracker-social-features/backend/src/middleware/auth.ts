import type { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import { env } from "../config/env.js";

export interface AuthenticatedRequest extends Request {
  auth?: {
    userId: string;
    email: string;
  };
}

export function authMiddleware(request: AuthenticatedRequest, response: Response, next: NextFunction) {
  const header = request.headers.authorization;
  if (!header?.startsWith("Bearer ")) {
    response.status(401).json({ error: "Missing bearer token" });
    return;
  }

  try {
    const payload = jwt.verify(header.slice("Bearer ".length), env.jwtSecret) as { sub: string; email: string; };
    request.auth = { userId: payload.sub, email: payload.email };
    next();
  } catch (error) {
    response.status(401).json({ error: "Invalid token" });
  }
}
