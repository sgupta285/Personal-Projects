"""
Randomized Controlled Trial Evaluation — Main Pipeline.

End-to-end:
  Data → Diagnostics → ITT/ATE → LATE/2SLS → Heterogeneity → GATES → Robustness

Usage: python -m src.main
"""

import os
import time
import numpy as np
import pandas as pd
import structlog

from src.config import config
from src.data.generator import generate_rct_data
from src.estimation.ate_estimators import (
    difference_in_means, lin_estimator, cuped_estimator,
    bootstrap_ate, permutation_test,
)
from src.estimation.iv_late import (
    wald_estimator, tsls_estimator, hausman_test, analyze_compliance,
)
from src.estimation.heterogeneity import (
    estimate_cate_subgroup, interaction_regression,
    CausalForestEstimator, estimate_gates, blp_test,
)
from src.diagnostics.checks import (
    covariate_balance, attrition_analysis, holm_correction,
    benjamini_hochberg, power_analysis,
)
from src.utils.visualization import (
    plot_balance, plot_ate_comparison, plot_cate_subgroups,
    plot_gates, plot_cate_distribution, plot_bootstrap,
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
    print(f"  RANDOMIZED CONTROLLED TRIAL EVALUATION")
    print(f"{'='*70}")
    print(f"  Subjects: {config.data.n_subjects:,} | Treatment: {config.data.treatment_fraction:.0%}")
    print(f"  True ATE: {config.data.ate} | True LATE: {config.data.late}")
    print(f"  Non-compliance: AT={config.data.noncompliance_always_taker:.0%}, "
          f"NT={config.data.noncompliance_never_taker:.0%}")
    print(f"{'='*70}\n")

    # ── Step 1: Generate Data ──
    print("1. Generating RCT data...")
    df, true_params = generate_rct_data(
        n_subjects=config.data.n_subjects,
        treatment_fraction=config.data.treatment_fraction,
        seed=config.data.seed,
    )
    print(f"   ✓ {len(df):,} subjects | N_treat={true_params['n_treatment']:,} "
          f"| N_ctrl={true_params['n_control']:,}")
    print(f"   Compliance: {true_params['compliance_rates']}")
    print(f"   First stage: {true_params['first_stage']:.4f}")
    print(f"   Attrition: {true_params['attrition_rate']:.1%}")

    # ── Step 2: Diagnostics ──
    print("\n2. RCT diagnostics...")

    # Covariate balance
    balance = covariate_balance(df, covariates=["age", "bmi", "pre_outcome", "biomarker_a", "biomarker_b"])
    print(f"   Covariate balance:")
    print(f"   {'Covariate':<18} {'SMD':>8} {'p-val':>8} {'Status':>8}")
    print(f"   {'-'*44}")
    for r in balance.rows:
        status = "✓" if r.balanced else "✗"
        print(f"   {r.covariate:<18} {r.smd:>+8.4f} {r.p_value:>8.4f} {status:>8}")
    print(f"   Joint F-test: F={balance.joint_f_stat:.2f}, p={balance.joint_f_p:.4f} "
          f"({'✓ balanced' if balance.joint_f_p > 0.05 else '✗ imbalanced'})")

    plot_balance(balance, output_dir)
    print(f"   ✓ Saved: {output_dir}/balance_love_plot.png")

    # Attrition
    attrition = attrition_analysis(df)
    print(f"\n   Attrition: overall={attrition.overall_rate:.1%}, "
          f"treat={attrition.treatment_rate:.1%}, ctrl={attrition.control_rate:.1%}")
    print(f"   Differential: {attrition.differential:+.4f} (p={attrition.differential_p:.4f}) "
          f"{'✗ DIFFERENTIAL' if attrition.is_differential else '✓ non-differential'}")
    if attrition.lee_bounds:
        print(f"   Lee bounds: [{attrition.lee_bounds[0]:.4f}, {attrition.lee_bounds[1]:.4f}]")

    # Power
    pwr = power_analysis(baseline_std=config.data.outcome_noise_std, mde=config.data.ate)
    print(f"\n   Power analysis: need {pwr.total_sample_size:,} total for MDE={pwr.mde}")

    # ── Step 3: ATE / ITT Estimation ──
    print("\n3. ATE / ITT estimation...")
    # Work on non-attrited sample for main analysis
    analysis_df = df[~df["attrited"]].copy()
    print(f"   Analysis sample: {len(analysis_df):,} (after excluding {df['attrited'].sum()} attrited)")

    ate_results = []

    # Difference-in-means (ITT)
    r = difference_in_means(analysis_df, true_value=true_params["itt"])
    ate_results.append(r)

    # Lin regression adjustment
    r = lin_estimator(analysis_df, true_value=true_params["itt"])
    ate_results.append(r)

    # CUPED
    r = cuped_estimator(analysis_df, true_value=true_params["itt"])
    ate_results.append(r)

    print(f"\n   {'Method':<30} {'Est':>8} {'SE':>7} {'p-val':>8} {'VarRed':>7} {'|Err|':>7}")
    print(f"   {'-'*72}")
    for r in ate_results:
        err_str = f"{r.estimation_error:.3f}" if r.estimation_error is not None else "N/A"
        print(f"   {r.method:<30} {r.estimate:>+8.4f} {r.std_error:>7.4f} "
              f"{r.p_value:>8.4f} {r.variance_reduction_pct:>6.1f}% {err_str:>7}")

    # Bootstrap
    boot_ate, boot_lo, boot_hi, boot_dist = bootstrap_ate(analysis_df, n_bootstrap=config.estimation.n_bootstrap)
    print(f"\n   Bootstrap (B={config.estimation.n_bootstrap}): "
          f"ATE={boot_ate:.4f}, 95% CI=[{boot_lo:.4f}, {boot_hi:.4f}]")
    plot_bootstrap(boot_dist, boot_ate, (boot_lo, boot_hi), output_dir)

    # Permutation test
    perm_stat, perm_p, _ = permutation_test(analysis_df, n_permutations=config.estimation.n_permutations)
    print(f"   Fisher permutation (N={config.estimation.n_permutations}): "
          f"stat={perm_stat:.4f}, p={perm_p:.4f}")

    # ── Step 4: LATE / 2SLS ──
    print("\n4. LATE / IV estimation (handling non-compliance)...")

    # Compliance analysis
    compliance = analyze_compliance(analysis_df)
    print(f"   Compliance structure:")
    print(f"     Compliers:     {compliance.complier_share:.1%} ({compliance.n_compliers_est:,} est.)")
    print(f"     Always-takers: {compliance.always_taker_share:.1%} ({compliance.n_always_takers_est:,} est.)")
    print(f"     Never-takers:  {compliance.never_taker_share:.1%} ({compliance.n_never_takers_est:,} est.)")

    # Wald estimator
    wald = wald_estimator(analysis_df, true_late=true_params["late"])
    ate_results.append(wald)
    print(f"\n   Wald LATE:  {wald.estimate:+.4f} ± {wald.std_error:.4f} (p={wald.p_value:.4f})")
    print(f"     First stage F={wald.first_stage.f_statistic:.1f} "
          f"({'✓ STRONG' if wald.first_stage.is_strong else '✗ WEAK'})")

    # Manual 2SLS with covariates
    tsls = tsls_estimator(analysis_df, true_late=true_params["late"])
    ate_results.append(tsls)
    print(f"   2SLS LATE:  {tsls.estimate:+.4f} ± {tsls.std_error:.4f} (p={tsls.p_value:.4f})")
    print(f"     First stage F={tsls.first_stage.f_statistic:.1f}, "
          f"Partial R²={tsls.first_stage.partial_r_squared:.4f}")

    # Hausman test
    hausman = hausman_test(analysis_df)
    print(f"\n   Hausman endogeneity test: t={hausman.test_statistic:.3f}, p={hausman.p_value:.4f}")
    print(f"     OLS={hausman.ols_estimate:.4f} vs IV={hausman.iv_estimate:.4f}")
    print(f"     → {hausman.interpretation}")

    plot_ate_comparison(ate_results, output_dir)
    print(f"   ✓ Saved: {output_dir}/ate_forest_plot.png")

    # ── Step 5: Heterogeneous Treatment Effects ──
    print("\n5. Heterogeneous treatment effects...")

    # Subgroup CATE
    for subgroup, true_cate in [("age_group", true_params["cate_by_age"]),
                                 ("severity", true_params["cate_by_severity"]),
                                 ("gender", true_params["cate_by_gender"])]:
        cate = estimate_cate_subgroup(analysis_df, subgroup_col=subgroup, true_cate=true_cate)
        print(f"\n   CATE by {subgroup}:")
        print(f"   {'Value':<12} {'Est':>8} {'SE':>7} {'True':>7} {'|Err|':>7} {'p':>8}")
        print(f"   {'-'*55}")
        for c in cate:
            t = c.true_cate if c.true_cate is not None else 0
            err = c.estimation_error if c.estimation_error is not None else 0
            print(f"   {c.subgroup_value:<12} {c.estimate:>+8.4f} {c.std_error:>7.4f} "
                  f"{t:>+7.4f} {err:>7.4f} {c.p_value:>8.4f}")
        plot_cate_subgroups(cate, subgroup, output_dir)

    # Interaction regression
    interactions = interaction_regression(analysis_df)
    print(f"\n   Interaction regression (R²={interactions.r_squared:.4f}):")
    print(f"   Base ATE: {interactions.base_ate:.4f} ± {interactions.base_se:.4f}")
    for mod, coef in interactions.interactions.items():
        p = interactions.interaction_pvals[mod]
        sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
        print(f"     T×{mod}: {coef:+.4f} (p={p:.4f}) {sig}")
    if interactions.significant_moderators:
        print(f"   Significant moderators: {', '.join(interactions.significant_moderators)}")

    # Causal forest
    print(f"\n   Causal forest (T-learner, cross-fit)...")
    cf = CausalForestEstimator(n_trees=config.estimation.n_trees,
                               min_samples_leaf=config.estimation.min_leaf_size)
    cf_result = cf.estimate(analysis_df)
    print(f"     ATE (forest): {cf_result.ate_estimate:.4f}")
    print(f"     Heterogeneity (std): {cf_result.cate_std:.4f}")
    print(f"     CATE IQR: [{cf_result.cate_iqr[0]:.4f}, {cf_result.cate_iqr[1]:.4f}]")
    print(f"     Feature importance: {dict(list(cf_result.feature_importances.items())[:5])}")

    plot_cate_distribution(cf_result.cate_predictions,
                           true_te=analysis_df["individual_te"].values, output_dir=output_dir)
    print(f"   ✓ Saved: {output_dir}/cate_distribution.png")

    # GATES
    gates = estimate_gates(analysis_df, cf_result.cate_predictions)
    print(f"\n   GATES (quintile analysis):")
    for i, (est, se, n) in enumerate(zip(gates.group_estimates, gates.group_ses, gates.group_sizes)):
        print(f"     Q{i+1}: GATE={est:+.4f} ± {se:.4f} (n={n})")
    print(f"   Heterogeneity test: p={gates.heterogeneity_p:.4f}")
    print(f"   Most affected:  {gates.most_affected_profile}")
    print(f"   Least affected: {gates.least_affected_profile}")

    plot_gates(gates, output_dir)
    print(f"   ✓ Saved: {output_dir}/gates.png")

    # BLP test
    blp = blp_test(analysis_df, cf_result.cate_predictions)
    print(f"\n   BLP heterogeneity test:")
    print(f"     β₁ = {blp.beta_1:.4f} ± {blp.beta_1_se:.4f} (p={blp.beta_1_p:.4f})")
    print(f"     Heterogeneity {'✓ DETECTED' if blp.heterogeneity_detected else '✗ not detected'}")

    # ── Step 6: Multiple Testing Correction ──
    print("\n6. Multiple testing correction...")
    all_p = [r.p_value for r in ate_results]
    holm = holm_correction(all_p)
    bh = benjamini_hochberg(all_p)
    print(f"   Holm:  {sum(1 for _, s in holm if s)}/{len(holm)} significant")
    print(f"   BH:    {sum(1 for _, s in bh if s)}/{len(bh)} significant")

    # ── Step 7: Export ──
    print(f"\n7. Exporting results...")
    rows = [{
        "method": r.method, "estimate": r.estimate, "std_error": r.std_error,
        "ci_lower": r.ci_lower, "ci_upper": r.ci_upper, "p_value": r.p_value,
        "true_value": r.true_value,
        "variance_reduction": r.variance_reduction_pct,
    } for r in ate_results]
    pd.DataFrame(rows).to_csv(f"{output_dir}/estimation_results.csv", index=False)
    print(f"   ✓ Exported to {output_dir}/")

    elapsed = time.perf_counter() - t0
    print(f"\n{'='*70}")
    print(f"  PIPELINE COMPLETE — {elapsed:.1f}s")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
