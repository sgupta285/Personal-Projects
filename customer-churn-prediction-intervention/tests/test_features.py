import pandas as pd

from churnintel.features import build_feature_table


def test_build_feature_table_creates_expected_columns():
    raw = pd.DataFrame(
        [
            {
                "account_id": "acct-1",
                "plan_tier": "growth",
                "contract_type": "monthly",
                "region": "North America",
                "industry": "SaaS",
                "monthly_recurring_revenue": 900.0,
                "seat_count": 10,
                "tenure_months": 6,
                "days_since_last_activity": 15,
                "avg_weekly_sessions_30d": 5.0,
                "avg_weekly_sessions_prev_30d": 10.0,
                "transactions_30d": 20,
                "transactions_prev_30d": 30,
                "support_tickets_90d": 4,
                "unresolved_tickets": 2,
                "payment_failures_90d": 1,
                "plan_change_count_180d": 1,
                "nps_score": 5,
                "csat_score": 3.8,
                "admin_logins_30d": 12,
                "api_calls_30d": 450,
                "feature_adoption_score": 0.5,
                "onboarding_completion_pct": 0.7,
                "training_sessions_attended": 1,
                "auto_renew": False,
                "last_marketing_touch_days": 9,
                "churned_60d": 1,
            }
        ]
    )
    feature_df = build_feature_table(raw)

    assert "engagement_delta" in feature_df.columns
    assert "ticket_burden" in feature_df.columns
    assert feature_df.loc[0, "engagement_delta"] == -5.0
    assert round(feature_df.loc[0, "ticket_burden"], 4) == 4.0
