# Findings

## Overview

This project benchmarks an object-storage stack with a MinIO-first deployment model, a cache layer for hot reads, and a local simulation backend for fast reproducibility.

## Architecture

- object store abstraction supporting local filesystem mode and MinIO mode
- in-memory cache for hot object access patterns
- concurrent benchmark runner covering upload, cold download, and hot download paths
- resilience suite for restart recovery, throttling, and simulated disk pressure
- report generation layer that exports CSV, JSON, HTML, and PNG artifacts

## Methodology

The benchmark evaluates multiple object sizes and concurrency levels. Upload and download workloads are separated so throughput and latency can be compared without conflating write and read contention. A dedicated hot-read scenario is used to quantify cache value.

## Findings and results

The generated benchmark run reached **756.32 MB/s** at its best upload point and **2783.5 MB/s** at its best cached hot-read point. The average hot-read cache hit rate across grouped scenarios was **22.2%**, and the repeated-read resilience check showed a **11.37x** speedup with caching enabled.

Moderate concurrency improved throughput more than single-threaded execution, but the p95 latency curves show the familiar tradeoff: past a certain point, more concurrency raises tail latency faster than it increases useful throughput.

## Limitations

- The included generated run uses the local backend rather than a live MinIO container.
- The Grafana dashboard assets are configuration files, not a live hosted dashboard.
- Redis is represented in the deployment topology, but the default runnable path uses an in-memory cache for simplicity.

## Future improvements

- add a true Redis cache client path
- benchmark larger multipart uploads
- add long-running soak tests with persistent volumes
- compare single-node MinIO against a distributed deployment
