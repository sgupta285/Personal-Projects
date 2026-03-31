import { AgentRun } from "../lib/types";

interface RunTableProps {
  runs: AgentRun[];
  selectedRunId: string;
  onSelect: (runId: string) => void;
}

export function RunTable({ runs, selectedRunId, onSelect }: RunTableProps) {
  return (
    <div className="panel">
      <div className="panel-header">
        <h2>Recent Runs</h2>
      </div>
      <table className="run-table">
        <thead>
          <tr>
            <th>Agent</th>
            <th>Status</th>
            <th>Model</th>
            <th>Cost</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.id} className={selectedRunId === run.id ? "selected" : ""} onClick={() => onSelect(run.id)}>
              <td>
                <div className="run-agent">{run.agentName}</div>
                <div className="run-intent">{run.userIntent}</div>
              </td>
              <td><span className={`status-pill status-${run.status}`}>{run.status}</span></td>
              <td>{run.model}</td>
              <td>${run.totalCostUsd.toFixed(4)}</td>
              <td>{run.totalLatencyMs} ms</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
