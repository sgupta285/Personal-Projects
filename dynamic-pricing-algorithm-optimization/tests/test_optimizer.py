import pandas as pd

from pricing_engine.optimizer import candidate_price_grid


def test_candidate_price_grid_respects_basic_bounds():
    row = pd.Series(
        {
            "price": 100.0,
            "base_price": 110.0,
            "unit_cost": 62.0,
            "competitor_price": 102.0,
            "inventory_pressure": 0.20,
        }
    )
    grid, guardrails = candidate_price_grid(row)
    assert grid.min() >= guardrails["min_price"] - 1e-6
    assert grid.max() <= guardrails["max_price"] + 1e-6
    assert guardrails["min_price"] > row["unit_cost"]
