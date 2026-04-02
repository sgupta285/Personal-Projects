from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(String(64), index=True)
    customer_name: Mapped[str] = mapped_column(String(128))
    event_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    endpoint: Mapped[str] = mapped_column(String(128), index=True)
    feature: Mapped[str] = mapped_column(String(128), index=True)
    region: Mapped[str] = mapped_column(String(32), index=True)
    plan: Mapped[str] = mapped_column(String(32), index=True)
    status_class: Mapped[str] = mapped_column(String(16), index=True)
    request_units: Mapped[int] = mapped_column(Integer)
    billable_units: Mapped[int] = mapped_column(Integer)
    cost_usd: Mapped[float] = mapped_column(Float)
    latency_ms: Mapped[float] = mapped_column(Float)
    export_count: Mapped[int] = mapped_column(Integer, default=0)


class UsageRollup(Base):
    __tablename__ = "usage_rollups"
    __table_args__ = (
        UniqueConstraint("workspace_id", "bucket_start", "interval", "metric_family", "group_value", name="uq_rollup_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[str] = mapped_column(String(64), index=True)
    bucket_start: Mapped[datetime] = mapped_column(DateTime, index=True)
    interval: Mapped[str] = mapped_column(String(16), index=True)
    metric_family: Mapped[str] = mapped_column(String(32), index=True)
    group_value: Mapped[str] = mapped_column(String(128), default="all")
    request_units: Mapped[int] = mapped_column(Integer)
    billable_units: Mapped[int] = mapped_column(Integer)
    total_cost_usd: Mapped[float] = mapped_column(Float)
    avg_latency_ms: Mapped[float] = mapped_column(Float)
    export_count: Mapped[int] = mapped_column(Integer)
