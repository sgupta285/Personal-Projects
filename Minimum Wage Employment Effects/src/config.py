"""Configuration for Minimum Wage Employment Effects Analysis."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DataConfig:
    n_states: int = 50
    n_quarters: int = 40          # 10 years quarterly
    start_year: int = 2014
    seed: int = 42
    # Treatment: states that raise minimum wage
    n_treated_states: int = 12
    treatment_quarter: int = 20   # Policy change at midpoint
    # True causal effect (for validation)
    true_employment_effect: float = -0.012   # -1.2% employment
    true_wage_effect: float = 0.045          # +4.5% wages
    true_hours_effect: float = -0.018        # -1.8% hours


@dataclass
class ModelConfig:
    # Difference-in-Differences
    cluster_se: bool = True
    include_state_fe: bool = True
    include_time_fe: bool = True

    # Event Study
    pre_periods: int = 8
    post_periods: int = 12
    reference_period: int = -1     # Period before treatment

    # Synthetic Control
    sc_pre_periods: int = 20
    sc_optimization: str = "nnls"  # Non-negative least squares

    # Regression Discontinuity
    rd_bandwidth: float = 1.50     # $/hr around threshold
    rd_polynomial: int = 1         # Local linear


@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    output_dir: str = "output"


config = Config()
