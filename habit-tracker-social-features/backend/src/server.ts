import { app } from "./app.js";
import { env } from "./config/env.js";
import { initInfrastructure } from "./db/index.js";

async function bootstrap() {
  await initInfrastructure();
  app.listen(env.port, () => {
    console.log(`Habit backend listening on http://localhost:${env.port}`);
  });
}

bootstrap().catch((error) => {
  console.error("Failed to boot service", error);
  process.exit(1);
});
