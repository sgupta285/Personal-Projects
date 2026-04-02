# Real-Time Data Processing Platform

A production-minded event processing platform built around the shape described in the portfolio README: Kafka-like ingestion, Lambda-style processing, DynamoDB-style state storage, dead-letter handling, idempotency, monitoring, and operational controls.

This repository is intentionally scoped like a serious take-home or portfolio build, not a giant platform clone. It runs locally with a lightweight Python stack while preserving the architectural boundaries you would expect in AWS: a streaming ingress layer, stateless processors, durable state, retry policies, DLQ workflows, and infrastructure definitions.

## What this project covers

- High-volume event ingestion with partitioned, Kafka-like topics
- Lambda-style event processing with retry handling
- DynamoDB-style persistence for entity state and processing metadata
- Exactly-once style behavior through idempotency keys
- Dead-letter queue capture and replay
- Queue depth, throughput, and latency monitoring
- Autoscaling recommendations based on queue pressure and target latency
- Terraform scaffolding for an AWS deployment shape

## Why this repo exists

The original project summary emphasizes a system that can handle **1,000+ events/sec**, stay under **500ms end-to-end latency**, and maintain **99.8% uptime** through fault tolerance, retries, monitoring, and recovery. The goal here is to make those ideas concrete in a repo that is easy to run and inspect.

Instead of requiring a live AWS account, local development uses:

- an in-process partitioned broker that behaves like a Kafka topic with partitions and consumer groups
- a Lambda-style async worker loop
- SQLite-backed persistence that mirrors the access patterns you would design for DynamoDB
- JSON metrics emission that resembles CloudWatch-style operational telemetry

That gives you something you can run on a laptop while still preserving the intended architecture.

## Architecture

```text
Clients / Producers
        |
        v
 FastAPI ingestion API
        |
        v
 Partitioned topic broker
  |         |         |
  v         v         v
worker   worker    worker      <- Lambda-style processing consumers
  |         |         |
  +-----> retry / failure policy
                |
                +--> DLQ store

Successful events
        |
        v
 DynamoDB-style state store
        |
        +--> entity snapshots
        +--> processed idempotency keys
        +--> processing ledger
        +--> operational metrics
```

## Repository layout

```text
real-time-data-processing-platform/
├── src/rtdp/
│   ├── api.py
│   ├── autoscaler.py
│   ├── broker.py
│   ├── config.py
│   ├── metrics.py
│   ├── schemas.py
│   ├── service.py
│   ├── storage.py
│   └── worker.py
├── tests/
│   ├── test_api.py
│   ├── test_broker.py
│   └── test_processing.py
├── scripts/
│   ├── benchmark.py
│   ├── demo_run.py
│   └── smoke_test.py
├── infra/
│   └── terraform/
│       ├── main.tf
│       ├── outputs.tf
│       └── variables.tf
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## Core flows

### 1. Ingestion

`POST /v1/events` accepts one event or a batch of events. Each event is written to a partition chosen from the entity key. That preserves ordering per entity while allowing horizontal consumption across partitions.

### 2. Processing

Workers pull batches from the topic broker, process them asynchronously, and write durable state. Retries are attempted for transient errors. Permanent failures or retry exhaustion route messages into the DLQ.

### 3. Idempotency

Every event includes an idempotency key. If the system sees the same key twice, the second copy is recorded as a duplicate and skipped, which is how the repo approximates exactly-once behavior in practice.

### 4. Persistence

Local persistence uses SQLite, but the access pattern mirrors a DynamoDB design:

- primary entity lookup by `entity_id`
- processing ledger by `event_id`
- processed idempotency keys for dedupe
- DLQ retrieval by failure state and time

### 5. Monitoring

The service tracks:

- throughput
- accepted vs duplicate events
- processing latency
- retry counts
- DLQ growth
- queue depth by partition
- autoscaler recommendations

## Data model

### Inbound event shape

```json
{
  "event_id": "evt_1001",
  "entity_id": "acct_42",
  "event_type": "purchase",
  "occurred_at": "2026-04-01T12:00:00Z",
  "payload": {
    "amount": 74.15,
    "currency": "USD"
  },
  "idempotency_key": "acct_42-purchase-evt_1001",
  "failure_mode": "none"
}
```

`failure_mode` is optional and exists mainly for smoke tests and benchmark scenarios. Supported values are:

- `none`
- `transient_once`
- `always`

## Local setup

### Requirements

- Python 3.11+
- `pip`
- optional: Docker and Docker Compose

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Environment variables

Copy the example file first.

```bash
cp .env.example .env
```

Key settings:

- `RTDP_DB_PATH`: SQLite database file
- `RTDP_PARTITIONS`: number of topic partitions
- `RTDP_MAX_RETRIES`: retry limit before DLQ
- `RTDP_BATCH_SIZE`: worker batch size
- `RTDP_WORKER_COUNT`: number of worker tasks
- `RTDP_TARGET_LATENCY_MS`: autoscaling target used for recommendations

## How to run

### Option 1: local API + background workers

```bash
uvicorn rtdp.api:app --reload --app-dir src
```

Then in another terminal, run the demo script.

```bash
python scripts/demo_run.py
```

### Option 2: Docker Compose

```bash
docker compose up --build
```

### Example API calls

Ingest a single event:

```bash
curl -X POST http://127.0.0.1:8000/v1/events   -H "Content-Type: application/json"   -d '{
    "event_id": "evt_1",
    "entity_id": "acct_1",
    "event_type": "purchase",
    "occurred_at": "2026-04-01T12:00:00Z",
    "payload": {"amount": 55.0},
    "idempotency_key": "acct_1-purchase-evt_1"
  }'
