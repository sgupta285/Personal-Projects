from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from did_lab.config import DataConfig


REGIONS = [
    "Northeast",
    "Midwest",
    "South",
    "West",
]


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def generate_sample_panel(config: DataConfig) -> pd.DataFrame:
    rng = np.random.default_rng(config.seed)
    units = [f"unit_{idx:03d}" for idx in range(config.n_units)]
    treated_count = max(1, int(round(config.n_units * config.treated_share)))
    treated_units = set(rng.choice(units, size=treated_count, replace=False).tolist())
    violating_units = set(list(treated_units)[: min(config.violating_units, treated_count)])

    unit_fe = {u: rng.normal(0.0, 1.2) for u in units}
    covariate_base = {u: rng.normal(0.0, 1.0) for u in units}
    unit_population = {u: int(rng.integers(30_000, 2_000_000)) for u in units}
    region_lookup = {u: REGIONS[idx % len(REGIONS)] for idx, u in enumerate(units)}

    rows = []
    for unit_idx, unit in enumerate(units):
        ever_treated = int(unit in treated_units)
        pretrend_slope = 0.18 if unit in violating_units else 0.0
        for t in range(config.n_periods):
            post = int(ever_treated == 1 and t >= config.treatment_start)
            treatment_time = t - config.treatment_start if ever_treated else np.nan
            macro_shock = np.sin(t / 2.8) + 0.12 * t
            seasonality = 0.5 * np.cos(t / 3.0 + unit_idx / 8)
            covariate = covariate_base[unit] + 0.15 * t + rng.normal(0.0, 0.35)
            adoption_pressure = _sigmoid(np.array([covariate + 0.4 * ever_treated]))[0]
            heterogeneous_effect = config.policy_effect * (0.8 + 0.35 * adoption_pressure)
            anticipation = 0.35 * ever_treated if t == config.treatment_start - 1 else 0.0
            outcome = (
                15.0
                + unit_fe[unit]
                + macro_shock
                + seasonality
                + 0.65 * covariate
                + pretrend_slope * t
                + heterogeneous_effect * post
                + anticipation
                + rng.normal(0.0, 0.7)
            )
            rows.append(
                {
                    "unit_id": unit,
                    "time_id": t,
                    "calendar_period": pd.Period("2019Q1", freq="Q") + t,
                    "region": region_lookup[unit],
                    "population": unit_population[unit],
                    "covariate": covariate,
                    "treated": post,
                    "post": int(t >= config.treatment_start),
                    "ever_treated": ever_treated,
                    "treatment_time": treatment_time,
                    "treatment_cohort": config.treatment_start if ever_treated else -1,
                    "parallel_trend_violation": int(unit in violating_units),
                    "outcome": outcome,
                }
            )
    frame = pd.DataFrame(rows)
    frame["calendar_period"] = frame["calendar_period"].astype(str)
    return frame.sort_values(["unit_id", "time_id"]).reset_index(drop=True)


def save_panel(frame: pd.DataFrame, path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(out_path, index=False)
    return out_path


def load_panel(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    return frame


def panel_summary(frame: pd.DataFrame) -> dict:
    return {
        "n_rows": int(frame.shape[0]),
        "n_units": int(frame["unit_id"].nunique()),
        "n_periods": int(frame["time_id"].nunique()),
        "treated_units": int(frame.loc[frame["ever_treated"] == 1, "unit_id"].nunique()),
        "control_units": int(frame.loc[frame["ever_treated"] == 0, "unit_id"].nunique()),
        "treatment_start": int(frame.loc[frame["ever_treated"] == 1, "treatment_cohort"].replace(-1, np.nan).dropna().min()),
    }
