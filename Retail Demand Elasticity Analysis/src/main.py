"""
Retail Demand Elasticity Analysis Pipeline.

End-to-end: synthetic data → OLS / Panel FE / IV estimation →
cross-price elasticity matrix → optimal pricing → visualization.

Usage: python -m src.main
"""

import os
import time
import numpy as np
import pandas as pd
import structlog

from src.config import config
from src.data.generator import generate_elasticity_data
from src.models.estimators import (
    OLSLogLogEstimator, PanelFEEstimator, IVEstimator, CrossPriceEstimator,
)
from src.analysis.pricing import (
    OptimalPricingAnalyzer, print_pricing_table,
)
from src.utils.visualization import (
    plot_demand_curves, plot_cross_elasticity_heatmap,
    plot_revenue_optimization, plot_elasticity_comparison,
    plot_price_quantity_scatter,
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
    print(f"  RETAIL DEMAND ELASTICITY ANALYSIS")
    print(f"{'='*70}")
    print(f"  Products: {config.data.n_products} | Stores: {config.data.n_stores} "
          f"| Weeks: {config.data.n_weeks} (~{config.data.n_weeks/52:.1f} years)")
    print(f"{'='*70}\n")

    # ── Step 1: Generate Data ──
    print("1. Generating panel data with known elasticities...")
    panel_df, true_cross_matrix, products = generate_elasticity_data(
        n_products=config.data.n_products,
        n_stores=config.data.n_stores,
        n_weeks=config.data.n_weeks,
        seed=config.data.seed,
    )
    product_ids = [p.product_id for p in products]
    true_elast = {p.product_id: p.own_elasticity for p in products}
    print(f"   ✓ {len(panel_df):,} observations generated")
    print(f"   ✓ True own-price elasticities: {[f'{e:.2f}' for e in true_elast.values()]}")

    # Scatter plot for first product
    plot_price_quantity_scatter(panel_df, product_ids[0], output_dir)

    # ── Step 2: OLS Log-Log Estimation ──
    print("\n2. OLS Log-Log estimation...")
    ols = OLSLogLogEstimator()
    ols_results = []
    for pid in product_ids:
        r = ols.estimate(panel_df, pid, controls=["is_promotion", "week_of_year"],
                         true_elasticity=true_elast[pid])
        ols_results.append(r)
        print(f"   {pid}: ε̂={r.own_elasticity:>6.3f} ± {r.std_error:.3f} "
              f"(true={r.true_elasticity:.3f}, err={r.estimation_error:.3f})")

    # ── Step 3: Panel Fixed Effects ──
    print("\n3. Panel Fixed Effects estimation (clustered SE)...")
    panel_fe = PanelFEEstimator()
    fe_results = []
    for pid in product_ids:
        r = panel_fe.estimate(panel_df, pid, true_elasticity=true_elast[pid])
        fe_results.append(r)
        print(f"   {pid}: ε̂={r.own_elasticity:>6.3f} ± {r.std_error:.3f} "
              f"(err={r.estimation_error:.3f})")

    # ── Step 4: IV/2SLS Estimation ──
    print("\n4. IV/2SLS estimation (instrument: cost_shock)...")
    iv = IVEstimator()
    iv_results = []
    for pid in product_ids:
        r, diag = iv.estimate(panel_df, pid, true_elasticity=true_elast[pid])
        iv_results.append(r)
        print(f"   {pid}: ε̂={r.own_elasticity:>6.3f} ± {r.std_error:.3f} "
              f"(1st stage F={diag.first_stage_f:.1f}, {diag.instrument_relevance})")

    # ── Step 5: Comparison Plot ──
    print("\n5. Comparing estimation methods...")
    results_by_method = {
        "OLS Log-Log": ols_results,
        "Panel FE (Clustered SE)": fe_results,
        "IV/2SLS": iv_results,
    }
    plot_elasticity_comparison(results_by_method, output_dir)
    print(f"   ✓ Saved: {output_dir}/elasticity_comparison.png")

    # Compute average estimation error by method
    for method, results in results_by_method.items():
        avg_err = np.mean([r.estimation_error for r in results if r.estimation_error is not None])
        print(f"   {method:<28} Avg |error|: {avg_err:.3f}")

    # ── Step 6: Cross-Price Elasticity ──
    print("\n6. Cross-price elasticity estimation...")
    cross_est = CrossPriceEstimator()
    est_cross_matrix, cross_results = cross_est.estimate(panel_df, product_ids, true_cross_matrix)

    plot_cross_elasticity_heatmap(est_cross_matrix, product_ids, output_dir)
    print(f"   ✓ Saved: {output_dir}/cross_elasticity_heatmap.png")

    substitutes = [r for r in cross_results if r.relationship == "substitute"]
    complements = [r for r in cross_results if r.relationship == "complement"]
    print(f"   Substitutes found: {len(substitutes)}, Complements: {len(complements)}")
    if substitutes:
        top = sorted(substitutes, key=lambda r: r.cross_elasticity, reverse=True)[:5]
        print(f"   Top substitutes:")
        for r in top:
            print(f"     {r.product_i} ↔ {r.product_j}: ε_cross={r.cross_elasticity:.3f} (p={r.p_value:.3f})")

    # ── Step 7: Optimal Pricing ──
    print("\n7. Optimal pricing analysis...")
    # Use Panel FE estimates (most robust)
    est_elasticities = {r.product_id: r.own_elasticity for r in fe_results}
    analyzer = OptimalPricingAnalyzer(products)
    pricing = analyzer.compute_optimal_prices(est_elasticities)
    print_pricing_table(pricing)

    # Demand curves & revenue optimization plots
    plot_demand_curves(products, est_elasticities, output_dir)
    plot_revenue_optimization(products, est_elasticities, output_dir)
    print(f"   ✓ Saved: demand_curves.png, revenue_optimization.png")

    # ── Step 8: Export ──
    print("\n8. Exporting results...")
    # Elasticity comparison
    rows = []
    for method, results in results_by_method.items():
        for r in results:
            rows.append({
                "product_id": r.product_id, "method": r.method,
                "elasticity": r.own_elasticity, "std_error": r.std_error,
                "p_value": r.p_value, "true_elasticity": r.true_elasticity,
                "estimation_error": r.estimation_error,
            })
    pd.DataFrame(rows).to_csv(f"{output_dir}/elasticity_estimates.csv", index=False)

    # Cross-price matrix
    pd.DataFrame(est_cross_matrix, index=product_ids, columns=product_ids).to_csv(
        f"{output_dir}/cross_elasticity_matrix.csv"
    )

    # Pricing recommendations
    pd.DataFrame([{
        "product_id": r.product_id, "current_price": r.current_price,
        "optimal_price": r.optimal_price, "price_change_pct": r.price_change_pct,
        "profit_uplift_pct": r.profit_uplift_pct, "elasticity": r.elasticity_used,
    } for r in pricing]).to_csv(f"{output_dir}/pricing_recommendations.csv", index=False)

    print(f"   ✓ Exported to {output_dir}/")

    elapsed = time.perf_counter() - t0
    print(f"\n{'='*70}")
    print(f"  ANALYSIS COMPLETE — {elapsed:.1f}s")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
