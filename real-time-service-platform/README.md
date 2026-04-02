# Real-Time Service Platform

A production-minded backend service platform built around low-latency request handling, reliability controls, and operational visibility. The project is intentionally scoped like something I would use as a foundation for a real internal platform: authentication, authorization, synchronous and asynchronous request flows, request tracing, rate limiting, circuit breaking, deployment manifests, and enough testing to make local iteration trustworthy.

This repository was built from the README portfolio brief for the **Real-Time Service Platform** project. The brief emphasized high-throughput request handling, sub-500ms latency, 99.5% uptime patterns, FastAPI, PostgreSQL, Redis, Kubernetes, Docker, Prometheus, Grafana, and GitHub Actions.

## What this repo includes

- FastAPI service with both sync and async request submission paths
- JWT-based auth with role-based access control
- Token bucket rate limiting at the middleware layer
- Circuit breaker around a simulated downstream dependency
- Correlation IDs carried through request lifecycle for debugging
- Prometheus metrics endpoint and Grafana provisioning
- Docker Compose for local infra, plus Kubernetes manifests for deployment
- GitHub Actions CI running automated tests
- Seed, smoke-test, and benchmark scripts

## Real-world framing

The goal here is not to mimic a single domain product. It is to model the service layer you build underneath several kinds of real systems: payments orchestration, partner integrations, real-time fulfillment, operational tooling, and event-driven internal platforms. Those systems are usually not interesting because of one endpoint. They are interesting because of what happens under stress: whether you can throttle abuse, recover from partial downstream failures, trace requests across logs, and keep latency predictable when load changes.

## Architecture

The platform is organized around a small number of building blocks:

1. **API layer** handles authentication, validation, request shaping, and endpoint orchestration.
2. **Service layer** owns sync execution, async queue-style background execution, and downstream dependency calls.
3. **Reliability layer** provides rate limiting and circuit breaking.
4. **Persistence layer** stores users and service requests in SQLAlchemy models backed by PostgreSQL in containerized runs or SQLite in local tests.
5. **Observability layer** exposes Prometheus metrics and correlation IDs.
6. **Deployment layer** includes Docker Compose, Kubernetes manifests, and CI.

```text
Client -> FastAPI -> Auth/RBAC -> Sync or Async handler -> Circuit breaker -> Downstream dependency
                          |                                  |
                          +-> SQLAlchemy / PostgreSQL        +-> Prometheus metrics
                          +-> Redis-ready config             +-> Correlation IDs in logs
```

## Folder structure

```text
real-time-service-platform/
├── .env.example
├── .github/workflows/ci.yml
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── middleware/
│   │   ├── observability/
│   │   ├── schemas/
│   │   └── services/
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── deploy/kubernetes/
├── ops/grafana/
├── ops/prometheus/
└── readme_assets/
```

## Core flows

### 1. Authentication and access control

- `POST /v1/auth/register` registers a user and returns a JWT
- `POST /v1/auth/login` authenticates an existing user and returns a JWT
- roles are simple but practical: `admin` and `operator`
- admin users can inspect all requests, operators can only see their own

### 2. Synchronous request path

`POST /v1/requests/sync` accepts a request payload, persists it, forwards it through the downstream executor, and returns the completed record when the dependency succeeds.

This path is appropriate for work that should complete during the request window and stay under the latency budget.

### 3. Asynchronous request path

`POST /v1/requests/async` persists the request and schedules background execution. It returns immediately with the request identifier and the correlation ID.

This path is appropriate for work that should not block the caller.

### 4. Operational endpoints

- `GET /v1/system/health`
- `GET /v1/system/ready`
- `GET /v1/system/trace`
- `GET /metrics/`

## Environment variables

