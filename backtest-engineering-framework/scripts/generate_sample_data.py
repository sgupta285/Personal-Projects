from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


OUTPUT = Path("data/sample/us_etf_sample.csv")
TICKERS = ["SPY", "QQQ", "IWM", "TLT", "GLD", "XLF"]
START = "2005-01-03"
END = "2025-01-31"
SEED = 42


DRIFT = {
    "SPY": 0.00035,
    "QQQ": 0.00045,
    "IWM": 0.00030,
    "TLT": 0.00018,
    "GLD": 0.00022,
    "XLF": 0.00028,
}

VOL = {
    "SPY": 0.010,
    "QQQ": 0.013,
    "IWM": 0.014,
    "TLT": 0.008,
    "GLD": 0.009,
    "XLF": 0.012,
}

BASE_PRICE = {
    "SPY": 120.0,
    "QQQ": 42.0,
    "IWM": 68.0,
    "TLT": 90.0,
    "GLD": 45.0,
    "XLF": 28.0,
}

BASE_VOLUME = {
    "SPY": 82_000_000,
    "QQQ": 60_000_000,
    "IWM": 36_000_000,
    "TLT": 18_000_000,
    "GLD": 20_000_000,
    "XLF": 28_000_000,
}


rng = np.random.default_rng(SEED)
dates = pd.bdate_range(START, END)
rows: list[dict] = []
market_shock = rng.normal(0.0, 0.006, len(dates))

for ticker in TICKERS:
    price = BASE_PRICE[ticker]
    for idx, date in enumerate(dates):
        idio = rng.normal(DRIFT[ticker], VOL[ticker])
        ret = 0.35 * market_shock[idx] + idio
        open_px = price
        close_px = max(1.0, open_px * (1.0 + ret))
        intraday = abs(rng.normal(0.0, VOL[ticker] * 0.55))
        high_px = max(open_px, close_px) * (1.0 + intraday)
        low_px = min(open_px, close_px) * (1.0 - intraday)
        volume = int(BASE_VOLUME[ticker] * max(0.25, 1.0 + rng.normal(0.0, 0.18)))
        rows.append({
            "date": date.date().isoformat(),
            "ticker": ticker,
            "open": round(open_px, 4),
            "high": round(high_px, 4),
            "low": round(low_px, 4),
            "close": round(close_px, 4),
            "volume": volume,
        })
        price = close_px

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(OUTPUT, index=False)
print(f"wrote {OUTPUT} with {len(rows)} rows")
