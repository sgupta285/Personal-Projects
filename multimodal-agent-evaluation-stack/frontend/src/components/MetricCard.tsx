type MetricCardProps = {
  label: string
  value: string | number
}

export function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="card metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  )
}
