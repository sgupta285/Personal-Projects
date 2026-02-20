"""
Synthetic Retail Data Generator with Known Elasticities.

Generates weekly store-product sales data using a constant-elasticity demand model:
    ln(Q) = α + ε_own * ln(P) + Σ ε_cross * ln(P_j) + β*X + noise

where ε_own is the own-price elasticity and ε_cross are cross-price elasticities.
True elasticities are embedded for validation of estimation methods.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from dataclasses import dataclass
import structlog

from src.config import config

logger = structlog.get_logger()


@dataclass
class ProductSpec:
    product_id: str
    category: str
    base_price: float
    base_quantity: float
    own_elasticity: float           # True own-price elasticity (negative)
    marginal_cost: float
    seasonality_amplitude: float


def generate_elasticity_data(
    n_products: int = 8,
    n_stores: int = 5,
    n_weeks: int = 156,
    seed: int = 42,
) -> Tuple[pd.DataFrame, np.ndarray, List[ProductSpec]]:
    """
    Generate synthetic panel data with known price elasticities.

    Returns:
        panel_df: Weekly store-product panel (store, product, week, price, quantity, ...)
        true_cross_elasticity: n_products × n_products matrix of true cross-price elasticities
        product_specs: List of product specifications with true parameters
    """
    np.random.seed(seed)

    categories = ["beverage", "snack", "dairy", "produce", "bakery", "frozen", "canned", "cereal"]
    base_prices = [3.49, 4.99, 5.29, 2.99, 3.99, 6.49, 2.49, 4.29]
    base_quantities = [500, 350, 400, 600, 300, 200, 450, 380]
    own_elasticities = [-1.8, -2.2, -1.5, -1.3, -2.0, -1.6, -1.1, -1.9]
    season_amps = [0.05, 0.15, 0.08, 0.25, 0.10, 0.20, 0.05, 0.12]

    products = []
    for i in range(n_products):
        idx = i % len(categories)
        products.append(ProductSpec(
            product_id=f"P{i:02d}",
            category=categories[idx],
            base_price=base_prices[idx] * np.random.uniform(0.8, 1.2),
            base_quantity=base_quantities[idx] * np.random.uniform(0.7, 1.3),
            own_elasticity=own_elasticities[idx] + np.random.randn() * 0.15,
            marginal_cost=base_prices[idx] * config.model.marginal_cost_pct,
            seasonality_amplitude=season_amps[idx],
        ))

    # --- Cross-price elasticity matrix ---
    # Positive = substitutes, zero = unrelated
    cross_matrix = np.zeros((n_products, n_products))
    for i in range(n_products):
        for j in range(n_products):
            if i == j:
                cross_matrix[i, j] = products[i].own_elasticity
            elif products[i].category == products[j].category:
                # Same category → strong substitutes
                cross_matrix[i, j] = np.random.uniform(0.20, 0.40)
            elif np.random.random() < 0.3:
                # Some cross-category substitution
                cross_matrix[i, j] = np.random.uniform(0.02, 0.15)
            # else 0 (unrelated)

    # --- Generate panel data ---
    weeks = pd.date_range(start="2021-01-04", periods=n_weeks, freq="W-MON")
    store_ids = [f"S{s:02d}" for s in range(n_stores)]

    records = []
    for store_idx, store_id in enumerate(store_ids):
        store_effect = np.random.randn() * 0.15  # Store fixed effect

        for week_idx, week_date in enumerate(weeks):
            # Prices for all products this week (with promotions and cost shocks)
            prices = np.zeros(n_products)
            cost_shocks = np.zeros(n_products)

            for i, prod in enumerate(products):
                # Supply-side cost shock (instrument for IV)
                cost_shock = np.random.randn() * 0.08
                cost_shocks[i] = cost_shock

                # Promotion (exogenous price variation)
                is_promo = np.random.random() < config.data.promo_frequency
                discount = np.random.uniform(*config.data.promo_discount_range) if is_promo else 0.0

                # Price = base * (1 + cost_shock) * (1 - discount) + small noise
                price = prod.base_price * (1 + cost_shock) * (1 - discount)
                price *= (1 + np.random.randn() * 0.02)  # micro noise
                prices[i] = max(price, 0.50)

            # Generate quantities using constant-elasticity demand
            for i, prod in enumerate(products):
                # ln(Q) = ln(Q0) + ε_own * ln(P/P0) + Σ ε_cross * ln(P_j/P0_j) + controls + noise
                log_q = np.log(prod.base_quantity)

                # Own-price effect
                log_q += prod.own_elasticity * np.log(prices[i] / prod.base_price)

                # Cross-price effects
                for j in range(n_products):
                    if j != i and cross_matrix[i, j] != 0:
                        log_q += cross_matrix[i, j] * np.log(prices[j] / products[j].base_price)

                # Store effect
                log_q += store_effect

                # Seasonality (annual)
                week_of_year = week_date.isocalendar()[1]
                log_q += prod.seasonality_amplitude * np.sin(2 * np.pi * week_of_year / 52)

                # Holiday boost (Thanksgiving/Christmas weeks)
                if week_date.month == 11 and 20 <= week_date.day <= 30:
                    log_q += 0.25
                elif week_date.month == 12 and 15 <= week_date.day <= 31:
                    log_q += 0.30

                # Trend
                log_q += 0.0005 * week_idx

                # AR noise + random
                log_q += np.random.randn() * 0.08

                quantity = max(1, int(np.round(np.exp(log_q))))
                revenue = quantity * prices[i]

                records.append({
                    "date": week_date,
                    "week": week_idx,
                    "store_id": store_id,
                    "product_id": prod.product_id,
                    "category": prod.category,
                    "price": round(prices[i], 2),
                    "quantity": quantity,
                    "revenue": round(revenue, 2),
                    "base_price": round(prod.base_price, 2),
                    "log_price": round(np.log(prices[i]), 4),
                    "log_quantity": round(np.log(quantity), 4),
                    "is_promotion": prices[i] < prod.base_price * 0.90,
                    "discount_pct": round(max(0, 1 - prices[i] / prod.base_price) * 100, 1),
                    "cost_shock": round(cost_shocks[i], 4),
                    "week_of_year": week_of_year,
                    "month": week_date.month,
                    "quarter": week_date.quarter,
                })

    panel_df = pd.DataFrame(records)
    logger.info("elasticity_data_generated",
                rows=len(panel_df), products=n_products, stores=n_stores, weeks=n_weeks)

    return panel_df, cross_matrix, products