```

Inspect platform status:

```bash
curl http://127.0.0.1:8000/v1/status
```

Inspect DLQ items:

```bash
curl http://127.0.0.1:8000/v1/dlq
```

Replay a DLQ record:

```bash
curl -X POST http://127.0.0.1:8000/v1/dlq/replay/dlq_1
```
```

## Smoke test

```bash
python scripts/smoke_test.py
```

That script sends:

- a normal event
- a duplicate event with the same idempotency key
- a transient-failure event that succeeds on retry
- a permanently failing event that lands in the DLQ

## Benchmark

```bash
python scripts/benchmark.py --events 1500 --concurrency 8
```

The benchmark writes a JSON artifact to `artifacts/benchmark_results.json` with:

- total accepted events
- duplicates skipped
- throughput
- mean latency
- p95 latency
- DLQ count
- autoscaler recommendation

## Tests

```bash
pytest -q
```

The test suite covers:

- partition routing and queue accounting
- idempotency and duplicate suppression
- retry-to-DLQ behavior
- API ingestion and replay flows

## Deployment notes

The Terraform files model the intended cloud shape:

- API Gateway or ALB fronting the ingestion service
- Kafka or MSK style stream topic
- Lambda consumers
- DynamoDB table for state
- SQS dead-letter queue
- CloudWatch alarms and dashboards

This repo does not pretend to be a full AWS production deployment. The point is to express the deployment shape cleanly and show what the code would look like behind it.

## Design decisions

### Why SQLite locally instead of DynamoDB?

Because local reproducibility matters. The repo uses a persistence layer shaped like DynamoDB access patterns, but keeps local startup friction low..

### How exactly-once works here

Strict exactly-once is a loaded term. In this repo, the practical behavior is achieved through:

- deterministic idempotency keys
- durable processed-key tracking
- atomic store updates guarded by the key

That is the same pattern many real event-driven systems use even when the transport itself is at-least-once.

## Operational expectations captured from the source spec

The source description for this project implies the following expectations, which shaped the repo:

- low latency from ingestion through storage
- strong duplicate protection
- health checks and recovery paths
- visible queue depth and backlog monitoring
- retry safety with manual DLQ replay
- a scaling story based on queue depth and processing latency

## License

MIT



