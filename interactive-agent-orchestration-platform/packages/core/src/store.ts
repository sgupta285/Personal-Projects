function cloneValue<T>(value: T): T {
  return JSON.parse(JSON.stringify(value));
}

import { AgentRun, StreamEvent } from "./types.js";

export class InMemoryRunStore {
  private readonly runs = new Map<string, AgentRun>();
  private readonly events = new Map<string, StreamEvent[]>();

  create(run: AgentRun): AgentRun {
    this.runs.set(run.id, cloneValue(run));
    this.events.set(run.id, []);
    return this.get(run.id)!;
  }

  save(run: AgentRun): AgentRun {
    this.runs.set(run.id, cloneValue(run));
    return this.get(run.id)!;
  }

  get(runId: string): AgentRun | undefined {
    const record = this.runs.get(runId);
    return record ? cloneValue(record) : undefined;
  }

  list(): AgentRun[] {
    return [...this.runs.values()].map((run) => cloneValue(run));
  }

  appendEvent(event: StreamEvent): void {
    const current = this.events.get(event.runId) ?? [];
    current.push(cloneValue(event));
    this.events.set(event.runId, current);
  }

  getEvents(runId: string): StreamEvent[] {
    return (this.events.get(runId) ?? []).map((event) => cloneValue(event));
  }
}
