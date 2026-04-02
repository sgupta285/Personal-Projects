class MockPlacesProvider:
    def enrich(self, external_place_id: str | None) -> dict:
        if not external_place_id:
            return {}
        return {
            "provider": "mock-places",
            "external_place_id": external_place_id,
            "open_now": True,
            "popular_times_summary": "Busiest between 6pm and 8pm",
            "price_hint": "Expect moderate wait times on weekends",
        }
