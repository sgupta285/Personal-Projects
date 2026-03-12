from churnintel.interventions import choose_intervention


def test_high_value_critical_account_gets_csm_motion():
    decision = choose_intervention(
        score=0.91,
        monthly_recurring_revenue=2600,
        unresolved_tickets=4,
        payment_failures_90d=1,
        feature_adoption_score=0.31,
        plan_tier="scale",
    )
    assert decision.priority == "P0"
    assert "CSM" in decision.recommended_action


def test_low_risk_account_is_monitored_only():
    decision = choose_intervention(
        score=0.18,
        monthly_recurring_revenue=300,
        unresolved_tickets=0,
        payment_failures_90d=0,
        feature_adoption_score=0.8,
        plan_tier="starter",
    )
    assert decision.recommended_action == "Monitor only"
