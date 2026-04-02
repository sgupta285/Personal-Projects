# Backtest Engineering Framework

A production-minded research and simulation repo for building trading backtests that are harder to fool.

This project is centered on one idea: the biggest gap between a promising strategy and a deployable strategy is usually not the signal itself. It is the engineering around execution realism, cost accounting, statistical discipline, and reproducibility. The framework in this repo is built to make those concerns first-class.

The README source for this project describes a rigorous backtesting system that emphasizes execution realism, transaction costs, proper statistical evaluation, and a six-tier execution model from M0 through M5. It also points to large parameter sweeps, walk-forward testing, and realistic fill simulation rather than optimistic paper trading. This implementation follows that shape closely with a C++ cost-modeling core, a Python research layer, deterministic sample data, and scripts for walk-forward analysis and parameter sweeps.

## What this repo includes

- A **six-tier execution realism ladder** from `M0` to `M5`
- A **Python backtesting engine** for daily-bar strategies
- **Walk-forward optimization** with train/test windows
- **Parameter sweeps** with **Holm-Bonferroni** multiple-testing correction
- A **transaction cost model** that accounts for spread, impact, route fees, latency, and short borrow
- A **C++ cost-modeling core** with tests and a tiny benchmark binary
- Deterministic **sample ETF-like data** covering 2005 to 2025
- Artifact generation for summary JSON, trade logs, fold summaries, and equity curves
- CI, Docker support, and a detailed local run path

## Real-world framing

A lot of backtests look strong because they assume perfect fills, instant execution, and unlimited liquidity. That is not useful once a strategy gets anywhere near production review. This framework is meant for a more skeptical workflow:

1. generate signals
2. convert those signals into target weights
3. simulate turnover and fills under a selected realism tier
4. account for execution drag explicitly
5. validate the strategy using walk-forward splits
6. correct for multiple testing before believing the result

That makes it easier to separate a real edge from a strategy that only works because the backtest was too kind.

## README-aligned scope

This implementation was built to stay aligned with the project description:

- **Category:** Quantitative Finance and Trading Systems
- **Overview:** rigorous backtesting with execution realism, transaction costs, and proper statistical evaluation
- **Key expectations reflected here:** 100K+ style parameter variation support, walk-forward analysis, multiple testing controls, realistic fill prices, and execution simulators that model market microstructure at a practical level
- **Focus areas represented:** backtesting, execution modeling, statistical analysis, quantitative research, transaction costs, and market microstructure
- **Tech stack represented:** C++, Python, NumPy, Pandas, SciPy/statistical tooling, and Matplotlib

## Architecture

```text
                +-------------------------+
                |  configs/*.yaml         |
                +------------+------------+
                             |
                             v
+----------------+   +------+------------------+   +----------------------+
| sample / real  |-->| Python research layer  |-->| artifacts / reports   |
| OHLCV data     |   | signal, PnL, WFO, stats|   | summary, CSV, PNG     |
+----------------+   +------+------------------+   +----------------------+
                             |
                             v
                  +----------+-----------+
                  | execution cost model |
                  | M0 .. M5 realism     |
                  +----------+-----------+
                             |
                             v
                  +----------+-----------+
                  | C++ core and bench   |
                  | cost calc, fill sim  |
                  +----------------------+
```

## Repository layout

