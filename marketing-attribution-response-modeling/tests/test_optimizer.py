from marketing_attribution.optimizer import optimize_budget
from marketing_attribution.response import fit_response_curves
from marketing_attribution.synthetic_data import generate_daily_spend_panel


def test_budget_optimizer_preserves_total_budget_and_bounds():
    panel = generate_daily_spend_panel(seed=5)
    curves = fit_response_curves(panel)
    result = optimize_budget(curves, step=250.0)
    df = result.allocations
    assert round(df["current_spend"].sum(), 6) == round(df["recommended_spend"].sum(), 6)
    assert ((df["recommended_spend"] >= df["current_spend"] * 0.60 - 1e-9)).all()
    assert ((df["recommended_spend"] <= df["current_spend"] * 1.40 + 1e-9)).all()
