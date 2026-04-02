from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class ExecutionConfig:
    tier: str
    commission_per_share: float
    spread_bps: float
    route_fee_bps: float
    latency_ms: float
    annual_borrow_bps: float = 0.0


@dataclass(slots=True)
class StrategyConfig:
    short_window: int
    long_window: int
    volatility_lookback: int
    target_gross_leverage: float


@dataclass(slots=True)
class WalkForwardConfig:
    train_days: int
    test_days: int
    step_days: int


@dataclass(slots=True)
class SweepConfig:
    short_windows: list[int]
    long_windows: list[int]


@dataclass(slots=True)
class AppConfig:
    data_path: str
    tickers: list[str]
    execution: ExecutionConfig
    strategy: StrategyConfig
    walk_forward: WalkForwardConfig
    sweep: SweepConfig
    initial_capital: float
    output_dir: str
    seed: int = 42


def load_config(path: str | Path) -> AppConfig:
    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text())
    return AppConfig(
        data_path=raw["data_path"],
        tickers=raw["tickers"],
        execution=ExecutionConfig(**raw["execution"]),
        strategy=StrategyConfig(**raw["strategy"]),
        walk_forward=WalkForwardConfig(**raw["walk_forward"]),
        sweep=SweepConfig(**raw["sweep"]),
        initial_capital=float(raw["initial_capital"]),
        output_dir=raw["output_dir"],
        seed=int(raw.get("seed", 42)),
    )
