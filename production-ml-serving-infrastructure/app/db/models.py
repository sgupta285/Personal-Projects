from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class OnlineFeature(Base):
    __tablename__ = "online_features"

    customer_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_tenure_days: Mapped[int] = mapped_column(Integer)
    avg_session_seconds: Mapped[float] = mapped_column(Float)
    prior_purchases: Mapped[int] = mapped_column(Integer)
    cart_additions_7d: Mapped[int] = mapped_column(Integer)
    email_click_rate: Mapped[float] = mapped_column(Float)
    discount_sensitivity: Mapped[float] = mapped_column(Float)
    inventory_score: Mapped[float] = mapped_column(Float)
    device_trust_score: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PredictionAuditLog(Base):
    __tablename__ = "prediction_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(128), index=True)
    customer_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    prediction_label: Mapped[str] = mapped_column(String(32))
    prediction_score: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(32))
    used_fallback: Mapped[int] = mapped_column(Integer, default=0)
    feature_payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
