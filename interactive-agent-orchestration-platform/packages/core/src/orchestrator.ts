import { EventEmitter } from "node:events";
import { buildInitialSteps } from "./planner.js";
import { InMemoryRunStore } from "./store.js";
import { AgentRun, CreateRunInput, OperatorIntervention, StepTrace, StreamEvent } from "./types.js";
import { nowIso, uid, wait } from "./utils.js";

export interface ExecutionOptions {
  failAtStepIndex?: number;
  minStepLatencyMs?: number;
  maxStepLatencyMs?: number;
}

export class OrchestrationEngine {
  readonly bus = new EventEmitter();

  constructor(private readonly store: InMemoryRunStore = new InMemoryRunStore()) {}

  getStore(): InMemoryRunStore {
    return this.store;
  }

  createRun(input: CreateRunInput): AgentRun {
    const timestamp = nowIso();
    const run: AgentRun = {
      id: uid("run"),
      agentName: input.agentName,
      userIntent: input.userIntent,
      status: "queued",
      createdAt: timestamp,
      updatedAt: timestamp,
      currentStepIndex: -1,
      model: input.model ?? "gpt-4.1-mini",
      promptConfig: input.promptConfig ?? "default.operator.v1",
      totalCostUsd: 0,
      totalLatencyMs: 0,
      tags: input.tags ?? [],
      steps: buildInitialSteps(input),
      interventions: []
    };

    this.store.create(run);
    this.emit({
      runId: run.id,
      type: "run.created",
      timestamp,
      payload: { agentName: run.agentName, intent: run.userIntent }
    });

    return this.store.get(run.id)!;
  }

  listRuns(): AgentRun[] {
    return this.store.list();
  }

  getRun(runId: string): AgentRun | undefined {
    return this.store.get(runId);
  }

  getEvents(runId: string): StreamEvent[] {
    return this.store.getEvents(runId);
  }

  recordIntervention(runId: string, intervention: Omit<OperatorIntervention, "id" | "createdAt">): AgentRun {
    const run = this.mustGetRun(runId);
    const fullIntervention: OperatorIntervention = {
      id: uid("intervention"),
      createdAt: nowIso(),
      ...intervention
    };
    run.interventions.push(fullIntervention);

    if (intervention.type === "pause") {
      run.status = "paused";
      this.emit({ runId, type: "run.paused", timestamp: fullIntervention.createdAt, payload: { actor: intervention.actor, note: intervention.note } });
    }

    if (intervention.type === "resume") {
      run.status = "running";
      this.emit({ runId, type: "run.resumed", timestamp: fullIntervention.createdAt, payload: { actor: intervention.actor, note: intervention.note } });
    }

    if (intervention.type === "retry_from_step") {
      const targetIndex = Number(intervention.details?.stepIndex ?? run.currentStepIndex);
      run.currentStepIndex = Math.max(-1, targetIndex - 1);
      for (let index = targetIndex; index < run.steps.length; index += 1) {
        run.steps[index].status = "pending";
        run.steps[index].error = undefined;
        run.steps[index].output = undefined;
        run.steps[index].startedAt = undefined;
        run.steps[index].completedAt = undefined;
      }
    }

    run.updatedAt = nowIso();
    this.store.save(run);
    this.emit({
      runId,
      type: "operator.intervened",
      timestamp: fullIntervention.createdAt,
      payload: {
        type: fullIntervention.type,
        actor: fullIntervention.actor,
        note: fullIntervention.note,
        details: fullIntervention.details ?? {}
      }
    });
    return this.store.get(runId)!;
  }

