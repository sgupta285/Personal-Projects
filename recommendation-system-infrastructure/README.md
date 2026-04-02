# Recommendation System Infrastructure

A production-minded recommendation platform that serves personalized results across home feed, search, and related-item surfaces. The repository is built around the exact shape described in the uploaded portfolio README: model serving infrastructure, online and offline feature stores, experimentation support, candidate generation with approximate nearest neighbor search, a two-stage ranking stack, and observability that is useful when the system is under real traffic.

The goal here was not to throw together a toy recommender that returns random items. I wanted a repository that feels like something I could actually talk through in an interview or put on GitHub without apology: a coherent serving layer, realistic data flow, sane operational hooks, and enough scaffolding to show how the pieces fit together.

## What the uploaded README required

The source README describes this project as an ML platform for personalized recommendations with three non-negotiable themes:

- model serving that can handle real-time recommendation traffic
- feature stores that keep training and serving aligned
- experimentation infrastructure for A/B testing and ranking iteration

It also explicitly calls out candidate generation with FAISS, a two-stage ranking setup, contextual and engagement-based features, position-bias correction, and sub-300ms serving targets at scale. This repository implements those ideas directly in a runnable local form.

## Repository layout

```text
recommendation-system-infrastructure/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── ml/
│   ├── models/
│   └── services/
├── artifacts/
│   ├── benchmarks/
│   ├── mlruns/
│   └── models/
├── configs/
│   ├── grafana/
│   └── prometheus.yml
├── data/
│   ├── processed/
│   └── raw/
├── infra/
│   └── kubernetes/
├── scripts/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── requirements.txt
```

## Architecture

### 1. Candidate generation

The first stage narrows a large item universe into a manageable candidate pool.

- User and item embeddings are trained from interaction data.
- FAISS is used when installed for approximate nearest neighbor retrieval.
- A NumPy fallback keeps local development simple if FAISS is unavailable.
- Related-item recommendations query the same index with an item vector instead of a user vector.

This maps directly to the uploaded README requirement for approximate nearest neighbor candidate generation over a large catalog.

### 2. Online and offline feature stores

The project keeps two lightweight stores in sync:

- `data/processed/offline_features.json` represents offline materialized features.
- `FeatureStore` exposes serving-time joins for user, item, and contextual features.
- The same feature definitions are reused during ranker training and request-time scoring.

That is the practical interpretation of the training-serving consistency requirement from the source README.

### 3. Two-stage ranking

After candidate generation, the ranking path has two layers:

- Stage 1 uses embedding similarity for cheap scoring over a large candidate pool.
- Stage 2 uses a small PyTorch MLP to rerank the strongest candidates with richer joined features.
- The neural reranker can be toggled through the experiment assignment layer.

This mirrors the README description of a fast first-stage model followed by an expensive reranker over the top slice of candidates.

### 4. Experimentation and A/B testing

Recommendation changes are dangerous when they ship without control. The repo includes:

- deterministic bucketing from stable user hashing
- per-user experiment assignment endpoint
- summary aggregation for CTR and conversion by variant
- a baseline variant and a neural rerank variant

This is the implementation of the README’s experimentation and metric-tracking expectations.

### 5. Observability and operations

The repo exposes operational hooks that matter when a recommender is on call:

- Prometheus metrics for request count, latency, and cache hits
- health endpoints for liveness and readiness
- Docker Compose for local services
- Grafana provisioning
- Kubernetes deployment, service, ConfigMap, and HPA manifests

The original project description framed this as ML infrastructure, not just model code, so the monitoring and deploy pieces are first-class here too.

## Core features

- Personalized home feed recommendations
- Search-surface recommendations using the same serving stack
- Related-item recommendations
- Context-aware reranking using hour-of-day and device type
- Stable A/B assignment for ranking experiments
- Position-bias-aware training signal construction
- Cache-backed responses for repeated requests
- MLflow-backed training runs and artifact tracking
- Benchmark script for local latency validation

## Tech stack

- Python
- PyTorch
- FastAPI
- FAISS with NumPy fallback
- Redis
- PostgreSQL
- MLflow
- Prometheus
- Grafana
- Docker
- Kubernetes

The stack stays aligned with the uploaded README rather than drifting into unrelated tooling.

## Data flow

1. `scripts/generate_sample_data.py` creates users, items, and interactions.
2. `app/ml/train.py` builds user and item embeddings and trains the second-stage ranker.
3. Artifacts are written into `artifacts/models/`.
4. App startup loads the feature store, embeddings, and ranker.
5. A request hits `/v1/recommendations/*`.
6. The system checks the response cache.
7. The candidate generator retrieves a candidate pool.
8. The feature store joins user, item, and context features.
9. The ranker reranks the pool under the assigned experiment variant.
10. The response is returned and cached.

## Local setup

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Seed the local dataset

```bash
make seed
```

### 3. Train the models

```bash
make train
```

### 4. Start the API

```bash
make run
```

### 5. Try a request

```bash
curl -X POST http://localhost:8000/v1/recommendations/home   -H "Content-Type: application/json"   -d '{
    "user_id": "user_0005",
    "surface": "home",
    "limit": 10,
    "context": {"hour_of_day": 20, "device_type": "ios"}
  }'
```

## Environment variables

A starter `.env.example` is included. The most important settings are:

- `DATABASE_URL` for local relational storage
- `REDIS_URL` for external cache integration
- `MLFLOW_TRACKING_URI` for run tracking
- `MODEL_DIR` for saved embeddings and reranker weights
- `OFFLINE_FEATURES_PATH` and `ITEM_METADATA_PATH` for materialized feature snapshots
- `CACHE_TTL_SECONDS` for response reuse

## API summary

### `POST /v1/recommendations/home`
Returns personalized home-feed recommendations.

### `POST /v1/recommendations/search`
Runs the same infrastructure for search-surface ranking.

### `POST /v1/recommendations/related`
Returns related items using item-to-item retrieval and the same reranking layer.

### `GET /v1/experiments/assignment/{user_id}`
Returns the assigned experiment and variant.

### `POST /v1/experiments/summary`
Aggregates experiment events into CTR and conversion summaries.

### `GET /health/live`
Basic liveness check.

### `GET /health/ready`
Readiness check that confirms model artifacts are loaded.

### `GET /metrics`
Prometheus scrape target.

## Testing

Run the test suite with:

```bash
make test
```

The tests cover:

- stable experiment bucketing
- end-to-end API recommendation responses
- runtime loading on trained artifacts

## Benchmarking

With the API running locally:

```bash
make bench
```

This sends repeated home-feed requests and writes a simple latency report to `artifacts/benchmarks/api_benchmark.json`.

## Docker and service composition

For a more production-like local environment:

```bash
docker compose up --build
```

This brings up:

- the FastAPI service
- Redis
- PostgreSQL
- MLflow UI
- Prometheus
- Grafana

## Deployment notes

The Kubernetes folder includes:

- Deployment
- Service
- ConfigMap
- HorizontalPodAutoscaler

That is enough to show how the API would be rolled out behind a service with readiness gating and horizontal scaling.

## License

MIT


