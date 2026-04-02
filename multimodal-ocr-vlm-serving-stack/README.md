# Multimodal OCR and VLM Serving Stack

This repository packages a production-minded serving stack for OCR, vision-language workloads, and document-centric multimodal inference. The scope comes directly from the attached portfolio README: queue-backed workers, batching, memory-aware scheduling, deployment tooling, and service-level observability for GPU-heavy workflows that need to stay debuggable under load.

The local implementation is intentionally lightweight so it can run on a laptop without a GPU, but the structure mirrors how I would wire a real service before swapping the mock engines for CUDA-backed OCR or VLM runtimes.

## What this project covers

- Queue-backed asynchronous job execution for OCR, VLM, and fused pipeline tasks
- Memory-aware batch selection so large documents do not crowd out the entire worker budget
- FastAPI control plane for submission, status polling, and metrics
- In-memory cache layer with a Redis-ready configuration surface
- Kubernetes and Helm deployment scaffolding
- Prometheus-friendly service metrics for queue depth, batch sizes, GPU memory estimates, and end-to-end latency
- A small C++ utility for tile and memory planning that fits the stack's Python + C++ shape

## README-backed build notes

From the source README, this project is defined as a stack for OCR, vision models, and GPU-heavy inference with queue-backed workers and memory-aware caching. The stated outcomes are 45% lower end-to-end latency through batching and scheduling, stronger deployment and observability, and 95% GPU utilization from better request packing. The focus areas and stack are OCR, VLM serving, batching, observability, Python, C++, Redis, Docker, Kubernetes, Helm, and CUDA.

I used that as the boundary for the repo. I did not turn this into a broader document intelligence product or a training pipeline because that would exceed the source spec.

## Architecture

```text
client
  -> FastAPI gateway
      -> job store
      -> queue
      -> worker orchestrator
          -> memory-aware scheduler
          -> OCR engine
          -> VLM engine
          -> fused OCR+VLM pipeline
      -> metrics endpoint
      -> cache
```

### Request flow

1. A client submits a job to `/ocr`, `/vlm`, or `/pipeline`.
2. The API persists a job record and enqueues it.
3. A background worker pulls a small batch from the queue.
4. The scheduler estimates memory footprint per job and chooses a safe batch.
5. The selected engine runs.
6. Results are cached and written back to the job store.
7. Prometheus metrics record queue depth, batch sizes, latency, and memory estimates.

## Repository layout

```text
app/
  api/            FastAPI entrypoints and shared dependencies
  core/           config, logging, metrics
  models/         Pydantic request and job schemas
  services/       queue, cache, scheduler, OCR/VLM engines, worker orchestration
charts/
  ocr-vlm-stack/  Helm chart
cpp/
  frame_budget_planner.cpp
k8s/              Kubernetes manifests
samples/          Generated sample images
scripts/          seed, smoke, benchmark, artifact helpers
tests/            API and scheduler tests
```

## Core design decisions

### 1. Queue-backed workers instead of inline inference
Inline OCR or VLM calls make a service easy to demo and hard to operate. The queue layer keeps API latency stable during bursts and makes it easier to reason about concurrency, retries, and resource packing.

### 2. Memory-aware scheduling before throughput tuning
For GPU-heavy serving, a pretty benchmark is not enough. The scheduler estimates per-document memory and prevents large jobs from overrunning the budget. The numbers are approximate in the local build, but the scheduling boundary is the important piece.

### 3. Mock engines with stable interfaces
The local repo avoids shipping heavyweight OCR and CUDA dependencies by default. Instead, the engines have clear seams where a production runtime could replace them.

### 4. Observability is part of the core path
Metrics are not bolted on later. Queue depth, job latency, batch size, and memory estimates are all emitted in the same code path that processes work.

## Local setup

### Prerequisites

- Python 3.10+
- `g++` for the small C++ utility
- Optional: Docker and Docker Compose

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Generate sample images

```bash
python scripts/seed_samples.py
```

### Run the API

```bash
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/metrics`
- `http://127.0.0.1:8000/healthz`

## Example API usage

### Submit an OCR job

```bash
curl -X POST http://127.0.0.1:8000/ocr   -H "Content-Type: application/json"   -d '{
    "items": [
      {
        "document_id": "invoice-1001",
        "text_hint": "Invoice 1001 total $44.18",
        "image_width": 1280,
        "image_height": 720,
        "page_count": 1
      }
    ],
    "language": "en",
    "use_layout": true
  }'
```

### Submit a VLM job

```bash
curl -X POST http://127.0.0.1:8000/vlm   -H "Content-Type: application/json"   -d '{
    "items": [
      {
        "document_id": "badge-17",
        "text_hint": "Employee badge",
        "image_width": 1024,
        "image_height": 768,
        "page_count": 1
      }
    ],
    "prompt": "Summarize the image and identify visible objects",
    "max_tokens": 128
  }'
```

### Submit the fused pipeline

```bash
curl -X POST http://127.0.0.1:8000/pipeline   -H "Content-Type: application/json"   -d '{
    "items": [
      {
        "document_id": "lab-report-22",
        "text_hint": "Observation stable",
        "image_width": 1600,
        "image_height": 1200,
        "page_count": 2
      }
    ],
    "prompt": "Extract key entities and summarize layout",
    "language": "en"
  }'
```

### Poll for results

```bash
curl http://127.0.0.1:8000/jobs/<job_id>
```

## Environment variables

| Variable | Purpose | Default |
|---|---|---|
| `MAX_BATCH_SIZE` | Maximum jobs the worker tries to batch | `4` |
| `BATCH_WAIT_MS` | Micro-batching wait window | `120` |
| `GPU_MEMORY_BUDGET_MB` | Estimated GPU memory cap for the scheduler | `4096` |
| `GPU_WORKER_COUNT` | Worker count surface for future expansion | `1` |
| `CACHE_TTL_SECONDS` | Result cache TTL | `300` |
| `ENABLE_REDIS` | Toggle for Redis-aware configuration | `false` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |

## C++ helper

The repository includes a tiny utility that estimates tiling and memory for oversized frames.

```bash
g++ -O2 -std=c++17 cpp/frame_budget_planner.cpp -o cpp/frame_budget_planner
./cpp/frame_budget_planner 1920 1080 2
```

## Docker

```bash
docker compose up --build
```

The compose file runs the API and a Redis sidecar. The local implementation does not require Redis to function, but it keeps the deployment footprint close to the README-backed stack.

## Kubernetes and Helm

- `k8s/` contains deployment, service, and HPA manifests
- `charts/ocr-vlm-stack/` contains a lightweight Helm chart with values for image, autoscaling, and environment settings

## Testing

```bash
pytest
```

## Smoke test

Start the server first, then run:

```bash
python scripts/smoke_test.py
```

## Benchmark

Start the server first, then run:

```bash
python scripts/benchmark.py
```

This submits a small burst of pipeline jobs and reports average, p95, and max completion time from the client side.

## Observability

The metrics endpoint exposes:

- job submission totals
- job completion totals by type and status
- end-to-end job latency
- queue depth
- observed batch sizes
- estimated GPU memory usage
- memory-cache hits

## License

MIT


