# Production ML Serving Infrastructure

A production-minded ML serving platform for real-time and batch prediction workloads.

This repository packages the parts that usually get hand-waved away in model demos: model training and registration, real-time inference, batch scoring, dynamic request batching, two-layer caching, feature retrieval, fallback behavior, metrics, health checks, local orchestration, and deployment scaffolding.

The project is intentionally built around a realistic operating model instead of a notebook-only workflow. The API serves online requests, a batch path handles larger offline jobs, Redis and local caching reduce repeated work, Prometheus and Grafana expose system and model behavior, and the repo includes Docker, Kubernetes, and Terraform support so the code does not stop at localhost.

## Why this repository exists

A lot of ML projects stop after training a model. Real teams still have to answer harder questions:

- How does the model get served under load?
- What happens when the feature store is slow?
- How do we batch requests without changing the client contract?
- How do we measure latency, cache hit rate, and prediction volume?
- How do we keep training artifacts reproducible?
- How do we run the same system locally and in a cluster?

This repo is my answer to those questions for a small but complete serving stack.

## What is included

- **Real-time inference API** built with FastAPI
- **Batch scoring endpoint** for larger offline workloads
- **Dynamic request batching** to reduce per-request inference overhead
- **Two-tier caching**
  - Redis for shared request caching
  - local in-memory TTL cache for hot keys and model metadata
- **Feature retrieval layer** with online and offline paths
- **PyTorch model training pipeline** with reproducible artifact output
- **Model registry hooks** using MLflow plus a local registry manifest
- **Prometheus metrics** and prewired Grafana dashboards
- **Docker Compose** stack for local development
- **Kubernetes manifests** for deployment and autoscaling
- **Terraform scaffolding** for basic AWS resources
- **Tests, smoke checks, and benchmark scripts**

## Architecture

```text
Client
  |
  v
FastAPI Service
  |---- Request validation
  |---- Cache lookup (local -> Redis)
  |---- Feature hydration
  |---- Dynamic batch queue
  |---- Model inference
  |---- Fallback model on degraded path
  |---- Metrics + structured response
  |
  +--> Prometheus scrape endpoint

Training pipeline
  |---- Synthetic training data generation
  |---- PyTorch training loop
  |---- Evaluation metrics
  |---- MLflow run logging
  |---- Registry manifest update

Persistence
  |---- PostgreSQL for online feature store and request audit records
  |---- Redis for distributed cache
  |---- Local artifact directory for model weights and registry manifest
```

## Repository layout

```text
production-ml-serving-infrastructure/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── ml/
│   ├── schemas/
│   └── services/
├── artifacts/
│   ├── model_registry/
│   └── models/
├── configs/
│   ├── grafana/
│   └── prometheus.yml
├── data/
│   ├── processed/
│   └── raw/
├── k8s/
├── scripts/
├── terraform/
├── tests/
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

## Core serving workflow

1. A client sends either a raw feature payload or a `customer_id`.
2. The API normalizes the request and builds a cache key.
3. Local cache is checked first, then Redis.
4. If the request misses cache and includes only a `customer_id`, the feature service hydrates features from the online store.
5. The request enters the dynamic batcher.
6. Batched tensors are scored together by the active model.
7. The response is cached, audited, and exposed through metrics.

## Model problem framing

The example workload predicts the probability that a user session converts. The task is intentionally simple enough to run locally while still feeling like a real serving problem:

- mixed numerical features
- online and batch prediction paths
- probability output plus label
- explicit fallback path
- repeatable training

The model is a small feedforward PyTorch network trained on synthetic but structured data with realistic feature relationships.

## Tech stack

- Python
- FastAPI
- PyTorch
- PostgreSQL
- Redis
- MLflow
- Prometheus
- Grafana
- Docker
- Kubernetes
- Terraform
- AWS scaffolding

## Local setup

### 1) Create an environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

### 2) Start infrastructure

You can run everything locally with Docker Compose:

```bash
docker compose up --build
```

This starts:

- API service
- PostgreSQL
- Redis
- Prometheus
- Grafana

### 3) Train a model artifact

In another shell:

```bash
python scripts/train_model.py
python scripts/seed_feature_store.py
```

### 4) Start the API locally without Docker

```bash
uvicorn app.main:app --reload
```

## Environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy connection string for the online feature store |
| `REDIS_URL` | Redis endpoint for distributed cache |
| `MLFLOW_TRACKING_URI` | MLflow tracking backend |
| `MODEL_PATH` | Active model weights file |
| `MODEL_REGISTRY_PATH` | JSON manifest for the active model |
| `REQUEST_BATCH_WINDOW_MS` | Batch collection window in milliseconds |
| `REQUEST_MAX_BATCH_SIZE` | Maximum dynamic batch size |
| `IN_MEMORY_CACHE_TTL_SECONDS` | TTL for the local cache |
| `REDIS_CACHE_TTL_SECONDS` | TTL for Redis cache entries |
| `ENABLE_DYNAMIC_BATCHING` | Toggle the async batch queue |
| `ENABLE_FALLBACK_MODEL` | Toggle degraded-path fallback model |

## Running the API

### Health checks

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

### Real-time prediction

```bash
curl -X POST http://localhost:8000/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req-1",
    "features": {
      "account_tenure_days": 210,
      "avg_session_seconds": 640,
      "prior_purchases": 8,
      "cart_additions_7d": 12,
      "email_click_rate": 0.32,
      "discount_sensitivity": 0.58,
      "inventory_score": 0.80,
      "device_trust_score": 0.91
    }
  }'
