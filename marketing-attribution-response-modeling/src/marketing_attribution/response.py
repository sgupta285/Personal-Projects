from __future__ import annotations

import math

import numpy as np
import pandas as pd


def response_function(spend: float | np.ndarray, alpha: float, beta: float) -> float | np.ndarray:
    return alpha * (1 - np.exp(-beta * spend))


def fit_single_channel_curve(channel_df: pd.DataFrame) -> dict:
    spend = channel_df["spend"].to_numpy(dtype=float)
    conversions = channel_df["conversions"].to_numpy(dtype=float)
    max_y = max(float(conversions.max()), 1.0)

    best = None
    alphas = np.linspace(max_y * 0.9, max_y * 2.2, 28)
    betas = np.logspace(-4.5, -2.0, 44)
    for alpha in alphas:
        for beta in betas:
            pred = response_function(spend, alpha, beta)
            mse = float(np.mean((pred - conversions) ** 2))
            if best is None or mse < best["mse"]:
                best = {"alpha": float(alpha), "beta": float(beta), "mse": mse}

    recent_spend = float(channel_df.tail(14)["spend"].mean())
    recent_revenue = float(channel_df.tail(14)["revenue"].mean())
    recent_conv = float(channel_df.tail(14)["conversions"].mean())
    aov = recent_revenue / recent_conv if recent_conv > 0 else 0.0
    marginal = float(best["alpha"] * best["beta"] * math.exp(-best["beta"] * recent_spend))

    return {
        "channel": str(channel_df["channel"].iloc[0]),
        "alpha": best["alpha"],
        "beta": best["beta"],
        "mse": best["mse"],
        "recent_avg_spend": recent_spend,
        "recent_avg_conversions": recent_conv,
        "recent_avg_revenue": recent_revenue,
        "aov": aov,
        "marginal_conversions_per_dollar": marginal,
        "current_roas": recent_revenue / recent_spend if recent_spend > 0 else 0.0,
    }


def fit_response_curves(panel: pd.DataFrame) -> pd.DataFrame:
    rows = [fit_single_channel_curve(group.copy()) for _, group in panel.groupby("channel")]
    return pd.DataFrame(rows).sort_values("marginal_conversions_per_dollar", ascending=False).reset_index(drop=True)
