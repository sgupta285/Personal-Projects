import { Router } from "express";
import { pool, redis } from "../db/index.js";

export const healthRouter = Router();

healthRouter.get("/", async (_request, response, next) => {
  try {
    await pool.query("select 1");
    response.json({
      status: "ok",
      services: {
        database: "ok",
        redis: redis.isOpen ? "ok" : "degraded"
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    next(error);
  }
});
