import Redis from "ioredis";

const REDIS_URL = process.env.REDIS_URL || "redis://localhost:6379";

let publisher: Redis | null = null;
let subscriber: Redis | null = null;

export function getPublisher(): Redis {
  if (!publisher) {
    publisher = new Redis(REDIS_URL, { maxRetriesPerRequest: 3, lazyConnect: true });
    publisher.on("error", (err) => console.error("[Redis Publisher Error]", err.message));
  }
  return publisher;
}

export function getSubscriber(): Redis {
  if (!subscriber) {
    subscriber = new Redis(REDIS_URL, { maxRetriesPerRequest: 3, lazyConnect: true });
    subscriber.on("error", (err) => console.error("[Redis Subscriber Error]", err.message));
  }
  return subscriber;
}

// Channels for pub/sub events
export const CHANNELS = {
  NEW_MESSAGE: "buckyconnect:message:new",
  EDIT_MESSAGE: "buckyconnect:message:edit",
  DELETE_MESSAGE: "buckyconnect:message:delete",
  USER_PRESENCE: "buckyconnect:user:presence",
  TYPING: "buckyconnect:typing",
  CHANNEL_UPDATE: "buckyconnect:channel:update",
} as const;

export async function publishEvent(channel: string, data: Record<string, any>): Promise<void> {
  try {
    await getPublisher().publish(channel, JSON.stringify(data));
  } catch (err) {
    console.error(`[Redis Publish Error] channel=${channel}`, err);
  }
}

export async function connectRedis(): Promise<boolean> {
  try {
    await getPublisher().connect();
    await getSubscriber().connect();
    await getPublisher().ping();
    console.log("[Redis] Connected successfully");
    return true;
  } catch (err) {
    console.warn("[Redis] Connection failed — running without pub/sub:", (err as Error).message);
    return false;
  }
}

export async function disconnectRedis(): Promise<void> {
  if (publisher) { publisher.disconnect(); publisher = null; }
  if (subscriber) { subscriber.disconnect(); subscriber = null; }
}

// Fallback in-memory pub/sub for when Redis is unavailable
type Handler = (channel: string, message: string) => void;
const localHandlers: Map<string, Set<Handler>> = new Map();

export const localPubSub = {
  subscribe(channel: string, handler: Handler) {
    if (!localHandlers.has(channel)) localHandlers.set(channel, new Set());
    localHandlers.get(channel)!.add(handler);
  },
  unsubscribe(channel: string, handler: Handler) {
    localHandlers.get(channel)?.delete(handler);
  },
  publish(channel: string, message: string) {
    localHandlers.get(channel)?.forEach((h) => h(channel, message));
  },
};
