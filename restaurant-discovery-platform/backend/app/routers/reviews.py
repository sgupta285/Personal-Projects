from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import Restaurant, Review, ReviewStatus, User
from ..schemas import ReviewCreate, ReviewModerationRequest, ReviewResponse
from ..services.search import recalculate_rating

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/restaurants/{restaurant_id}", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    restaurant_id: int,
    payload: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id, Restaurant.is_active.is_(True)).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    existing = db.query(Review).filter(Review.restaurant_id == restaurant_id, Review.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already reviewed this restaurant")
    review = Review(
        restaurant_id=restaurant_id,
        user_id=current_user.id,
        rating=payload.rating,
        title=payload.title,
        body=payload.body,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/restaurants/{restaurant_id}", response_model=list[ReviewResponse])
def list_reviews(restaurant_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(Review)
        .filter(Review.restaurant_id == restaurant_id, Review.status == ReviewStatus.approved.value)
        .all()
    )
    return reviews


@router.get("/moderation/pending", response_model=list[ReviewResponse])
def list_pending_reviews(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(Review).filter(Review.status == ReviewStatus.pending.value).all()


@router.post("/moderation/{review_id}", response_model=ReviewResponse)
def moderate_review(
    review_id: int,
    payload: ReviewModerationRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    review.status = ReviewStatus.approved.value if payload.action == "approve" else ReviewStatus.rejected.value
    db.add(review)
    db.commit()
    db.refresh(review)
    restaurant = db.query(Restaurant).filter(Restaurant.id == review.restaurant_id).first()
    if restaurant:
        recalculate_rating(db, restaurant)
    return review
