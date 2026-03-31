# Infrastructure Automation Framework

A practical internal-platform-style tooling repo that automates repetitive infrastructure work: service scaffolding, environment creation, Helm manifest rendering, rollout planning, and Terraform validation. The project is intentionally local-first and config-driven so it is easy to review, run, and extend without needing cloud credentials just to understand how it works.

## What this repo does

- initializes a new service from metadata instead of manual copy-paste
- creates environment config bundles for dev, staging, and prod
- renders Kubernetes manifests from service metadata
- validates Terraform directories with dry-run safety built in
- generates rollout plans with explicit steps and checkpoints
- ships example configs and generated outputs so the repo feels complete when opened

## Why this architecture

Most infra automation repos start useful but degrade into script sprawl. This one stays structured by splitting responsibilities into a small CLI, a template layer, validators, and sample configs. The result feels closer to an internal developer platform tool than a one-off shell script folder.

## Core commands

```bash
infraforge init-service examples/configs/service_orders.toml --output examples/generated/service-orders
infraforge create-env examples/configs/env_dev.toml --output examples/generated/env-dev
infraforge render-helm examples/configs/service_orders.toml --env examples/configs/env_dev.toml --output examples/generated/helm-orders
infraforge validate-terraform examples/terraform/sample-stack --dry-run
infraforge rollout-plan examples/configs/rollout_orders.toml --output examples/generated/rollout-orders
```

## Repository layout

```text
infrastructure-automation-framework/
├── docs/
├── examples/
│   ├── configs/
│   ├── generated/
│   └── terraform/
├── src/infraforge/
├── tests/
└── .github/workflows/
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
infraforge demo --output examples/generated
pytest
```

## Demo outputs included

The repository already includes generated sample outputs under `examples/generated/`:
- scaffolded `orders-api` service
- `dev` environment bundle
- rendered Helm manifests
- rollout plan markdown and JSON
- validation summary

## Testing

```bash
pytest
```

## License

MIT