  async executeRun(runId: string, options: ExecutionOptions = {}): Promise<AgentRun> {
    const run = this.mustGetRun(runId);
    if (run.status === "completed") {
      return run;
    }

    run.status = "running";
    run.startedAt ??= nowIso();
    run.updatedAt = nowIso();
    this.store.save(run);
    this.emit({ runId, type: "run.started", timestamp: nowIso(), payload: { totalSteps: run.steps.length } });

    for (let index = run.currentStepIndex + 1; index < run.steps.length; index += 1) {
      const fresh = this.mustGetRun(runId);
      if (fresh.status === "paused") {
        break;
      }

      const step = fresh.steps[index];
      fresh.currentStepIndex = index;
      this.markStepStarted(fresh, step);
      await wait(this.sampleLatency(options.minStepLatencyMs ?? 15, options.maxStepLatencyMs ?? 40));

      if (options.failAtStepIndex === index) {
        step.status = "failed";
        step.error = `Simulated failure at step ${index}`;
        step.completedAt = nowIso();
        step.latencyMs += 25;
        step.costUsd += 0.0012;
        fresh.totalLatencyMs += step.latencyMs;
        fresh.totalCostUsd = Number((fresh.totalCostUsd + step.costUsd).toFixed(4));
        fresh.status = "failed";
        fresh.failureReason = step.error;
        fresh.updatedAt = nowIso();
        this.store.save(fresh);
        this.emit({ runId, type: "step.failed", timestamp: nowIso(), payload: { stepId: step.id, stepName: step.name, error: step.error } });
        this.emit({ runId, type: "run.failed", timestamp: nowIso(), payload: { failureReason: fresh.failureReason } });
        return this.store.get(runId)!;
      }

      this.markStepCompleted(fresh, step, index);
    }

    const finalRun = this.mustGetRun(runId);
    const hasPending = finalRun.steps.some((step) => step.status === "pending" || step.status === "running");

    if (!hasPending && finalRun.status !== "failed") {
      finalRun.status = "completed";
      finalRun.completedAt = nowIso();
      finalRun.updatedAt = nowIso();
      this.store.save(finalRun);
      this.emit({ runId, type: "run.completed", timestamp: nowIso(), payload: { totalCostUsd: finalRun.totalCostUsd, totalLatencyMs: finalRun.totalLatencyMs } });
    }

    return this.store.get(runId)!;
  }

  private markStepStarted(run: AgentRun, step: StepTrace): void {
    step.status = "running";
    step.startedAt = nowIso();
    run.updatedAt = nowIso();
    this.store.save(run);
    this.emit({
      runId: run.id,
      type: "step.started",
      timestamp: step.startedAt,
      payload: { stepId: step.id, stepName: step.name, toolName: step.toolName }
    });
  }

  private markStepCompleted(run: AgentRun, step: StepTrace, index: number): void {
    step.status = "completed";
    step.completedAt = nowIso();
    step.latencyMs += 25 + index * 10;
    step.costUsd += Number((0.0008 + index * 0.0004).toFixed(4));
    step.output = {
      summary: `${step.toolName} finished successfully`,
      confidence: Number((0.87 - index * 0.03).toFixed(2))
    };

    run.totalLatencyMs += step.latencyMs;
    run.totalCostUsd = Number((run.totalCostUsd + step.costUsd).toFixed(4));
    run.updatedAt = nowIso();
    this.store.save(run);

    this.emit({
      runId: run.id,
      type: "step.completed",
      timestamp: step.completedAt,
      payload: {
        stepId: step.id,
        stepName: step.name,
        latencyMs: step.latencyMs,
        costUsd: step.costUsd,
        toolName: step.toolName
      }
    });

    this.emit({
      runId: run.id,
      type: "run.cost_updated",
      timestamp: nowIso(),
      payload: { totalCostUsd: run.totalCostUsd, totalLatencyMs: run.totalLatencyMs }
    });
  }

  private emit(event: StreamEvent): void {
    this.store.appendEvent(event);
    this.bus.emit(event.runId, event);
    this.bus.emit("all", event);
  }

  private mustGetRun(runId: string): AgentRun {
    const run = this.store.get(runId);
    if (!run) {
      throw new Error(`Run not found: ${runId}`);
    }
    return run;
  }

  private sampleLatency(min: number, max: number): number {
    if (max <= min) {
      return min;
    }
    return Math.round(Math.random() * (max - min) + min);
  }
}
