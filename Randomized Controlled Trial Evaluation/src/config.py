"""Configuration for RCT Evaluation Framework."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DataConfig:
    n_subjects: int = 5000
    treatment_fraction: float = 0.50
    seed: int = 42
    # True treatment effects
    ate: float = 2.5                    # Average Treatment Effect
    late: float = 3.2                   # Local Average Treatment Effect (compliers)
    # Heterogeneous effects
    cate_by_age: Dict[str, float] = field(default_factory=lambda: {
        "young": 3.8, "middle": 2.2, "old": 1.2
    })
    cate_by_severity: Dict[str, float] = field(default_factory=lambda: {
        "mild": 1.5, "moderate": 2.5, "severe": 4.5
    })
    cate_by_gender: Dict[str, float] = field(default_factory=lambda: {
        "male": 2.8, "female": 2.2
    })
    # Non-compliance
    noncompliance_always_taker: float = 0.05   # Control who take treatment
    noncompliance_never_taker: float = 0.08    # Treated who refuse
    # Outcome noise
    outcome_noise_std: float = 8.0
    # Attrition
    attrition_rate: float = 0.06


@dataclass
class EstimationConfig:
    confidence_level: float = 0.95
    n_bootstrap: int = 2000
    n_permutations: int = 5000
    # CUPED
    cuped_pre_metric: str = "pre_outcome"
    # Causal forest
    n_trees: int = 500
    min_leaf_size: int = 50


@dataclass
class DiagnosticsConfig:
    smd_threshold: float = 0.10         # Standardized mean diff threshold
    significance_level: float = 0.05
    multiple_testing: str = "holm"
    min_subgroup_size: int = 100


@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    estimation: EstimationConfig = field(default_factory=EstimationConfig)
    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)
    output_dir: str = "output"


config = Config()
