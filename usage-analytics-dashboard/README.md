# Usage Analytics Dashboard

A customer-facing analytics dashboard for usage-based products, built around the exact scope implied by the portfolio README: interactive visualizations, real-time-ish API access to precomputed aggregations, PostgreSQL-backed rollups, Redis caching, and export flows for CSV and PDF reporting. The project is intentionally focused on transparency into consumption patterns, not on building a generic internal BI suite.

The repo is split into a FastAPI backend and a React + TypeScript frontend. The backend owns raw usage ingestion, precomputed rollups, summary and drill-down APIs, caching, and reporting exports. The frontend turns those APIs into a dashboard that supports interval changes, breakdown pivots, and customer-friendly KPI views.

## Why this repo exists

The portfolio README describes a dashboard serving 10K+ users with custom date ranges, drill-down analysis, flexible aggregation, PDF and CSV export, materialized views, and Redis caching. This implementation takes those requirements literally and turns them into a runnable repo with production-minded structure, but without padding the scope with unrelated features.

## README-backed build spec

From the uploaded README, this project is defined by the following requirements:

- Customer-facing analytics dashboard for usage metrics, trends, and insights.
- Interactive visualizations with line charts, bar charts, heatmap-style breakdowns, and custom metrics.
- FastAPI backend serving aggregated data from PostgreSQL with query optimization and pagination-oriented design.
- Precomputed aggregations and materialized-view-style refreshes to reduce time-to-insight.
- Redis caching for frequently accessed date ranges and metric combinations.
- Export support for CSV and PDF.
- Tech stack centered on React, TypeScript, Python, FastAPI, PostgreSQL, Redis, Recharts, and Docker.

## Architecture

```text
usage_events.csv / production event stream
            |
            v
    FastAPI ingest + seed scripts
            |
            v
  usage_events table in PostgreSQL or SQLite fallback
            |
            +--> refresh_rollups.py
            |         |
            |         v
            |   usage_rollups table
            |   and optional PostgreSQL materialized views
            |
            +--> /usage/summary
            +--> /usage/breakdown
            +--> /usage/export.csv
            +--> /usage/export.pdf
            +--> /metric-catalog
                        |
                        v
               React + Recharts frontend
```

## What is included

- **Backend API** with summary, breakdown, export, health, metrics, and metadata endpoints.
- **Rollup refresh flow** that simulates incremental materialized-view refreshes using a durable rollup table.
- **Sample data generation** spanning multiple customers, endpoints, features, regions, and plans.
- **Frontend dashboard** built with React, TypeScript, and Recharts.
- **Redis-aware caching layer** with in-memory fallback for lightweight development.
- **Prometheus metrics endpoint** for request rates, latency, and cache hit visibility.
- **Docker Compose stack** for backend, frontend, PostgreSQL, and Redis.
- **Kubernetes manifests** for the API deployment path.
- **Backend tests and smoke scripts** for quick verification.

## Folder structure

```text
usage-analytics-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── repositories/
│   │   └── services/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   └── lib/
│   ├── Dockerfile
│   └── package.json
├── configs/
├── data/
├── infra/
├── sql/
├── docker-compose.yml
└── Makefile
```

## Core features

### 1. Usage rollups with interval control

The API supports `hour`, `day`, and `month` intervals through a single rollup model. This mirrors the README requirement to serve multiple aggregation levels without forcing expensive calculations on every request.

### 2. Drill-down analysis

Breakdown endpoints support grouping by feature, endpoint, region, plan, and status class. That gives customers a way to understand not just how much they used, but where the consumption came from.

### 3. Export workflows

- `GET /usage/export.csv` returns time-series data for spreadsheet-friendly analysis.
- `GET /usage/export.pdf` returns a customer report with summary totals and breakdown rows.

### 4. Caching for repeated queries

A lot of customer behavior in dashboards is repetitive. Teams reopen the same billing range or compare the same month several times. The cache layer stores common summaries and breakdowns, backed by Redis when available.

