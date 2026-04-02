import { useEffect, useState } from 'react'
import { getEvents } from './api/client'

type TicketTier = { id: number; name: string; price_cents: number; capacity: number }
type Event = {
  id: number
  title: string
  description: string
  location: string
  starts_at: string
  ends_at: string
  ticket_tiers: TicketTier[]
}

export default function App() {
  const [events, setEvents] = useState<Event[]>([])

  useEffect(() => {
    getEvents().then(setEvents).catch(() => setEvents([]))
  }, [])

  return (
    <div className="shell">
      <header>
        <h1>Event Management System</h1>
        <p>Organizer-ready event operations for registration, ticketing, waitlists, and check-in.</p>
      </header>
      <main className="grid">
        {events.map((event) => (
          <section key={event.id} className="card">
            <h2>{event.title}</h2>
            <p>{event.description}</p>
            <p><strong>Location:</strong> {event.location}</p>
            <p><strong>Starts:</strong> {new Date(event.starts_at).toLocaleString()}</p>
            <div>
              <strong>Ticket tiers</strong>
              <ul>
                {event.ticket_tiers.map((tier) => (
                  <li key={tier.id}>{tier.name} · ${(tier.price_cents / 100).toFixed(2)} · cap {tier.capacity}</li>
                ))}
              </ul>
            </div>
          </section>
        ))}
        {events.length === 0 && <section className="card"><p>No published events found. Seed the demo backend and refresh.</p></section>}
      </main>
    </div>
  )
}
