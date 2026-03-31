# Ads Integrity & Content Moderation Platform

A portfolio-ready backend system that screens ad submissions before they enter an ad serving pipeline. The project simulates the workflow an ads integrity team would care about: ingestion, event-driven moderation, risk scoring, policy review, and analytics for advertiser fraud patterns.

## Why I built it

I wanted a project that looked closer to real ad platform infrastructure than a generic CRUD app. This stack focuses on the pieces that matter in ads integrity and trust engineering:

- event-driven moderation with Kafka
- real-time risk caching with Redis
- durable ad metadata and moderation history in Postgres
- a lightweight ML classifier for suspicious creative copy
- a deterministic rule engine for policy violations
- reviewer actions and operational analytics through REST APIs and a React dashboard

## What the platform does

1. Advertisers submit ads through a FastAPI service.
2. The API stores metadata in Postgres and emits an `ads.submitted` event.
3. A moderation worker consumes the event from Kafka.
4. The worker runs:
   - text and metadata policy rules
   - a lightweight ML classifier trained on synthetic ad copy
   - a score combiner that decides `approved`, `in_review`, or `blocked`
5. The worker writes the latest risk score to Redis for fast access.
6. The final moderation state is persisted in Postgres and published to `ads.moderated`.
7. The dashboard surfaces volume, decision mix, policy-hit patterns, and advertiser risk.

## Architecture

```text
Advertiser / UI
      |
      v
FastAPI API  ---> Postgres
      |
      +----> Kafka topic: ads.submitted
                      |
                      v
              Moderation Worker
            /        |          \
       Rules Engine  ML Model   Redis Cache
            \        |          /
             +---- Decision ----+
                      |
                      v
             Postgres + Kafka topic: ads.moderated
                      |
                      v
                React Dashboard
```

More implementation detail lives in [`docs/architecture.md`](docs/architecture.md).

## Project layout

```text
.
├── backend
│   ├── app
│   │   ├── api
│   │   ├── core
│   │   └── services
│   ├── tests
│   └── worker
├── docs
├── frontend
├── infra
├── scripts
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Quick start

### Option 1: Run the full stack with Docker

```bash
docker compose up --build
```

Services:
- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:3000`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`
- Kafka: `localhost:9092`

Seed sample ads after the stack is up:

```bash
python scripts/seed_ads.py
```

### Option 2: Run backend services locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=backend

uvicorn app.main:app --reload --port 8000
python -m worker.main
```

You can retrain the toy classifier whenever you want:

```bash
python scripts/train_classifier.py
```

## Core APIs

- `POST /api/v1/ads` submit a new ad
- `GET /api/v1/ads` list recent ads
- `GET /api/v1/ads/{ad_id}` fetch a specific ad
- `POST /api/v1/ads/{ad_id}/rescan` requeue an ad for moderation
- `POST /api/v1/reviews/{ad_id}/decision` apply a manual reviewer decision
- `GET /api/v1/analytics/overview` summary metrics
- `GET /api/v1/analytics/advertisers` top risky advertisers
- `GET /api/v1/analytics/fraud-patterns` policy-hit patterns and category breakdowns

## Moderation logic

The moderation worker combines two signals:

### Rule engine
A deterministic rules layer catches obvious issues such as:
- misleading financial claims
- fake urgency
- prohibited product categories
- suspicious URL patterns
- scam-style copy

### ML classifier
A simple scikit-learn pipeline scores the ad copy for spam and fraud-like language. It is intentionally lightweight, easy to inspect, and easy to retrain.

### Final decision policy
- `risk >= 0.85` → `blocked`
- `0.55 <= risk < 0.85` → `in_review`
- `risk < 0.55` → `approved`

## A few realistic touches

- advertiser risk is rolled up over time instead of attached to only one ad
- manual reviews are stored separately from automated decisions
- Redis acts as the latest-score cache to support fast downstream access
- Kafka topics separate ingestion from moderation so the API stays thin
- SQLite can be used for quick local smoke testing, while Docker Compose uses Postgres

## Notes

This is a portfolio project, so some pieces are intentionally simplified:
- creative scanning is text-first rather than full multimodal computer vision
- the classifier uses synthetic training data shipped with the repo
- the dashboard is focused on operational moderation metrics, not ad delivery metrics

Even with those simplifications, the codebase is structured the way I would structure a small internal trust and safety service: clear separation between API, worker, infra, and dashboard.

## Demo flow

1. Start the stack with `docker compose up --build`
2. Visit `http://localhost:8000/docs`
3. Submit a few ads manually or run `python scripts/seed_ads.py`
4. Open `http://localhost:3000`
5. Watch the dashboard update as ads move into approved, review, or blocked buckets

