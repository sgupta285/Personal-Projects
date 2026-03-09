from sqlalchemy import select

from app.db import SessionLocal
from app.models import AdSubmission, Advertiser
from app.services.cache import set_latest_risk


def apply_moderation_result(ad_id: str, result: dict) -> bool:
    with SessionLocal() as db:
        ad = db.get(AdSubmission, ad_id)
        if not ad:
            return False

        ad.status = result["decision"]
        ad.rule_score = result["rule_score"]
        ad.model_score = result["model_score"]
        ad.risk_score = result["risk_score"]
        ad.policy_hits = result["policy_hits"]
        ad.review_reason = result["review_reason"]

        advertiser = db.get(Advertiser, ad.advertiser_id)
        if advertiser:
            historical = [existing.risk_score for existing in advertiser.ads if existing.id != ad.id]
            historical.append(ad.risk_score)
            advertiser.risk_score = round(sum(historical) / len(historical), 4)

        db.commit()

    set_latest_risk(
        ad_id,
        {
            "decision": result["decision"],
            "risk_score": result["risk_score"],
            "policy_hits": result["policy_hits"],
        },
    )
    return True
