from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


CATEGORIES = {
    "electronics": {"base_price": (80, 220), "cost_ratio": 0.58, "elasticity": 1.45, "base_demand": 18},
    "home": {"base_price": (35, 140), "cost_ratio": 0.52, "elasticity": 1.10, "base_demand": 22},
    "beauty": {"base_price": (18, 75), "cost_ratio": 0.40, "elasticity": 1.70, "base_demand": 28},
    "sports": {"base_price": (30, 160), "cost_ratio": 0.50, "elasticity": 1.25, "base_demand": 20},
}
CHANNELS = {"web": 1.00, "mobile": 1.08, "marketplace": 0.87}
REGIMES = {"low": 0.87, "normal": 1.0, "peak": 1.18}


@dataclass(slots=True)
class GenerationConfig:
    n_products: int = 48
    days: int = 240
    seed: int = 42


def build_product_catalog(n_products: int = 48, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    category_names = list(CATEGORIES.keys())
    for i in range(1, n_products + 1):
        category = category_names[(i - 1) % len(category_names)]
        cfg = CATEGORIES[category]
        base_price = float(rng.uniform(*cfg["base_price"]))
        unit_cost = round(base_price * rng.uniform(cfg["cost_ratio"] - 0.05, cfg["cost_ratio"] + 0.04), 2)
        elasticity = round(float(rng.normal(cfg["elasticity"], 0.12)), 3)
        base_demand = round(float(rng.normal(cfg["base_demand"], 3.0)), 3)
        max_inventory = int(rng.integers(90, 320))
        rows.append(
            {
                "product_id": f"sku-{i:03d}",
                "category": category,
                "base_price": round(base_price, 2),
                "unit_cost": max(1.0, unit_cost),
                "elasticity": max(0.65, elasticity),
                "base_demand": max(6.0, base_demand),
                "max_inventory": max_inventory,
            }
        )
    return pd.DataFrame(rows)


def regime_for_date(date: pd.Timestamp) -> str:
    if date.month in {11, 12}:
        return "peak"
    if date.month in {1, 2, 7}:
        return "low"
    return "normal"


def seasonality_index(date: pd.Timestamp) -> float:
    day_of_year = date.dayofyear
    wave = 1 + 0.16 * np.sin(2 * np.pi * day_of_year / 365.0)
    weekend = 0.05 if date.weekday() >= 5 else 0.0
    holiday = 0.18 if date.month == 11 and 20 <= date.day <= 30 else 0.0
    return round(float(wave + weekend + holiday), 4)


def expected_units(row: pd.Series, catalog_row: pd.Series, candidate_price: float) -> float:
    price_ratio = max(candidate_price / max(float(catalog_row["base_price"]), 1e-6), 0.35)
    competitor_gap = (float(row["competitor_price"]) - candidate_price) / max(float(row["competitor_price"]), 1.0)
    promo_effect = 1 + 0.55 * float(row["promotion_intensity"])
    inventory_pressure = 1 - min(float(row["inventory_level"]) / max(float(catalog_row["max_inventory"]), 1.0), 1.0)
    channel_effect = CHANNELS[str(row["channel"])]
    regime_effect = REGIMES[str(row["demand_regime"])]
    recency_effect = 0.82 + 0.45 * float(row["returning_customer_share"])
    cart_effect = 0.70 + 1.15 * float(row["cart_add_rate"])
    holiday_effect = 1.14 if int(row["is_holiday"]) == 1 else 1.0

    demand = (
        float(catalog_row["base_demand"])
        * float(row["seasonality_index"])
        * channel_effect
        * regime_effect
        * recency_effect
        * cart_effect
        * promo_effect
        * holiday_effect
        * np.exp(-float(catalog_row["elasticity"]) * np.log(price_ratio))
        * np.exp(0.65 * competitor_gap)
        * (1 - 0.18 * inventory_pressure)
    )
    return max(0.05, float(demand))


def generate_transactions(catalog: pd.DataFrame, days: int = 240, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start_date = pd.Timestamp("2025-07-01")
    dates = pd.date_range(start_date, periods=days, freq="D")
    rows = []

    for _, product in catalog.iterrows():
        inventory_level = int(rng.integers(int(product["max_inventory"] * 0.45), product["max_inventory"]))
        for current_date in dates:
            for channel in CHANNELS:
                if inventory_level < int(product["max_inventory"] * 0.15):
                    inventory_level = int(rng.integers(int(product["max_inventory"] * 0.55), product["max_inventory"]))

                discount_pct = float(np.clip(rng.normal(0.08, 0.07), 0.0, 0.35))
                competitor_price = float(product["base_price"] * rng.uniform(0.9, 1.12))
                listed_price = float(product["base_price"] * rng.uniform(0.94, 1.1))
                realized_price = round(max(1.0, listed_price * (1 - discount_pct)), 2)

                regime = regime_for_date(current_date)
                season_idx = seasonality_index(current_date)
                returning_share = float(np.clip(rng.normal(0.48 if channel != "marketplace" else 0.33, 0.14), 0.05, 0.95))
                page_views = int(np.clip(rng.normal(product["base_demand"] * 8 * CHANNELS[channel], 25), 25, 800))
                cart_add_rate = float(np.clip(rng.normal(0.17 if channel == "mobile" else 0.15, 0.04), 0.02, 0.45))
                is_holiday = int(current_date.month == 11 and 20 <= current_date.day <= 30)

                context_row = pd.Series(
                    {
                        "channel": channel,
                        "competitor_price": competitor_price,
                        "promotion_intensity": discount_pct,
                        "inventory_level": inventory_level,
                        "seasonality_index": season_idx,
                        "demand_regime": regime,
                        "returning_customer_share": returning_share,
                        "cart_add_rate": cart_add_rate,
                        "is_holiday": is_holiday,
                    }
                )
                base_expected = expected_units(context_row, product, realized_price)
                noisy_expected = base_expected * float(rng.lognormal(mean=0.0, sigma=0.12))
                units_sold = int(min(inventory_level, rng.poisson(max(noisy_expected, 0.05))))

                inventory_level = max(0, inventory_level - units_sold)
                if current_date.weekday() in {1, 4}:
                    inventory_level = min(int(product["max_inventory"]), inventory_level + int(rng.integers(4, 18)))

                rows.append(
                    {
                        "date": current_date.date().isoformat(),
                        "product_id": product["product_id"],
                        "category": product["category"],
                        "channel": channel,
                        "base_price": product["base_price"],
                        "unit_cost": product["unit_cost"],
                        "price": realized_price,
                        "discount_pct": round(discount_pct, 4),
                        "competitor_price": round(competitor_price, 2),
                        "inventory_level": inventory_level,
                        "max_inventory": int(product["max_inventory"]),
                        "seasonality_index": season_idx,
                        "demand_regime": regime,
                        "returning_customer_share": round(returning_share, 4),
                        "page_views": page_views,
                        "cart_add_rate": round(cart_add_rate, 4),
                        "is_holiday": is_holiday,
                        "weekday": int(current_date.weekday()),
                        "month": int(current_date.month),
                        "units_sold": units_sold,
                    }
                )
    return pd.DataFrame(rows)


def save_catalog(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def save_transactions(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
