from expower.analysis_plan import recommend_analysis_plan


def test_analysis_plan_contains_estimand():
    plan = recommend_analysis_plan("between_subjects", "continuous")
    assert "Average treatment effect" in plan.estimand
    assert len(plan.notes) >= 2
