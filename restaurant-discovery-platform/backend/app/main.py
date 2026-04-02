from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, SessionLocal, engine
from .models import Restaurant, User, UserRole
from .routers import auth, reservations, restaurants, reviews, system
from .services.search import recalculate_rating

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_if_needed()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from .metrics import MetricsMiddleware  # noqa: E402

app.add_middleware(MetricsMiddleware)
app.include_router(system.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(restaurants.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
app.include_router(reservations.router, prefix="/api/v1")


def seed_if_needed() -> None:
    db = SessionLocal()
    try:
        if db.query(Restaurant).count() > 0:
            return
        from .auth import hash_password

        admin = User(
            email="moderator.admin@example.com",
            full_name="Moderation Admin",
            password_hash=hash_password("password123"),
            role=UserRole.admin.value,
        )
        customer = User(
            email="alex@example.com",
            full_name="Alex Chen",
            password_hash=hash_password("password123"),
            role=UserRole.customer.value,
        )
        db.add_all([admin, customer])
        db.flush()

        restaurants_seed = [
            Restaurant(
                name="Lakeview Tandoor",
                slug="lakeview-tandoor",
                city="Chicago",
                cuisine="Indian",
                neighborhood="Lakeview",
                description="Modern Indian plates, strong vegetarian menu, and weeknight tasting menus.",
                price_tier=2,
                vegetarian_friendly=True,
                latitude=41.9415,
                longitude=-87.6534,
                image_url="https://images.unsplash.com/photo-1544025162-d76694265947",
                external_place_id="place_chi_001",
            ),
            Restaurant(
                name="West Loop Ember House",
                slug="west-loop-ember-house",
                city="Chicago",
                cuisine="American",
                neighborhood="West Loop",
                description="Open-fire cooking, seasonal menu, and strong date-night reservation demand.",
                price_tier=4,
                vegetarian_friendly=False,
                latitude=41.8841,
                longitude=-87.6477,
                image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
                external_place_id="place_chi_002",
            ),
            Restaurant(
                name="Green Mint Kitchen",
                slug="green-mint-kitchen",
                city="Chicago",
                cuisine="Mediterranean",
                neighborhood="Lincoln Park",
                description="Casual Mediterranean kitchen with grain bowls, mezze, and fast lunch service.",
                price_tier=2,
                vegetarian_friendly=True,
                latitude=41.9255,
                longitude=-87.6482,
                image_url="https://images.unsplash.com/photo-1555396273-367ea4eb4db5",
                external_place_id="place_chi_003",
            ),
            Restaurant(
                name="Sora Omakase Bar",
                slug="sora-omakase-bar",
                city="Chicago",
                cuisine="Japanese",
                neighborhood="River North",
                description="Small omakase counter with limited seating and prepaid booking windows.",
                price_tier=4,
                vegetarian_friendly=False,
                latitude=41.8923,
                longitude=-87.6338,
                image_url="https://images.unsplash.com/photo-1579027989536-b7b1f875659b",
                external_place_id="place_chi_004",
            ),
            Restaurant(
                name="Harbor Cafe",
                slug="harbor-cafe",
                city="Milwaukee",
                cuisine="Cafe",
                neighborhood="Historic Third Ward",
                description="All-day cafe with pastry program, light brunch menu, and laptop-friendly seating.",
                price_tier=1,
                vegetarian_friendly=True,
                takes_reservations=False,
                latitude=43.0320,
                longitude=-87.9065,
                image_url="https://images.unsplash.com/photo-1552566626-52f8b828add9",
                external_place_id="place_mke_001",
            ),
        ]
        db.add_all(restaurants_seed)
        db.commit()
        for restaurant in restaurants_seed:
            recalculate_rating(db, restaurant)
    finally:
        db.close()
