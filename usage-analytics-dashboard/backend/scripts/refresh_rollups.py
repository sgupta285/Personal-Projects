from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import UsageEvent, UsageRollup

DIMENSIONS = ["feature", "endpoint", "region", "plan", "status_class"]
INTERVALS = ["hour", "day", "month"]


def bucketize(ts: datetime, interval: str) -> datetime:
    if interval == "hour":
        return ts.replace(minute=0, second=0, microsecond=0)
    if interval == "day":
        return ts.replace(hour=0, minute=0, second=0, microsecond=0)
    return ts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def refresh_rollups() -> int:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        events = session.scalars(select(UsageEvent)).all()
        session.query(UsageRollup).delete()
        aggregates: dict[tuple, dict] = defaultdict(lambda: {
            "request_units": 0,
            "billable_units": 0,
            "total_cost_usd": 0.0,
            "latency_sum": 0.0,
            "count": 0,
            "export_count": 0,
        })

        for event in events:
            for interval in INTERVALS:
                bucket = bucketize(event.event_time, interval)
                base_key = (event.workspace_id, bucket, interval, "overview", "all")
                entry = aggregates[base_key]
                entry["request_units"] += event.request_units
                entry["billable_units"] += event.billable_units
                entry["total_cost_usd"] += event.cost_usd
                entry["latency_sum"] += event.latency_ms
                entry["count"] += 1
                entry["export_count"] += event.export_count
                for dimension in DIMENSIONS:
                    group_value = getattr(event, dimension)
                    dim_key = (event.workspace_id, bucket, interval, dimension, group_value)
                    dim_entry = aggregates[dim_key]
                    dim_entry["request_units"] += event.request_units
                    dim_entry["billable_units"] += event.billable_units
                    dim_entry["total_cost_usd"] += event.cost_usd
                    dim_entry["latency_sum"] += event.latency_ms
                    dim_entry["count"] += 1
                    dim_entry["export_count"] += event.export_count

        session.bulk_save_objects([
            UsageRollup(
                workspace_id=workspace_id,
                bucket_start=bucket_start,
                interval=interval,
                metric_family=metric_family,
                group_value=group_value,
                request_units=values["request_units"],
                billable_units=values["billable_units"],
                total_cost_usd=round(values["total_cost_usd"], 4),
                avg_latency_ms=round(values["latency_sum"] / values["count"], 2) if values["count"] else 0.0,
                export_count=values["export_count"],
            )
            for (workspace_id, bucket_start, interval, metric_family, group_value), values in aggregates.items()
        ])
        session.commit()
        return len(aggregates)


if __name__ == "__main__":
    count = refresh_rollups()
    print(f"Refreshed {count} rollup rows")
