# Architecture

## Core flow

1. **Source threads** generate fixed-size messages at high frequency.
2. Each source pushes into a dedicated bounded ring buffer.
3. The **ingestion thread** polls all producer queues in round-robin order.
4. Accepted messages are timestamped and validated.
5. Messages move into a writer queue for batched binary persistence.
6. The writer flushes batches to disk and records metrics.
7. A replay utility reads the binary stream back for post-processing.

## Why per-source queues

A single shared mutex queue is easy to write but becomes noisy under pressure. This project uses one queue per producer so each source can write with minimal interference. The ingestion thread stays single-consumer, which makes the queue implementation simpler and predictable.

## Overload handling

Two kinds of overload show up in the scenarios:

- **source-side overflow** when a producer queue fills up
- **writer-side overload** when the ingest thread outruns disk persistence

The system responds by:
- counting drops explicitly
- shedding low-priority heartbeat messages first when the writer queue is above a watermark
- continuing to write accepted messages in batches

## Storage format

Each accepted message is serialized to a fixed-size binary record. That keeps replay simple and allows the acquisition path to avoid string parsing or heavy object encoding.

## Metrics

The acquisition run emits:
- total produced, accepted, and dropped messages
- invalid message count
- source overflow count
- writer overload count
- average, p50, p95, and max end-to-end latency
- queue-depth snapshots over time
- throughput per reporting interval
