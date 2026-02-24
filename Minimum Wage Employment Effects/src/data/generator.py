"""
Synthetic State-Level Panel Data Generator.

Generates quarterly state-level data for minimum wage employment analysis:
- 50 states, 40 quarters (10 years)
- Staggered treatment: 12 states raise minimum wage at quarter 20
- Employment, average wages, hours worked, restaurant employment
- State fixed effects, time trends, business cycle, known causal effects
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
import structlog

from src.config import config

logger = structlog.get_logger()

STATE_NAMES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California",
    "Colorado", "Connecticut", "Delaware", "Florida", "Georgia",
    "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri",
    "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
    "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming",
]


def generate_panel_data(
    n_states: int = 50,
    n_quarters: int = 40,
    seed: int = 42,
) -> Tuple[pd.DataFrame, Dict]:
    """
    Generate synthetic state-quarter panel with known treatment effects.

    Returns:
        panel_df: State-quarter panel (state, quarter, employment, wages, ...)
        true_params: Dictionary of true causal parameters
    """
    np.random.seed(seed)
    cfg = config.data

    states = STATE_NAMES[:n_states]
    quarters = list(range(n_quarters))

    # Select treated states
    treated_idx = np.random.choice(n_states, cfg.n_treated_states, replace=False)
    treated_states = set(np.array(states)[treated_idx])

    # State-level parameters
    state_fe = np.random.randn(n_states) * 3            # State fixed effects
    state_trend = np.random.uniform(-0.002, 0.004, n_states)  # State-specific trends
    state_base_emp = np.random.uniform(0.90, 0.97, n_states)  # Base employment rate
    state_base_wage = np.random.uniform(9.0, 16.0, n_states)  # Base hourly wage
    state_base_hours = np.random.uniform(32, 40, n_states)     # Base weekly hours

    # Business cycle (common shock)
    cycle = 0.02 * np.sin(2 * np.pi * np.arange(n_quarters) / 16)
    # Add a recession
    cycle[8:14] -= 0.015

    records = []
    for s, state in enumerate(states):
        is_treated = state in treated_states
        min_wage_base = np.random.uniform(7.25, 10.50)

        for t in quarters:
            year = cfg.start_year + t // 4
            q = t % 4 + 1

            # Time effects
            time_trend = state_trend[s] * t
            business_cycle = cycle[t]

            # Treatment indicator
            post = int(t >= cfg.treatment_quarter)
            treat = int(is_treated)
            did = treat * post

            # Minimum wage
            if is_treated and t >= cfg.treatment_quarter:
                min_wage = min_wage_base + 2.50  # $2.50 increase
            else:
                min_wage = min_wage_base + 0.10 * (t / n_quarters)  # Small inflation adj

            # --- Employment rate ---
            emp = (state_base_emp[s]
                   + state_fe[s] * 0.005
                   + time_trend
                   + business_cycle
                   + did * cfg.true_employment_effect
                   + np.random.randn() * 0.008)
            emp = np.clip(emp, 0.80, 0.99)

            # --- Average wage ---
            wage = (state_base_wage[s]
                    + 0.15 * t / n_quarters  # Wage growth
                    + state_fe[s] * 0.2
                    + did * cfg.true_wage_effect * state_base_wage[s]
                    + np.random.randn() * 0.30)
            wage = max(7.25, wage)

            # --- Hours worked ---
            hours = (state_base_hours[s]
                     + state_fe[s] * 0.1
                     + business_cycle * 10
                     + did * cfg.true_hours_effect * state_base_hours[s]
                     + np.random.randn() * 1.2)
            hours = np.clip(hours, 20, 45)

            # --- Restaurant employment (more affected sector) ---
            rest_emp = (state_base_emp[s] * 0.95
                        + time_trend * 0.8
                        + business_cycle * 1.3
                        + did * cfg.true_employment_effect * 1.8  # Larger effect
                        + np.random.randn() * 0.012)
            rest_emp = np.clip(rest_emp, 0.75, 0.99)

            # --- Teen employment (most affected) ---
            teen_emp = (state_base_emp[s] * 0.85
                        + time_trend * 0.5
                        + business_cycle * 2.0
                        + did * cfg.true_employment_effect * 2.5
                        + np.random.randn() * 0.020)
            teen_emp = np.clip(teen_emp, 0.60, 0.95)

            # Population and GDP controls
            pop = np.random.lognormal(14.5 + state_fe[s] * 0.05, 0.7)
            gdp_pc = 40000 + state_fe[s] * 3000 + t * 200 + np.random.randn() * 2000

            records.append({
                "state": state,
                "state_id": s,
                "quarter": t,
                "year": year,
                "q": q,
                "year_quarter": f"{year}Q{q}",
                "treated": treat,
                "post": post,
                "did": did,
                "min_wage": round(min_wage, 2),
                "employment_rate": round(emp, 4),
                "avg_wage": round(wage, 2),
                "avg_hours": round(hours, 1),
                "restaurant_emp": round(rest_emp, 4),
                "teen_emp": round(teen_emp, 4),
                "log_emp": round(np.log(emp), 4),
                "log_wage": round(np.log(wage), 4),
                "population": int(pop),
                "gdp_per_capita": round(gdp_pc, 0),
            })

    panel_df = pd.DataFrame(records)

    true_params = {
        "employment_effect": cfg.true_employment_effect,
        "wage_effect": cfg.true_wage_effect,
        "hours_effect": cfg.true_hours_effect,
        "n_treated": cfg.n_treated_states,
        "n_control": n_states - cfg.n_treated_states,
        "treatment_quarter": cfg.treatment_quarter,
        "treated_states": sorted(treated_states),
    }

    logger.info("panel_generated", states=n_states, quarters=n_quarters,
                treated=cfg.n_treated_states, true_emp_effect=cfg.true_employment_effect)

    return panel_df, true_params
