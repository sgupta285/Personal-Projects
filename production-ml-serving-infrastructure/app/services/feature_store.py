from app.db.models import OnlineFeature
from app.db.session import get_session
from app.schemas.prediction import FeaturePayload


class FeatureStore:
    def get_customer_features(self, customer_id: str) -> FeaturePayload | None:
        with get_session() as session:
            record = session.get(OnlineFeature, customer_id)
            if record is None:
                return None
            return FeaturePayload(
                account_tenure_days=record.account_tenure_days,
                avg_session_seconds=record.avg_session_seconds,
                prior_purchases=record.prior_purchases,
                cart_additions_7d=record.cart_additions_7d,
                email_click_rate=record.email_click_rate,
                discount_sensitivity=record.discount_sensitivity,
                inventory_score=record.inventory_score,
                device_trust_score=record.device_trust_score,
            )
