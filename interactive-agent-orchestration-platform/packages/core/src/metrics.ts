import { AgentRun, MetricsSummary, RunStatus } from "./types.js";

const STATUSES: RunStatus[] = ["queued", "running", "paused", "completed", "failed", "cancelled"];

export function summarizeRuns(runs: AgentRun[]): MetricsSummary {
  const byStatus = Object.fromEntries(STATUSES.map((status) => [status, 0])) as Record<RunStatus, number>;

  let totalCostUsd = 0;
  let totalLatencyMs = 0;
  let runsWithInterventions = 0;
  let failedRuns = 0;

  for (const run of runs) {
    byStatus[run.status] += 1;
    totalCostUsd += run.totalCostUsd;
    totalLatencyMs += run.totalLatencyMs;
    if (run.interventions.length > 0) {
      runsWithInterventions += 1;
    }
    if (run.status === "failed") {
      failedRuns += 1;
    }
  }

  const divisor = runs.length || 1;

  return {
    totalRuns: runs.length,
    byStatus,
    averageCostUsd: Number((totalCostUsd / divisor).toFixed(4)),
    averageLatencyMs: Math.round(totalLatencyMs / divisor),
    interventionRate: Number((runsWithInterventions / divisor).toFixed(4)),
    failureRate: Number((failedRuns / divisor).toFixed(4))
  };
}
