import { AgentRun } from "../lib/types";

interface RunDetailProps {
  run: AgentRun;
}

export function RunDetail({ run }: RunDetailProps) {
  return (
    <div className="panel detail-grid">
      <div className="panel-header">
        <h2>Run Detail</h2>
        <div className={`status-pill status-${run.status}`}>{run.status}</div>
      </div>

      <section>
        <h3>Execution Summary</h3>
        <ul className="kv-list">
          <li><strong>Intent:</strong> {run.userIntent}</li>
          <li><strong>Prompt Config:</strong> {run.promptConfig}</li>
          <li><strong>Total Cost:</strong> ${run.totalCostUsd.toFixed(4)}</li>
          <li><strong>Total Latency:</strong> {run.totalLatencyMs} ms</li>
        </ul>
      </section>

      <section>
        <h3>Steps</h3>
        <div className="step-list">
          {run.steps.map((step, index) => (
            <div className="step-card" key={step.id}>
              <div className="step-head">
                <span>Step {index + 1}</span>
                <span className={`status-pill status-${step.status}`}>{step.status}</span>
              </div>
              <div className="step-name">{step.name}</div>
              <div className="step-meta">Tool: {step.toolName}</div>
              <div className="step-meta">Latency: {step.latencyMs} ms</div>
              <div className="step-meta">Cost: ${step.costUsd.toFixed(4)}</div>
              <p>{step.rationale}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3>Operator Interventions</h3>
        {run.interventions.length === 0 ? (
          <p>No operator intervention was required for this run.</p>
        ) : (
          <div className="intervention-list">
            {run.interventions.map((item) => (
              <div className="intervention-card" key={item.id}>
                <strong>{item.type}</strong>
                <div>{item.actor}</div>
                <p>{item.note}</p>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
