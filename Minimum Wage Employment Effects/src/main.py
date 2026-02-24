"""
Minimum Wage Employment Effects — Main Pipeline.

End-to-end causal inference analysis:
  Data → DiD → Event Study → Synthetic Control → RDD → Robustness

Usage: python -m src.main
"""

import os
import time
import numpy as np
import pandas as pd
import structlog

from src.config import config
from src.data.generator import generate_panel_data
from src.models.did import DiDEstimator, EventStudyEstimator, test_parallel_trends
from src.models.synthetic_control import SyntheticControlEstimator
from src.models.rdd_robustness import RDDEstimator, RobustnessAnalyzer
from src.utils.visualization import (
    plot_parallel_trends, plot_event_study,
    plot_synthetic_control, plot_rdd, plot_robustness_summary,
)

logger = structlog.get_logger()


def main():
    structlog.configure(
        processors=[structlog.processors.add_log_level, structlog.dev.ConsoleRenderer()],
        wrapper_class=structlog.make_filtering_bound_logger(30),
    )

    output_dir = config.output_dir
    os.makedirs(output_dir, exist_ok=True)
    t0 = time.perf_counter()

    print(f"\n{'='*70}")
    print(f"  MINIMUM WAGE EMPLOYMENT EFFECTS ANALYSIS")
    print(f"{'='*70}")
    print(f"  States: {config.data.n_states} | Quarters: {config.data.n_quarters} "
          f"| Treated: {config.data.n_treated_states}")
    print(f"  True effects: Emp={config.data.true_employment_effect:+.3f}, "
          f"Wage={config.data.true_wage_effect:+.3f}, Hours={config.data.true_hours_effect:+.3f}")
    print(f"{'='*70}\n")

    # ── Step 1: Generate Data ──
    print("1. Generating state-quarter panel data...")
    panel_df, true_params = generate_panel_data(
        n_states=config.data.n_states,
        n_quarters=config.data.n_quarters,
        seed=config.data.seed,
    )
    print(f"   ✓ {len(panel_df):,} observations ({config.data.n_states} states × {config.data.n_quarters} quarters)")
    print(f"   Treated states: {', '.join(true_params['treated_states'][:5])}...")

    # Plot parallel trends
    plot_parallel_trends(panel_df, config.data.treatment_quarter, output_dir=output_dir)
    print(f"   ✓ Saved: {output_dir}/parallel_trends.png")

    # ── Step 2: Difference-in-Differences ──
    print("\n2. Two-way Fixed Effects DiD estimation...")
    did = DiDEstimator()
    outcomes = {
        "employment_rate": config.data.true_employment_effect,
        "avg_wage": config.data.true_wage_effect * 12,  # Approx level effect
        "avg_hours": config.data.true_hours_effect * 36,
        "restaurant_emp": config.data.true_employment_effect * 1.8,
        "teen_emp": config.data.true_employment_effect * 2.5,
    }

    print(f"   {'Outcome':<20} {'DiD Est':>10} {'SE':>8} {'p-value':>8} {'True':>10}")
    print(f"   {'-'*60}")

    did_results = {}
    for outcome, true_eff in outcomes.items():
        r = did.estimate(panel_df, outcome=outcome, treatment="did", true_effect=true_eff)
        did_results[outcome] = r
        print(f"   {outcome:<20} {r.estimate:>+10.4f} {r.std_error:>8.4f} "
              f"{r.p_value:>8.4f} {true_eff:>+10.4f}")

    # ── Step 3: Parallel Trends Test ──
    print("\n3. Testing parallel pre-trends...")
    trend_coef, trend_p, holds = test_parallel_trends(panel_df)
    print(f"   Pre-trend coefficient: {trend_coef:.6f} (p={trend_p:.4f})")
    print(f"   Parallel trends: {'✓ HOLD' if holds else '✗ VIOLATED'}")

    # ── Step 4: Event Study ──
    print("\n4. Event study (dynamic treatment effects)...")
    es = EventStudyEstimator()
    es_result = es.estimate(
        panel_df, outcome="employment_rate",
        treatment_quarter=config.data.treatment_quarter,
        pre_periods=config.model.pre_periods,
        post_periods=config.model.post_periods,
    )

    print(f"   Pre-trend F-test: p={es_result.pre_trend_p_value:.4f} "
          f"({'✓' if es_result.parallel_trends_hold else '✗'})")
    print(f"   Post-treatment average effect: {es_result.post_treatment_avg:+.4f}")

    plot_event_study(es_result, output_dir)
    print(f"   ✓ Saved: {output_dir}/event_study.png")

    # ── Step 5: Synthetic Control ──
    print("\n5. Synthetic control method...")
    sc = SyntheticControlEstimator()
    treated_state = true_params["treated_states"][0]
    sc_result = sc.estimate(
        panel_df, treated_state=treated_state,
        outcome="employment_rate",
        treatment_quarter=config.data.treatment_quarter,
    )

    print(f"   Treated state: {treated_state}")
    print(f"   Donor weights: {dict(list(sc_result.weights.items())[:5])}...")
    print(f"   Pre-treatment RMSPE: {sc_result.pre_rmspe:.6f}")
    print(f"   Estimated effect: {sc_result.estimated_effect:+.4f}")

    plot_synthetic_control(sc_result, config.data.treatment_quarter, output_dir)
    print(f"   ✓ Saved: {output_dir}/synthetic_control.png")

    # Placebo test
    print("\n   Running placebo tests (this takes a moment)...")
    try:
        placebo_results, p_val = sc.placebo_test(
            panel_df, treated_state, treatment_quarter=config.data.treatment_quarter,
        )
        print(f"   Placebo p-value: {p_val} (rank {next(r.rank for r in placebo_results if r.is_treated)} "
              f"of {len(placebo_results)})")
    except Exception as e:
        print(f"   Placebo test skipped: {e}")

    # ── Step 6: Regression Discontinuity ──
    print("\n6. Regression discontinuity (minimum wage threshold)...")
    rdd = RDDEstimator()
    post_data = panel_df[panel_df["post"] == 1]
    cutoff = post_data["min_wage"].median()

    rdd_result = rdd.estimate(
        post_data, outcome="employment_rate", running_var="min_wage",
        cutoff=cutoff, bandwidth=config.model.rd_bandwidth,
    )
    print(f"   Cutoff: ${cutoff:.2f}/hr, Bandwidth: ±${config.model.rd_bandwidth:.2f}")
    print(f"   RDD estimate: {rdd_result.estimate:+.4f} (p={rdd_result.p_value:.4f})")
    print(f"   N below: {rdd_result.n_below}, N above: {rdd_result.n_above}")

    plot_rdd(post_data, rdd_result, cutoff, output_dir)
    print(f"   ✓ Saved: {output_dir}/rdd.png")

    # Bandwidth sensitivity
    bw_results = rdd.bandwidth_sensitivity(post_data, cutoff=cutoff)
    print(f"\n   Bandwidth sensitivity:")
    for r in bw_results:
        sig = "***" if r.p_value < 0.01 else "**" if r.p_value < 0.05 else "*" if r.p_value < 0.10 else ""
        print(f"     BW={r.bandwidth:.2f}: τ̂={r.estimate:+.4f} (p={r.p_value:.3f}) {sig}")

    # ── Step 7: Robustness Checks ──
    print("\n7. Robustness checks...")
    robust = RobustnessAnalyzer()
    checks = robust.run_all_checks(panel_df, did_results["employment_rate"].estimate)

    for c in checks:
        status = "✓ PASS" if c.passes else "✗ FAIL"
        print(f"   {status} {c.test_name}: {c.notes}")

    plot_robustness_summary(checks, output_dir)
    print(f"   ✓ Saved: {output_dir}/robustness.png")
    print(f"   Passed: {sum(1 for c in checks if c.passes)}/{len(checks)}")

    # ── Step 8: Export ──
    print(f"\n8. Exporting results...")

    # DiD results
    did_rows = [{
        "outcome": r.outcome, "estimate": r.estimate, "std_error": r.std_error,
        "p_value": r.p_value, "true_effect": r.true_effect,
    } for r in did_results.values()]
    pd.DataFrame(did_rows).to_csv(f"{output_dir}/did_results.csv", index=False)

    # Event study
    es_rows = [{"period": c.relative_period, "estimate": c.estimate,
                "ci_lower": c.ci_lower, "ci_upper": c.ci_upper, "p_value": c.p_value}
               for c in es_result.coefficients]
    pd.DataFrame(es_rows).to_csv(f"{output_dir}/event_study.csv", index=False)

    print(f"   ✓ Exported to {output_dir}/")

    elapsed = time.perf_counter() - t0
    print(f"\n{'='*70}")
    print(f"  ANALYSIS COMPLETE — {elapsed:.1f}s")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
