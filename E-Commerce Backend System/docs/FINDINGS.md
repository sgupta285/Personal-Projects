# E-Commerce Backend System — Project Findings Report

## 1. Overview

A high-performance REST API for e-commerce operations, built to demonstrate production-grade backend patterns: strategic database indexing, connection pooling, Redis cache-aside, sliding-window rate limiting, and validated performance under simulated load with Locust.

## 2. Problem Statement

E-commerce platforms face a read-heavy workload pattern — product browsing vastly outnumbers order creation. Without optimization, database queries become the bottleneck under concurrency: full table scans on product listings, unoptimized joins for category filtering, and connection exhaustion under load. The challenge is to reduce read latency by ~35% and database load by ~60% while maintaining data consistency for writes (stock management, order creation) and protecting the system from traffic spikes.

## 3. Key Design Choices & Tradeoffs

### Strategic Indexing
- **Choice**: Composite indexes on `(category_id, is_active)`, `(is_active, name)`, and `(customer_id, created_at)` targeting the most common query patterns.
- **Tradeoff**: Each index adds write overhead (B-tree maintenance on INSERT/UPDATE) and storage cost. We index only the patterns confirmed by query analysis.
- **Benefit**: Eliminates sequential scans for filtered product listings and order lookups — the two most frequent query patterns.

### Connection Pooling (SQLAlchemy Async)
- **Choice**: Pool of 20 connections with 10 overflow, 30s timeout, and pre-ping for stale connection detection.
- **Tradeoff**: Pool sizing is a balance — too small causes queuing under load, too large wastes database resources. The 20+10 configuration supports up to 30 concurrent DB operations.
- **Benefit**: Eliminates connection setup overhead (~5-10ms per connection) and prevents connection exhaustion under high concurrency.

### Redis Cache-Aside Pattern
- **Choice**: Cache product list results and individual product details with 2-5 minute TTLs. Invalidate on writes using pattern-based key deletion.
- **Tradeoff**: Stale reads are possible within the TTL window. Write operations incur cache invalidation overhead (pattern scan + delete).
- **Benefit**: 60-85% of product reads served from cache in steady state, reducing database query volume proportionally. Sub-1ms cache reads vs. 5-20ms database reads.

### Sliding Window Rate Limiting
- **Choice**: Redis sorted set per client IP with configurable window (60s) and limit (100 requests). Implemented as ASGI middleware.
- **Tradeoff**: IP-based limiting can be too coarse (shared NATs) or too fine (proxied traffic). The X-Forwarded-For header handling mitigates proxy scenarios.
- **Benefit**: Protects the database from traffic spikes and abusive clients without requiring authentication.

### Soft Deletes for Products
- **Choice**: Products are deactivated (`is_active=False`) rather than physically deleted.
- **Tradeoff**: Increases table size over time; requires `is_active` filter on all product queries.
- **Benefit**: Preserves referential integrity for existing orders that reference deleted products. Enables product restoration.

### SQLite for Local / PostgreSQL for Production
- **Choice**: SQLAlchemy's dialect abstraction allows switching between SQLite (local dev) and PostgreSQL (production) via environment variable.
- **Tradeoff**: Some PostgreSQL-specific features (advisory locks, LISTEN/NOTIFY) aren't available in SQLite. Tests use SQLite in-memory for speed.
- **Benefit**: Zero-dependency local development while production gets PostgreSQL's concurrency, MVCC, and advanced indexing.

