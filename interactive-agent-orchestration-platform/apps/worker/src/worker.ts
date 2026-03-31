import Redis from "ioredis";
import { OrchestrationEngine } from "@orchestration/core";

const redisUrl = process.env.REDIS_URL ?? "redis://localhost:6379";
const queueName = process.env.RUN_QUEUE ?? "agent:runs";
const redis = new Redis(redisUrl);
const engine = new OrchestrationEngine();

async function main(): Promise<void> {
  console.log(`Worker waiting on ${queueName} using ${redisUrl}`);

  while (true) {
    const result = await redis.brpop(queueName, 0);
    if (!result) {
      continue;
    }

    const payload = JSON.parse(result[1]) as { runId: string; failAtStepIndex?: number };
    console.log(`Executing run ${payload.runId}`);
    await engine.executeRun(payload.runId, { failAtStepIndex: payload.failAtStepIndex });
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