### 5. Observability hooks

The backend exposes `/metrics` in Prometheus format and records:

- request counts by path and status code
- request latency histograms
- cache hits and misses by endpoint

## Data model

### `usage_events`

Raw fact table for customer usage activity.

| Column | Meaning |
|---|---|
| `workspace_id` | Customer workspace slug |
| `customer_name` | Human-readable customer name |
| `event_time` | Timestamp of activity |
| `endpoint` | API route or product action |
| `feature` | Product capability driving usage |
| `region` | Region handling the request |
| `plan` | Billing tier |
| `status_class` | Status-code family |
| `request_units` | Raw usage units |
| `billable_units` | Billable version of usage |
| `cost_usd` | Modeled cost |
| `latency_ms` | Observed request latency |
| `export_count` | Number of exports triggered |

### `usage_rollups`

Precomputed aggregates keyed by workspace, bucket, interval, metric family, and group value.

This is the main serving table for dashboard reads in local development.

## API summary

### `GET /metric-catalog`
Returns supported intervals, dimensions, metrics, and discovered workspaces.

### `GET /usage/summary`
Example:

```bash
curl "http://localhost:8000/usage/summary?workspace_id=acme-cloud&interval=day"
```

### `GET /usage/breakdown`
Example:

```bash
curl "http://localhost:8000/usage/breakdown?workspace_id=acme-cloud&interval=day&dimension=feature"
```

### `GET /usage/export.csv`
Example:

```bash
curl -OJ "http://localhost:8000/usage/export.csv?workspace_id=acme-cloud&interval=month"
```

### `GET /usage/export.pdf`
Example:

```bash
curl -OJ "http://localhost:8000/usage/export.pdf?workspace_id=acme-cloud&interval=month&dimension=plan"
```

### `GET /metrics`
Prometheus-compatible metrics endpoint.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed_usage_data.py
python scripts/refresh_rollups.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Full stack with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

## Environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string |
| `REDIS_URL` | Optional Redis cache backend |
| `CACHE_TTL_SECONDS` | Cache retention for repeated queries |
| `DEFAULT_LOOKBACK_DAYS` | Fallback time window for dashboard reads |
| `API_PORT` | API listen port |
| `FRONTEND_PORT` | Vite dev port |

## Testing and validation

### Pytest

```bash
cd backend
pytest
```

### Smoke test

```bash
cd backend
python scripts/smoke_test.py
```

### Basic benchmark

```bash
cd backend
python scripts/benchmark_api.py
```

## Deployment notes

- `docker-compose.yml` brings up PostgreSQL, Redis, backend, and frontend for local or demo environments.
- `infra/kubernetes/` contains API deployment, service, and HPA manifests.
- `sql/materialized_views.sql` shows how to switch the production deployment to true PostgreSQL materialized views.

## Design decisions

### Rollup table first, PostgreSQL materialized views second

The README calls out materialized views specifically. I included a production-facing SQL example for that path, but kept the running app on explicit rollup tables because that makes the repo easier to run locally, test in CI, and inspect without a heavier operational dependency.

### SQLite fallback for reproducibility

The README’s source-of-truth stack is PostgreSQL. The code still supports a SQLite fallback so the project remains self-contained for quick local runs and tests. In a real deployment, the default should stay on PostgreSQL.

### Customer-facing scope only

This repo is intentionally about usage transparency, drill-downs, and exports. It does not drift into billing collection, full admin tooling, or unrelated warehouse orchestration.

## Tradeoffs

- The PDF export is intentionally simple and stable, not a highly designed marketing artifact.
- The local refresh script recomputes all rollups for determinism. In production, that would become an incremental refresh job keyed by watermark timestamps.
- The frontend is intentionally lean and avoids state-management sprawl.

## Reproducibility notes

- Sample data generation uses a fixed random seed.
- API tests expect the seeded dataset to be present.
- The benchmark script uses FastAPI’s test client to keep the measurement path easy to reproduce.
