# Portfolio Rebalancing and Risk Management

A portfolio is easy to describe in a slide deck and surprisingly messy to run day to day. The interesting work is not just calculating weights once. It is watching drift accumulate, understanding whether recent correlation structure changed the portfolio you think you hold, and making a rebalance decision that respects real constraints instead of blindly snapping back to target.

This repository is a compact portfolio management system built around that operating loop. It loads price history, positions, and target allocations, computes daily risk metrics, estimates the current correlation structure, runs a constrained optimizer, and produces a rebalancing plan you can review before trading.

The project is grounded in the README brief for **Portfolio Rebalancing and Risk Management**: automated rebalancing, portfolio-level VaR and CVaR, correlation monitoring, and an optimization engine that traces an efficient frontier under allocation constraints. The implementation stays narrow on purpose. It is not a broker integration or a live OMS. It is the analytics and recommendation layer you would schedule daily, store in PostgreSQL, and hand to a PM or execution workflow. This maps directly to the README brief around portfolio management, risk management, optimization, asset allocation, and quantitative finance using Python, cvxpy, Pandas, NumPy, Jupyter, and PostgreSQL.

## What is in the repo

- Daily portfolio snapshot creation from positions, latest prices, and target allocations
- Drift monitoring in basis points against target weights
- Historical VaR and CVaR from realized portfolio returns
- Correlation matrix generation for current regime inspection
- Constrained minimum-variance optimizer with a turnover cap
- Efficient frontier generation across target return levels
- Rebalancing recommendation output with buy and sell notional values
- Local SQLite persistence for smoke tests, with PostgreSQL schema included for deployment
- Jupyter notebook for quick exploratory analysis
- Tests, demo scripts, CI, Docker, and a lightweight benchmark

## Repository structure

```text
portfolio-rebalancing-risk-management/
├── artifacts/demo/                 # Demo reports written by the CLI
├── benchmarks/                    # Simple performance checks
├── data/raw/                      # Sample prices, targets, positions
├── migrations/sql/                # PostgreSQL schema bootstrap
├── notebooks/                     # Jupyter analysis notebook
├── scripts/                       # Sample data generation and demo entrypoints
├── src/portfolio_risk/            # Core library and CLI
├── tests/                         # Unit tests
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements-lite.txt
└── requirements.txt
```

## Architecture

The runtime has four steps:

1. **Load state** from CSV or warehouse extracts. The repo ships with sample `prices.csv`, `positions.csv`, and `targets.csv` files.
2. **Measure the portfolio** by computing market values, current weights, weight drift, daily portfolio returns, VaR, CVaR, volatility, Sharpe ratio, and cross-asset correlations.
3. **Optimize under constraints** with a minimum-variance objective, no shorting, min and max weights, and a turnover cap. If `cvxpy` is available, the optimizer uses it directly. If not, a fallback inverse-volatility heuristic keeps the local demo runnable.
4. **Write outputs** as JSON and CSV reports, then persist the risk snapshot into a local shadow database or a PostgreSQL-backed deployment.

## Core design decisions

### 1. Keep the system portfolio-centric
The project focuses on a portfolio-level recommendation loop rather than individual security alpha. Inputs are positions and allocations, not signal generation.

### 2. Separate analytics from execution
The repo generates rebalance recommendations but does not fire orders. That keeps the logic auditable and reproducible.

### 3. Make the optimization path honest
The README explicitly called out `cvxpy`. This repo supports that path, but it also includes a fallback so local smoke tests do not depend on an optimization solver being installed everywhere.

### 4. Use PostgreSQL in deployment, SQLite in local smoke tests
The project brief includes PostgreSQL. The schema is included under `migrations/sql`. Local demo runs persist snapshots into a lightweight SQLite shadow database so setup stays fast.

## Sample universe

The sample portfolio includes five liquid ETFs across asset classes:

- `SPY` for US equity
- `AGG` for fixed income
- `GLD` for commodities
- `VNQ` for real estate
- `EFA` for international developed equity

The price history is generated from a correlated synthetic process so the demo is deterministic and reproducible while still producing realistic drift and covariance behavior.

## Environment variables

