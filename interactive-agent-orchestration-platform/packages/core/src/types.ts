export type StepStatus = "pending" | "running" | "completed" | "failed" | "paused" | "skipped";
export type RunStatus = "queued" | "running" | "paused" | "completed" | "failed" | "cancelled";
export type EventType =
  | "run.created"
  | "run.started"
  | "run.completed"
  | "run.failed"
  | "run.paused"
  | "run.resumed"
  | "step.started"
  | "step.completed"
  | "step.failed"
  | "operator.intervened"
  | "run.cost_updated";

export interface StepTrace {
  id: string;
  name: string;
  rationale: string;
  toolName: string;
  status: StepStatus;
  input: Record<string, unknown>;
  output?: Record<string, unknown>;
  error?: string;
  startedAt?: string;
  completedAt?: string;
  costUsd: number;
  latencyMs: number;
  retryCount: number;
}

export interface OperatorIntervention {
  id: string;
  type: "pause" | "resume" | "retry_from_step" | "swap_prompt_config" | "switch_model" | "override_output";
  actor: string;
  note: string;
  createdAt: string;
  details?: Record<string, unknown>;
}

export interface AgentRun {
  id: string;
  agentName: string;
  userIntent: string;
  status: RunStatus;
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
  currentStepIndex: number;
  model: string;
  promptConfig: string;
  totalCostUsd: number;
  totalLatencyMs: number;
  failureReason?: string;
  tags: string[];
  steps: StepTrace[];
  interventions: OperatorIntervention[];
}

export interface StreamEvent {
  runId: string;
  type: EventType;
  timestamp: string;
  payload: Record<string, unknown>;
}

export interface CreateRunInput {
  agentName: string;
  userIntent: string;
  model?: string;
  promptConfig?: string;
  tags?: string[];
  steps?: Array<Pick<StepTrace, "name" | "toolName" | "rationale" | "input">>;
}

export interface MetricsSummary {
  totalRuns: number;
  byStatus: Record<RunStatus, number>;
  averageCostUsd: number;
  averageLatencyMs: number;
  interventionRate: number;
  failureRate: number;
}
