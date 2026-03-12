# Rollout plan for orders-api

- version: 2026.03.12
- environment: dev
- namespace: commerce-dev
- strategy: canary

## Prechecks
- **terraform plan clean**: Confirm no unexpected infrastructure drift.
- **helm render reviewed**: Validate image tag, host, and resource requests before apply.
- **synthetic order flow**: Run smoke checks against create-order and list-order endpoints.

## Rollout phases
- shift traffic to 10% for orders-api:2026.03.12 and observe for 120s
- shift traffic to 25% for orders-api:2026.03.12 and observe for 120s
- shift traffic to 50% for orders-api:2026.03.12 and observe for 120s
- shift traffic to 100% for orders-api:2026.03.12 and observe for 120s

## Abort conditions
- **error rate spike**: 5xx error rate > 2% for 5m
- **latency regression**: p95 latency > 400ms for 10m

## Success metric
error_rate < 1% and p95_latency < 300ms
