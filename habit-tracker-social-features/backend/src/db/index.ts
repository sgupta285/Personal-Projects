import { Pool } from "pg";
import { createClient } from "redis";
import { env } from "../config/env.js";

export const pool = new Pool({
  connectionString: env.databaseUrl
});

export const redis = createClient({
  url: env.redisUrl
});

redis.on("error", (error) => {
  console.warn("Redis connection issue", error instanceof Error ? error.message : error);
});

export async function initInfrastructure() {
  await pool.query("select 1");
  if (!redis.isOpen) {
    try {
      await redis.connect();
    } catch (error) {
      console.warn("Redis unavailable, continuing without cache");
    }
  }
}
