# Findings

## Overview

This project demonstrates a practical cloud-native platform pattern instead of a pure application repo. The value is in showing deployment thinking, service boundaries, observability, and operations readiness together.

## Architecture

- local development path uses Docker Compose and generated screenshots
- AWS target path uses Terraform modules for network, ECS services, database, and observability
- frontend, gateway, catalog, and orders are modeled as separate deployable units
- monitoring is based on Prometheus and Grafana locally, with CloudWatch-oriented operational notes for AWS

## Methodology

The implementation is intentionally split into:
1. runnable local services
2. infrastructure as code for cloud deployment
3. CI/CD pipeline configuration
4. operational documentation

This makes the repo easy to review in layers. A reviewer can read the docs, run the services locally, inspect metrics, then inspect the Terraform module structure.

## Findings and results

A good platform repo needs to answer more than “does the app run?” It should also answer:
- where requests enter
- how services are deployed
- how failures are detected
- how bad releases are rolled back
- what the cost tradeoffs are between environments

The strongest part of this repo is the separation between local developer ergonomics and production infrastructure shape. That is a realistic pattern for small teams.

## Limitations

- the AWS infrastructure is not applied from this environment
- local persistence uses SQLite in the orders service while the Terraform target models a managed relational database
- local monitoring is Prometheus/Grafana focused rather than a full managed AWS observability stack

## Practical takeaway

This repo is useful as a portfolio project because it shows platform instincts:
- stateless service boundaries
- cost-aware design choices
- CI/CD structure
- health and metrics instrumentation
- ops and rollback documentation