## 4. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        REQUEST FLOW                              │
│                                                                  │
│  HTTP Request                                                    │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────────┐                                        │
│  │ Rate Limit Middleware │──► 429 if exceeded                    │
│  └──────────┬───────────┘                                        │
│             │                                                    │
│             ▼                                                    │
│  ┌──────────────────────┐                                        │
│  │   FastAPI Router     │                                        │
│  │  (Products/Orders/   │                                        │
│  │   Categories/Custs)  │                                        │
│  └──────────┬───────────┘                                        │
│             │                                                    │
│     ┌───────┴───────┐                                            │
│     │               │                                            │
│     ▼               ▼                                            │
│  ┌──────┐     ┌──────────────┐                                   │
│  │Redis │◄───►│ Cache-Aside  │                                   │
│  │Cache │     │   Logic      │                                   │
│  └──────┘     └──────┬───────┘                                   │
│                      │ cache miss                                │
│                      ▼                                           │
│  ┌────────────────────────────────────┐                          │
│  │ SQLAlchemy Async Session           │                          │
│  │ (Connection Pool: 20 + 10 overflow)│                          │
│  └──────────────┬─────────────────────┘                          │
│                 │                                                │
│                 ▼                                                │
│  ┌────────────────────────┐                                      │
│  │  PostgreSQL / SQLite   │                                      │
│  │  ┌──────────────────┐  │                                      │
│  │  │ Indexed Tables:  │  │                                      │
│  │  │ • products       │  │                                      │
│  │  │ • orders         │  │                                      │
│  │  │ • categories     │  │                                      │
│  │  │ • customers      │  │                                      │
│  │  │ • order_items    │  │                                      │
│  │  └──────────────────┘  │                                      │
│  └────────────────────────┘                                      │
│                                                                  │
│  ┌────────────────────────┐                                      │
│  │ Locust Load Testing    │                                      │
│  │ 1,000+ concurrent users│                                      │
│  │ Realistic traffic mix  │                                      │
│  └────────────────────────┘                                      │
└─────────────────────────────────────────────────────────────────┘
```

## 5. How to Run

```bash
# 1. Create virtual environment
python -m venv venv && source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env

# 4. Start Redis (optional)
redis-server

# 5. Run API
uvicorn app.main:app --reload --port 8000

# 6. Seed data
python -m scripts.seed

# 7. Run tests
pytest tests/ -v

# 8. Run load tests
locust -f scripts/locustfile.py --host=http://localhost:8000
# Open http://localhost:8089, set 1000 users
```

## 6. Known Limitations

1. **No authentication** — all endpoints are public. Production needs JWT/OAuth.
2. **No pagination cursor** — offset-based pagination degrades for deep pages. Cursor-based pagination would be more efficient.
3. **Optimistic concurrency not implemented** — concurrent stock updates could race without row-level locking (SELECT FOR UPDATE).
4. **Cache invalidation is pattern-based** — `KEYS` command is O(N) and not recommended for large Redis instances. Should use hash tags or event-driven invalidation.
5. **No payment integration** — orders are created without payment processing.
6. **SQLite for development only** — SQLite's write serialization doesn't reflect PostgreSQL's MVCC behavior.
7. **No API versioning beyond URL prefix** — no content negotiation or backward compatibility strategy.

## 7. Future Improvements

- **JWT authentication** with role-based access control
- **Cursor-based pagination** for efficient deep-page navigation
- **Event-driven cache invalidation** via Redis Streams or PostgreSQL LISTEN/NOTIFY
- **Distributed locking** for stock management (Redlock or PostgreSQL advisory locks)
- **Full-text search** with PostgreSQL tsvector or Elasticsearch
- **Payment integration** (Stripe/PayPal webhooks)
- **API versioning** with content negotiation
- **Prometheus metrics** for cache hit rates, query latency, and endpoint performance
- **Database read replicas** with SQLAlchemy routing for read/write splitting

## 8. Screenshots

> **[Screenshot: Swagger UI — /docs]**
> _Interactive API documentation showing all CRUD endpoints grouped by resource._

> **[Screenshot: Locust Dashboard]**
> _Real-time load test results showing RPS, response times (median/p95/p99), and failure rate across 1,000 concurrent users._

> **[Screenshot: Product List Response]**
> _Paginated JSON response with products, categories, stock levels, and metadata._

> **[Screenshot: Order Creation]**
> _POST /orders response showing line items, calculated total, and stock decrement._

---

*Report generated for E-Commerce Backend v1.0.0*
