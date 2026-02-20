"""
Feature Engineering Pipeline.

Generates temporal, lag, rolling, Fourier, holiday, promotion, and weather features
for ML-based demand forecasting.
"""

import numpy as np
import pandas as pd
from typing import List, Optional
import structlog

from src.config import config

logger = structlog.get_logger()


class FeatureEngineer:
    """Build feature matrix for demand forecasting."""

    def __init__(self, cfg=None):
        self.cfg = cfg or config.features

    def build_features(self, df: pd.DataFrame, target_col: str = "quantity") -> pd.DataFrame:
        """
        Build complete feature matrix from daily sales data.

        Expects columns: date, quantity, and optionally:
            discount_pct, is_promotion, temperature, store_id, product_id

        Returns DataFrame with features + target (no NaN rows).
        """
        df = df.copy().sort_values("date").reset_index(drop=True)
        df["date"] = pd.to_datetime(df["date"])

        # --- Calendar features ---
        df["day_of_week"] = df["date"].dt.dayofweek
        df["day_of_month"] = df["date"].dt.day
        df["day_of_year"] = df["date"].dt.dayofyear
        df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
        df["month"] = df["date"].dt.month
        df["quarter"] = df["date"].dt.quarter
        df["year"] = df["date"].dt.year
        df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
        df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
        df["is_month_end"] = df["date"].dt.is_month_end.astype(int)

        # Days since epoch (linear trend proxy)
        df["days_since_start"] = (df["date"] - df["date"].min()).dt.days

        # --- Lag features ---
        for lag in self.cfg.lag_days:
            df[f"lag_{lag}"] = df[target_col].shift(lag)

        # --- Rolling statistics ---
        for w in self.cfg.rolling_windows:
            rolled = df[target_col].shift(1).rolling(w)
            df[f"roll_mean_{w}"] = rolled.mean()
            df[f"roll_std_{w}"] = rolled.std()
            df[f"roll_min_{w}"] = rolled.min()
            df[f"roll_max_{w}"] = rolled.max()
            df[f"roll_median_{w}"] = rolled.median()

        # --- EWM features ---
        for span in self.cfg.ewm_spans:
            df[f"ewm_{span}"] = df[target_col].shift(1).ewm(span=span).mean()

        # --- Fourier features (capture cyclic patterns) ---
        for k in range(1, self.cfg.fourier_order + 1):
            df[f"sin_weekly_{k}"] = np.sin(2 * np.pi * k * df["day_of_week"] / 7)
            df[f"cos_weekly_{k}"] = np.cos(2 * np.pi * k * df["day_of_week"] / 7)
            df[f"sin_annual_{k}"] = np.sin(2 * np.pi * k * df["day_of_year"] / 365.25)
            df[f"cos_annual_{k}"] = np.cos(2 * np.pi * k * df["day_of_year"] / 365.25)

        # --- Holiday features ---
        if self.cfg.include_holidays and "is_holiday" in df.columns:
            df["is_holiday"] = df["is_holiday"].astype(int)
            # Days to/from nearest holiday
            holiday_dates = df.loc[df["is_holiday"] == 1, "date"]
            if len(holiday_dates) > 0:
                df["days_to_holiday"] = df["date"].apply(
                    lambda d: min(abs((d - h).days) for h in holiday_dates[:50])
                )
                df["days_to_holiday"] = df["days_to_holiday"].clip(upper=30)

        # --- Promotion features ---
        if self.cfg.include_promotions:
            if "discount_pct" in df.columns:
                df["discount_pct"] = df["discount_pct"].fillna(0)
            if "is_promotion" in df.columns:
                df["is_promotion"] = df["is_promotion"].astype(int)
                df["promo_lag1"] = df["is_promotion"].shift(1).fillna(0)
                # Rolling promo frequency
                df["promo_count_7"] = df["is_promotion"].shift(1).rolling(7).sum().fillna(0)

        # --- Weather features ---
        if self.cfg.include_weather and "temperature" in df.columns:
            df["temp"] = df["temperature"]
            df["temp_lag1"] = df["temperature"].shift(1)
            df["temp_roll7"] = df["temperature"].shift(1).rolling(7).mean()
            df["temp_sq"] = df["temperature"] ** 2  # Non-linear effect

        # --- Interaction features ---
        if "is_weekend" in df.columns and "is_promotion" in df.columns:
            df["weekend_x_promo"] = df["is_weekend"] * df.get("is_promotion", 0)

        # --- Drop NaN rows from lags/rolling ---
        max_lookback = max(self.cfg.rolling_windows + self.cfg.lag_days)
        df = df.iloc[max_lookback:].reset_index(drop=True)

        logger.info("features_built", n_features=len(df.columns), n_rows=len(df))
        return df

    @staticmethod
    def get_feature_columns(df: pd.DataFrame, exclude: Optional[List[str]] = None) -> List[str]:
        """Return list of feature column names (excluding target, date, IDs)."""
        exclude = set(exclude or [])
        skip = {"date", "quantity", "revenue", "store_id", "product_id",
                "avg_temp", "n_promotions", "avg_discount", "temperature",
                "base_price", "sell_price", "is_holiday"} | exclude
        return [c for c in df.columns if c not in skip and df[c].dtype in ("float64", "int64", "int32", "float32")]
