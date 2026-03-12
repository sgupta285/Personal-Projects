# Dynamic Pricing Algorithm Optimization

A production-style pricing engine that recommends prices using demand modeling, competitive context, inventory pressure, seasonality, and channel behavior.

This repo is built to look like a real pricing science project rather than a toy notebook. It generates synthetic transactional data, trains an XGBoost demand model, simulates candidate prices under guardrails, compares model-driven pricing against static pricing in an offline backtest, serves recommendations through FastAPI, and publishes a lightweight dashboard artifact with pricing outcomes.

## What the project does

- builds realistic transaction-level retail pricing data with seasonality, promotions, channel mix, and competitor effects
- engineers elasticity and pricing context features
- trains a demand model to predict units sold at different prices
- optimizes candidate prices for gross profit under practical guardrails
- enforces price floors, maximum daily move limits, inventory-aware constraints, and fairness bands versus competitors
- exports a top recommendation queue and backtest summary
- exposes pricing recommendations through `/recommend-price`
- ships a browser-based dashboard and a notebook for scenario analysis

## Pricing objective

The current optimizer maximizes **expected gross profit** while respecting operational guardrails. Revenue estimates are also produced, but gross profit is the primary decision target because it better reflects practical pricing tradeoffs.

## Architecture

```text
Synthetic transactions -> feature pipeline -> XGBoost demand model
          |                         |                   |
          v                         v                   v
      SQLite store           elasticity context   price simulation
          |                                              |
          +-----------------> recommendation engine <----+
                                   |
                                   v
                          FastAPI + dashboard artifacts
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
make bootstrap
make api
```

Open the API at `http://127.0.0.1:8000` and the browser dashboard at `http://127.0.0.1:8000/dashboard`.

## Main outputs after bootstrap

- `data/raw/product_catalog.csv`
- `data/raw/transactions.csv`
- `data/processed/pricing_features.csv`
- `data/pricing.db`
- `artifacts/model.json`
- `artifacts/metrics.json`
- `artifacts/backtest_summary.json`
- `artifacts/top_recommendations.csv`
- `artifacts/elasticity_report.csv`
- `artifacts/sample_price_curve.csv`
- `dashboard/output/pricing_dashboard.html`
- `dashboard/output/recommendation_snapshot.png`

## API endpoints

- `GET /health`
- `GET /dashboard`
- `GET /backtest-summary`
- `GET /top-recommendations?limit=25`
- `GET /sample-sensitivity`
- `POST /recommend-price`

## Example request

The repo includes `data/sample_request.json`. You can call the API with:

```bash
curl -X POST "http://127.0.0.1:8000/recommend-price" \
  -H "Content-Type: application/json" \
  -d @data/sample_request.json
```

## Dashboard behavior

The dashboard is a lightweight static page served by FastAPI. It reads the generated JSON and CSV artifacts and renders:
- backtest uplift metrics
- recommended price changes
- by-category uplift
- sample sensitivity curve
- latest recommendation queue

## Testing

```bash
make test
```

## Repository layout

```text
dynamic-pricing-algorithm-optimization/
├── api/
├── artifacts/
├── dashboard/
├── data/
├── docs/
├── notebooks/
├── scripts/
├── sql/
├── src/pricing_engine/
└── tests/
```
