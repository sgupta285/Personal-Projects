from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from pricing_engine.features import align_model_frame, model_input_frame


@dataclass(slots=True)
class Recommendation:
    product_id: str
    current_price: float
    recommended_price: float
    expected_units_current: float
    expected_units_recommended: float
    expected_revenue_current: float
    expected_revenue_recommended: float
    expected_profit_current: float
    expected_profit_recommended: float
    expected_profit_uplift_pct: float
    price_change_pct: float
    guardrails: dict
    explanation: list[str]


def candidate_price_grid(row: pd.Series) -> tuple[np.ndarray, dict]:
    current = float(row["price"])
    base_price = float(row["base_price"])
    unit_cost = float(row["unit_cost"])
    competitor = float(row["competitor_price"])
    low = max(unit_cost * 1.08, base_price * 0.85, current * 0.80)
    high = min(base_price * 1.25, competitor * 1.15, current * 1.20)

    if float(row["inventory_pressure"]) > 0.75:
        low = max(low, current)

    if high <= low:
        high = low * 1.06

    grid = np.linspace(low, high, 11)
    guardrails = {
        "min_price": round(float(low), 2),
        "max_price": round(float(high), 2),
        "fairness_cap_vs_competitor": round(float(competitor * 1.15), 2),
        "floor_above_cost": round(float(unit_cost * 1.08), 2),
    }
    return grid, guardrails


def _candidate_frame(row: pd.Series, grid: np.ndarray) -> pd.DataFrame:
    records = []
    for candidate_price in grid:
        payload = row.to_dict()
        payload["price"] = round(float(candidate_price), 2)
        payload["discount_pct"] = max(0.0, 1 - payload["price"] / max(payload["base_price"], 0.01))
        payload["promotion_intensity"] = payload["discount_pct"]
        payload["competitor_gap_pct"] = (payload["price"] - payload["competitor_price"]) / max(payload["competitor_price"], 0.01)
        payload["gross_margin_per_unit"] = payload["price"] - payload["unit_cost"]
        payload["price_index_vs_base"] = payload["price"] / max(payload["base_price"], 0.01)
        payload["price_change_pct"] = (payload["price"] - payload["price_lag_1"]) / max(payload["price_lag_1"], 0.01)
        records.append(payload)
    return pd.DataFrame(records)


def price_curve(row: pd.Series, model, metadata: dict) -> tuple[pd.DataFrame, dict]:
    grid, guardrails = candidate_price_grid(row)
    candidates = _candidate_frame(row, grid)
    model_frame = model_input_frame(candidates)
    aligned = align_model_frame(model_frame, metadata["feature_columns"])
    predictions = np.maximum(model.predict(aligned), 0.0)
    predictions = np.minimum(predictions, float(row["inventory_level"]))

    curve = pd.DataFrame(
        {
            "candidate_price": np.round(grid, 2),
            "predicted_units": np.round(predictions, 4),
        }
    )
    curve["expected_revenue"] = np.round(curve["candidate_price"] * curve["predicted_units"], 4)
    curve["expected_profit"] = np.round(
        np.maximum(curve["candidate_price"] - float(row["unit_cost"]), 0.0) * curve["predicted_units"], 4
    )
    return curve, guardrails


def recommend_for_row(row: pd.Series, model, metadata: dict) -> Recommendation:
    curve, guardrails = price_curve(row, model, metadata)
    best = curve.sort_values("expected_profit", ascending=False).iloc[0]
    current_match = curve.iloc[(curve["candidate_price"] - float(row["price"])).abs().argsort()[:1]].iloc[0]

    recommended_price = float(best["candidate_price"])
    recommended_units = float(best["predicted_units"])
    recommended_revenue = float(best["expected_revenue"])
    recommended_profit = float(best["expected_profit"])
    current_units = float(current_match["predicted_units"])
    current_revenue = float(current_match["expected_revenue"])
    current_profit = float(current_match["expected_profit"])

    uplift = 0.0
    if current_profit > 0:
        uplift = (recommended_profit - current_profit) / current_profit * 100

    explanations = []
    if float(row["inventory_pressure"]) > 0.70 and recommended_price >= float(row["price"]):
        explanations.append("Inventory is tight, so the optimizer protects margin instead of chasing volume.")
    if float(row["competitor_price"]) < float(row["price"]) and recommended_price <= float(row["price"]):
        explanations.append("Competitor pricing is below current, so the recommendation narrows the price gap.")
    if str(row["demand_regime"]) == "peak" and recommended_price >= float(row["price"]):
        explanations.append("Demand is in a stronger regime, which supports a higher price point.")
    if float(row["promotion_intensity"]) > 0.18 and recommended_price > float(row["price"]):
        explanations.append("Current discounting is deeper than needed for expected demand at this context.")
    explanations.append(
        f"Guardrails keep the recommendation between {guardrails['min_price']:.2f} and {guardrails['max_price']:.2f}."
    )

    return Recommendation(
        product_id=str(row["product_id"]),
        current_price=round(float(row["price"]), 2),
        recommended_price=round(recommended_price, 2),
        expected_units_current=round(float(current_units), 3),
        expected_units_recommended=round(recommended_units, 3),
        expected_revenue_current=round(float(current_revenue), 2),
        expected_revenue_recommended=round(recommended_revenue, 2),
        expected_profit_current=round(float(current_profit), 2),
        expected_profit_recommended=round(recommended_profit, 2),
        expected_profit_uplift_pct=round(float(uplift), 2),
        price_change_pct=round((recommended_price - float(row["price"])) / max(float(row["price"]), 0.01) * 100, 2),
        guardrails=guardrails,
        explanation=explanations,
    )
