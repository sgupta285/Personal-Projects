import dotenv from "dotenv";

dotenv.config();

function requireValue(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export const env = {
  port: Number(process.env.PORT ?? 4000),
  databaseUrl: requireValue("DATABASE_URL", "postgresql://habits:habits@localhost:5432/habits"),
  redisUrl: requireValue("REDIS_URL", "redis://localhost:6379"),
  jwtSecret: requireValue("JWT_SECRET", "change-me"),
  fcmServerKey: requireValue("FCM_SERVER_KEY", "demo-key")
};
