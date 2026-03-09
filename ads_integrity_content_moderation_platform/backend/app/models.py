import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Advertiser(Base):
    __tablename__ = "advertisers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), index=True)
    domain: Mapped[str] = mapped_column(String(255), index=True)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ads: Mapped[list["AdSubmission"]] = relationship(back_populates="advertiser", cascade="all, delete-orphan")


class AdSubmission(Base):
    __tablename__ = "ads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    advertiser_id: Mapped[str] = mapped_column(ForeignKey("advertisers.id"), index=True)

    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    landing_page_url: Mapped[str] = mapped_column(String(500))
    call_to_action: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(120))
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    creative_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    creative_tags: Mapped[list] = mapped_column(JSON, default=list)
    geo_targets: Mapped[list] = mapped_column(JSON, default=list)
    budget_cents: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(40), default="submitted", index=True)
    policy_hits: Mapped[list] = mapped_column(JSON, default=list)
    rule_score: Mapped[float] = mapped_column(Float, default=0.0)
    model_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    review_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    advertiser: Mapped["Advertiser"] = relationship(back_populates="ads")
    reviews: Mapped[list["ManualReview"]] = relationship(back_populates="ad", cascade="all, delete-orphan")


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    ad_id: Mapped[str] = mapped_column(ForeignKey("ads.id"), index=True)
    reviewer_name: Mapped[str] = mapped_column(String(255))
    decision: Mapped[str] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ad: Mapped["AdSubmission"] = relationship(back_populates="reviews")
