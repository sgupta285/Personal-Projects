import { createServer } from "node:http";
import { WebSocketServer } from "ws";
import { OrchestrationEngine } from "@orchestration/core";

const engine = new OrchestrationEngine();
const port = Number(process.env.PORT ?? 8090);
const server = createServer();
const wss = new WebSocketServer({ server });

wss.on("connection", (socket, request) => {
  const url = new URL(request.url ?? "/", `http://${request.headers.host}`);
  const runId = url.searchParams.get("runId");

  if (!runId) {
    socket.send(JSON.stringify({ type: "error", message: "runId query parameter is required" }));
    socket.close();
    return;
  }

  for (const event of engine.getEvents(runId)) {
    socket.send(JSON.stringify(event));
  }

  const handler = (event: unknown) => {
    socket.send(JSON.stringify(event));
  };

  engine.bus.on(runId, handler);
  socket.on("close", () => {
    engine.bus.off(runId, handler);
  });
});

server.listen(port, () => {
  console.log(`Realtime service listening on ws://localhost:${port}`);
});
