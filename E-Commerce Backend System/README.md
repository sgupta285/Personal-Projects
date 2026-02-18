# 🛒 E-Commerce Backend System

High-performance REST API for e-commerce operations built with FastAPI, PostgreSQL/SQLite, and Redis. Designed for read-heavy workloads with strategic indexing, connection pooling, cache-aside pattern, and rate limiting.

Load-tested with Locust to validate performance under 1,000+ concurrent users.

---

## Features

- **FastAPI REST API** — full CRUD for products, categories, customers, and orders
- **Redis Cache-Aside** — transparent caching for read-heavy product queries with automatic invalidation on writes
- **Sliding Window Rate Limiting** — per-IP rate limiting via Redis sorted sets
- **Strategic Indexing** — composite indexes on category+active, price ranges, SKU lookups, and order lookups by customer
- **Connection Pooling** — SQLAlchemy async pool with configurable size, overflow, timeout, and pre-ping
- **Stock Management** — atomic stock decrement on order creation, restoration on cancellation
- **Soft Deletes** — products are deactivated, not removed
- **Locust Load Tests** — realistic traffic simulation with 1,000+ concurrent users
- **Async Everything** — fully async with SQLAlchemy 2.0 + asyncio

## Architecture

```
┌──────────────┐    ┌───────────────────────────────────────────┐
│   Clients    │    │              FastAPI Application           │
│              │───►│                                           │
│  (Locust /   │    │  ┌────────────┐  ┌─────────────────────┐ │
│   Browser)   │    │  │ Rate Limit │─►│  Route Handlers     │ │
│              │    │  │ Middleware │  │  (Products, Orders,  │ │
└──────────────┘    │  └────────────┘  │   Categories, etc.)  │ │
                    │                  └──────────┬───────────┘ │
                    │                    ┌────────┴────────┐    │
                    │                    │  Cache-Aside    │    │
                    │                    └───┬─────────┬───┘    │
                    │                        │         │        │
                    │                   ┌────▼───┐ ┌───▼────┐   │
                    │                   │ Redis  │ │ SQLAlch│   │
                    │                   │ Cache  │ │ (Pool) │   │
                    │                   └────────┘ └───┬────┘   │
                    │                                  │        │
                    │                          ┌───────▼──────┐ │
                    │                          │  PostgreSQL  │ │
                    │                          │  / SQLite    │ │
                    │                          └──────────────┘ │
                    └───────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- Redis (optional — degrades gracefully)

### Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
```

### Run

```bash
# Start Redis (optional)
redis-server

# Start server
uvicorn app.main:app --reload --port 8000

# Seed sample data
python -m scripts.seed
```

Visit http://localhost:8000/docs for interactive API documentation.

### Run with Docker (PostgreSQL)

```bash
docker-compose up --build
```

### Run Tests

```bash
pytest tests/ -v
```

### Run Load Tests

```bash
# Start the API first, then:
locust -f scripts/locustfile.py --host=http://localhost:8000

# Open http://localhost:8089, set 1000 users, spawn rate 50
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/products` | List products (filter, search, paginate) |
| `GET` | `/api/v1/products/:id` | Product detail |
| `POST` | `/api/v1/products` | Create product |
| `PUT` | `/api/v1/products/:id` | Update product |
| `DELETE` | `/api/v1/products/:id` | Soft-delete product |
| `GET` | `/api/v1/categories` | List categories |
| `POST` | `/api/v1/categories` | Create category |
| `GET` | `/api/v1/orders` | List orders |
| `POST` | `/api/v1/orders` | Create order (validates stock) |
| `PATCH` | `/api/v1/orders/:id/status` | Update order status |
| `GET` | `/api/v1/customers` | List customers |
| `POST` | `/api/v1/customers` | Create customer |
| `GET` | `/health` | Health check |

## Performance Results

Validated via Locust load testing:

| Metric | Result |
|--------|--------|
| Latency reduction | ~35% (with cache-aside) |
| DB load reduction | ~60% (cache offloads reads) |
| Concurrent users | 1,000+ sustained |
| Cache hit rate | 70-85% for product reads |

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (async) |
| Database | PostgreSQL / SQLite |
| ORM | SQLAlchemy 2.0 (async) |
| Cache | Redis |
| Load Testing | Locust |
| Container | Docker + docker-compose |

## License

MIT
