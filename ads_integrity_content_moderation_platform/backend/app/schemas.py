from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class AdCreate(BaseModel):
    advertiser_name: str = Field(..., min_length=2, max_length=255)
    advertiser_domain: str = Field(..., min_length=3, max_length=255)
    title: str = Field(..., min_length=4, max_length=255)
    body: str = Field(..., min_length=10)
    landing_page_url: HttpUrl
    call_to_action: str = Field(..., min_length=2, max_length=120)
    category: str = Field(..., min_length=2, max_length=120)
    image_url: Optional[HttpUrl] = None
    creative_text: Optional[str] = None
    creative_tags: List[str] = Field(default_factory=list)
    geo_targets: List[str] = Field(default_factory=list)
    budget_cents: int = 0


class ManualReviewCreate(BaseModel):
    reviewer_name: str
    decision: str
    notes: Optional[str] = None


class AdResponse(BaseModel):
    id: str
    advertiser_id: str
    title: str
    body: str
    landing_page_url: str
    call_to_action: str
    category: str
    image_url: Optional[str]
    creative_text: Optional[str]
    creative_tags: List[str]
    geo_targets: List[str]
    budget_cents: int
    status: str
    policy_hits: List[str]
    rule_score: float
    model_score: float
    risk_score: float
    review_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OverviewResponse(BaseModel):
    total_ads: int
    approved_ads: int
    blocked_ads: int
    in_review_ads: int
    average_risk_score: float
    unique_advertisers: int


class AdvertiserRiskItem(BaseModel):
    advertiser_name: str
    advertiser_domain: str
    average_risk_score: float
    total_ads: int
    blocked_ads: int


class FraudPatternResponse(BaseModel):
    policy_hits: List[dict]
    categories: List[dict]
    recent_volume: List[dict]


class RescanResponse(BaseModel):
    ad_id: str
    status: str
    message: str


class HealthResponse(BaseModel):
    status: str
    app_env: str
