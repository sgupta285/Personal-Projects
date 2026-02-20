"""
Synthetic Retail Data Generator.

Generates realistic daily demand with:
- Store-level heterogeneity (location, size, base demand)
- Product categories with distinct seasonality patterns
- Weekly/monthly/annual seasonality (Fourier components)
- Holiday effects (US holidays + Black Friday / back-to-school)
- Promotional price discounts with demand uplift
- Weather-driven demand variation
- Trend + autoregressive noise
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict
import structlog

logger = structlog.get_logger()

US_HOLIDAYS = {
    (1, 1): "New Year", (2, 14): "Valentine's Day",
    (5, 27): "Memorial Day", (7, 4): "July 4th",
    (9, 2): "Labor Day", (10, 31): "Halloween",
    (11, 28): "Thanksgiving", (12, 25): "Christmas",
    (12, 31): "New Year's Eve",
}

PRODUCT_CATEGORIES = {
    "grocery": {"base": 200, "trend": 0.02, "weekly_amp": 0.25, "annual_amp": 0.10, "promo_lift": 0.30},
    "electronics": {"base": 30, "trend": 0.05, "weekly_amp": 0.15, "annual_amp": 0.35, "promo_lift": 0.50},
    "clothing": {"base": 50, "trend": 0.03, "weekly_amp": 0.10, "annual_amp": 0.30, "promo_lift": 0.40},
    "home_garden": {"base": 40, "trend": 0.02, "weekly_amp": 0.12, "annual_amp": 0.25, "promo_lift": 0.25},
    "health": {"base": 80, "trend": 0.04, "weekly_amp": 0.08, "annual_amp": 0.15, "promo_lift": 0.20},
}


def generate_retail_data(
    n_stores: int = 10,
    n_products: int = 50,
    n_days: int = 1095,
    start_date: str = "2021-01-01",
    seed: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate synthetic retail demand data.

    Returns:
        sales_df: Daily sales (store_id, product_id, date, quantity, revenue, ...)
        stores_df: Store metadata
        products_df: Product metadata
    """
    np.random.seed(seed)
    dates = pd.date_range(start=start_date, periods=n_days, freq="D")

    # --- Store metadata ---
    store_sizes = np.random.choice(["small", "medium", "large"], n_stores, p=[0.3, 0.5, 0.2])
    size_multiplier = {"small": 0.6, "medium": 1.0, "large": 1.5}
    stores_df = pd.DataFrame({
        "store_id": [f"S{i:03d}" for i in range(n_stores)],
        "size": store_sizes,
        "size_mult": [size_multiplier[s] for s in store_sizes],
        "lat": np.random.uniform(25, 48, n_stores),
        "lng": np.random.uniform(-122, -73, n_stores),
    })

    # --- Product metadata ---
    categories = list(PRODUCT_CATEGORIES.keys())
    product_cats = np.random.choice(categories, n_products)
    products_df = pd.DataFrame({
        "product_id": [f"P{i:03d}" for i in range(n_products)],
        "category": product_cats,
        "base_price": np.round(np.random.uniform(2, 200, n_products), 2),
        "shelf_life_days": np.random.choice([0, 7, 14, 30, 365], n_products),
    })

    # --- Generate daily sales ---
    records = []
    for store_idx in range(n_stores):
        store_id = stores_df.loc[store_idx, "store_id"]
        s_mult = stores_df.loc[store_idx, "size_mult"]

        for prod_idx in range(n_products):
            product_id = products_df.loc[prod_idx, "product_id"]
            cat = products_df.loc[prod_idx, "category"]
            base_price = products_df.loc[prod_idx, "base_price"]
            cat_params = PRODUCT_CATEGORIES[cat]

            base_demand = cat_params["base"] * s_mult
            trend_rate = cat_params["trend"] / 365  # daily

            # Pre-compute series for this store-product
            demand = np.zeros(n_days)
            ar_noise = 0.0

            for t, date in enumerate(dates):
                day_of_week = date.dayofweek
                day_of_year = date.dayofyear
                month = date.month

                # 1. Trend
                trend = base_demand * (1 + trend_rate * t)

                # 2. Weekly seasonality (weekend uplift)
                weekly = cat_params["weekly_amp"] * np.sin(2 * np.pi * day_of_week / 7)
                if day_of_week >= 5:  # Sat/Sun
                    weekly += 0.15

                # 3. Annual seasonality
                annual = cat_params["annual_amp"] * (
                    np.sin(2 * np.pi * day_of_year / 365) +
                    0.3 * np.cos(4 * np.pi * day_of_year / 365)
                )

                # 4. Holiday effect
                holiday_mult = 1.0
                key = (date.month, date.day)
                if key in US_HOLIDAYS:
                    holiday_mult = 1.5 if cat == "grocery" else 2.0
                # Black Friday (day after Thanksgiving, ~Nov 24-30)
                if month == 11 and 24 <= date.day <= 30 and day_of_week == 4:
                    holiday_mult = 3.0 if cat == "electronics" else 2.0
                # Back to school (Aug)
                if month == 8 and cat in ("clothing", "electronics"):
                    holiday_mult = 1.3

                # 5. Promotion (random ~15% of days)
                is_promo = np.random.random() < 0.15
                promo_mult = 1.0 + cat_params["promo_lift"] if is_promo else 1.0
                discount = np.random.uniform(0.10, 0.35) if is_promo else 0.0

                # 6. Weather effect (simplified: temperature-based)
                temp = 50 + 25 * np.sin(2 * np.pi * (day_of_year - 80) / 365) + np.random.randn() * 8
                weather_mult = 1.0
                if cat == "home_garden" and temp > 65:
                    weather_mult = 1.2
                elif cat == "grocery" and temp < 35:
                    weather_mult = 1.1  # comfort food

                # 7. AR(1) noise
                ar_noise = 0.6 * ar_noise + np.random.randn() * base_demand * 0.08

                # Combine
                raw_demand = trend * (1 + weekly + annual) * holiday_mult * promo_mult * weather_mult + ar_noise
                quantity = max(0, int(np.round(raw_demand)))
                sell_price = base_price * (1 - discount)
                revenue = quantity * sell_price

                records.append({
                    "date": date,
                    "store_id": store_id,
                    "product_id": product_id,
                    "quantity": quantity,
                    "revenue": round(revenue, 2),
                    "base_price": base_price,
                    "sell_price": round(sell_price, 2),
                    "discount_pct": round(discount * 100, 1),
                    "is_promotion": is_promo,
                    "is_holiday": (date.month, date.day) in US_HOLIDAYS,
                    "temperature": round(temp, 1),
                    "day_of_week": day_of_week,
                    "month": month,
                })

    sales_df = pd.DataFrame(records)
    logger.info("data_generated",
                rows=len(sales_df), stores=n_stores, products=n_products, days=n_days)
    return sales_df, stores_df, products_df


def aggregate_daily(sales_df: pd.DataFrame, level: str = "store") -> pd.DataFrame:
    """Aggregate sales to daily level by store or product."""
    if level == "store":
        group_cols = ["date", "store_id"]
    elif level == "product":
        group_cols = ["date", "product_id"]
    else:
        group_cols = ["date", "store_id", "product_id"]

    agg = sales_df.groupby(group_cols).agg(
        quantity=("quantity", "sum"),
        revenue=("revenue", "sum"),
        avg_discount=("discount_pct", "mean"),
        n_promotions=("is_promotion", "sum"),
        avg_temp=("temperature", "mean"),
    ).reset_index()
    return agg
