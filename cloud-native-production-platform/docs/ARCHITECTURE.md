# Architecture

## Reference application

The platform uses a small multi-service reference app because platform design is easier to evaluate when there is a concrete workload behind it.

- **frontend** serves a simple static UI
- **gateway** is the public API layer and dependency aggregator
- **catalog** returns product inventory
- **orders** persists and serves order records

## Local architecture

The local stack uses Docker Compose:
- frontend on port 8080
- gateway on port 8000
- catalog on port 8001
- orders on port 8002
- Prometheus on port 9090
- Grafana on port 3000

Prometheus scrapes `/metrics` from each application service. Grafana is pre-provisioned against Prometheus.

## AWS target architecture

The Terraform layout targets an ECS on Fargate deployment:
1. Route 53 entry
2. Application Load Balancer
3. ECS services for frontend, gateway, catalog, and orders
4. RDS PostgreSQL for the orders persistence layer
5. CloudWatch logs and metrics
6. autoscaling on CPU and memory targets

This is intentionally a pragmatic target architecture rather than an overbuilt platform. For a team that wants production basics with lower control-plane overhead, ECS is an efficient choice.

## Environments

The repo separates `dev` and `prod`:
- **dev** is cost-sensitive and defaults to lower desired counts
- **prod** scales higher, keeps stronger protections, and assumes stricter uptime goals

## Observability

- metrics: Prometheus scrape config plus Grafana dashboard
- logs: container stdout locally, CloudWatch logs in AWS
- health: `/health` on every service
- alerting: Prometheus alert rules included for local demonstration, mirrored conceptually to CloudWatch alarms or AMP in AWS

## Rollback and recovery

See `docs/OPERATIONS.md` for the release rollback approach, incident first checks, and service recovery notes.
