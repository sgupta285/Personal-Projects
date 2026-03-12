from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InterventionDecision:
    risk_tier: str
    recommended_action: str
    priority: str
    owner: str
    rationale: str


def risk_tier(score: float) -> str:
    if score >= 0.80:
        return "critical"
    if score >= 0.65:
        return "high"
    if score >= 0.40:
        return "medium"
    return "low"


def choose_intervention(
    score: float,
    monthly_recurring_revenue: float,
    unresolved_tickets: int,
    payment_failures_90d: int,
    feature_adoption_score: float,
    plan_tier: str,
) -> InterventionDecision:
    tier = risk_tier(score)

    if tier == "critical" and (monthly_recurring_revenue >= 1500 or plan_tier == "enterprise"):
        return InterventionDecision(
            risk_tier=tier,
            recommended_action="Direct CSM outreach with recovery plan",
            priority="P0",
            owner="customer-success",
            rationale="High-value account with acute churn risk. Human outreach is justified.",
        )

    if tier == "critical":
        return InterventionDecision(
            risk_tier=tier,
            recommended_action="Targeted save offer and executive check-in",
            priority="P0",
            owner="lifecycle-ops",
            rationale="Risk is severe, but the save motion can start with a scalable offer.",
        )

    if tier == "high" and payment_failures_90d > 0:
        return InterventionDecision(
            risk_tier=tier,
            recommended_action="Billing recovery sequence plus product education",
            priority="P1",
            owner="revenue-ops",
            rationale="Risk is elevated and billing friction is contributing to churn probability.",
        )

    if tier == "high" and (unresolved_tickets > 2 or feature_adoption_score < 0.45):
        return InterventionDecision(
            risk_tier=tier,
            recommended_action="Customer success outreach plus onboarding refresh",
            priority="P1",
            owner="customer-success",
            rationale="Usage is fragile and the account needs help removing adoption blockers.",
        )

    if tier == "high":
        return InterventionDecision(
            risk_tier=tier,
            recommended_action="Lifecycle email with tailored value proof",
            priority="P1",
            owner="growth-marketing",
            rationale="Risk is elevated but the account can start with a lower-touch retention motion.",
        )

    if tier == "medium":
        return InterventionDecision(
            risk_tier=tier,
            recommended_action="Education campaign and in-app guidance",
            priority="P2",
            owner="product-marketing",
            rationale="There are early warning signs, but the account is not yet urgent.",
        )

    return InterventionDecision(
        risk_tier=tier,
        recommended_action="Monitor only",
        priority="P3",
        owner="system",
        rationale="The account is healthy enough to remain outside the intervention queue.",
    )
