from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import AdCreate, AdResponse, RescanResponse
from app.services.ad_service import get_ad_by_id, list_ads, rescan_ad, submit_ad

router = APIRouter(prefix="/ads", tags=["ads"])


@router.post("", response_model=AdResponse, summary="Submit an ad for moderation")
def create_ad(payload: AdCreate, db: Session = Depends(get_db)):
    return submit_ad(db, payload)


@router.get("", response_model=list[AdResponse], summary="List recent ads")
def read_ads(limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)):
    return list_ads(db, limit=limit)


@router.get("/{ad_id}", response_model=AdResponse, summary="Get a single ad")
def read_ad(ad_id: str, db: Session = Depends(get_db)):
    ad = get_ad_by_id(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


@router.post("/{ad_id}/rescan", response_model=RescanResponse, summary="Requeue an ad for moderation")
def rescan(ad_id: str, db: Session = Depends(get_db)):
    success = rescan_ad(db, ad_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ad not found")
    return {"ad_id": ad_id, "status": "queued", "message": "Ad placed back on the moderation topic."}
