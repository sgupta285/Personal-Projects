# Event Management System

A full-stack event management platform for conferences, meetups, and workshops. The project covers event creation, ticket tiers, registration, waitlist handling, check-in, confirmation workflows, and organizer analytics.

The build is grounded in the uploaded portfolio README, which describes an event platform with registration, ticketing, attendee management, check-in, waitlist automation, admin tools, and a stack centered on React, TypeScript, Python, Django, PostgreSQL, Stripe, and SendGrid.

## What this repo includes

- Django backend with a modular app layout
- React + TypeScript frontend for organizers and attendees
- Ticket tiers with capacity enforcement
- Registration flow with paid and free tickets
- Waitlist promotion service when space opens up
- QR-style check-in token generation and validation
- Payment provider abstraction with a Stripe-compatible stub
- Email provider abstraction with a SendGrid-compatible stub
- Organizer analytics endpoints and dashboard cards
- Docker Compose for local development
- Seed script and test suite

## Architecture

### Backend

The backend is organized into focused Django apps:

- `core`: shared utilities, provider adapters, health checks
- `events`: event, venue, and ticket tier management
- `registrations`: checkout, attendee records, waitlist logic, analytics
- `checkin`: admission tokens and on-site validation

### Frontend

The frontend is a Vite React app with a lightweight dashboard and attendee-facing event discovery flow.

- organizer dashboard
- event detail page
- registration checkout form
- attendee list and check-in page

## Folder structure

```text
event-management-system/
├── backend/
│   ├── config/
│   ├── apps/
│   │   ├── core/
│   │   ├── events/
│   │   ├── registrations/
│   │   └── checkin/
│   ├── manage.py
│   └── tests/
├── frontend/
│   ├── src/
│   └── package.json
├── infra/
├── scripts/
└── docker-compose.yml
```

## Core features

### Organizer workflow

- create and update events
- define ticket tiers with price and capacity
- review attendee roster and registration status
- promote people from the waitlist
- track check-ins and registration totals

### Attendee workflow

- browse published events
- view ticket tiers and seat availability
- register for free or paid tickets
- receive confirmation metadata and admission token
- join the waitlist when a tier is sold out

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Full stack with Docker

```bash
docker compose up --build
```

## Environment variables

### Backend

Copy `.env.example` to `.env` inside `backend/`.

| Variable | Purpose | Default |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key | `dev-secret-key` |
| `DJANGO_DEBUG` | Debug toggle | `1` |
| `DATABASE_URL` | Database connection string | SQLite fallback |
| `EMAIL_PROVIDER` | `console` or `sendgrid_stub` | `console` |
| `PAYMENT_PROVIDER` | `stub` or `stripe_stub` | `stub` |
| `FRONTEND_BASE_URL` | Used in confirmation links | `http://localhost:5173` |

## Testing

```bash
cd backend
pytest
```

## Demo accounts

The seed command creates:

- organizer: `organizer@example.com`
- check-in staff: `staff@example.com`

Password for both demo users: `demo12345`

## API summary

- `GET /api/events/` published events
- `POST /api/events/` create event
- `GET /api/events/{id}/` event detail
- `POST /api/registrations/checkout/` register attendee
- `POST /api/registrations/waitlist/` join waitlist
- `POST /api/registrations/promote/` move waitlist attendee into confirmed registration
- `POST /api/checkin/validate/` validate check-in token
- `GET /api/analytics/events/{id}/summary/` organizer summary

## License

MIT

