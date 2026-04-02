from __future__ import annotations

import sys
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from portfolio_risk.data_loader import load_positions, load_prices, load_targets
from portfolio_risk.portfolio import portfolio_snapshot
from portfolio_risk.risk import return_matrix, risk_snapshot

prices = load_prices(ROOT / "data/raw/prices.csv")
positions = load_positions(ROOT / "data/raw/positions.csv")
targets = load_targets(ROOT / "data/raw/targets.csv")
snapshot = portfolio_snapshot(prices, positions, targets)
returns = return_matrix(prices)

start = time.perf_counter()
for _ in range(300):
    risk_snapshot(returns, snapshot, 0.02, 0.95)
elapsed = time.perf_counter() - start
print({"iterations": 300, "elapsed_seconds": round(elapsed, 4), "per_call_ms": round((elapsed / 300) * 1000, 4)})
