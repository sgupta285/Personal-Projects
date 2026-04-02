import type { NextFunction, Request, Response } from "express";

export function errorMiddleware(error: unknown, request: Request, response: Response, next: NextFunction) {
  console.error("Unhandled application error", error);
  response.status(500).json({
    error: "internal_error",
    message: error instanceof Error ? error.message : "Unknown server error"
  });
}
