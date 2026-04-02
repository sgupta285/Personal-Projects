import { useEffect, useMemo, useState } from 'react'
import { FilterBar } from '../components/FilterBar'
import { Restaurant, RestaurantCard } from '../components/RestaurantCard'

type RestaurantDetail = Restaurant & {
  reviews: Array<{ id: number; title: string; body: string; rating: number }>
  place_enrichment?: { popular_times_summary?: string; price_hint?: string }
}

const API_BASE = (import.meta as ImportMeta & { env: { VITE_API_BASE?: string } }).env.VITE_API_BASE ?? 'http://localhost:8000'

export function App() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([])
  const [selectedRestaurant, setSelectedRestaurant] = useState<RestaurantDetail | null>(null)
  const [city, setCity] = useState('Chicago')
  const [cuisine, setCuisine] = useState('')
  const [vegetarianOnly, setVegetarianOnly] = useState(false)

  const queryString = useMemo(() => {
    const params = new URLSearchParams()
    if (city) params.set('city', city)
    if (cuisine) params.set('cuisine', cuisine)
    if (vegetarianOnly) params.set('vegetarian', 'true')
    return params.toString()
  }, [city, cuisine, vegetarianOnly])

  useEffect(() => {
    fetch(`${API_BASE}/api/v1/restaurants?${queryString}`)
      .then((response) => response.json())
      .then((payload) => setRestaurants(payload.items ?? []))
      .catch(() => setRestaurants([]))
  }, [queryString])

  const openDetails = async (id: number) => {
    const response = await fetch(`${API_BASE}/api/v1/restaurants/${id}`)
    const payload = await response.json()
    setSelectedRestaurant(payload)
  }

  return (
    <div className="app-shell">
      <header>
        <p className="eyebrow">Restaurant Discovery Platform</p>
        <h1>Search restaurants, browse reviews, and book tables without leaving one workflow.</h1>
        <p className="hero-copy">
          This demo frontend is intentionally simple. The backend carries the heavier logic around search, filtering,
          moderation, and booking-provider integration.
        </p>
      </header>

      <FilterBar
        city={city}
        cuisine={cuisine}
        vegetarianOnly={vegetarianOnly}
        setCity={setCity}
        setCuisine={setCuisine}
        setVegetarianOnly={setVegetarianOnly}
      />

      <main className="layout-grid">
        <section className="restaurant-list">
          {restaurants.map((restaurant) => (
            <RestaurantCard key={restaurant.id} restaurant={restaurant} onSelect={openDetails} />
          ))}
        </section>

        <aside className="detail-panel">
          {selectedRestaurant ? (
            <>
              <h2>{selectedRestaurant.name}</h2>
              <p>{selectedRestaurant.description}</p>
              <div className="detail-meta">
                <span>{selectedRestaurant.cuisine}</span>
                <span>{selectedRestaurant.takes_reservations ? 'Online booking enabled' : 'Walk-ins only'}</span>
              </div>
              <div className="detail-card">
                <h3>Third-party enrichment</h3>
                <p>{selectedRestaurant.place_enrichment?.popular_times_summary ?? 'No enrichment available.'}</p>
                <p>{selectedRestaurant.place_enrichment?.price_hint ?? ''}</p>
              </div>
              <div className="detail-card">
                <h3>Reviews</h3>
                {selectedRestaurant.reviews.length === 0 ? (
                  <p className="muted">No approved reviews yet.</p>
                ) : (
                  selectedRestaurant.reviews.map((review) => (
                    <div key={review.id} className="review-item">
                      <strong>{review.title}</strong>
                      <span>⭐ {review.rating}</span>
                      <p>{review.body}</p>
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h2>Select a restaurant</h2>
              <p>Choose a card on the left to see restaurant details, reviews, and booking context.</p>
            </div>
          )}
        </aside>
      </main>
    </div>
  )
}
