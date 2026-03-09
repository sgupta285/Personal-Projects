from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.analytics_service import build_advertiser_risk, build_fraud_patterns, build_overview

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", summary="Aggregate moderation metrics")
def overview(db: Session = Depends(get_db)):
    return build_overview(db)


@router.get("/advertisers", summary="Advertiser risk leaderboard")
def advertisers(db: Session = Depends(get_db)):
    return build_advertiser_risk(db)


@router.get("/fraud-patterns", summary="Policy-hit and category patterns")
def fraud_patterns(db: Session = Depends(get_db)):
    return build_fraud_patterns(db)
