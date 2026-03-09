from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import AdResponse, ManualReviewCreate
from app.services.ad_service import apply_manual_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/{ad_id}/decision", response_model=AdResponse, summary="Apply a reviewer decision")
def review_ad(ad_id: str, payload: ManualReviewCreate, db: Session = Depends(get_db)):
    ad = apply_manual_review(db, ad_id, payload)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad
