# Findings

## Overview

This project turns common infrastructure chores into deterministic, config-driven CLI workflows. Instead of manually cloning service folders, copying Helm manifests, and hand-editing environment files, operators define intent in a small TOML config and let the framework generate consistent outputs.

## Architecture

The repo is organized around four layers:

1. CLI layer for user-facing commands.
2. Config and validation layer for strict metadata parsing.
3. Template rendering layer for service, environment, and Helm assets.
4. Execution layer for safe validation wrappers and rollout planning.

## Methodology

The automation was designed around five realistic operator tasks:
- initialize a new service
- create a new environment bundle
- render deployment manifests
- validate Terraform safely
- generate a rollout plan before deployment

Each command supports explicit output paths and dry-run behavior where it matters.

## Findings and results

Using config-driven generation removes several common sources of error:
- inconsistent naming across repos, services, and namespaces
- stale copy-paste values in manifests
- missing environment defaults
- rollout steps that live only in tribal knowledge
- Terraform validation being skipped until late in the flow

The generated outputs in `examples/generated/` show how a single service definition can produce app scaffolding, CI metadata, deployment YAML, and environment-specific rollout instructions from one source of truth.

## Limitations

- The framework is intentionally local-first and does not call cloud APIs directly.
- Terraform and Helm wrappers are best-effort if those binaries are not installed.
- The service scaffold is opinionated and optimized for containerized Python services.
- Secrets are placeholder stubs by design and should be wired to a proper secret manager in production.
