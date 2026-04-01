from app.schemas.prediction import FeaturePayload


def fallback_score(features: FeaturePayload) -> float:
    score = (
        0.10
        + min(features.prior_purchases / 15.0, 0.25)
        + min(features.cart_additions_7d / 20.0, 0.20)
        + min(features.avg_session_seconds / 1200.0, 0.20)
        + 0.15 * features.email_click_rate
        + 0.10 * features.device_trust_score
    )
    return max(0.0, min(score, 0.999))
