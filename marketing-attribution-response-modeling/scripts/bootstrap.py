from __future__ import annotations

from marketing_attribution.attribution import compute_model_based_attribution, compute_rule_based_attribution
from marketing_attribution.config import settings
from marketing_attribution.optimizer import optimize_budget
from marketing_attribution.reporting import build_reports
from marketing_attribution.response import fit_response_curves
from marketing_attribution.storage import persist_to_sqlite
from marketing_attribution.synthetic_data import generate_bundle


def main() -> None:
    settings.ensure_dirs()
    bundle = generate_bundle(seed=settings.seed)

    touch_path = settings.raw_dir / "touchpoints.csv"
    spend_path = settings.raw_dir / "daily_spend.csv"
    journey_path = settings.processed_dir / "journeys.csv"
    baseline_path = settings.processed_dir / "channel_attribution_baselines.csv"
    model_path = settings.processed_dir / "model_attribution.csv"
    curve_path = settings.processed_dir / "response_curves.csv"
    budget_path = settings.processed_dir / "budget_reallocation.csv"

    bundle.touchpoints.to_csv(touch_path, index=False)
    bundle.daily_spend.to_csv(spend_path, index=False)
    bundle.journeys.to_csv(journey_path, index=False)

    baselines = compute_rule_based_attribution(bundle.touchpoints, bundle.journeys)
    baselines.to_csv(baseline_path, index=False)

    model_attr, _ = compute_model_based_attribution(bundle.touchpoints, bundle.journeys)
    model_attr.to_csv(model_path, index=False)

    curves = fit_response_curves(bundle.daily_spend)
    curves.to_csv(curve_path, index=False)

    budget = optimize_budget(curves)
    budget.allocations.to_csv(budget_path, index=False)

    persist_to_sqlite(
        settings.database_path,
        {
            "touchpoints": bundle.touchpoints,
            "journeys": bundle.journeys,
            "daily_spend": bundle.daily_spend,
            "rule_based_attribution": baselines,
            "model_attribution": model_attr,
            "response_curves": curves,
            "budget_reallocation": budget.allocations,
        },
    )

    summary = build_reports(
        baselines=baselines,
        model_attr=model_attr,
        curves=curves,
        budget_df=budget.allocations,
        journeys=bundle.journeys,
        touchpoints=bundle.touchpoints,
        reports_dir=settings.reports_dir,
        dashboard_dir=settings.dashboard_dir,
        docs_dir=settings.docs_dir,
    )
    print("Bootstrap complete.")
    print(summary)


if __name__ == "__main__":
    main()