```

### Prediction by customer id

```bash
curl -X POST http://localhost:8000/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req-2",
    "customer_id": "cust-1002"
  }'
```

### Batch prediction

```bash
curl -X POST http://localhost:8000/v1/batch/predict \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "batch-1",
    "requests": [
      {
        "request_id": "b1",
        "customer_id": "cust-1001"
      },
      {
        "request_id": "b2",
        "features": {
          "account_tenure_days": 87,
          "avg_session_seconds": 420,
          "prior_purchases": 3,
          "cart_additions_7d": 5,
          "email_click_rate": 0.11,
          "discount_sensitivity": 0.70,
          "inventory_score": 0.63,
          "device_trust_score": 0.78
        }
      }
    ]
  }'
```

## API summary

| Endpoint | Method | Purpose |
|---|---|---|
| `/health/live` | GET | Liveness check |
| `/health/ready` | GET | Readiness check including model availability |
| `/v1/predict` | POST | Real-time single-request prediction |
| `/v1/batch/predict` | POST | Offline-style batch scoring |
| `/v1/model/info` | GET | Active model metadata |
| `/v1/cache/clear` | POST | Clear local and Redis cache |
| `/metrics` | GET | Prometheus metrics |

## Data model notes

### Feature vector

The inference service expects these eight features:

- `account_tenure_days`
- `avg_session_seconds`
- `prior_purchases`
- `cart_additions_7d`
- `email_click_rate`
- `discount_sensitivity`
- `inventory_score`
- `device_trust_score`

### Persistence

The online store contains customer features and request audit data.

- `online_features`
- `prediction_audit_log`

The training job also writes a processed CSV snapshot under `data/processed/`.

## Training and reproducibility

Training is deterministic within the limits of the runtime seed configuration.

```bash
python scripts/train_model.py
```

This does the following:

- generates a structured synthetic dataset
- trains a small feedforward network
- evaluates log loss and accuracy
- writes model weights to `artifacts/models/current_model.pt`
- writes a registry manifest to `artifacts/model_registry/current.json`
- logs the run to MLflow

## Tests

```bash
pytest
```

The tests cover:

- request validation
- cache behavior
- feature hydration fallback
- batcher behavior
- API responses

## Benchmarking

A lightweight async benchmark client is included.

```bash
python scripts/benchmark.py --requests 200 --concurrency 20
```

It records:

- total requests
- average latency
- p50
- p95
- p99
- error count
- throughput

Results are stored in `artifacts/benchmarks/`.

## Observability

### Prometheus

Prometheus scrapes the API at `/metrics`. The service exports:

- request counts
- request latency
- cache hits and misses
- batch sizes
- model inference duration
- fallback invocation counts

### Grafana

Grafana is preconfigured with a basic datasource and a starter dashboard that shows:

- request rate
- p95 latency
- cache hit ratio
- average batch size
- fallback rate

Default local credentials:

- username: `admin`
- password: `admin`

## Deployment notes

### Docker

Build the service image:

```bash
docker build -t production-ml-serving-infrastructure .
```

### Kubernetes

The `k8s/` directory contains:

- namespace
- config map
- deployment
- service
- horizontal pod autoscaler

The HPA uses CPU utilization and can be extended to custom latency metrics.

### Terraform

The `terraform/` directory provides a starting point for:

- ECR repository
- S3 bucket for artifacts
- CloudWatch log group

It is intentionally small and meant to be adapted to the target AWS account.

## Design decisions

### Why both Redis and an in-memory cache?

Redis reduces duplicated work across replicas. The local cache removes a network hop for the hottest requests and model metadata lookups.

### Why a synthetic dataset?

A repo like this should be runnable without requiring proprietary data. The synthetic dataset keeps the project self-contained while still supporting real training and inference code paths.

### Why keep MLflow and a local registry manifest?

MLflow is great for experiment tracking, but a lightweight manifest is convenient for the serving layer to resolve the active artifact quickly and deterministically.

### Why expose batch and real-time paths in the same service?

It mirrors how smaller ML teams often operate in practice. A single serving repo handles both latency-sensitive requests and scheduled scoring jobs before the system grows into separate services.

## Tradeoffs

- The example model is intentionally compact, so it does not show GPU-heavy inference.
- The feature store is minimal and does not implement full point-in-time joins.
- Canary and rollback behavior are represented through config and deployment scaffolding rather than a full progressive delivery controller.

## Limitations

- The synthetic data generator is realistic enough for demos, not for domain conclusions.
- The benchmark client is for local and staging-style load checks, not a full distributed performance test.
- The Terraform module is a clean starting point, not a full AWS platform bootstrap.

## Reproducibility notes

- All seeds are centralized in the training code.
- Feature ordering is fixed in one place.
- Model metadata is versioned in a registry manifest.
- Local setup does not require external managed services.

## Quick demo flow

```bash
docker compose up --build
python scripts/train_model.py
python scripts/seed_feature_store.py
curl http://localhost:8000/health/ready
python scripts/smoke_test.py
python scripts/benchmark.py --requests 100 --concurrency 10
```

## License

MIT
