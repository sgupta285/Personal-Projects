export type RunStatus = "queued" | "running" | "paused" | "completed" | "failed" | "cancelled";

export interface StepTrace {
  id: string;
  name: string;
  rationale: string;
  toolName: string;
  status: string;
  costUsd: number;
  latencyMs: number;
  retryCount: number;
}

export interface AgentRun {
  id: string;
  agentName: string;
  userIntent: string;
  status: RunStatus;
  model: string;
  promptConfig: string;
  totalCostUsd: number;
  totalLatencyMs: number;
  steps: StepTrace[];
  interventions: Array<{ id: string; actor: string; type: string; note: string }>;
}

export interface MetricsSummary {
  totalRuns: number;
  byStatus: Record<RunStatus, number>;
  averageCostUsd: number;
  averageLatencyMs: number;
  interventionRate: number;
  failureRate: number;
}
