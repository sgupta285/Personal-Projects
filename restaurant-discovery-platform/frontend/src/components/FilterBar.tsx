type Props = {
  city: string
  cuisine: string
  vegetarianOnly: boolean
  setCity: (value: string) => void
  setCuisine: (value: string) => void
  setVegetarianOnly: (value: boolean) => void
}

export function FilterBar({ city, cuisine, vegetarianOnly, setCity, setCuisine, setVegetarianOnly }: Props) {
  return (
    <div className="filter-bar">
      <label>
        City
        <input value={city} onChange={(event) => setCity(event.target.value)} placeholder="Chicago" />
      </label>
      <label>
        Cuisine
        <input value={cuisine} onChange={(event) => setCuisine(event.target.value)} placeholder="Indian" />
      </label>
      <label className="checkbox-label">
        <input checked={vegetarianOnly} onChange={(event) => setVegetarianOnly(event.target.checked)} type="checkbox" />
        Vegetarian friendly
      </label>
    </div>
  )
}