Copy `.env.example` to `.env` if you want to override defaults.

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | Persistence target | `sqlite:///artifacts/demo/portfolio_local.db` |
| `RISK_FREE_RATE` | Used in Sharpe ratio | `0.02` |
| `VAR_CONFIDENCE` | Historical VaR and CVaR confidence | `0.95` |
| `TRADING_DAYS` | Annualization factor | `252` |
| `MAX_TURNOVER` | Optimization turnover cap | `0.15` |
| `MIN_WEIGHT` | Lower bound per asset | `0.00` |
| `MAX_WEIGHT` | Upper bound per asset | `0.40` |

## Local setup

### Option 1: lightweight local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lite.txt
pip install -e .[dev]
python scripts/generate_sample_data.py
python scripts/run_demo.py
```

### Option 2: full optimizer path

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .[dev,opt,postgres]
python scripts/generate_sample_data.py
python scripts/run_demo.py
```

## How to run

### Generate sample data

```bash
python scripts/generate_sample_data.py
```

### Run the portfolio workflow

```bash
portfolio-risk   --prices data/raw/prices.csv   --positions data/raw/positions.csv   --targets data/raw/targets.csv   --report-dir artifacts/demo
```

### Typical output

The CLI prints a summary payload and writes:

- `artifacts/demo/portfolio_report.json`
- `artifacts/demo/portfolio_snapshot.csv`
- `artifacts/demo/rebalancing_plan.csv`
- `artifacts/demo/portfolio_local.db`

## Data model notes

### `prices.csv`

| column | meaning |
|---|---|
| `date` | trading date |
| `ticker` | asset identifier |
| `close` | end-of-day close |

### `positions.csv`

| column | meaning |
|---|---|
| `ticker` | asset identifier |
| `shares` | shares currently held |
| `lot_cost` | simple cost basis field used for bookkeeping |

### `targets.csv`

| column | meaning |
|---|---|
| `ticker` | asset identifier |
| `asset_class` | reporting bucket |
| `target_weight` | target portfolio weight |

## Risk metrics

The daily report includes:

- **Historical VaR** at the configured confidence level
- **Historical CVaR** from the tail beyond VaR
- **Annualized volatility** from realized daily returns
- **Sharpe ratio** using the configured risk-free rate
- **Correlation matrix** for the latest return history

This intentionally matches the README emphasis on portfolio-level risk metrics and correlation structure updates. fileciteturn25file3

## Optimization notes

The optimizer solves a constrained minimum-variance problem:

- full investment, weights sum to 1
- long-only bounds
- per-asset min and max weights
- turnover cap against current weights

The efficient frontier module sweeps target return levels and solves a minimum-variance problem at each point. In lightweight environments where `cvxpy` is missing, the repo falls back to a normalized inverse-volatility heuristic. That fallback is not presented as mathematically equivalent. It exists so the rest of the system remains runnable and testable.

## Persistence and deployment notes

The deployment path assumes PostgreSQL. A bootstrap schema is included under `migrations/sql/001_schema.sql` for:

- `price_history`
- `target_allocations`
- `positions`
- `risk_snapshots`

For local smoke tests, the code writes snapshots into a SQLite file under `artifacts/demo/`.

To bring up the demo stack with PostgreSQL:

```bash
docker compose up --build
```

## Benchmarking

A lightweight benchmark is included to time repeated risk snapshot calculations.

```bash
python benchmarks/benchmark_risk.py
```

This is not a microsecond-level HFT benchmark. It is meant to catch obvious regressions in core analytics code.

## Testing

Run the unit tests with:

```bash
pytest
```

The tests cover:

- risk metric sanity checks
- optimizer weight normalization
- correlation matrix structure
- rebalance recommendation labeling

## Notebook workflow

Open `notebooks/portfolio_analysis.ipynb` after generating the sample data. It mirrors the CLI path and is useful for inspection or quick extensions.

## Reproducibility notes

- Sample data generation is seeded
- The CLI consumes plain CSV inputs
- Report outputs are written deterministically from those inputs
- The fallback optimizer is deterministic
- CI regenerates sample data on each run before testing

## Limitations

A few things are intentionally out of scope:

- no broker connectivity
- no tax-lot-aware optimization
- no transaction cost model beyond turnover control
- no intraday pricing or live market data
- no stress testing against historical crash windows

That keeps the project aligned with the README brief instead of pretending to be a full portfolio OMS.
