# Restaurant Discovery Platform

A full-stack restaurant discovery and reservation platform built around the workflow people actually use when deciding where to eat: search, compare, read reviews, and book a table. The project is grounded in the README brief for this portfolio entry, which described a product with search, filtering, reviews, booking integration, third-party API hooks, and user-generated content management in a realistic full-stack setup.

The implementation in this repository is intentionally production-minded without becoming bloated. The backend handles restaurant search, user accounts, review submission and moderation, booking-provider integration, and lightweight observability. The frontend stays focused on the customer journey rather than trying to impersonate a complete consumer marketplace.

## What this repository includes

- FastAPI backend with search, review, and reservation APIs
- React + TypeScript frontend for discovery and detail views
- Seeded restaurant catalog for local development
- Mock third-party adapters for booking and place enrichment
- Review moderation workflow to support user-generated content management
- Docker Compose setup for local full-stack development
- Backend tests covering search, reviews, moderation, and reservations
- Benchmark and smoke scripts for quick validation
- Kubernetes manifests for simple deployment scaffolding

## Real-world framing

Consumer restaurant products usually fail in one of two ways. Either the discovery side is polished but the reservation handoff is brittle, or the booking experience works but the review and filtering experience feels thin. I wanted this repository to sit in the middle. It is not just a list of restaurants and it is not just a booking form. It is a small but coherent platform that shows how search, user-generated content, and third-party booking hooks fit together.

The README source for this project emphasizes these exact ideas: search, filtering, reviews, booking integration, full-stack development, third-party API integration, and user-generated content management. That is the scope I preserved here.

## Source-of-truth interpretation

The attached portfolio README gives this project a lighter summary than some of the earlier infrastructure-heavy builds. Specifically, it describes the project as a **Restaurant Discovery Platform** and says it includes search, filtering, reviews, and booking integration, while showcasing full-stack development, third-party API integration, and user-generated content management.

Because the original summary is intentionally concise, I kept the repo disciplined and only filled in implementation details that are directly implied by that description:

- Discovery requires searchable restaurant records and filterable catalog APIs
- Reviews imply user accounts, content submission, and moderation state
- Booking integration implies an adapter boundary rather than hard-coding reservation logic into the API
- Third-party API integration implies a provider abstraction that can be swapped for a live service later
- Full-stack delivery implies both backend APIs and a working frontend surface

## Architecture

```text
frontend (React + TypeScript)
  |
  | HTTP
  v
backend (FastAPI)
  |- auth router
  |- restaurant search router
  |- review router
  |- reservation router
  |- metrics + health endpoints
  |
  |- SQLAlchemy models
  |- search service
  |- booking provider adapter
  |- places enrichment adapter
  v
SQLite by default, PostgreSQL-compatible model layer
```

### Core design decisions

**1. Provider boundaries instead of vendor lock-in**

The booking flow goes through a provider abstraction. For local development, the repository uses a mock OpenTable-style provider that returns deterministic confirmation codes. The same pattern is used for place enrichment.

**2. Moderated reviews instead of direct publication**

User-generated content is useful until it is untrusted. Reviews enter the system as `pending`, and an admin account can approve or reject them. Restaurant ratings only include approved reviews.

**3. Search first, not map first**

The most important experience in a lightweight project repo is search and filtering. I prioritized queryable restaurant discovery APIs over map rendering or large geospatial dependencies.

**4. SQLite locally, PostgreSQL-friendly models**

The schema runs locally with SQLite for simplicity, but the SQLAlchemy model layer is structured so the app can move to PostgreSQL without architectural rewrites.

## Repository structure

```text
restaurant-discovery-platform/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── deps.py
│   │   ├── main.py
│   │   ├── metrics.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── scripts/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles.css
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env.example
├── infra/
│   └── k8s/
├── scripts/
│   ├── benchmark_search.py
│   └── smoke_test.py
├── docker-compose.yml
└── README.md
```

## Core features

### 1. Restaurant discovery

- Search by free text across name, cuisine, neighborhood, and description
- Filter by city, cuisine, vegetarian friendliness, reservation availability, and price tier
- Sort by rating, review volume, price, or distance when user coordinates are supplied
- Fetch restaurant detail views with approved reviews and enrichment metadata

### 2. Reviews and moderation

- User registration and login
- Authenticated review submission
- One review per restaurant per user
- Admin moderation queue for pending reviews
- Ratings recalculated only from approved reviews

### 3. Reservation flow

- Authenticated reservation creation
- Restaurant-level control over reservation availability
- Provider confirmation codes generated through adapter boundary
- Personal reservation history endpoint

### 4. Third-party integration hooks

- Mock booking provider that mirrors the shape of a real booking API integration
- Mock places enrichment provider for data like open status and popular times summary
- Both integrations can be swapped out without rewriting route logic

### 5. Operational basics

- `/health` endpoint for container checks
- `/metrics` endpoint for Prometheus scraping
- Lightweight request count and latency histograms
- Docker Compose for local bring-up

## Backend API summary

### Authentication

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Restaurants

