from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


TARGET_COLUMN = "units_sold"
ID_COLUMNS = ["date", "product_id"]
CATEGORICAL_COLUMNS = ["category", "channel", "demand_regime"]


def build_feature_table(transactions: pd.DataFrame) -> pd.DataFrame:
    df = transactions.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["product_id", "channel", "date"]).reset_index(drop=True)

    df["price_index_vs_base"] = df["price"] / df["base_price"].clip(lower=0.01)
    df["competitor_gap_pct"] = (df["price"] - df["competitor_price"]) / df["competitor_price"].clip(lower=0.01)
    df["promotion_intensity"] = df["discount_pct"]
    df["inventory_pressure"] = 1 - (df["inventory_level"] / df["max_inventory"].clip(lower=1))
    df["gross_margin_per_unit"] = df["price"] - df["unit_cost"]
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)
    df["markdown_flag"] = (df["discount_pct"] > 0.10).astype(int)

    grouped = df.groupby(["product_id", "channel"], sort=False)
    df["units_sold_lag_1"] = grouped["units_sold"].shift(1).fillna(df["units_sold"].median())
    df["units_sold_lag_7"] = grouped["units_sold"].shift(7).fillna(df["units_sold"].median())
    df["units_sold_rolling_7"] = grouped["units_sold"].transform(lambda s: s.shift(1).rolling(7, min_periods=1).mean()).fillna(df["units_sold"].median())
    df["price_lag_1"] = grouped["price"].shift(1).fillna(df["price"])
    df["price_change_pct"] = (df["price"] - df["price_lag_1"]) / df["price_lag_1"].replace(0, 1)
    df["conversion_proxy"] = (df["page_views"] * df["cart_add_rate"]).clip(lower=0.01)

    ordered = [
        "date",
        "product_id",
        "category",
        "channel",
        "demand_regime",
        "base_price",
        "unit_cost",
        "price",
        "discount_pct",
        "promotion_intensity",
        "competitor_price",
        "competitor_gap_pct",
        "inventory_level",
        "max_inventory",
        "inventory_pressure",
        "seasonality_index",
        "returning_customer_share",
        "page_views",
        "cart_add_rate",
        "conversion_proxy",
        "weekday",
        "month",
        "is_weekend",
        "is_holiday",
        "price_index_vs_base",
        "gross_margin_per_unit",
        "markdown_flag",
        "units_sold_lag_1",
        "units_sold_lag_7",
        "units_sold_rolling_7",
        "price_lag_1",
        "price_change_pct",
        "units_sold",
    ]
    return df[ordered]


def model_input_frame(feature_df: pd.DataFrame) -> pd.DataFrame:
    X = feature_df.drop(columns=[TARGET_COLUMN, "product_id"], errors="ignore").copy()
    X["date_ordinal"] = pd.to_datetime(X["date"]).map(pd.Timestamp.toordinal)
    X = X.drop(columns=["date"])
    encoded = pd.get_dummies(X, columns=CATEGORICAL_COLUMNS, drop_first=False)
    return encoded


def align_model_frame(frame: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    return frame.reindex(columns=feature_columns, fill_value=0)


def save_feature_table(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
