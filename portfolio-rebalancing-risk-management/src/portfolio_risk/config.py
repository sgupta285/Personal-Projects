from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///artifacts/demo/portfolio_local.db")
    risk_free_rate: float = float(os.getenv("RISK_FREE_RATE", "0.02"))
    var_confidence: float = float(os.getenv("VAR_CONFIDENCE", "0.95"))
    trading_days: int = int(os.getenv("TRADING_DAYS", "252"))
    max_turnover: float = float(os.getenv("MAX_TURNOVER", "0.15"))
    min_weight: float = float(os.getenv("MIN_WEIGHT", "0.00"))
    max_weight: float = float(os.getenv("MAX_WEIGHT", "0.40"))
