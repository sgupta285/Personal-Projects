from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json
import yaml


@dataclass(slots=True)
class DataConfig:
    n_units: int = 40
    n_periods: int = 24
    seed: int = 42
    treated_share: float = 0.25
    treatment_start: int = 14
    policy_effect: float = 2.25
    violating_units: int = 2
    output_path: str = "data/sample/panel.csv"


@dataclass(slots=True)
class AnalysisConfig:
    outcome_col: str = "outcome"
    unit_col: str = "unit_id"
    time_col: str = "time_id"
    treated_col: str = "treated"
    post_col: str = "post"
    ever_treated_col: str = "ever_treated"
    treatment_time_col: str = "treatment_time"
    cohort_col: str = "treatment_cohort"
    cluster_col: str = "unit_id"
    placebo_shift: int = 4
    pre_periods_for_parallel_trends: int = 6
    min_pre_periods_for_synth: int = 8
    output_dir: str = "artifacts"


@dataclass(slots=True)
class BenchmarkConfig:
    replications: int = 3
    seed: int = 123
    output_path: str = "artifacts/benchmarks/benchmark_results.json"


@dataclass(slots=True)
class ProjectConfig:
    data: DataConfig = field(default_factory=DataConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)

    @classmethod
    def from_file(cls, path: str | Path) -> "ProjectConfig":
        raw_path = Path(path)
        payload = yaml.safe_load(raw_path.read_text()) if raw_path.suffix in {".yml", ".yaml"} else json.loads(raw_path.read_text())
        return cls(
            data=DataConfig(**payload.get("data", {})),
            analysis=AnalysisConfig(**payload.get("analysis", {})),
            benchmark=BenchmarkConfig(**payload.get("benchmark", {})),
        )

    def to_dict(self) -> dict:
        return asdict(self)
