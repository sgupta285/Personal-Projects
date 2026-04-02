from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Reservation, Restaurant, User
from ..schemas import ReservationCreate, ReservationResponse
from ..services.booking import MockBookingProvider

router = APIRouter(prefix="/reservations", tags=["reservations"])
booking_provider = MockBookingProvider()


@router.post("/restaurants/{restaurant_id}", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    restaurant_id: int,
    payload: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id, Restaurant.is_active.is_(True)).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    if not restaurant.takes_reservations:
        raise HTTPException(status_code=400, detail="This restaurant does not accept online reservations")
    confirmation = booking_provider.create_booking(
        restaurant_slug=restaurant.slug,
        reservation_time=payload.reservation_time,
        party_size=payload.party_size,
    )
    reservation = Reservation(
        restaurant_id=restaurant.id,
        user_id=current_user.id,
        reservation_time=payload.reservation_time,
        party_size=payload.party_size,
        status="confirmed",
        provider_name=confirmation.provider_name,
        provider_confirmation_code=confirmation.confirmation_code,
        notes=payload.notes,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.get("/me", response_model=list[ReservationResponse])
def my_reservations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Reservation)
        .filter(Reservation.user_id == current_user.id)
        .order_by(Reservation.reservation_time.desc())
        .all()
    )
