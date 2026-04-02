# Production Service API Platform

A production-minded, versioned API platform built around clean REST design, strong request validation, multiple authentication paths, partner-friendly documentation, and the operational hooks you need once the API is no longer just a local prototype. This repository is intentionally shaped like something I would keep as a reusable internal platform starter: straightforward enough to run on a laptop, but opinionated enough to support real integration work.

The scope is driven by the uploaded portfolio README. That source describes a scalable API platform with end-to-end ownership from design through deployment, support for internal users and external partners, path-based versioning, strong documentation, request validation, API keys plus OAuth and service tokens, rate limiting and quota management, endpoint-level monitoring, and automated test coverage. fileciteturn8file3

## What this repo includes

- FastAPI service with versioned REST endpoints under `/api/v1` and `/api/v2`
- Pydantic request validation with clear error responses
- Authentication via API keys, signed bearer tokens for OAuth-style access, and signed service tokens
- Rate limiting and daily quota enforcement per client
- Pagination patterns for both page-based and cursor-based access
- OpenAPI docs, integration notes, and request examples
- PostgreSQL-ready persistence with SQLite fallback for local runs
- Redis-aware response caching with in-memory fallback
- Prometheus metrics endpoint and request-level observability middleware
- Docker, Docker Compose, Kubernetes manifests, CI workflow, tests, smoke script, and benchmark script
- Lightweight Java client example for external integration teams

## Real-world framing

This repository models a common platform problem: an API starts as a small internal service, then gradually becomes something multiple teams and outside partners depend on. At that point, raw correctness is not enough. Versioning, auth models, quotas, docs, compatibility, and monitoring become just as important as the handler logic itself.

I kept the business domain intentionally simple so the platform concerns stay front and center. The sample resource in this repo is an `order`, which makes it easy to show create, list, update, pagination, versioning, idempotency, caching, and client-scoped usage controls without burying the platform under a fake enterprise domain.

## README-backed design goals

From the source README, the project should reflect these expectations: served internal users and external partners with 99.7% uptime, reduced response time through query optimization and caching, exposed comprehensive OpenAPI-based documentation, followed REST naming and status code conventions, supported multiple API versions during migrations, validated requests using Pydantic, supported API keys plus OAuth and service-to-service tokens, enforced rate limiting and quotas, tracked API usage and error rates by endpoint, and shipped with happy-path, edge-case, error-condition, and performance benchmark coverage. fileciteturn8file3

## Architecture

```text
Clients
  |- Internal tools using signed bearer tokens
  |- Partner apps using API keys
  |- Service-to-service jobs using signed service tokens
        |
        v
FastAPI application
  |- Auth and scope checks
  |- Versioned routers
  |- Request validation
  |- Rate limiting and quotas
  |- Caching layer
  |- Metrics and request IDs
        |
        +--> SQLAlchemy storage layer (SQLite locally, PostgreSQL in deployment)
        +--> Redis cache when enabled
        +--> Prometheus scrape endpoint
```

## API shape

### v1

`/api/v1/orders`

- page-based pagination
- compact response shape
- useful for older clients that need stability over extra metadata

### v2

`/api/v2/orders`

- cursor-style pagination
- richer response metadata
- idempotency support on create
- resource links and audit stamps

## Authentication modes

### API key

Pass `X-API-Key`.

This is the best fit for partner integrations where distributing a scoped credential is simpler than standing up a full user-login flow.

### OAuth-style bearer token

Pass `Authorization: Bearer <token>`.

The repo signs tokens locally so development stays simple. In a fuller deployment, the same interface can sit behind an actual identity provider.

### Service token

Also a bearer token, but with `token_type=service` in the claims. This is intended for backend jobs and internal service traffic.

## Folder structure

```text
production-service-api-platform/
├── app/
│   ├── api/
│   │   ├── dependencies.py
│   │   └── routes/
│   ├── core/
│   ├── services/
│   ├── db.py
│   ├── main.py
│   └── models.py
├── benchmarks/
├── docs/
├── java-client/
├── k8s/
├── scripts/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Local setup

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Copy environment variables

```bash
cp .env.example .env
```

### 3. Seed example data

```bash
python scripts/bootstrap_data.py
```

### 4. Run the API

```bash
uvicorn app.main:create_app --factory --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/metrics`

## Example auth flows

### Use the seeded API key

```bash
curl -H "X-API-Key: partner-demo-key"   http://127.0.0.1:8000/api/v1/orders
```

### Generate a bearer token

```bash
python scripts/create_token.py --client-id internal-admin --token-type service
```

### Call with a bearer token

```bash
TOKEN=$(python scripts/create_token.py --client-id internal-admin --token-type service)
curl -H "Authorization: Bearer ${TOKEN}"   http://127.0.0.1:8000/api/v1/orders
```

## Example create request

### v1 create

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders   -H "Content-Type: application/json"   -H "X-API-Key: partner-demo-key"   -d '{
    "customer_name": "Acme Labs",
    "item_sku": "SKU-500",
    "quantity": 3,
    "total_cents": 15999,
    "notes": "priority shipment"
  }'
```

### v2 create with idempotency

```bash
curl -X POST http://127.0.0.1:8000/api/v2/orders   -H "Content-Type: application/json"   -H "X-API-Key: partner-demo-key"   -H "Idempotency-Key: ord-create-001"   -d '{
    "customer_name": "Acme Labs",
    "item_sku": "SKU-500",
    "quantity": 3,
    "total_cents": 15999,
    "notes": "priority shipment"
  }'
```

## Data model

### `api_clients`

Stores client credentials, auth mode, scopes, rate limits, and daily quotas.

### `orders`

Stores the sample business resource for the API platform.

### `idempotency_records`

Maps an idempotency key and client pair to a previously created resource so retries do not create duplicates.

## Validation and error handling

- request schemas enforce length, type, and numeric bounds
- missing auth returns `401`
- missing scopes return `403`
- rate-limit and quota issues return `429`
- unknown resources return `404`
- idempotent retries on v2 safely return the same created order
- each response includes `X-Request-ID`

## Caching and performance notes

The source README explicitly calls out response-time reduction through query optimization, caching strategies, and efficient serialization. To reflect that, the implementation uses ORJSON responses, short-lived cached list endpoints, and a structure that can swap from SQLite to PostgreSQL without changing the application code. fileciteturn8file3

For local work, caching falls back to a simple in-memory store. When Redis is enabled, the same interface uses Redis instead.

## Observability

The source README also calls out monitoring for API usage patterns, error rates by endpoint, and client-specific metrics. This repo includes:

- middleware timing every request
- Prometheus metrics at `/metrics`
- client request counters
- endpoint error summaries at `/internal/usage-summary`
- request IDs attached to responses for traceability

## Testing

Run the test suite:

```bash
pytest -q
```

Coverage in this repo focuses on:

- happy-path reads and writes
- bearer token and API key auth paths
- idempotent v2 create behavior
- validation failures
- missing-resource behavior
- metrics exposure

## Benchmarking

Start the app locally, then run:

```bash
python benchmarks/api_benchmark.py
```

This script fires concurrent read traffic and prints a simple average and p95 latency summary.

## Smoke validation

```bash
python scripts/smoke_test.py
```

## Docker

Build and run locally:

```bash
docker compose up --build
```

That setup uses PostgreSQL and Redis containers to exercise the more production-like path.

## Kubernetes

The `k8s/` directory includes:

- `deployment.yaml`
- `service.yaml`
- `configmap.yaml`
- `hpa.yaml`



## 
