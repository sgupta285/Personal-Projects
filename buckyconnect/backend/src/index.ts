import "dotenv/config";
import express from "express";
import cors from "cors";
import http from "http";
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { typeDefs } from "./graphql/schema";
import { resolvers } from "./graphql/resolvers";
import { setupWebSocket, getConnectedClientsCount } from "./websocket/handler";
import { authMiddleware } from "./middleware/auth";
import { getDb, closeDb } from "./models/database";
import { disconnectRedis } from "./utils/redis";

const PORT = parseInt(process.env.PORT || "4000", 10);
const CORS_ORIGIN = process.env.CORS_ORIGIN || "http://localhost:5173";

async function main() {
  const app = express();
  const httpServer = http.createServer(app);

  // Initialize database
  getDb();
  console.log("[DB] SQLite initialized");

  // CORS
  app.use(cors({ origin: CORS_ORIGIN, credentials: true }));
  app.use(express.json());
  app.use(authMiddleware);

  // Health check
  app.get("/health", (_req, res) => {
    res.json({
      status: "ok",
      uptime: process.uptime(),
      connections: getConnectedClientsCount(),
      timestamp: new Date().toISOString(),
    });
  });

  // Apollo GraphQL server
  const apollo = new ApolloServer({ typeDefs, resolvers });
  await apollo.start();

  app.use(
    "/graphql",
    expressMiddleware(apollo, {
      context: async ({ req }) => ({
        user: (req as any).user || null,
      }),
    })
  );

  // WebSocket setup
  const wss = setupWebSocket(httpServer);
  console.log("[WS] WebSocket server ready at /ws");

  // Start listening
  httpServer.listen(PORT, () => {
    console.log(`\n🚀 BuckyConnect Server running on http://localhost:${PORT}`);
    console.log(`   GraphQL:   http://localhost:${PORT}/graphql`);
    console.log(`   WebSocket: ws://localhost:${PORT}/ws`);
    console.log(`   Health:    http://localhost:${PORT}/health\n`);
  });

  // Graceful shutdown
  const shutdown = async () => {
    console.log("\n[Shutdown] Closing connections...");
    wss.close();
    await apollo.stop();
    await disconnectRedis();
    closeDb();
    httpServer.close(() => {
      console.log("[Shutdown] Complete");
      process.exit(0);
    });
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
