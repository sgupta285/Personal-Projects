from backtest_engineering.execution import ExecutionParams, TIER_MULTIPLIER


def test_execution_tiers_increase_cost_intensity():
    assert TIER_MULTIPLIER["M5"] > TIER_MULTIPLIER["M1"] > TIER_MULTIPLIER["M0"]


def test_execution_params_constructable():
    params = ExecutionParams(
        tier="M3",
        commission_per_share=0.003,
        spread_bps=2.0,
        route_fee_bps=0.5,
        latency_ms=5.0,
    )
    assert params.tier == "M3"
