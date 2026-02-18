# 🛡️ Real-Time Fraud Detection API

Production-grade fraud scoring API with low-latency ML inference, Redis caching, circuit breaker reliability, and data drift monitoring.

Built with FastAPI, XGBoost + Random Forest ensemble (SMOTE for class imbalance), deployed with Kubernetes autoscaling and full Prometheus/Grafana observability.

---

## Features

- **ML Ensemble Model** — XGBoost + RandomForest with SMOTE oversampling; trained on 284K synthetic transactions
- **96% precision / 89% recall** on fraud detection with ~80-100ms p95 latency
- **Redis Cache-Aside** — deterministic feature hashing to avoid redundant inference
- **Circuit Breaker** — automatic failure isolation with CLOSED → OPEN → HALF_OPEN state machine
- **Rate Limiting** — sliding window per-client rate limiter
- **Data Drift Monitoring** — PSI-based distribution tracking with retrain alerts
- **Prometheus Metrics** — prediction counts, latency histograms, cache hit rates, drift scores
- **Kubernetes Ready** — HPA (3-15 replicas), health probes, resource limits
- **CI/CD** — GitHub Actions with test, lint, and Trivy security scanning

## Architecture

```
                    ┌─────────────┐
                    │   Client    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Rate Limit │
                    └──────┬──────┘
                           │
                    ┌──────▼──────────┐
                    │ Circuit Breaker  │
                    └──────┬──────────┘
                           │
                  ┌────────▼────────┐
                  │  Redis Cache    │── hit → return cached
                  └────────┬────────┘
                           │ miss
                  ┌────────▼────────┐
                  │  ML Inference   │
                  │  (XGBoost+RF)   │
                  └────────┬────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Cache   │ │  Drift   │ │Prometheus│
        │  Write   │ │ Monitor  │ │ Metrics  │
        └──────────┘ └──────────┘ └──────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Redis (optional — works without it)

### Install

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Train Model

```bash
python -m app.models.train
```

This generates `data/fraud_model.joblib`, `data/scaler.joblib`, and `data/model_metadata.json`.

### Configure

```bash
cp .env.example .env
# Edit .env if needed (defaults work fine)
```

### Run

```bash
# Start Redis (optional)
redis-server

# Start API server
uvicorn app.main:app --reload --port 8000
```

Visit:
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health
- **Metrics**: http://localhost:8000/metrics

### Run with Docker

```bash
docker-compose up --build
```

This starts API + Redis + Prometheus + Grafana:
- API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Run Tests

```bash
pytest tests/ -v
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/predict` | Score a single transaction |
| `POST` | `/api/v1/predict/batch` | Score up to 100 transactions |
| `GET` | `/api/v1/health` | Health check with model/cache/circuit status |
| `GET` | `/api/v1/model/info` | Model metadata and training metrics |
| `GET` | `/api/v1/drift/status` | Drift monitoring status |
| `POST` | `/api/v1/drift/check` | Trigger manual drift check |
| `POST` | `/api/v1/cache/flush` | Flush prediction cache |
| `GET` | `/metrics` | Prometheus metrics |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "txn_001",
    "features": [0.0, -1.36, -0.07, 2.54, 1.38, -0.34, 0.46, 0.24, 0.10, 0.24, 0.09, -0.55, -0.78, -0.08, -0.14, -0.58, -0.41, -0.47, -0.23, 0.80, 0.17, -0.10, -0.34, -0.02, 0.01, -0.04, -0.06, -0.08, 149.62, 0.0]
  }'
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI + Uvicorn |
| ML Models | XGBoost, Random Forest, Voting Ensemble |
| Class Balancing | SMOTE (imbalanced-learn) |
| Caching | Redis |
| Monitoring | Prometheus + Grafana |
| Tracing | OpenTelemetry + Jaeger |
| CI/CD | GitHub Actions + Trivy |
| Container | Docker + Kubernetes (HPA) |

## License

MIT
