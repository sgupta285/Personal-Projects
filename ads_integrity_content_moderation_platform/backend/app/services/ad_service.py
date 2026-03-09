from collections import defaultdict

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import AdSubmission, Advertiser, ManualReview
from app.schemas import AdCreate, ManualReviewCreate
from app.services.cache import get_latest_risk
from app.services.kafka_service import publisher


def _get_or_create_advertiser(db: Session, name: str, domain: str) -> Advertiser:
    advertiser = db.execute(
        select(Advertiser).where(Advertiser.name == name, Advertiser.domain == domain)
    ).scalar_one_or_none()

    if advertiser:
        return advertiser

    advertiser = Advertiser(name=name, domain=domain)
    db.add(advertiser)
    db.flush()
    return advertiser


def submit_ad(db: Session, payload: AdCreate) -> AdSubmission:
    advertiser = _get_or_create_advertiser(db, payload.advertiser_name, payload.advertiser_domain)

    ad = AdSubmission(
        advertiser_id=advertiser.id,
        title=payload.title,
        body=payload.body,
        landing_page_url=str(payload.landing_page_url),
        call_to_action=payload.call_to_action,
        category=payload.category,
        image_url=str(payload.image_url) if payload.image_url else None,
        creative_text=payload.creative_text,
        creative_tags=payload.creative_tags,
        geo_targets=payload.geo_targets,
        budget_cents=payload.budget_cents,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)

    publisher.publish(
        settings.kafka_ads_submitted_topic,
        {
            "ad_id": ad.id,
            "advertiser_id": advertiser.id,
            "advertiser_name": advertiser.name,
            "advertiser_domain": advertiser.domain,
            "title": ad.title,
            "body": ad.body,
            "landing_page_url": ad.landing_page_url,
            "call_to_action": ad.call_to_action,
            "category": ad.category,
            "image_url": ad.image_url,
            "creative_text": ad.creative_text,
            "creative_tags": ad.creative_tags,
            "geo_targets": ad.geo_targets,
            "budget_cents": ad.budget_cents,
        },
    )
    return ad


def list_ads(db: Session, limit: int = 50) -> list[AdSubmission]:
    return list(
        db.execute(select(AdSubmission).order_by(desc(AdSubmission.created_at)).limit(limit)).scalars().all()
    )


def get_ad_by_id(db: Session, ad_id: str) -> AdSubmission | None:
    ad = db.get(AdSubmission, ad_id)
    if not ad:
        return None

    cached_risk = get_latest_risk(ad_id)
    if cached_risk:
        ad.risk_score = cached_risk.get("risk_score", ad.risk_score)
    return ad


def rescan_ad(db: Session, ad_id: str) -> bool:
    ad = db.get(AdSubmission, ad_id)
    if not ad:
        return False

    advertiser = db.get(Advertiser, ad.advertiser_id)
    ad.status = "submitted"
    db.commit()

    publisher.publish(
        settings.kafka_ads_submitted_topic,
        {
            "ad_id": ad.id,
            "advertiser_id": ad.advertiser_id,
            "advertiser_name": advertiser.name if advertiser else "unknown",
            "advertiser_domain": advertiser.domain if advertiser else "unknown",
            "title": ad.title,
            "body": ad.body,
            "landing_page_url": ad.landing_page_url,
            "call_to_action": ad.call_to_action,
            "category": ad.category,
            "image_url": ad.image_url,
            "creative_text": ad.creative_text,
            "creative_tags": ad.creative_tags,
            "geo_targets": ad.geo_targets,
            "budget_cents": ad.budget_cents,
        },
    )
    return True


def apply_manual_review(db: Session, ad_id: str, payload: ManualReviewCreate) -> AdSubmission | None:
    ad = db.get(AdSubmission, ad_id)
    if not ad:
        return None

    review = ManualReview(
        ad_id=ad_id,
        reviewer_name=payload.reviewer_name,
        decision=payload.decision,
        notes=payload.notes,
    )
    db.add(review)

    normalized = payload.decision.strip().lower()
    if normalized in {"approved", "approve"}:
        ad.status = "approved"
        ad.review_reason = payload.notes or "Approved by human reviewer."
    elif normalized in {"blocked", "block", "reject"}:
        ad.status = "blocked"
        ad.review_reason = payload.notes or "Blocked by human reviewer."
        ad.risk_score = max(ad.risk_score, settings.risk_block_threshold)
    else:
        ad.status = "in_review"
        ad.review_reason = payload.notes or "Sent back to queue by reviewer."

    db.commit()
    db.refresh(ad)
    return ad