| Variable | Purpose |
|---|---|
| `APP_NAME` | service name reported in root endpoint |
| `ENVIRONMENT` | development, staging, or production style environment |
| `LOG_LEVEL` | logging verbosity |
| `SECRET_KEY` | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | token lifetime |
| `DATABASE_URL` | SQLAlchemy database URL |
| `REDIS_URL` | Redis URL for future externalization of counters and caches |
| `RATE_LIMIT_CAPACITY` | token bucket size |
| `RATE_LIMIT_REFILL_PER_SECOND` | refill rate |
| `CIRCUIT_BREAKER_FAILURE_THRESHOLD` | failures before opening circuit |
| `CIRCUIT_BREAKER_RECOVERY_TIMEOUT` | seconds before half-open retry |
| `DOWNSTREAM_BASE_LATENCY_MS` | simulated downstream baseline latency |
| `DOWNSTREAM_JITTER_MS` | latency jitter |

## Local setup

### Option 1: run the API directly

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
python scripts/seed.py
uvicorn app.main:app --reload
```

### Option 2: run the full local stack

```bash
docker compose up --build
```

That starts:
- API on `http://localhost:8000`
- Prometheus on `http://localhost:9090`
- Grafana on `http://localhost:3000`
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

## Sample API usage

Register a user:

```bash
curl -X POST http://localhost:8000/v1/auth/register   -H "Content-Type: application/json"   -d '{
    "username": "operator1",
    "full_name": "Platform Operator",
    "password": "secret123",
    "role": "operator"
  }'
```

Login:

```bash
curl -X POST http://localhost:8000/v1/auth/login   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=operator1&password=secret123"
```

Submit a synchronous request:

```bash
curl -X POST http://localhost:8000/v1/requests/sync   -H "Authorization: Bearer <TOKEN>"   -H "Content-Type: application/json"   -d '{
    "kind": "payment_authorization",
    "payload": {"order_id": "ord_1001", "amount": 42.5},
    "priority": 2
  }'
```

Submit an asynchronous request:

```bash
curl -X POST http://localhost:8000/v1/requests/async   -H "Authorization: Bearer <TOKEN>"   -H "Content-Type: application/json"   -d '{
    "kind": "shipment_update",
    "payload": {"tracking_number": "TRK123"},
    "priority": 4
  }'
```

## Testing and validation

Run automated tests:

```bash
make test
```

Run the smoke test:

```bash
make smoke
```

Run the lightweight latency benchmark:

```bash
make bench
```

The benchmark is intentionally simple. It is there to exercise the synchronous request path repeatedly and surface a rough local average and p95. It is not trying to pretend to be a full load lab.

## Metrics and observability

The project exposes counters, latency histograms, active request gauges, downstream result counters, and circuit breaker state.

The most useful metrics here are:

- `service_platform_requests_total`
- `service_platform_request_latency_seconds`
- `service_platform_active_requests`
- `service_platform_downstream_calls_total`
- `service_platform_circuit_breaker_state`

The request middleware also injects an `X-Correlation-ID` header into each response. That gives you an anchor for tracing production issues across logs and requests.

## Reliability decisions

### Rate limiting

The README brief explicitly called for rate limiting with a token bucket algorithm. That is implemented in middleware with a simple in-memory bucket keyed off IP plus auth context. In a multi-instance deployment you would externalize that state to Redis. I kept the implementation local here so the project stays runnable without requiring that whole path just to understand the design.

### Circuit breaker

The downstream dependency simulation is intentionally small, but the circuit breaker behavior is real enough to test. After repeated failures, the breaker opens and the platform returns a fast 503 instead of repeatedly hammering a dependency that is already unhealthy.

### Sync and async split

The README called out both synchronous and asynchronous endpoints. The repo makes that explicit instead of hiding background work behind a single vague endpoint. That keeps latency-sensitive flows separate from work that should be queued or retried later.

## Deployment notes

### Docker

The backend ships with a focused Dockerfile and the root includes a Compose stack for API, PostgreSQL, Redis, Prometheus, and Grafana.

### Kubernetes

The Kubernetes manifests include:
- deployment with readiness and liveness probes
- service resource
- horizontal pod autoscaler

These map directly to the operational expectations described in the portfolio brief: rolling updates, health checks, and autoscaling.


## Default seeded users

- `admin / adminpass`
- `operator / operatorpass`

## License

MIT
