"""
Configuration for Pairs Trading Pipeline.
"""

import os
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    host: str = os.getenv("PT_DB_HOST", "localhost")
    port: int = int(os.getenv("PT_DB_PORT", "5432"))
    name: str = os.getenv("PT_DB_NAME", "pairs_trading")
    user: str = os.getenv("PT_DB_USER", "pt_user")
    password: str = os.getenv("PT_DB_PASSWORD", "pt_pass")

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    host: str = os.getenv("PT_REDIS_HOST", "localhost")
    port: int = int(os.getenv("PT_REDIS_PORT", "6379"))
    enabled: bool = os.getenv("PT_REDIS_ENABLED", "true").lower() == "true"
    signal_channel: str = "pt:signals"
    tick_channel: str = "pt:ticks"


@dataclass
class CointegrationConfig:
    min_history_days: int = 252       # 1 year minimum
    max_pairs: int = 200              # Max pairs to track
    significance_level: float = 0.05  # Johansen test threshold
    half_life_max: int = 60           # Max mean-reversion half-life (days)
    half_life_min: int = 5            # Min half-life
    min_correlation: float = 0.50     # Pre-filter: minimum correlation
    rescan_interval_days: int = 30    # Re-run cointegration scan


@dataclass
class TradingConfig:
    entry_z: float = 2.0              # Z-score entry threshold
    exit_z: float = 0.5               # Z-score exit threshold
    stop_z: float = 4.0               # Stop-loss z-score
    lookback_window: int = 60         # Rolling z-score window
    max_position_pct: float = 0.05    # Max 5% per pair
    max_pairs_active: int = 20        # Max simultaneous pairs
    initial_capital: float = 10_000_000.0
    commission_bps: float = 5.0       # 5 bps per side
    slippage_bps: float = 3.0


@dataclass
class KalmanConfig:
    delta: float = 1e-4               # State transition noise
    observation_noise: float = 1.0    # Measurement noise
    initial_state_mean: float = 0.0
    initial_state_cov: float = 1.0


@dataclass
class MonitoringConfig:
    metrics_port: int = 9090
    alert_latency_ms: float = 100.0   # Alert if signal > 100ms
    alert_drawdown_pct: float = 0.10  # Alert at 10% drawdown
    log_level: str = "INFO"
    heartbeat_interval_s: int = 30


@dataclass
class Config:
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    coint: CointegrationConfig = field(default_factory=CointegrationConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    kalman: KalmanConfig = field(default_factory=KalmanConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)


config = Config()
