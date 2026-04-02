import type { ReactNode } from 'react'

interface Props {
  label: string
  value: string
  helper?: string
  icon?: ReactNode
}

export function KpiCard({ label, value, helper, icon }: Props) {
  return (
    <div className="card kpi-card">
      <div className="kpi-header">
        <span>{label}</span>
        <span>{icon}</span>
      </div>
      <strong>{value}</strong>
      {helper ? <p>{helper}</p> : null}
    </div>
  )
}