- `GET /api/v1/restaurants`
- `GET /api/v1/restaurants/{restaurant_id}`

### Reviews

- `POST /api/v1/reviews/restaurants/{restaurant_id}`
- `GET /api/v1/reviews/restaurants/{restaurant_id}`
- `GET /api/v1/reviews/moderation/pending`
- `POST /api/v1/reviews/moderation/{review_id}`

### Reservations

- `POST /api/v1/reservations/restaurants/{restaurant_id}`
- `GET /api/v1/reservations/me`

### System

- `GET /health`
- `GET /metrics`

## Data model notes

### `users`

Stores login identity, display name, password hash, and role. A user can be a customer or admin.

### `restaurants`

Stores core catalog fields such as cuisine, neighborhood, price tier, description, geolocation, and whether the restaurant accepts online reservations.

### `reviews`

Stores rating, title, body, moderation status, and the link to the author and restaurant. The schema enforces one review per user per restaurant.

### `reservations`

Stores reservation time, party size, status, provider name, provider confirmation code, and notes.

## Environment variables

### Backend

Copy `backend/.env.example` to `backend/.env` if you want to customize settings.

| Variable | Purpose |
|---|---|
| `APP_NAME` | FastAPI application title |
| `ENVIRONMENT` | Runtime environment label |
| `SECRET_KEY` | JWT signing key |
| `DATABASE_URL` | SQLite or PostgreSQL connection string |
| `CORS_ORIGINS` | Comma-separated frontend origins |
| `BOOKING_PROVIDER` | Current booking provider label |
| `PLACES_PROVIDER` | Current enrichment provider label |

### Frontend

Copy `frontend/.env.example` to `frontend/.env`.

| Variable | Purpose |
|---|---|
| `VITE_API_BASE` | Base URL for the backend API |

## Local setup

### Backend only

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend seeds sample users and restaurants automatically the first time it boots.

Default seeded credentials:

- Admin: `moderator.admin@example.com` / `password123`
- Demo user: `alex@example.com` / `password123`

### Frontend only

```bash
cd frontend
npm install
npm run dev
```

### Full stack with Docker Compose

```bash
docker compose up --build
```

This starts:

- backend on `http://localhost:8000`
- frontend on `http://localhost:5173`

## Example API usage

### Search Chicago restaurants with vegetarian filter

```bash
curl "http://localhost:8000/api/v1/restaurants?city=Chicago&vegetarian=true"
```

### Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jordan@example.com",
    "full_name": "Jordan Lee",
    "password": "password123"
  }'
```

### Log in

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jordan@example.com",
    "password": "password123"
  }'
```

### Create a reservation

```bash
curl -X POST http://localhost:8000/api/v1/reservations/restaurants/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_time": "2026-04-10T19:00:00Z",
    "party_size": 4,
    "notes": "Window seat if available"
  }'
```

## Testing

Backend tests live under `backend/tests` and cover the main user journey.

```bash
cd backend
pytest
```

Covered flows:

- discovery search and filtering
- review creation
- review moderation by admin
- reservation creation with provider confirmation
- distance-based sorting

## Benchmarking and smoke validation

### Smoke test

Bring up the backend first, then run:

```bash
python scripts/smoke_test.py
```

### Search benchmark

```bash
python scripts/benchmark_search.py
```

This script measures average and p95 latency for repeated search requests against the local API.

## Deployment notes

This repository includes lightweight Kubernetes manifests under `infra/k8s/`. They are intentionally simple and meant to show the path from local development to container deployment.

Important deployment assumptions:

- replace SQLite with PostgreSQL in shared environments
- mount secrets rather than keeping `.env` files in the container
- wire `/metrics` into a Prometheus scrape job
- swap mock providers for live booking and place-enrichment connectors

## Observability notes

The original project brief does not explicitly require a full observability stack, but the portfolio README consistently emphasizes production-minded delivery. To stay aligned with that style without overbuilding the repo, I added:

- request counters labeled by method, path, and status
- request latency histograms
- health endpoint for orchestration readiness and liveness
- simple smoke and benchmark scripts for repeatable validation

## Tradeoffs

A few things are deliberately simplified:

- The frontend is a focused demo interface, not a complete design system.
- The booking integration is mocked because the brief implies third-party integration but does not require coupling the repo to a live vendor.
- Restaurant search uses SQL text matching and lightweight distance sorting instead of full geospatial indexing.
- Moderation is an admin API flow rather than a separate back-office UI.

These tradeoffs keep the project believable and runnable while staying loyal to the source brief.

## Limitations

- No payment or prepaid reservation handling
- No image upload or asset moderation pipeline
- No email or SMS notification workflow
- No real external provider credentials included
- Frontend does not yet include account management screens beyond API-driven flows

## Reproducibility

The repository is designed to be reproducible from a fresh checkout:

1. install backend dependencies or use Docker Compose
2. boot the API, which auto-seeds the initial dataset
3. run the frontend against the local backend
4. validate with tests, smoke script, and benchmark script

That flow is enough to inspect the search experience, create content, moderate it, and test reservation booking end to end.
