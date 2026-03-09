from collections import Counter, defaultdict
from statistics import mean

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AdSubmission, Advertiser


def build_overview(db: Session) -> dict:
    ads = list(db.execute(select(AdSubmission)).scalars().all())
    advertisers = list(db.execute(select(Advertiser)).scalars().all())

    total_ads = len(ads)
    approved = sum(1 for ad in ads if ad.status == "approved")
    blocked = sum(1 for ad in ads if ad.status == "blocked")
    in_review = sum(1 for ad in ads if ad.status == "in_review")
    avg_risk = round(mean([ad.risk_score for ad in ads]) if ads else 0.0, 3)

    return {
        "total_ads": total_ads,
        "approved_ads": approved,
        "blocked_ads": blocked,
        "in_review_ads": in_review,
        "average_risk_score": avg_risk,
        "unique_advertisers": len(advertisers),
    }


def build_advertiser_risk(db: Session) -> list[dict]:
    advertisers = list(db.execute(select(Advertiser)).scalars().all())
    results = []

    for advertiser in advertisers:
        ads = advertiser.ads
        total_ads = len(ads)
        blocked_ads = sum(1 for ad in ads if ad.status == "blocked")
        avg_risk = round(mean([ad.risk_score for ad in ads]) if ads else advertiser.risk_score, 3)
        results.append(
            {
                "advertiser_name": advertiser.name,
                "advertiser_domain": advertiser.domain,
                "average_risk_score": avg_risk,
                "total_ads": total_ads,
                "blocked_ads": blocked_ads,
            }
        )

    return sorted(results, key=lambda item: item["average_risk_score"], reverse=True)


def build_fraud_patterns(db: Session) -> dict:
    ads = list(db.execute(select(AdSubmission)).scalars().all())

    policy_counter = Counter()
    category_counter = Counter()
    volume_by_day = defaultdict(int)

    for ad in ads:
        for hit in ad.policy_hits or []:
            policy_counter[hit] += 1
        category_counter[f"{ad.category}:{ad.status}"] += 1
        volume_by_day[ad.created_at.strftime("%Y-%m-%d")] += 1

    policy_hits = [{"label": label, "count": count} for label, count in policy_counter.most_common(8)]
    categories = [
        {"label": label, "count": count}
        for label, count in category_counter.most_common(12)
    ]
    recent_volume = [
        {"date": date, "count": count}
        for date, count in sorted(volume_by_day.items())
    ]

    return {
        "policy_hits": policy_hits,
        "categories": categories,
        "recent_volume": recent_volume,
    }
