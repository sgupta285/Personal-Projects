from math import asin, cos, radians, sin, sqrt
from typing import Iterable

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session

from ..models import Restaurant, Review, ReviewStatus


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return earth_radius * c


def recalculate_rating(db: Session, restaurant: Restaurant) -> None:
    approved: Iterable[Review] = (
        db.query(Review)
        .filter(Review.restaurant_id == restaurant.id, Review.status == ReviewStatus.approved.value)
        .all()
    )
    approved = list(approved)
    restaurant.review_count = len(approved)
    restaurant.average_rating = round(sum(item.rating for item in approved) / len(approved), 2) if approved else 0.0
    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)


def search_restaurants(
    db: Session,
    *,
    query: str | None = None,
    city: str | None = None,
    cuisine: str | None = None,
    vegetarian: bool | None = None,
    takes_reservations: bool | None = None,
    price_tier: int | None = None,
    sort_by: str = "rating",
    user_lat: float | None = None,
    user_lon: float | None = None,
) -> list[Restaurant]:
    statement = db.query(Restaurant).filter(Restaurant.is_active.is_(True))
    if query:
        like_query = f"%{query.lower()}%"
        statement = statement.filter(
            or_(
                Restaurant.name.ilike(like_query),
                Restaurant.description.ilike(like_query),
                Restaurant.neighborhood.ilike(like_query),
                Restaurant.cuisine.ilike(like_query),
            )
        )
    if city:
        statement = statement.filter(Restaurant.city.ilike(city))
    if cuisine:
        statement = statement.filter(Restaurant.cuisine.ilike(cuisine))
    if vegetarian is not None:
        statement = statement.filter(Restaurant.vegetarian_friendly.is_(vegetarian))
    if takes_reservations is not None:
        statement = statement.filter(Restaurant.takes_reservations.is_(takes_reservations))
    if price_tier is not None:
        statement = statement.filter(Restaurant.price_tier == price_tier)

    if sort_by == "price":
        statement = statement.order_by(asc(Restaurant.price_tier), desc(Restaurant.average_rating))
    elif sort_by == "reviews":
        statement = statement.order_by(desc(Restaurant.review_count), desc(Restaurant.average_rating))
    else:
        statement = statement.order_by(desc(Restaurant.average_rating), desc(Restaurant.review_count))

    restaurants = statement.all()
    if user_lat is not None and user_lon is not None:
        restaurants = sorted(
            restaurants,
            key=lambda restaurant: haversine_km(user_lat, user_lon, restaurant.latitude or user_lat, restaurant.longitude or user_lon),
        )
    return restaurants
