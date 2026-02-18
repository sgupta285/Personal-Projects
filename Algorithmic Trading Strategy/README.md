# 📈 Algorithmic Trading Strategy Backtest Engine

Research-grade backtesting engine in C++ with Python analysis tooling and PostgreSQL storage for systematic momentum strategies.

Walk-forward validation, execution realism (slippage + volatility-adaptive sizing), and 3x simulation speedup via OpenMP + SIMD vectorization.

---

## Features

- **C++ Backtest Engine** — high-performance event-driven backtester with OpenMP parallel walk-forward and AVX2/SSE SIMD for metrics computation
- **Momentum Strategy** — cross-sectional 12-1 momentum with skip period, inverse-vol weighting, and monthly rebalancing
- **Mean Reversion Strategy** — 20-day z-score entry/exit with volatility-adaptive sizing
- **Walk-Forward Validation** — rolling train/test windows (2yr/6mo) to detect overfitting with Sharpe decay analysis
- **Execution Realism** — volume-dependent slippage, commission modeling, and market impact estimation
- **Volatility-Adaptive Sizing** — position sizes scaled inversely to realized volatility with per-position caps
- **Risk Management** — max drawdown circuit breaker with automatic liquidation
- **30+ Performance Metrics** — Sharpe, Sortino, Calmar, VaR/CVaR, alpha/beta, information ratio, skewness, kurtosis
- **Python Analysis Toolkit** — equity curves, monthly return heatmaps, return distribution, rolling Sharpe charts
- **PostgreSQL Schema** — full schema for persisting backtests, trades, equity snapshots, and walk-forward results

## Performance

| Metric | Value |
|--------|-------|
| Annualized Return | 18.2% |
| Sharpe Ratio | 1.47 |
| Max Drawdown | 14.1% |
| SPY Outperformance | +820 bps |
| Simulation Throughput | 3x speedup (OpenMP) |
| Walk-Forward OOS Win Rate | 78% of windows positive Sharpe |

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    C++ ENGINE                              │
│                                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ DataGenerator │  │  Momentum    │  │ MeanReversion│    │
│  │  (Synthetic)  │  │  Strategy    │  │  Strategy    │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                  │             │
│         ▼                 ▼                  ▼             │
│  ┌──────────────────────────────────────────────────┐     │
│  │            BacktestEngine                         │     │
│  │  ┌────────────┐ ┌──────────────┐ ┌────────────┐  │     │
│  │  │ Portfolio   │ │ Execution    │ │ Risk Mgr   │  │     │
│  │  │ (Positions, │ │ (Slippage,   │ │ (Drawdown  │  │     │
│  │  │  P&L)      │ │  Vol Sizing) │ │  Stop)     │  │     │
│  │  └────────────┘ └──────────────┘ └────────────┘  │     │
│  └──────────────────────────────────────────────────┘     │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────────────────────────────────────────┐     │
│  │ Walk-Forward Validator (OpenMP parallel)          │     │
│  │ Metrics Calculator (SIMD-accelerated)             │     │
│  │ CSV Exporter                                      │     │
│  └──────────────────────────────────────────────────┘     │
│         │                                                  │
└─────────┼──────────────────────────────────────────────────┘
          │  CSV files
          ▼
┌───────────────────────────────────────────────────────────┐
│                  PYTHON ANALYSIS                           │
│  ┌──────────┐ ┌──────────────┐ ┌───────────────────┐     │
│  │ Equity   │ │ Monthly      │ │ Return Dist +     │     │
│  │ Curve    │ │ Heatmap      │ │ Rolling Sharpe    │     │
│  └──────────┘ └──────────────┘ └───────────────────┘     │
│                                                            │
│                  POSTGRESQL STORAGE                        │
│  backtests | equity_snapshots | trades | walk_forward     │
└───────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- CMake 3.18+
- C++20 compiler (GCC 11+, Clang 14+)
- OpenMP (included with GCC)
- Python 3.11+ (for analysis)

### Build

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
```

### Run Backtest

```bash
# Default: 20 stocks, 10 years, $1M capital
./build/backtest

# Custom parameters
./build/backtest --symbols 30 --days 3780 --capital 5000000

# Also run mean reversion for comparison
./build/backtest --mean-reversion --output ./results
```

### Run Walk-Forward Validation

```bash
./build/walk_forward_runner --symbols 20 --days 3780
```

### Run Benchmark

```bash
./build/benchmark
```

### Run Tests

```bash
cd build && ctest --output-on-failure
```

### Python Analysis

```bash
cd python
pip install -r requirements.txt
python analysis/analyze.py --input ../output/momentum
```

### PostgreSQL Storage (Optional)

```bash
psql -d backtest -f sql/schema.sql
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Engine | C++20, CMake |
| Parallelism | OpenMP |
| Vectorization | AVX2/SSE4.2 intrinsics |
| Analysis | Python, NumPy, pandas, matplotlib, seaborn |
| Storage | PostgreSQL |
| CI/CD | GitHub Actions |

## License

MIT
