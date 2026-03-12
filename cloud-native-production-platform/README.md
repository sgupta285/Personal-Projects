# Cloud-Native Production Platform

A production-style platform engineering project built around a small multi-service reference application, local container orchestration, and AWS infrastructure as code.

This repository is structured to show how I think about shipping a service beyond application code. It includes a working local environment with Docker Compose, service-level metrics, Prometheus and Grafana configuration, Terraform modules for AWS networking and ECS-based deployment, GitHub Actions CI/CD, architecture documentation, and operational runbooks.

## What is inside

- `services/` contains three containerized services:
  - `frontend`: static UI served through Nginx
  - `gateway`: public API layer and service aggregation
  - `catalog`: product inventory API
  - `orders`: order creation and read API
- `monitoring/` contains Prometheus scraping config, Grafana provisioning, and alert rules.
- `infra/terraform/` contains reusable Terraform modules plus dev and prod environments.
- `.github/workflows/ci.yml` runs tests, builds service images, and validates Terraform.
- `docs/` contains the architecture write-up, cost-aware design notes, rollback strategy, incident basics, generated screenshots, and findings.

## Why ECS instead of EKS here

For a small production platform or startup-stage environment, ECS on Fargate offers a simpler operational footprint than EKS. The Terraform in this repo reflects that tradeoff:
- fewer moving parts to manage
- lower operational overhead for a small team
- easier path to autoscaling stateless services
- still compatible with ALB, Route 53, CloudWatch, and Secrets Manager

If the platform later needs more control over scheduling, sidecars, or cluster-level policy, the same service boundaries here make an EKS migration straightforward.

## Local quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
make bootstrap
docker compose up --build
```

Open:
- Frontend: `http://localhost:8080`
- Gateway docs: `http://localhost:8000/docs`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Test

```bash
pytest
```

## Terraform layout

```text
infra/terraform/
├── environments/
│   ├── dev/
│   └── prod/
└── modules/
    ├── network/
    ├── service/
    ├── database/
    └── observability/
```

## Local service map

```text
Browser -> Frontend -> Gateway -> Catalog
                           \-> Orders
Prometheus -> scrape /metrics on all services
Grafana -> Prometheus dashboards
```

## Cost-aware choices

The Terraform and documentation intentionally separate dev and prod:
- **dev** favors lower-cost single-AZ defaults and fewer replicas
- **prod** increases desired count, enables autoscaling, and adds stronger guardrails

The repo is designed to be realistic without pretending every small service needs the most expensive possible setup.

## Operations notes included

- health checks and readiness paths
- rollback approach for bad container releases
- alert meanings and first checks
- incident recovery basics
- cost tradeoff thinking
- environment separation strategy

## Generated assets

Run `make bootstrap` to generate or refresh:
- `docs/screenshots/architecture-overview.png`
- `docs/screenshots/local-stack.png`
- `docs/screenshots/metrics-overview.png`

## Suggested GitHub description

Production-style cloud platform demo with containerized services, ECS-focused Terraform modules, Prometheus/Grafana observability, CI/CD workflow, and platform operations docs.
