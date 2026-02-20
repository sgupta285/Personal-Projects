"""Configuration for Retail Demand Forecasting System."""

from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class DataConfig:
    n_stores: int = 10
    n_products: int = 50
    n_days: int = 1095          # 3 years
    start_date: str = "2021-01-01"
    train_pct: float = 0.75
    val_pct: float = 0.10
    test_pct: float = 0.15
    seed: int = 42


@dataclass
class FeatureConfig:
    lag_days: List[int] = field(default_factory=lambda: [1, 7, 14, 28])
    rolling_windows: List[int] = field(default_factory=lambda: [7, 14, 28, 56])
    ewm_spans: List[int] = field(default_factory=lambda: [7, 28])
    fourier_order: int = 3
    include_holidays: bool = True
    include_weather: bool = True
    include_promotions: bool = True


@dataclass
class ModelConfig:
    # SARIMA
    sarima_order: tuple = (1, 1, 1)
    sarima_seasonal: tuple = (1, 1, 1, 7)  # Weekly seasonality

    # XGBoost / LightGBM
    xgb_n_estimators: int = 500
    xgb_max_depth: int = 6
    xgb_learning_rate: float = 0.05
    lgb_n_estimators: int = 500
    lgb_num_leaves: int = 31
    lgb_learning_rate: float = 0.05

    # Prophet
    prophet_changepoint_prior: float = 0.05
    prophet_seasonality_prior: float = 10.0

    # Ensemble
    ensemble_weights: dict = field(default_factory=lambda: {
        "xgboost": 0.35, "lightgbm": 0.35, "prophet": 0.20, "sarima": 0.10
    })

    # Walk-forward
    wf_train_days: int = 365
    wf_test_days: int = 28
    wf_step_days: int = 28


@dataclass
class DatabaseConfig:
    host: str = os.getenv("DF_DB_HOST", "localhost")
    port: int = int(os.getenv("DF_DB_PORT", "5432"))
    name: str = os.getenv("DF_DB_NAME", "demand_forecast")
    user: str = os.getenv("DF_DB_USER", "df_user")
    password: str = os.getenv("DF_DB_PASSWORD", "df_pass")

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    output_dir: str = "output"


config = Config()
