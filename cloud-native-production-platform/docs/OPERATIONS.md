# Operations Notes

## Health checks

Each service exposes:
- `GET /health`
- `GET /metrics`

ALB target groups should point to `/health` for readiness and liveness checks.

## Rollback strategy

### Bad application deploy
1. Stop the rollout in GitHub Actions.
2. Repoint the ECS service to the last known-good task definition.
3. Verify health checks and request success at the ALB.
4. Confirm gateway dependency health before reopening traffic.

### Partial outage
1. Check ALB target health.
2. Check gateway logs first because it surfaces downstream failures quickly.
3. Confirm catalog and orders health independently.
4. If orders is unhealthy, inspect database connectivity and recent schema changes.

## Alert meanings

### GatewayHighLatencyP95
- likely causes: downstream slowness, container CPU pressure, noisy network path, recent deploy regression
- first checks: gateway logs, request volume, catalog and orders latency, CPU and memory

### OrderCreateErrors
- likely causes: dependency mismatch, invalid upstream payload, storage issue
- first checks: orders logs, recent order traffic, database write path, gateway error logs

## Incident basics

- protect the public API first
- roll back code before attempting risky hotfixes
- isolate whether the failure is gateway, dependency, or infrastructure
- keep stateful recovery separate from stateless service scaling
