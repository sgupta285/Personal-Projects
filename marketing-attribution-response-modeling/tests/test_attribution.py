from marketing_attribution.attribution import compute_model_based_attribution, compute_rule_based_attribution
from marketing_attribution.synthetic_data import generate_bundle


def test_rule_based_methods_sum_to_total_conversions():
    bundle = generate_bundle(seed=11)
    baselines = compute_rule_based_attribution(bundle.touchpoints, bundle.journeys)
    total_conversions = float(bundle.journeys["converted"].sum())
    for _, group in baselines.groupby("method"):
        assert abs(group["conversions"].sum() - total_conversions) < 1e-6


def test_model_based_attribution_is_normalized_to_total_conversions():
    bundle = generate_bundle(seed=12)
    model_attr, _ = compute_model_based_attribution(bundle.touchpoints, bundle.journeys)
    total_conversions = float(bundle.journeys["converted"].sum())
    assert abs(model_attr["attributed_conversions"].sum() - total_conversions) < 1e-6
    assert (model_attr["attributed_conversions"] >= 0).all()
