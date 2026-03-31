import { useEffect, useMemo, useState } from 'react'
import { fetchJson } from './lib/api'
import { MetricCard } from './components/MetricCard'
import { SectionCard } from './components/SectionCard'

type SummaryReport = {
  total_runs: number
  total_evaluated_runs: number
  average_score: number
  success_rate: number
  average_latency_ms: number
  average_cost_usd: number
  runs_by_model: Record<string, number>
  runs_by_benchmark: Record<string, number>
}

type FailureSummary = {
  counts: Record<string, number>
}

type Run = {
  run_id: string
  benchmark_id: string
  model_name: string
  prompt_version: string
  total_latency_ms: number
  estimated_cost_usd: number
  status: string
  created_at: string
  trajectory: Array<{
    step_index: number
    tool_name: string
    action: string
    success: boolean
  }>
}

export default function App() {
  const [summary, setSummary] = useState<SummaryReport | null>(null)
  const [failureSummary, setFailureSummary] = useState<FailureSummary | null>(null)
  const [runs, setRuns] = useState<Run[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function load() {
      try {
        const [summaryData, failureData, runData] = await Promise.all([
          fetchJson<SummaryReport>('/reports/summary'),
          fetchJson<FailureSummary>('/reports/failure-modes'),
          fetchJson<Run[]>('/runs'),
        ])
        setSummary(summaryData)
        setFailureSummary(failureData)
        setRuns(runData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const latestRuns = useMemo(() => runs.slice(0, 8), [runs])

  if (loading) {
    return <div className="app-shell"><p>Loading evaluation dashboard...</p></div>
  }

  if (error) {
    return <div className="app-shell"><p>Failed to load dashboard data: {error}</p></div>
  }

  return (
    <div className="app-shell">
      <header className="page-header">
        <div>
          <p className="eyebrow">Agent Quality Control Plane</p>
          <h1>Multimodal Agent Evaluation Stack</h1>
          <p className="intro">
            Inspect benchmark runs, compare agent behavior, and analyze where trajectory quality breaks down.
          </p>
        </div>
      </header>

      {summary && (
        <div className="metric-grid">
          <MetricCard label="Total runs" value={summary.total_runs} />
          <MetricCard label="Evaluated runs" value={summary.total_evaluated_runs} />
          <MetricCard label="Average score" value={summary.average_score} />
          <MetricCard label="Success rate" value={summary.success_rate} />
          <MetricCard label="Avg latency (ms)" value={summary.average_latency_ms} />
          <MetricCard label="Avg cost (USD)" value={summary.average_cost_usd} />
        </div>
      )}

      <div className="content-grid">
        <SectionCard title="Runs by model">
          <ul className="plain-list">
            {summary && Object.entries(summary.runs_by_model).map(([name, count]) => (
              <li key={name}><strong>{name}</strong>: {count}</li>
            ))}
          </ul>
        </SectionCard>

        <SectionCard title="Failure modes">
          <ul className="plain-list">
            {failureSummary && Object.entries(failureSummary.counts).map(([name, count]) => (
              <li key={name}><strong>{name}</strong>: {count}</li>
            ))}
          </ul>
        </SectionCard>
      </div>

      <SectionCard title="Latest runs">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Run ID</th>
                <th>Benchmark</th>
                <th>Model</th>
                <th>Prompt</th>
                <th>Steps</th>
                <th>Latency</th>
                <th>Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {latestRuns.map((run) => (
                <tr key={run.run_id}>
                  <td className="mono">{run.run_id.slice(0, 8)}...</td>
                  <td>{run.benchmark_id}</td>
                  <td>{run.model_name}</td>
                  <td>{run.prompt_version}</td>
                  <td>{run.trajectory.length}</td>
                  <td>{run.total_latency_ms}</td>
                  <td>{run.estimated_cost_usd.toFixed(2)}</td>
                  <td>{run.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>
    </div>
  )
}
