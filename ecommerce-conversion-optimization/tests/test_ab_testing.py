import pandas as pd
from ecomopt.ab_testing import compare_variants, minimum_detectable_effect


def test_compare_variants_detects_positive_lift():
    rows = []
    for i in range(1000):
        rows.append({"session_id": f"c-{i}", "variant": "control", "purchased": 1 if i < 100 else 0, "order_value": 50 if i < 100 else 0})
        rows.append({"session_id": f"t-{i}", "variant": "treatment", "purchased": 1 if i < 125 else 0, "order_value": 50 if i < 125 else 0})
    cohorts = pd.DataFrame(rows)
    summary = compare_variants(cohorts)
    assert summary["absolute_lift"] > 0
    assert summary["treatment_conversion_rate"] > summary["control_conversion_rate"]


def test_mde_is_positive():
    assert minimum_detectable_effect(0.08, 5000) > 0
