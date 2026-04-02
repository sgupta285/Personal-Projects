from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    title: str = Field(min_length=3, max_length=160)
    body: str = Field(min_length=10, max_length=2000)


class ReviewResponse(BaseModel):
    id: int
    rating: int
    title: str
    body: str
    status: str
    created_at: datetime
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)


class ReviewModerationRequest(BaseModel):
    action: Literal["approve", "reject"]


class RestaurantSummary(BaseModel):
    id: int
    name: str
    slug: str
    city: str
    cuisine: str
    neighborhood: str | None
    description: str
    price_tier: int
    average_rating: float
    review_count: int
    takes_reservations: bool
    vegetarian_friendly: bool
    image_url: str | None
    distance_km: float | None = None

    model_config = ConfigDict(from_attributes=True)


class RestaurantDetail(RestaurantSummary):
    latitude: float | None = None
    longitude: float | None = None
    external_place_id: str | None = None
    place_enrichment: dict | None = None
    reviews: list[ReviewResponse] = []


class ReservationCreate(BaseModel):
    reservation_time: datetime
    party_size: int = Field(ge=1, le=20)
    notes: str | None = Field(default=None, max_length=300)


class ReservationResponse(BaseModel):
    id: int
    restaurant_id: int
    user_id: int
    reservation_time: datetime
    party_size: int
    status: str
    provider_name: str
    provider_confirmation_code: str
    notes: str | None

    model_config = ConfigDict(from_attributes=True)


class SearchResponse(BaseModel):
    total: int
    items: list[RestaurantSummary]
