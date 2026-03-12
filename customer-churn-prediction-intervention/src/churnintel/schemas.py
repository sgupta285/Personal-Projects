from __future__ import annotations

from pydantic import BaseModel, Field


class AccountPayload(BaseModel):
    account_id: str = Field(..., examples=["acct-demo-001"])
    plan_tier: str
    contract_type: str
    region: str
    industry: str
    monthly_recurring_revenue: float
    seat_count: int
    tenure_months: int
    days_since_last_activity: int
    avg_weekly_sessions_30d: float
    avg_weekly_sessions_prev_30d: float
    transactions_30d: int
    transactions_prev_30d: int
    support_tickets_90d: int
    unresolved_tickets: int
    payment_failures_90d: int
    plan_change_count_180d: int
    nps_score: float
    csat_score: float
    admin_logins_30d: int
    api_calls_30d: int
    feature_adoption_score: float
    onboarding_completion_pct: float
    training_sessions_attended: int
    auto_renew: bool
    last_marketing_touch_days: int


class Driver(BaseModel):
    feature: str
    display_name: str
    feature_value: float
    impact: float
    direction: str


class PredictionResponse(BaseModel):
    account_id: str
    churn_probability: float
    risk_tier: str
    recommended_action: str
    priority: str
    owner: str
    rationale: str
    top_drivers: list[Driver]


class ExplanationResponse(BaseModel):
    account_id: str
    churn_probability: float
    risk_tier: str
    recommended_action: str
    priority: str
    rationale: str
    drivers: list[Driver]
