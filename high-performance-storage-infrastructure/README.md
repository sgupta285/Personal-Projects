# High-Performance Storage Infrastructure

A reproducible storage benchmarking project built around a MinIO-first object-storage architecture, a hot-object cache layer, resilience experiments, and performance reporting.

The repository is designed to be useful in two modes:

1. **Local simulation mode** for quick benchmarking without Docker or cloud dependencies.
2. **Containerized MinIO mode** using Docker Compose for a more realistic object-storage deployment with Prometheus and Grafana configs included.

## What this project covers

- object storage benchmarking across multiple object sizes and concurrency levels
- throughput and latency measurement for uploads and downloads
- hot-object cache behavior and cache hit analysis
- resilience scenarios including restart recovery, artificial throttling, and simulated disk pressure
- tuning notes for concurrency, multipart thresholds, and cache sizing
- monitoring assets for Prometheus and Grafana

## Architecture

```text
benchmark client
   |----> object store abstraction ----> local filesystem or MinIO
   |----> cache abstraction ----------- > in-memory cache
   |
   +----> benchmark results (CSV / JSON)
   +----> reports and plots
   +----> monitoring configs
```

## Quick start

### Option 1: local simulation mode

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
make bootstrap
```

Outputs are written to:

- `data/benchmarks/`
- `data/reports/`

### Option 2: MinIO mode with Docker Compose

```bash
docker compose up -d
```

Then point the benchmark runner at MinIO:

```bash
export STORAGE_MODE=minio
export CACHE_MODE=memory
python scripts/run_benchmarks.py
```

The default MinIO console is available at `http://localhost:9001` and Grafana at `http://localhost:3000`.

## Repository layout

```text
high-performance-storage-infrastructure/
├── config/
├── data/
├── docs/
├── monitoring/
├── scripts/
├── src/storageinfra/
└── tests/
```

## Benchmark methodology

The benchmark runner executes:

- **upload** workloads across object sizes from 64 KB to 1 MB
- **download_cold** workloads against previously written objects
- **download_hot** workloads that repeatedly access a small hot set through a cache

Each scenario is evaluated under multiple concurrency levels so the summary can show how throughput scales and where latency begins to bend.

## Resilience scenarios

The repo includes reproducible resilience checks for:

- restart recovery
- throttled network simulation
- simulated disk pressure
- cache on vs cache off comparison for hot objects

## Included generated artifacts

This zip ships with generated local benchmark outputs so the repository feels complete immediately after unzip:

- `data/benchmarks/raw_results.csv`
- `data/benchmarks/summary.csv`
- `data/benchmarks/summary.json`
- `data/benchmarks/resilience_results.json`
- `data/reports/performance_report.md`
- `data/reports/dashboard.html`
- `data/reports/throughput_by_concurrency.png`
- `data/reports/latency_p95_by_size.png`
- `docs/FINDINGS.md`

## Notes

- The primary supported storage backend is MinIO. Ceph is intentionally left out of the runnable setup to keep the project local and practical.
- Redis is referenced in the deployment topology, but the benchmark defaults to an in-memory cache so the repo works with a single Python install.

## License 

MIT
