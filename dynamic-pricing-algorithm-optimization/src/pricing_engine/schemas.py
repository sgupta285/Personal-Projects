from __future__ import annotations

from pydantic import BaseModel


class PricingRequest(BaseModel):
    date: str
    product_id: str
    category: str
    channel: str
    demand_regime: str
    base_price: float
    unit_cost: float
    price: float
    discount_pct: float
    promotion_intensity: float
    competitor_price: float
    competitor_gap_pct: float
    inventory_level: int
    max_inventory: int
    inventory_pressure: float
    seasonality_index: float
    returning_customer_share: float
    page_views: int
    cart_add_rate: float
    conversion_proxy: float
    weekday: int
    month: int
    is_weekend: int
    is_holiday: int
    price_index_vs_base: float
    gross_margin_per_unit: float
    markdown_flag: int
    units_sold_lag_1: float
    units_sold_lag_7: float
    units_sold_rolling_7: float
    price_lag_1: float
    price_change_pct: float


class PricingResponse(BaseModel):
    product_id: str
    current_price: float
    recommended_price: float
    price_change_pct: float
    expected_profit_current: float
    expected_profit_recommended: float
    expected_profit_uplift_pct: float
    expected_units_current: float
    expected_units_recommended: float
    expected_revenue_current: float
    expected_revenue_recommended: float
    guardrails: dict
    explanation: list[str]
