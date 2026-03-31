import { useMemo, useState } from "react";
import { useRunFeed } from "../hooks/useRunFeed";
import { MetricCard } from "../components/MetricCard";
import { RunTable } from "../components/RunTable";
import { RunDetail } from "../components/RunDetail";

export function App() {
  const { runs, summary } = useRunFeed();
  const [selectedRunId, setSelectedRunId] = useState(runs[0]?.id ?? "");
  const selectedRun = useMemo(() => runs.find((run) => run.id === selectedRunId) ?? runs[0], [runs, selectedRunId]);

  return (
    <div className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Operator Console</p>
          <h1>Interactive Agent Orchestration Platform</h1>
          <p className="hero-copy">
            Observe step-by-step execution, inspect tool traces, and intervene before an autonomous run drifts out of bounds.
          </p>
        </div>
      </header>

      <section className="metrics-grid">
        <MetricCard label="Total Runs" value={String(summary.totalRuns)} detail="Across the current window" />
        <MetricCard label="Average Cost" value={`$${summary.averageCostUsd.toFixed(4)}`} detail="Per run" />
        <MetricCard label="Average Latency" value={`${summary.averageLatencyMs} ms`} detail="Per run" />
        <MetricCard label="Intervention Rate" value={`${(summary.interventionRate * 100).toFixed(0)}%`} detail="Operator involvement" />
      </section>

      <main className="content-grid">
        <RunTable runs={runs} selectedRunId={selectedRunId} onSelect={setSelectedRunId} />
        {selectedRun ? <RunDetail run={selectedRun} /> : null}
      </main>
    </div>
  );
}
