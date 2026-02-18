import { WebSocketServer, WebSocket } from "ws";
import { IncomingMessage, Server as HttpServer } from "http";
import { v4 as uuidv4 } from "uuid";
import * as db from "../models/database";
import {
  getSubscriber,
  publishEvent,
  CHANNELS,
  localPubSub,
  connectRedis,
} from "../utils/redis";

interface ClientInfo {
  ws: WebSocket;
  userId: string;
  username: string;
  channels: Set<string>;
}

const clients = new Map<string, ClientInfo>();
let redisAvailable = false;

export function setupWebSocket(server: HttpServer): WebSocketServer {
  const wss = new WebSocketServer({ server, path: "/ws" });

  // Try to set up Redis subscriber for fanout
  initRedisSubscriber();

  wss.on("connection", (ws: WebSocket, req: IncomingMessage) => {
    const connectionId = uuidv4();
    console.log(`[WS] New connection: ${connectionId}`);

    ws.on("message", (raw: Buffer) => {
      try {
        const data = JSON.parse(raw.toString());
        handleClientMessage(connectionId, ws, data);
      } catch (err) {
        sendToClient(ws, { type: "error", message: "Invalid JSON" });
      }
    });

    ws.on("close", () => {
      const client = clients.get(connectionId);
      if (client) {
        db.updateUserStatus(client.userId, "offline");
        broadcastToAll({
          type: "presence",
          userId: client.userId,
          username: client.username,
          status: "offline",
        });
        clients.delete(connectionId);
      }
      console.log(`[WS] Disconnected: ${connectionId}`);
    });

    ws.on("error", (err) => {
      console.error(`[WS] Error on ${connectionId}:`, err.message);
    });
  });

  // Heartbeat to detect dead connections
  const heartbeat = setInterval(() => {
    wss.clients.forEach((ws) => {
      if ((ws as any).__isAlive === false) return ws.terminate();
      (ws as any).__isAlive = false;
      ws.ping();
    });
  }, 30000);

  wss.on("close", () => clearInterval(heartbeat));

  wss.on("connection", (ws) => {
    (ws as any).__isAlive = true;
    ws.on("pong", () => { (ws as any).__isAlive = true; });
  });

  return wss;
}

function handleClientMessage(connectionId: string, ws: WebSocket, data: any) {
  switch (data.type) {
    case "auth": {
      const { userId, username } = data;
      if (!userId || !username) {
        return sendToClient(ws, { type: "error", message: "userId and username required" });
      }
      clients.set(connectionId, { ws, userId, username, channels: new Set() });
      db.updateUserStatus(userId, "online");

      // Notify all clients of user presence
      broadcastToAll({ type: "presence", userId, username, status: "online" });
      sendToClient(ws, { type: "auth_ok", connectionId });
      break;
    }

    case "join_channel": {
      const client = clients.get(connectionId);
      if (!client) return sendToClient(ws, { type: "error", message: "Not authenticated" });
      client.channels.add(data.channelId);
      db.joinChannel(data.channelId, client.userId);
      broadcastToChannel(data.channelId, {
        type: "user_joined",
        channelId: data.channelId,
        userId: client.userId,
        username: client.username,
      });
      break;
    }

    case "leave_channel": {
      const client = clients.get(connectionId);
      if (!client) return;
      client.channels.delete(data.channelId);
      broadcastToChannel(data.channelId, {
        type: "user_left",
        channelId: data.channelId,
        userId: client.userId,
        username: client.username,
      });
      break;
    }

    case "message": {
      const client = clients.get(connectionId);
      if (!client) return sendToClient(ws, { type: "error", message: "Not authenticated" });
      const msgId = uuidv4();
      const msg = db.createMessage(msgId, data.channelId, client.userId, data.content);

      const payload = { type: "new_message", channelId: data.channelId, message: msg };

      if (redisAvailable) {
        publishEvent(CHANNELS.NEW_MESSAGE, payload);
      } else {
        broadcastToChannel(data.channelId, payload);
      }
      break;
    }

    case "typing": {
      const client = clients.get(connectionId);
      if (!client) return;
      const typingPayload = {
        type: "typing",
        channelId: data.channelId,
        userId: client.userId,
        username: client.username,
        isTyping: data.isTyping ?? true,
      };

      if (redisAvailable) {
        publishEvent(CHANNELS.TYPING, typingPayload);
      } else {
        broadcastToChannel(data.channelId, typingPayload, connectionId);
      }
      break;
    }

    case "ping": {
      sendToClient(ws, { type: "pong", timestamp: Date.now() });
      break;
    }

    default:
      sendToClient(ws, { type: "error", message: `Unknown message type: ${data.type}` });
  }
}

async function initRedisSubscriber() {
  try {
    redisAvailable = await connectRedis();
    if (!redisAvailable) return;

    const sub = getSubscriber();
    const channels = Object.values(CHANNELS);

    for (const ch of channels) {
      await sub.subscribe(ch);
    }

    sub.on("message", (channel: string, rawMessage: string) => {
      try {
        const data = JSON.parse(rawMessage);
        // Fanout to connected WebSocket clients
        if (data.channelId) {
          broadcastToChannel(data.channelId, data);
        } else {
          broadcastToAll(data);
        }
      } catch (err) {
        console.error("[Redis Sub] Parse error:", err);
      }
    });

    console.log("[WS] Redis subscriber listening on", channels.length, "channels");
  } catch (err) {
    console.warn("[WS] Redis not available, using local broadcast only");
    redisAvailable = false;
  }
}

function sendToClient(ws: WebSocket, data: any) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(data));
  }
}

function broadcastToChannel(channelId: string, data: any, excludeConnectionId?: string) {
  clients.forEach((client, connId) => {
    if (client.channels.has(channelId) && connId !== excludeConnectionId) {
      sendToClient(client.ws, data);
    }
  });
}

function broadcastToAll(data: any, excludeConnectionId?: string) {
  clients.forEach((client, connId) => {
    if (connId !== excludeConnectionId) {
      sendToClient(client.ws, data);
    }
  });
}

export function getConnectedClientsCount(): number {
  return clients.size;
}

export function getOnlineUsers(): string[] {
  const users: string[] = [];
  clients.forEach((client) => {
    if (!users.includes(client.userId)) users.push(client.userId);
  });
  return users;
}
