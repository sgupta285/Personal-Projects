# Resilience Test Notes

This project includes lightweight resilience checks in local simulation mode so the behavior is easy to inspect without a cluster.

## Scenarios

### Restart recovery
The object store client is recreated against the same persisted backing directory. The test verifies that previously written objects are still readable after the restart event.

### Artificial throttling
The storage backend adds a small delay to every operation. This is a stand-in for reduced network throughput or a noisy path to the storage node. The benchmark compares baseline latency and throughput against the throttled run.

### Simulated disk pressure
Once a configurable amount of data is written, the backend injects extra delay on future writes. This mimics a storage node that remains healthy but slows under pressure.

### Cache benefit
A repeated hot-object workload is executed with and without the in-memory cache so the report can quantify hit rate and download latency reduction.

## What to check first in a real deployment

- object store disk utilization and filesystem saturation
- container restart count
- network retransmits or bandwidth throttling
- cache hit ratio and eviction churn
- client-side timeout settings and multipart configuration
