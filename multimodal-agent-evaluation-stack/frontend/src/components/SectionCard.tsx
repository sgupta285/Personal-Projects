import { ReactNode } from 'react'

type SectionCardProps = {
  title: string
  children: ReactNode
}

export function SectionCard({ title, children }: SectionCardProps) {
  return (
    <section className="card">
      <h2>{title}</h2>
      {children}
    </section>
  )
}
