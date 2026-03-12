# Cost-Aware Architecture Notes

This project intentionally balances credibility with practical cost control.

## Why this design is cost-conscious

### ECS on Fargate instead of EKS
For a small platform:
- no cluster control plane to manage
- simpler deployment workflow
- easier learning curve for small teams
- cleaner fit for stateless services

### Separate dev and prod
The dev environment should not mirror prod cost-for-cost.
- lower desired task count
- fewer replicas
- smaller database footprint
- single-AZ acceptable for personal projects and demos

### Stateless where possible
Frontend, gateway, and catalog are stateless, which makes autoscaling and rollback simpler.

### Database only where it matters
Orders is the only stateful service in this demo. That keeps the persistence boundary narrow and easier to reason about.

## What I would change for a larger production footprint

- use managed secrets everywhere through AWS Secrets Manager
- consider Redis or ElastiCache for caching and rate protection
- move metrics to AWS managed Prometheus and Grafana if the team wants lower operational overhead
- add WAF and stronger network segmentation for public traffic
