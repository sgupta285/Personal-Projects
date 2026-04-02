from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)
dates = pd.bdate_range("2023-01-03", periods=504)
assets = {
    "SPY": (0.09 / 252, 0.18 / np.sqrt(252)),
    "AGG": (0.035 / 252, 0.06 / np.sqrt(252)),
    "GLD": (0.045 / 252, 0.14 / np.sqrt(252)),
    "VNQ": (0.06 / 252, 0.21 / np.sqrt(252)),
    "EFA": (0.07 / 252, 0.19 / np.sqrt(252)),
}
correlation = np.array([
    [1.0, -0.15, 0.05, 0.55, 0.72],
    [-0.15, 1.0, 0.10, -0.05, -0.08],
    [0.05, 0.10, 1.0, 0.08, 0.12],
    [0.55, -0.05, 0.08, 1.0, 0.48],
    [0.72, -0.08, 0.12, 0.48, 1.0],
])
vols = np.array([assets[t][1] for t in assets])
means = np.array([assets[t][0] for t in assets])
cov = np.outer(vols, vols) * correlation
returns = rng.multivariate_normal(means, cov, size=len(dates))

price_rows = []
for col_idx, ticker in enumerate(assets):
    series = 100 * np.cumprod(1 + returns[:, col_idx])
    for date, price in zip(dates, series):
        price_rows.append({"date": date.date().isoformat(), "ticker": ticker, "close": round(float(price), 4)})

pd.DataFrame(price_rows).to_csv(OUT / "prices.csv", index=False)
pd.DataFrame(
    [
        {"ticker": "SPY", "asset_class": "US Equity", "target_weight": 0.35},
        {"ticker": "AGG", "asset_class": "Fixed Income", "target_weight": 0.25},
        {"ticker": "GLD", "asset_class": "Commodities", "target_weight": 0.10},
        {"ticker": "VNQ", "asset_class": "Real Estate", "target_weight": 0.15},
        {"ticker": "EFA", "asset_class": "International Equity", "target_weight": 0.15},
    ]
).to_csv(OUT / "targets.csv", index=False)
pd.DataFrame(
    [
        {"ticker": "SPY", "shares": 260.0, "lot_cost": 370.0},
        {"ticker": "AGG", "shares": 410.0, "lot_cost": 98.0},
        {"ticker": "GLD", "shares": 90.0, "lot_cost": 169.0},
        {"ticker": "VNQ", "shares": 140.0, "lot_cost": 89.0},
        {"ticker": "EFA", "shares": 125.0, "lot_cost": 72.0},
    ]
).to_csv(OUT / "positions.csv", index=False)
print(f"Sample data written to {OUT}")
