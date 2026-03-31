import { AgentRun, MetricsSummary } from "./types";

export const mockRuns: AgentRun[] = [
  {
    id: "run_1",
    agentName: "billing-agent",
    userIntent: "Download the latest invoice and email it to finance.",
    status: "completed",
    model: "gpt-4.1-mini",
    promptConfig: "default.operator.v1",
    totalCostUsd: 0.0052,
    totalLatencyMs: 112,
    interventions: [],
    steps: [
      { id: "s1", name: "Load account workspace", rationale: "Enter billing area first", toolName: "browser.navigate", status: "completed", costUsd: 0.0008, latencyMs: 25, retryCount: 0 },
      { id: "s2", name: "Open billing screen", rationale: "Expose downloadable invoices", toolName: "browser.click", status: "completed", costUsd: 0.0012, latencyMs: 35, retryCount: 0 },
      { id: "s3", name: "Download latest invoice", rationale: "Fetch artifact", toolName: "browser.download", status: "completed", costUsd: 0.0016, latencyMs: 45, retryCount: 0 }
    ]
  },
  {
    id: "run_2",
    agentName: "ops-agent",
    userIntent: "Summarize the dashboard and send the report.",
    status: "paused",
    model: "claude-3.7-sonnet",
    promptConfig: "ops.review.v2",
    totalCostUsd: 0.0031,
    totalLatencyMs: 65,
    interventions: [{ id: "i1", actor: "operator@local", type: "pause", note: "Pause before final send" }],
    steps: [
      { id: "s4", name: "Collect result context", rationale: "Read latest data", toolName: "context.read", status: "completed", costUsd: 0.0008, latencyMs: 25, retryCount: 0 },
      { id: "s5", name: "Draft operator summary", rationale: "Prepare operator review", toolName: "llm.summarize", status: "running", costUsd: 0.0012, latencyMs: 40, retryCount: 0 }
    ]
  }
];

export const mockSummary: MetricsSummary = {
  totalRuns: 2,
  byStatus: {
    queued: 0,
    running: 0,
    paused: 1,
    completed: 1,
    failed: 0,
    cancelled: 0
  },
  averageCostUsd: 0.0042,
  averageLatencyMs: 89,
  interventionRate: 0.5,
  failureRate: 0
};
