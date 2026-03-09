# Architecture Notes

## Service boundaries

### API service
The API handles ad ingestion and reviewer actions. It is intentionally lightweight:
- validate payloads
- store metadata
- enqueue moderation work
- expose analytics and review endpoints

### Moderation worker
The worker is where the risk logic lives:
- consume `ads.submitted`
- run policy rules
- run the lightweight classifier
- combine scores into a final risk decision
- persist outcomes
- publish `ads.moderated`

### Redis
Redis stores the latest risk score and moderation snapshot per ad. In a production system, this is the sort of cache another service might hit before allowing an ad into an auction or delivery pipeline.

### Postgres
Postgres stores the source of truth:
- advertisers
- ad submissions
- moderation fields
- manual review records

### Frontend
The React dashboard gives reviewers and operators a quick view of:
- status distribution
- top policy hits
- risky advertisers
- recent ads and their moderation state

## Data model choices

The schema is intentionally simple. In a production environment I would probably separate ad creative metadata, moderation events, and policy-hit details into their own tables, but for a portfolio project a denormalized ad table keeps the code easier to follow while still showing the core workflow.

## Why Kafka

Kafka makes the ingestion and moderation steps loosely coupled. That mirrors how a real ads platform would keep ad submission latency low while letting downstream scanners scale independently.

## Why combine rules and ML

Rules are precise and easy to audit. ML is flexible and catches language patterns that do not map neatly to exact match rules. For moderation systems, the combination is usually more useful than either one alone.

## Cloud deployment path

This repo is designed so it can be deployed a few ways:
- Docker Compose for local development
- ECS or Cloud Run for small managed deployments
- Kubernetes later if the system outgrows a simple setup
