from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Restaurant, Review, ReviewStatus
from ..schemas import RestaurantDetail, RestaurantSummary, SearchResponse
from ..services.places import MockPlacesProvider
from ..services.search import haversine_km, search_restaurants

router = APIRouter(prefix="/restaurants", tags=["restaurants"])
places_provider = MockPlacesProvider()


@router.get("", response_model=SearchResponse)
def list_restaurants(
    q: str | None = Query(default=None),
    city: str | None = Query(default=None),
    cuisine: str | None = Query(default=None),
    vegetarian: bool | None = Query(default=None),
    takes_reservations: bool | None = Query(default=None),
    price_tier: int | None = Query(default=None, ge=1, le=4),
    sort_by: str = Query(default="rating", pattern="^(rating|price|reviews|distance)$"),
    user_lat: float | None = Query(default=None),
    user_lon: float | None = Query(default=None),
    db: Session = Depends(get_db),
):
    effective_sort = "rating" if sort_by == "distance" else sort_by
    restaurants = search_restaurants(
        db,
        query=q,
        city=city,
        cuisine=cuisine,
        vegetarian=vegetarian,
        takes_reservations=takes_reservations,
        price_tier=price_tier,
        sort_by=effective_sort,
        user_lat=user_lat if sort_by == "distance" else None,
        user_lon=user_lon if sort_by == "distance" else None,
    )
    items: list[RestaurantSummary] = []
    for restaurant in restaurants:
        item = RestaurantSummary.model_validate(restaurant)
        if user_lat is not None and user_lon is not None and restaurant.latitude is not None and restaurant.longitude is not None:
            item.distance_km = round(haversine_km(user_lat, user_lon, restaurant.latitude, restaurant.longitude), 2)
        items.append(item)
    return SearchResponse(total=len(items), items=items)


@router.get("/{restaurant_id}", response_model=RestaurantDetail)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = (
        db.query(Restaurant)
        .options(joinedload(Restaurant.reviews).joinedload(Review.user))
        .filter(Restaurant.id == restaurant_id, Restaurant.is_active.is_(True))
        .first()
    )
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    approved_reviews = [review for review in restaurant.reviews if review.status == ReviewStatus.approved.value]
    response = RestaurantDetail.model_validate(restaurant)
    response.reviews = approved_reviews
    response.place_enrichment = places_provider.enrich(restaurant.external_place_id)
    return response
