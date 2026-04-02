export type Restaurant = {
  id: number
  name: string
  cuisine: string
  city: string
  neighborhood?: string | null
  description: string
  price_tier: number
  average_rating: number
  review_count: number
  vegetarian_friendly: boolean
  takes_reservations: boolean
}

type Props = {
  restaurant: Restaurant
  onSelect: (id: number) => void
}

export function RestaurantCard({ restaurant, onSelect }: Props) {
  return (
    <button className="restaurant-card" onClick={() => onSelect(restaurant.id)}>
      <div className="restaurant-card__top">
        <h3>{restaurant.name}</h3>
        <span>{'$'.repeat(restaurant.price_tier)}</span>
      </div>
      <p>{restaurant.cuisine} • {restaurant.city}{restaurant.neighborhood ? ` • ${restaurant.neighborhood}` : ''}</p>
      <p className="muted">{restaurant.description}</p>
      <div className="restaurant-card__footer">
        <span>⭐ {restaurant.average_rating.toFixed(1)} ({restaurant.review_count})</span>
        <span>{restaurant.takes_reservations ? 'Reservations available' : 'Walk-ins only'}</span>
      </div>
    </button>
  )
}
