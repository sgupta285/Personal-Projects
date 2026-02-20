"""
Optimal Pricing Analysis.

Given estimated elasticities, compute profit-maximizing prices using:
  π(P) = (P - MC) * Q(P) where Q(P) = Q₀ * (P/P₀)^ε

Optimal price (Lerner condition): P* = MC * ε / (ε + 1) for ε < -1
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass
import structlog

from src.data.generator import ProductSpec

logger = structlog.get_logger()


@dataclass
class PricingResult:
    product_id: str
    current_price: float
    optimal_price: float
    price_change_pct: float
    current_quantity: float
    optimal_quantity: float
    current_profit: float
    optimal_profit: float
    profit_uplift_pct: float
    elasticity_used: float
    marginal_cost: float
    lerner_index: float           # (P - MC) / P — market power measure


class OptimalPricingAnalyzer:
    """Compute profit-maximizing prices from estimated elasticities."""

    def __init__(self, products: List[ProductSpec]):
        self.products = {p.product_id: p for p in products}

    def compute_optimal_prices(
        self, elasticities: Dict[str, float], price_grid_n: int = 50
    ) -> List[PricingResult]:
        """
        Compute optimal price for each product.

        Uses the Lerner condition for constant-elasticity demand:
            P* = MC * |ε| / (|ε| - 1) when |ε| > 1

        Also performs grid search validation.
        """
        results = []

        for prod_id, elasticity in elasticities.items():
            prod = self.products.get(prod_id)
            if not prod:
                continue

            mc = prod.marginal_cost
            p0 = prod.base_price
            q0 = prod.base_quantity

            # --- Lerner optimal price ---
            abs_e = abs(elasticity)
            if abs_e > 1.0:
                p_star_lerner = mc * abs_e / (abs_e - 1.0)
            else:
                # Inelastic demand — no interior optimum, price as high as possible
                p_star_lerner = p0 * 1.5  # Cap at 150% of base

            # --- Grid search validation ---
            prices = np.linspace(mc * 1.05, p0 * 2.5, price_grid_n)
            profits = np.zeros(price_grid_n)

            for i, p in enumerate(prices):
                q = q0 * (p / p0) ** elasticity
                profits[i] = (p - mc) * q

            best_idx = np.argmax(profits)
            p_star_grid = prices[best_idx]
            max_profit_grid = profits[best_idx]

            # Use grid search result (more robust)
            p_star = p_star_grid

            # Current state
            q_current = q0
            profit_current = (p0 - mc) * q_current

            # Optimal state
            q_optimal = q0 * (p_star / p0) ** elasticity
            profit_optimal = (p_star - mc) * q_optimal

            lerner = (p_star - mc) / p_star if p_star > 0 else 0
            uplift = (profit_optimal / profit_current - 1) * 100 if profit_current > 0 else 0

            results.append(PricingResult(
                product_id=prod_id,
                current_price=round(p0, 2),
                optimal_price=round(p_star, 2),
                price_change_pct=round((p_star / p0 - 1) * 100, 1),
                current_quantity=round(q_current, 0),
                optimal_quantity=round(q_optimal, 0),
                current_profit=round(profit_current, 0),
                optimal_profit=round(profit_optimal, 0),
                profit_uplift_pct=round(uplift, 1),
                elasticity_used=round(elasticity, 3),
                marginal_cost=round(mc, 2),
                lerner_index=round(lerner, 3),
            ))

        results.sort(key=lambda r: r.profit_uplift_pct, reverse=True)
        return results

    @staticmethod
    def compute_demand_curve(
        base_price: float, base_quantity: float, elasticity: float,
        price_range: Tuple[float, float] = (0.5, 2.0), n_points: int = 100,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate demand curve Q(P) for plotting."""
        prices = np.linspace(base_price * price_range[0], base_price * price_range[1], n_points)
        quantities = base_quantity * (prices / base_price) ** elasticity
        return prices, quantities

    @staticmethod
    def compute_revenue_curve(
        base_price: float, base_quantity: float, elasticity: float,
        price_range: Tuple[float, float] = (0.5, 2.0), n_points: int = 100,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate revenue curve R(P) = P * Q(P)."""
        prices = np.linspace(base_price * price_range[0], base_price * price_range[1], n_points)
        quantities = base_quantity * (prices / base_price) ** elasticity
        revenues = prices * quantities
        return prices, revenues


def print_pricing_table(results: List[PricingResult]):
    """Print optimal pricing recommendations."""
    print(f"\n{'='*90}")
    print(f"  OPTIMAL PRICING RECOMMENDATIONS")
    print(f"{'='*90}")
    print(f"  {'Product':<8} {'ε':>6} {'Current$':>9} {'Optimal$':>9} {'Δ%':>7} "
          f"{'CurrProfit':>11} {'OptProfit':>11} {'Uplift%':>8}")
    print(f"  {'-'*85}")

    total_current = 0
    total_optimal = 0
    for r in results:
        total_current += r.current_profit
        total_optimal += r.optimal_profit
        print(f"  {r.product_id:<8} {r.elasticity_used:>6.2f} "
              f"${r.current_price:>7.2f} ${r.optimal_price:>7.2f} "
              f"{r.price_change_pct:>+6.1f}% "
              f"${r.current_profit:>9,.0f} ${r.optimal_profit:>9,.0f} "
              f"{r.profit_uplift_pct:>+7.1f}%")

    total_uplift = (total_optimal / total_current - 1) * 100 if total_current > 0 else 0
    print(f"  {'-'*85}")
    print(f"  {'TOTAL':<8} {'':>6} {'':>9} {'':>9} {'':>7} "
          f"${total_current:>9,.0f} ${total_optimal:>9,.0f} {total_uplift:>+7.1f}%")
    print(f"{'='*90}\n")
