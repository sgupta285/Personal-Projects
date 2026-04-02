from app.db import SessionLocal, init_db
from app.models import ApiClient, Order
from app.services.tokens import hash_api_key


def main() -> None:
    init_db()
    session = SessionLocal()
    try:
        if not session.query(ApiClient).count():
            client = ApiClient(
                name="partner-sandbox",
                client_id="partner-sandbox",
                api_key_hash=hash_api_key("partner-demo-key"),
                auth_mode="api_key",
                rate_limit_per_minute=120,
                daily_quota=5000,
                scopes="orders:read orders:write",
                is_active=True,
            )
            session.add(client)
        if not session.query(Order).count():
            for idx in range(1, 11):
                session.add(
                    Order(
                        external_id=f"order-{idx}",
                        customer_name=f"Customer {idx}",
                        item_sku=f"SKU-{1000 + idx}",
                        quantity=idx,
                        status="pending" if idx % 2 else "fulfilled",
                        total_cents=idx * 1999,
                        notes="Seeded example order",
                    )
                )
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
