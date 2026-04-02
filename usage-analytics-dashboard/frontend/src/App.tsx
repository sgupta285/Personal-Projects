import { useEffect, useMemo, useState } from 'react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from 'recharts'
import { fetchBreakdown, fetchMetricCatalog, fetchSummary } from './lib/api'
import { KpiCard } from './components/KpiCard'

interface SummaryPoint {
  bucket_start: string
  request_units: number
  billable_units: number
  total_cost_usd: number
  avg_latency_ms: number
  export_count: number
}

interface SummaryResponse {
  workspace_id: string
  interval: string
  totals: {
    request_units: number
    billable_units: number
    total_cost_usd: number
    avg_latency_ms: number
    export_count: number
  }
  time_series: SummaryPoint[]
}

interface BreakdownRow {
  group_value: string
  request_units: number
  billable_units: number
  total_cost_usd: number
  avg_latency_ms: number
  export_count: number
}

export function App() {
  const [workspaceId, setWorkspaceId] = useState('acme-cloud')
  const [interval, setInterval] = useState('day')
  const [dimension, setDimension] = useState('feature')
  const [workspaces, setWorkspaces] = useState<string[]>([])
  const [summary, setSummary] = useState<SummaryResponse | null>(null)
  const [breakdown, setBreakdown] = useState<BreakdownRow[]>([])

  useEffect(() => {
    fetchMetricCatalog().then((catalog) => setWorkspaces(catalog.workspaces))
  }, [])

  useEffect(() => {
    fetchSummary({ workspace_id: workspaceId, interval }).then(setSummary)
    fetchBreakdown({ workspace_id: workspaceId, interval, dimension }).then((data) => setBreakdown(data.rows))
  }, [workspaceId, interval, dimension])

  const chartRows = useMemo(
    () =>
      (summary?.time_series ?? []).map((point) => ({
        ...point,
        bucket: new Date(point.bucket_start).toLocaleDateString(),
      })),
    [summary],
  )

  return (
    <div className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">Customer-facing analytics dashboard</p>
          <h1>Usage Analytics Dashboard</h1>
          <p className="subtitle">
            Interactive usage reporting with date-range rollups, drill-down breakdowns, and export flows backed by precomputed aggregates.
          </p>
        </div>
        <div className="toolbar card">
          <label>
            Workspace
            <select value={workspaceId} onChange={(event) => setWorkspaceId(event.target.value)}>
              {workspaces.map((workspace) => (
                <option key={workspace} value={workspace}>
                  {workspace}
                </option>
              ))}
            </select>
          </label>
          <label>
            Interval
            <select value={interval} onChange={(event) => setInterval(event.target.value)}>
              <option value="hour">hour</option>
              <option value="day">day</option>
              <option value="month">month</option>
            </select>
          </label>
          <label>
            Breakdown
            <select value={dimension} onChange={(event) => setDimension(event.target.value)}>
              <option value="feature">feature</option>
              <option value="endpoint">endpoint</option>
              <option value="region">region</option>
              <option value="plan">plan</option>
              <option value="status_class">status</option>
            </select>
          </label>
        </div>
      </header>

      <section className="kpi-grid">
        <KpiCard label="Request units" value={Intl.NumberFormat().format(summary?.totals.request_units ?? 0)} helper="Precomputed from rollup tables" />
        <KpiCard label="Billable units" value={Intl.NumberFormat().format(summary?.totals.billable_units ?? 0)} helper="Billing-ready usage estimate" />
        <KpiCard label="Revenue estimate" value={`$${(summary?.totals.total_cost_usd ?? 0).toFixed(2)}`} helper="Based on modeled unit pricing" />
        <KpiCard label="Avg latency" value={`${(summary?.totals.avg_latency_ms ?? 0).toFixed(1)} ms`} helper="Useful for service-quality reviews" />
      </section>

      <section className="chart-grid">
        <div className="card chart-card">
          <div className="card-header">
            <h2>Usage over time</h2>
            <a href={`http://localhost:8000/usage/export.csv?workspace_id=${workspaceId}&interval=${interval}`}>Export CSV</a>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartRows}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bucket" minTickGap={24} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="request_units" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="billable_units" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card chart-card">
          <div className="card-header">
            <h2>{dimension} breakdown</h2>
            <a href={`http://localhost:8000/usage/export.pdf?workspace_id=${workspaceId}&interval=${interval}&dimension=${dimension}`}>Export PDF</a>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={breakdown}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="group_value" hide />
              <YAxis />
              <Tooltip />
              <Bar dataKey="request_units" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="breakdown-table">
            {breakdown.map((row) => (
              <div className="breakdown-row" key={row.group_value}>
                <span>{row.group_value}</span>
                <span>{Intl.NumberFormat().format(row.request_units)} units</span>
                <span>${row.total_cost_usd.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