```text
backtest-engineering-framework/
├── cpp/
│   ├── include/bef/
│   ├── src/
│   └── tests/
├── python/backtest_engineering/
├── configs/
├── data/sample/
├── scripts/
├── benchmarks/
├── tests/
├── .github/workflows/
├── CMakeLists.txt
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Core design decisions

### 1. Execution realism is explicit, not hidden

The execution ladder is the heart of the repo.

- `M0`: frictionless reference case
- `M1`: commissions and a small portion of quoted spread
- `M2`: wider spread and basic route fee pressure
- `M3`: adds market impact proportional to participation and volatility
- `M4`: includes stronger impact and latency-sensitive slippage
- `M5`: the harshest mode in this repo, representing stressed execution realism

This is intentionally simple enough to run locally but structured enough to reflect the gap between clean research assumptions and harsher production assumptions.

### 2. Walk-forward beats a single in-sample backtest

The repo supports rolling train/test windows so a parameter choice is selected on historical data and then evaluated on a later holdout segment. That is not perfect, but it is much closer to a live research loop than tuning once on the full dataset.

### 3. Multiple testing correction is built into the sweep flow

If you try enough parameter combinations, some will look good by luck alone. The sweep script computes p-values and applies Holm-Bonferroni correction so the ranking is less naive.

### 4. C++ is used where it makes sense

The repo uses C++ for the execution cost core and benchmark path, while Python handles the research workflow. That keeps the project easy to run while still reflecting the C++ + Python split described in the source project summary.

## Data model

The sample dataset is a deterministic synthetic ETF-style daily OHLCV panel.

### Required columns

- `date`
- `ticker`
- `open`
- `high`
- `low`
- `close`
- `volume`

The generator creates multiple ETF-like series with shared market shocks and asset-specific noise so cross-sectional strategies and regime behavior look more realistic than pure random walks.

## Python modules

### `config.py`
Loads YAML config into typed dataclasses.

### `data.py`
Validates and loads historical price data.

### `strategy.py`
Builds a volatility-scaled trend signal using short and long moving averages.

### `execution.py`
Applies the `M0` to `M5` execution model to simulated trades.

### `engine.py`
Runs a single backtest from signals to trade log to portfolio returns.

### `walk_forward.py`
Runs train/test rolling windows, chooses the best in-sample parameter pair, and stitches out-of-sample returns.

### `metrics.py`
Computes annualized return, annualized volatility, Sharpe ratio, max drawdown, t-statistics, p-values, and Holm-Bonferroni adjustments.

### `reporting.py`
Writes summary files and plots the stitched equity curve.

## C++ core

The C++ layer is intentionally focused.

### `cost_model.cpp`
Implements a reusable cost estimator and derived fill price calculation.

### `fill_simulator.cpp`
Wraps the cost model and returns executed price plus cost breakdown.

### `cost_model_bench.cpp`
A simple benchmark binary for repeated fill calculation.

### `test_cost_model.cpp`
A lightweight test binary compiled and run by CTest.

## Configuration

The default quickstart config lives at `configs/momentum_walk_forward.yaml`. A broader sweep with more symbols and a larger parameter grid is available at `configs/research_scale.yaml`.

### Important fields

- `data_path`: CSV for historical data
- `tickers`: symbols to include
- `execution`: realism tier and fee assumptions
- `strategy`: base signal settings
- `walk_forward`: training horizon, test horizon, step size
- `sweep`: parameter candidates
- `initial_capital`: portfolio base
- `output_dir`: artifact destination

## Local setup

### Python path

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Generate sample data

```bash
python scripts/generate_sample_data.py
```

### Run the walk-forward pipeline

```bash
python scripts/run_walk_forward.py --config configs/momentum_walk_forward.yaml
```

### Run the full parameter sweep

```bash
python scripts/parameter_sweep.py --config configs/momentum_walk_forward.yaml
```

### Run the throughput benchmark

```bash
python benchmarks/throughput_benchmark.py
```

## C++ build and test

```bash
cmake -S . -B build
cmake --build build --config Release
ctest --test-dir build --output-on-failure
./build/cost_model_bench
```

## Expected artifacts

After a walk-forward run, the repo writes:

- `artifacts/summary.json`
- `artifacts/walk_forward_folds.csv`
- `artifacts/trade_log.csv`
- `artifacts/equity_curve.png`
- `artifacts/parameter_sweep.csv` when the sweep script is run

## Example output interpretation

### Fold summary

The fold summary shows which parameter pair won in-sample for each window and how it behaved on the following out-of-sample segment.

### Trade log

The trade log includes share count, fill price, and cost drag, which is useful for debugging whether a strategy is dying because the signal is bad or because turnover is too expensive.

### Summary JSON

The summary JSON is meant for reproducibility and automated regression checks in CI or future experiment tracking.

## Reproducibility notes

- Sample data generation uses a fixed seed
- Config is file-driven, not buried in notebook state
- Walk-forward splits are deterministic
- Sweep results are written to disk for later review
- CI regenerates data before tests run

## Statistical safeguards in this implementation

This repo does not pretend to solve all inference problems in quant research, but it does include some practical guardrails:

- train/test separation via walk-forward windows
- p-values based on a simple t-stat approximation
- Holm-Bonferroni adjustment across tested parameter sets
- explicit transaction cost deductions before portfolio summary metrics are reported

## Tradeoffs

- The sample engine uses **daily data**, not tick-level replay, because the goal is a local, runnable framework rather than a market simulator that requires large proprietary datasets
- The execution model is **stylized**, not exchange-specific
- The statistical testing layer is **practical and lightweight**, not a full academic inference package
- The C++ layer focuses on the **cost model path**, while the research orchestration stays in Python for readability and iteration speed

## Limitations

- No corporate actions pipeline is included
- No borrow locate inventory feed is included
- The fill model uses approximations rather than venue-specific queue-position logic
- The strategy library is intentionally small in this repo
- The sample data is synthetic and meant for demonstration and repo verification, not production research

## Docker

A lightweight Docker path is included for reproducible local runs.

```bash
docker build -t backtest-engineering-framework .
docker run --rm backtest-engineering-framework python scripts/run_walk_forward.py
```

## CI

GitHub Actions runs the following on pushes and pull requests:

- Python dependency install
- sample data generation
- Python test suite
- C++ build
- C++ test suite via CTest

## How this repo maps to the source project brief

The source project brief emphasized:

- rigorous backtesting
- execution realism
- transaction costs
- statistical evaluation
- large-scale strategy variation testing
- realistic fill simulation

This repo reflects those priorities directly. It is not a generic finance notebook collection. It is a backtesting repo built to make optimistic assumptions visible and expensive assumptions explicit.
