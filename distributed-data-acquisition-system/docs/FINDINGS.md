# Findings

## Overview

This project simulates a distributed acquisition pipeline where multiple fast producers generate sensor events that must be buffered, persisted, and replayed later. The goal is to understand how batching, bounded queues, and overload protection affect throughput and loss.

## Methodology

Three scenarios are run by default:

- **baseline**: steady traffic with no artificial writer slowdown
- **burst_traffic**: short traffic spikes at regular intervals
- **slow_consumer**: steady traffic but the writer intentionally sleeps after each flush

Each run captures message-level persistence, interval metrics, and replay summaries.

## What showed up in the runs

1. **Baseline** stayed stable with low drop rate and modest queue depth.
2. **Burst traffic** increased queue pressure quickly. Bounded queues kept memory predictable, but short bursts caused temporary source-side drops.
3. **Slow consumer** stressed durability the most. Batching still helped throughput, but end-to-end latency and writer-queue pressure rose visibly.

## Interpretation

The project demonstrates a classic systems tradeoff. If you want durability and batching, the writer path becomes more efficient, but tail latency can climb when the sink slows down. If you want minimal latency, you flush more frequently and pay higher I/O overhead.

## Limitations

- producers are simulated in process rather than using real network sockets
- storage uses a fixed-size binary record instead of Parquet
- the queue implementation is intentionally simple and tuned for readability
- metrics are emitted to files rather than a live monitoring backend

## Why it still matters

Even in simulation mode, the repo shows the important design choices clearly:
- isolate producer hot paths
- measure queue pressure continuously
- make overload visible
- keep replay simple so downstream analysis is easy
