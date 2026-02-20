"""Configuration for Demand Elasticity Analysis."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DataConfig:
    n_products: int = 8
    n_stores: int = 5
    n_weeks: int = 156          # 3 years weekly
    seed: int = 42
    # True elasticities (for validation)
    base_own_elasticity: float = -1.8   # Elastic demand
    cross_elasticity_range: tuple = (0.05, 0.40)  # Substitutes
    # Price variation
    promo_frequency: float = 0.20       # 20% of weeks on promo
    promo_discount_range: tuple = (0.10, 0.30)


@dataclass
class ModelConfig:
    # Log-log OLS
    include_controls: bool = True       # Seasonality, store FE
    cluster_se: bool = True             # Cluster standard errors by store

    # Instrumental Variables
    iv_instrument: str = "cost_shock"   # Supply-side cost instrument
    iv_first_stage_f_min: float = 10.0  # Weak instrument threshold

    # Optimal pricing
    marginal_cost_pct: float = 0.45     # Cost = 45% of base price
    price_grid_points: int = 50


@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    output_dir: str = "output"


config = Config()
