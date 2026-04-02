from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    rng = np.random.default_rng(42)
    n_rows = 2500
    sessions = rng.poisson(12, size=n_rows)
    spend = np.clip(rng.normal(88, 36, size=n_rows), 5, None)
    support_tickets = rng.poisson(1.2, size=n_rows)
    account_age = rng.integers(30, 1800, size=n_rows)
    avg_session_minutes = np.clip(rng.normal(14, 5, size=n_rows), 1, None)
    region = rng.choice(["midwest", "west", "south", "northeast"], size=n_rows, p=[0.28, 0.27, 0.25, 0.2])
    device_type = rng.choice(["ios", "android", "web"], size=n_rows, p=[0.35, 0.45, 0.2])
    plan_tier = rng.choice(["basic", "pro", "business"], size=n_rows, p=[0.55, 0.3, 0.15])
    signup_channel = rng.choice(["organic", "sales", "partner", "paid"], size=n_rows, p=[0.45, 0.18, 0.12, 0.25])
    is_premium = (plan_tier != "basic").astype(int)

    churn_score = (
        -0.025 * spend
        -0.08 * sessions
        + 0.45 * support_tickets
        -0.003 * account_age
        + 0.15 * (plan_tier == "basic")
        + 0.22 * (signup_channel == "paid")
        + rng.normal(0, 0.9, size=n_rows)
    )
    churn_probability = 1 / (1 + np.exp(-churn_score))
    churned = (churn_probability > 0.52).astype(int)

    df = pd.DataFrame(
        {
            "customer_id": np.arange(100000, 100000 + n_rows),
            "monthly_spend": spend.round(2),
            "sessions_last_30d": sessions,
            "avg_session_minutes": avg_session_minutes.round(2),
            "support_tickets": support_tickets,
            "account_age_days": account_age,
            "region": region,
            "device_type": device_type,
            "plan_tier": plan_tier,
            "signup_channel": signup_channel,
            "is_premium": is_premium,
            "churned": churned,
        }
    )

    for column in ["avg_session_minutes", "region", "signup_channel"]:
        idx = rng.choice(df.index, size=80, replace=False)
        df.loc[idx, column] = np.nan

    outlier_idx = rng.choice(df.index, size=15, replace=False)
    df.loc[outlier_idx, "monthly_spend"] *= 6
    duplicate_rows = df.sample(10, random_state=7)
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    output_path = Path("data/raw/customer_events.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Wrote sample dataset to {output_path} with shape {df.shape}")


if __name__ == "__main__":
    main()
