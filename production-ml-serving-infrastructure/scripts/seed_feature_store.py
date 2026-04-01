import random

from app.db.models import OnlineFeature
from app.db.session import get_session, init_db


def seed() -> None:
    init_db()
    rng = random.Random(42)
    rows = []
    for idx in range(1, 101):
        rows.append(
            OnlineFeature(
                customer_id=f"cust-{1000 + idx}",
                account_tenure_days=rng.randint(20, 700),
                avg_session_seconds=round(rng.uniform(60, 1200), 2),
                prior_purchases=rng.randint(0, 18),
                cart_additions_7d=rng.randint(0, 20),
                email_click_rate=round(rng.uniform(0.01, 0.75), 4),
                discount_sensitivity=round(rng.uniform(0.05, 0.95), 4),
                inventory_score=round(rng.uniform(0.40, 0.99), 4),
                device_trust_score=round(rng.uniform(0.45, 0.99), 4),
            )
        )

    with get_session() as session:
        session.query(OnlineFeature).delete()
        session.add_all(rows)
        session.commit()


if __name__ == "__main__":
    seed()
    print("seeded online feature store")
