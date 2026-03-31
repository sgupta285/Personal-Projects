import express from "express";
import cors from "cors";
import { z } from "zod";
import { OrchestrationEngine, summarizeRuns } from "@orchestration/core";

const app = express();
const port = Number(process.env.PORT ?? 8080);
const engine = new OrchestrationEngine();

app.use(cors());
app.use(express.json());

const createRunSchema = z.object({
  agentName: z.string().min(1),
  userIntent: z.string().min(1),
  model: z.string().optional(),
  promptConfig: z.string().optional(),
  tags: z.array(z.string()).optional()
});

const interventionSchema = z.object({
  actor: z.string().min(1),
  type: z.enum(["pause", "resume", "retry_from_step", "swap_prompt_config", "switch_model", "override_output"]),
  note: z.string().min(1),
  details: z.record(z.string(), z.unknown()).optional()
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

app.get("/runs", (_req, res) => {
  res.json({ data: engine.listRuns(), summary: summarizeRuns(engine.listRuns()) });
});

app.post("/runs", (req, res) => {
  const payload = createRunSchema.parse(req.body);
  const run = engine.createRun(payload);
  res.status(201).json({ data: run });
});

app.get("/runs/:runId", (req, res) => {
  const run = engine.getRun(req.params.runId);
  if (!run) {
    return res.status(404).json({ error: "Run not found" });
  }
  return res.json({ data: run, events: engine.getEvents(run.id) });
});

app.post("/runs/:runId/execute", async (req, res) => {
  try {
    const run = await engine.executeRun(req.params.runId, req.body ?? {});
    return res.json({ data: run });
  } catch (error) {
    return res.status(400).json({ error: error instanceof Error ? error.message : "Unknown execution error" });
  }
});

app.post("/runs/:runId/interventions", (req, res) => {
  try {
    const payload = interventionSchema.parse(req.body);
    const run = engine.recordIntervention(req.params.runId, payload);
    return res.status(201).json({ data: run });
  } catch (error) {
    return res.status(400).json({ error: error instanceof Error ? error.message : "Unknown intervention error" });
  }
});

app.listen(port, () => {
  console.log(`API listening on http://localhost:${port}`);
});
