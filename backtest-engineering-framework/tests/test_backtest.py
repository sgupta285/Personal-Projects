from pathlib import Path

from backtest_engineering.data import load_prices
from backtest_engineering.engine import run_backtest
from backtest_engineering.execution import ExecutionParams
from backtest_engineering.walk_forward import run_walk_forward


DATA_PATH = Path("data/sample/us_etf_sample.csv")


def test_single_backtest_runs():
    prices = load_prices(DATA_PATH, ["SPY", "QQQ", "IWM"])
    result = run_backtest(
        prices,
        ExecutionParams(
            tier="M3",
            commission_per_share=0.0035,
            spread_bps=3.0,
            route_fee_bps=0.5,
            latency_ms=7.0,
        ),
        short_window=10,
        long_window=40,
        volatility_lookback=20,
        target_gross_leverage=1.0,
        initial_capital=100000.0,
    )
    assert len(result.portfolio_returns) > 100
    assert "sharpe_ratio" in result.summary
    assert result.summary["transaction_cost_dollars"] >= 0.0


def test_walk_forward_produces_multiple_folds():
    prices = load_prices(DATA_PATH, ["SPY", "QQQ", "IWM"])
    output = run_walk_forward(
        prices,
        ExecutionParams(
            tier="M4",
            commission_per_share=0.0035,
            spread_bps=3.0,
            route_fee_bps=0.5,
            latency_ms=7.0,
        ),
        sweep_short_windows=[10, 15],
        sweep_long_windows=[40, 60],
        volatility_lookback=20,
        target_gross_leverage=1.0,
        train_days=252,
        test_days=63,
        step_days=63,
        initial_capital=100000.0,
    )
    assert len(output.fold_results) >= 2
    assert len(output.stitched_result.trade_log) > 0
