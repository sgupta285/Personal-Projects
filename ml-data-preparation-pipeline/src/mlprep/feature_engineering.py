from __future__ import annotations

import numpy as np
import pandas as pd


class FeatureEngineer:
    def __init__(self, config: dict):
        self.config = config

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        enriched = df.copy()
        options = self.config.get("feature_engineering", {})

        if options.get("spend_per_session") and {"monthly_spend", "sessions_last_30d"}.issubset(enriched.columns):
            enriched["spend_per_session"] = enriched["monthly_spend"] / enriched["sessions_last_30d"].replace(0, np.nan)
            enriched["spend_per_session"] = enriched["spend_per_session"].fillna(0)

        if options.get("ticket_rate") and {"support_tickets", "account_age_days"}.issubset(enriched.columns):
            enriched["ticket_rate"] = enriched["support_tickets"] / enriched["account_age_days"].replace(0, np.nan)
            enriched["ticket_rate"] = enriched["ticket_rate"].fillna(0)

        if options.get("engagement_bucket") and "sessions_last_30d" in enriched.columns:
            enriched["engagement_bucket"] = pd.cut(
                enriched["sessions_last_30d"],
                bins=[-1, 5, 15, 1000],
                labels=["low", "medium", "high"],
            ).astype(str)

        return enriched
