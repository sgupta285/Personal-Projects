"""
Product Metrics & Analytics Framework — Main Pipeline.

End-to-end: data generation → engagement metrics → retention cohorts →
funnel analysis → A/B testing → segmentation → revenue/LTV.

Usage: python -m src.main
"""

import os
import time
import numpy as np
import pandas as pd
import structlog

from src.config import config
from src.data.generator import generate_product_data, ONBOARDING_FUNNEL
from src.metrics.engagement import EngagementAnalyzer
from src.metrics.retention import RetentionAnalyzer
from src.metrics.funnel_revenue import FunnelAnalyzer, RevenueAnalyzer
from src.experimentation.ab_testing import (
    FrequentistTester, BayesianTester, SequentialTester, PowerCalculator,
)
from src.segmentation.segments import RFMSegmenter, BehavioralClusterer
from src.utils.visualization import (
    plot_dau_wau_mau, plot_retention_heatmap, plot_retention_curves,
    plot_funnel, plot_ab_test_results, plot_rfm_segments,
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

    print(f"\n{'='*65}")
    print(f"  PRODUCT METRICS & ANALYTICS FRAMEWORK")
    print(f"{'='*65}")
    print(f"  Users: {config.data.n_users:,}  |  Period: {config.data.n_days} days")
    print(f"{'='*65}\n")

    # ── Step 1: Generate Data ──
    print("1. Generating product data...")
    users_df, sessions_df, events_df = generate_product_data(
        n_users=config.data.n_users, n_days=config.data.n_days,
        start_date=config.data.start_date, seed=config.data.seed,
    )
    print(f"   ✓ {len(users_df):,} users, {len(sessions_df):,} sessions, {len(events_df):,} events")

    # ── Step 2: Engagement Metrics ──
    print("\n2. Computing engagement metrics...")
    engagement = EngagementAnalyzer()
    dau_wau_mau = engagement.compute_dau_wau_mau(sessions_df)
    session_metrics = engagement.compute_session_metrics(sessions_df)

    latest = dau_wau_mau.iloc[-1]
    print(f"   DAU: {latest['dau']:,} | WAU: {latest['wau']:,} | MAU: {latest['mau']:,}")
    print(f"   Stickiness (DAU/MAU): {latest['stickiness']:.1%}")
    print(f"   Avg session duration: {session_metrics['avg_duration'].mean():.0f}s")

    plot_dau_wau_mau(dau_wau_mau, output_dir)
    print(f"   ✓ Saved: {output_dir}/dau_wau_mau.png")

    # Feature adoption
    mau = int(latest["mau"])
    adoption = engagement.compute_feature_adoption(sessions_df, events_df, config.data.feature_set, mau)
    print(f"\n   Feature Adoption (of {mau:,} MAU):")
    for fa in adoption[:5]:
        print(f"     {fa.feature:<20} {fa.adoption_rate:.1%} adoption, "
              f"{fa.avg_uses_per_user:.1f} uses/user")

    # ── Step 3: Retention Analysis ──
    print("\n3. Computing retention cohorts...")
    retention = RetentionAnalyzer()
    cohort_table = retention.build_cohort_table(users_df, sessions_df, cohort_freq="W", periods=12)
    print(f"   ✓ {len(cohort_table)} weekly cohorts")

    plot_retention_heatmap(cohort_table, output_dir)
    print(f"   ✓ Saved: {output_dir}/retention_heatmap.png")

    # Retention curves
    ret_curve = retention.compute_retention_curve(users_df, sessions_df)
    print(f"   Day-N retention:")
    for _, row in ret_curve.iterrows():
        print(f"     Day {int(row['day']):>3}: {row['retention_rate']:.1%} "
              f"({int(row['n_retained']):,} / {int(row['n_eligible']):,})")

    churn = retention.estimate_churn_rate(ret_curve)
    print(f"   Monthly churn: {churn.get('monthly_churn', 0):.1%} | "
          f"Half-life: {churn.get('half_life_days', 0):.0f} days")

    # Retention by platform
    ret_by_platform = retention.retention_by_segment(users_df, sessions_df, "platform")
    plot_retention_curves(ret_by_platform, output_dir)
    print(f"   ✓ Saved: {output_dir}/retention_curves.png")

    # ── Step 4: Funnel Analysis ──
    print("\n4. Analyzing onboarding funnel...")
    funnel = FunnelAnalyzer()
    funnel_result = funnel.analyze_funnel(users_df, ONBOARDING_FUNNEL)
    for s in funnel_result.stages:
        print(f"   {s.stage:<20} {s.users:>8,} ({s.rate_from_top:.1%} from top, "
              f"-{s.drop_off_pct:.0f}% drop)")
    print(f"   Biggest drop: {funnel_result.biggest_drop_stage} "
          f"(-{funnel_result.biggest_drop_pct:.0f}%)")

    plot_funnel(funnel_result, output_dir)
    print(f"   ✓ Saved: {output_dir}/funnel.png")

    # ── Step 5: A/B Testing ──
    print("\n5. A/B test analysis (control vs treatment)...")
    control = users_df[users_df["variant"] == "control"]
    treatment = users_df[users_df["variant"] == "treatment"]

    freq_tester = FrequentistTester()
    bayes_tester = BayesianTester()

    # Test multiple metrics
    ab_results = []

    # Conversion
    r = freq_tester.test_proportion(
        control["completed_onboarding"].values.astype(float),
        treatment["completed_onboarding"].values.astype(float),
        "onboarding_completion"
    )
    ab_results.append(r)

    # Retention proxy (>1 session)
    r = freq_tester.test_proportion(
        (control["total_sessions"] > 1).values.astype(float),
        (treatment["total_sessions"] > 1).values.astype(float),
        "retention_d1+"
    )
    ab_results.append(r)

    # Revenue
    r = freq_tester.test_continuous(
        control["total_revenue"].values,
        treatment["total_revenue"].values,
        "revenue_per_user"
    )
    ab_results.append(r)

    # Sessions
    r = freq_tester.test_continuous(
        control["total_sessions"].values.astype(float),
        treatment["total_sessions"].values.astype(float),
        "sessions_per_user"
    )
    ab_results.append(r)

    print(f"   {'Metric':<25} {'Ctrl':>8} {'Treat':>8} {'Lift%':>7} {'p-val':>8} {'Sig':>5}")
    print(f"   {'-'*62}")
    for r in ab_results:
        print(f"   {r.metric_name:<25} {r.control_mean:>8.4f} {r.treatment_mean:>8.4f} "
              f"{r.relative_lift_pct:>+6.1f}% {r.p_value:>8.4f} {'✓' if r.is_significant else '✗':>5}")

    # Bayesian
    bayes_r = bayes_tester.test_proportion(
        control["completed_onboarding"].values.astype(float),
        treatment["completed_onboarding"].values.astype(float),
        "onboarding_completion"
    )
    print(f"\n   Bayesian: P(treatment > control) = {bayes_r.prob_treatment_better:.1%}")
    print(f"   Expected loss (control): {bayes_r.expected_loss_control:.4f}")

    # Multiple testing correction
    p_vals = [r.p_value for r in ab_results]
    corrected = freq_tester.bonferroni_correction(p_vals)
    print(f"\n   Bonferroni correction: {sum(1 for _, s in corrected if s)}/{len(corrected)} significant")

    # Power analysis
    power_calc = PowerCalculator()
    n_required = power_calc.sample_size_proportion(0.15, 0.02)
    duration = power_calc.estimate_duration(n_required, config.data.daily_signups_mean)
    print(f"   Power analysis: n={n_required:,}/group for 2pp MDE → ~{duration} days")

    plot_ab_test_results(ab_results, output_dir)
    print(f"   ✓ Saved: {output_dir}/ab_test_results.png")

    # ── Step 6: Revenue & LTV ──
    print("\n6. Revenue & LTV analysis...")
    rev_analyzer = RevenueAnalyzer()
    rev = rev_analyzer.compute_revenue_metrics(users_df, events_df)
    print(f"   Total revenue:     ${rev.total_revenue:>12,.2f}")
    print(f"   ARPU:              ${rev.arpu:>12.2f}")
    print(f"   ARPPU:             ${rev.arppu:>12.2f}")
    print(f"   Paying user %:     {rev.paying_user_pct:>12.1%}")
    print(f"   Avg order value:   ${rev.avg_order_value:>12.2f}")
    print(f"   LTV (30d):         ${rev.ltv_30d:>12.2f}")
    print(f"   LTV (90d):         ${rev.ltv_90d:>12.2f}")
    print(f"   LTV (projected):   ${rev.ltv_projected:>12.2f}")

    # ── Step 7: Segmentation ──
    print("\n7. User segmentation...")
    rfm = RFMSegmenter()
    rfm_df = rfm.compute_rfm(users_df, sessions_df)
    segments = rfm.segment_summary(rfm_df)

    print(f"   {'Segment':<18} {'Users':>7} {'%':>6} {'Recency':>8} {'Freq':>6} {'Revenue':>9}")
    print(f"   {'-'*58}")
    for s in segments:
        print(f"   {s.segment_name:<18} {s.n_users:>7,} {s.pct_of_total:>5.1f}% "
              f"{s.avg_recency:>7.0f}d {s.avg_frequency:>5.0f} ${s.avg_monetary:>8.2f}")

    plot_rfm_segments(segments, output_dir)
    print(f"   ✓ Saved: {output_dir}/rfm_segments.png")

    # Behavioral clustering
    clusterer = BehavioralClusterer()
    clustered = clusterer.cluster_users(users_df, sessions_df, n_clusters=5)
    cluster_summary = clustered.groupby("cluster_label").agg(
        n_users=("user_id", "count"),
        avg_sessions=("total_sessions", "mean"),
        avg_revenue=("total_revenue", "mean"),
    ).round(2)
    print(f"\n   Behavioral Clusters:")
    print(cluster_summary.to_string())

    # ── Step 8: Export ──
    print(f"\n8. Exporting results...")
    dau_wau_mau.to_csv(f"{output_dir}/engagement_metrics.csv", index=False)
    cohort_table.to_csv(f"{output_dir}/retention_cohorts.csv")
    rfm_df.to_csv(f"{output_dir}/rfm_scores.csv", index=False)

    elapsed = time.perf_counter() - t0
    print(f"\n{'='*65}")
    print(f"  PIPELINE COMPLETE — {elapsed:.1f}s")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
