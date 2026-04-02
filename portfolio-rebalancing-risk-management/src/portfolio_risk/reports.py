from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

import pandas as pd

from .models import EfficientFrontierPoint, RebalanceTrade, RiskSnapshot


def _to_plain_record(record: RebalanceTrade) -> dict[str, float | str]:
    return {
        "ticker": record.ticker,
        "current_weight": round(record.current_weight, 6),
        "target_weight": round(record.target_weight, 6),
        "recommended_weight": round(record.recommended_weight, 6),
        "trade_value": round(record.trade_value, 2),
        "action": record.action,
    }


def write_report(report_dir: str | Path, risk_snapshot: RiskSnapshot, portfolio_snapshot: pd.DataFrame, rebalancing_plan: list[RebalanceTrade], frontier: list[EfficientFrontierPoint], correlation: pd.DataFrame) -> Path:
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "risk_snapshot": {
            "portfolio_value": round(risk_snapshot.portfolio_value, 2),
            "daily_var": round(risk_snapshot.daily_var, 6),
            "daily_cvar": round(risk_snapshot.daily_cvar, 6),
            "annualized_volatility": round(risk_snapshot.annualized_volatility, 6),
            "sharpe_ratio": round(risk_snapshot.sharpe_ratio, 6),
        },
        "portfolio_snapshot": portfolio_snapshot.to_dict(orient="records"),
        "rebalancing_plan": [_to_plain_record(t) for t in rebalancing_plan],
        "efficient_frontier": [asdict(point) for point in frontier],
        "correlation_matrix": correlation.round(4).to_dict(),
    }
    out = report_dir / "portfolio_report.json"
    out.write_text(json.dumps(payload, indent=2))
    portfolio_snapshot.to_csv(report_dir / "portfolio_snapshot.csv", index=False)
    if rebalancing_plan:
        pd.DataFrame([_to_plain_record(t) for t in rebalancing_plan]).to_csv(report_dir / "rebalancing_plan.csv", index=False)
    return out
