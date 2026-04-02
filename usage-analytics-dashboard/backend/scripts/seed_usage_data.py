from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import UsageEvent

random.seed(42)
fake = Faker()
Faker.seed(42)
ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "usage_events.csv"


def generate_rows() -> list[dict]:
    workspaces = [
        ("acme-cloud", "Acme Cloud"),
        ("northstar-ai", "Northstar AI"),
        ("orbit-ops", "Orbit Ops"),
    ]
    endpoints = ["/v1/chat/completions", "/v1/embeddings", "/v1/images", "/v1/reports/export"]
    features = ["tokens", "embeddings", "reports", "alerts", "forecasting"]
    regions = ["us-east-1", "us-west-2", "eu-west-1"]
    plans = ["growth", "business", "enterprise"]
    statuses = ["2xx", "4xx", "5xx"]
    start = datetime.utcnow() - timedelta(days=120)
    rows: list[dict] = []
    for hour_offset in range(120 * 24):
        bucket = start + timedelta(hours=hour_offset)
        for workspace_id, customer_name in workspaces:
            for _ in range(random.randint(3, 8)):
                endpoint = random.choices(endpoints, weights=[5, 3, 1, 1])[0]
                feature = random.choices(features, weights=[4, 3, 2, 2, 1])[0]
                request_units = random.randint(40, 400)
                billable_units = int(request_units * random.uniform(0.86, 0.98))
                rows.append(
                    {
                        "workspace_id": workspace_id,
                        "customer_name": customer_name,
                        "event_time": (bucket + timedelta(minutes=random.randint(0, 59))).isoformat(),
                        "endpoint": endpoint,
                        "feature": feature,
                        "region": random.choice(regions),
                        "plan": random.choice(plans),
                        "status_class": random.choices(statuses, weights=[18, 2, 1])[0],
                        "request_units": request_units,
                        "billable_units": billable_units,
                        "cost_usd": round(billable_units * random.uniform(0.0025, 0.006), 4),
                        "latency_ms": round(random.uniform(85, 520), 2),
                        "export_count": random.randint(0, 4) if endpoint.endswith("export") else random.randint(0, 1),
                    }
                )
    return rows


def write_csv(rows: list[dict]) -> None:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RAW_PATH.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def load_database(rows: list[dict]) -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        session.query(UsageEvent).delete()
        session.bulk_save_objects(
            [
                UsageEvent(
                    workspace_id=row["workspace_id"],
                    customer_name=row["customer_name"],
                    event_time=datetime.fromisoformat(row["event_time"]),
                    endpoint=row["endpoint"],
                    feature=row["feature"],
                    region=row["region"],
                    plan=row["plan"],
                    status_class=row["status_class"],
                    request_units=int(row["request_units"]),
                    billable_units=int(row["billable_units"]),
                    cost_usd=float(row["cost_usd"]),
                    latency_ms=float(row["latency_ms"]),
                    export_count=int(row["export_count"]),
                )
                for row in rows
            ]
        )
        session.commit()


if __name__ == "__main__":
    generated = generate_rows()
    write_csv(generated)
    load_database(generated)
    print(f"Seeded {len(generated)} usage events")
