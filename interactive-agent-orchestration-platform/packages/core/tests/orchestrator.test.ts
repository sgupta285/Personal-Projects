import test from "node:test";
import assert from "node:assert/strict";
import { OrchestrationEngine, summarizeRuns } from "../src/index.js";

test("engine creates and completes a run", async () => {
  const engine = new OrchestrationEngine();
  const run = engine.createRun({
    agentName: "ops-agent",
    userIntent: "download the latest invoice and send it to finance"
  });

  const completed = await engine.executeRun(run.id, { minStepLatencyMs: 1, maxStepLatencyMs: 1 });

  assert.equal(completed.status, "completed");
  assert.equal(completed.steps.length >= 3, true);
  assert.equal(completed.steps.every((step) => step.status === "completed"), true);
  assert.equal(completed.totalCostUsd > 0, true);
  assert.equal(engine.getEvents(run.id).length > 0, true);
});

test("engine records failure and failure reason", async () => {
  const engine = new OrchestrationEngine();
  const run = engine.createRun({
    agentName: "ops-agent",
    userIntent: "summarize the dashboard and email the result"
  });

  const failed = await engine.executeRun(run.id, {
    failAtStepIndex: 1,
    minStepLatencyMs: 1,
    maxStepLatencyMs: 1
  });

  assert.equal(failed.status, "failed");
  assert.match(failed.failureReason ?? "", /Simulated failure/);
  assert.equal(failed.steps[1].status, "failed");
});

test("retry intervention resets downstream steps", async () => {
  const engine = new OrchestrationEngine();
  const run = engine.createRun({
    agentName: "ops-agent",
    userIntent: "download the latest invoice"
  });

  await engine.executeRun(run.id, { failAtStepIndex: 1, minStepLatencyMs: 1, maxStepLatencyMs: 1 });
  const afterFailure = engine.getRun(run.id)!;
  assert.equal(afterFailure.status, "failed");

  engine.recordIntervention(run.id, {
    actor: "operator@local",
    type: "retry_from_step",
    note: "Retry from failed step after selector fix",
    details: { stepIndex: 1 }
  });

  const reset = engine.getRun(run.id)!;
  assert.equal(reset.currentStepIndex, 0);
  assert.equal(reset.steps[1].status, "pending");
  assert.equal(reset.steps[2].status, "pending");
});

test("metrics summarize outcomes and intervention rate", async () => {
  const engine = new OrchestrationEngine();
  const first = engine.createRun({ agentName: "ops-agent", userIntent: "download the latest invoice" });
  const second = engine.createRun({ agentName: "ops-agent", userIntent: "email the result" });

  await engine.executeRun(first.id, { minStepLatencyMs: 1, maxStepLatencyMs: 1 });
  await engine.executeRun(second.id, { failAtStepIndex: 0, minStepLatencyMs: 1, maxStepLatencyMs: 1 });
  engine.recordIntervention(second.id, {
    actor: "reviewer@local",
    type: "pause",
    note: "Inspect failure before resume"
  });

  const summary = summarizeRuns(engine.listRuns());

  assert.equal(summary.totalRuns, 2);
  assert.equal(summary.byStatus.completed, 1);
  assert.equal(summary.byStatus.paused, 1);
  assert.equal(summary.interventionRate, 0.5);
});
