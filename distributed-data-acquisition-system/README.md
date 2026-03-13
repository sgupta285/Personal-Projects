# Distributed Data Acquisition System

A low-latency data acquisition project that simulates multiple high-rate sensor streams, ingests them through bounded queues, persists the accepted stream in binary batches, and exposes throughput, drop, queue-depth, and latency metrics for stress analysis.

## What this project covers

- multiple simulated producers emitting at configurable rates
- bounded single-producer single-consumer queues to keep contention low
- ingestion with timestamping, validation, and overload handling
- batched binary logging for durable replay
- scenario-driven stress tests for burst traffic and slow-consumer behavior
- replay utility for recorded streams
- benchmark analysis with plots and summary artifacts

## Architecture

```text
source threads -> per-source ring buffers -> ingestion thread -> writer queue -> binary log
                                             |                    |
                                             +--> metrics snapshots +--> replay utility
```

Each source gets its own queue, which avoids a single lock bottleneck on the hot path. The ingestion thread polls those queues in round-robin order, validates messages, stamps ingest timestamps, and forwards accepted messages to the writer. If the writer queue is close to saturation, the system starts shedding low-priority heartbeat events before it starts losing more valuable data.

## Repository layout

```text
distributed-data-acquisition-system/
├── config/
├── data/generated/
├── docs/
├── notebooks/
├── results/
├── scripts/
├── src/
└── tests/
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

make build
make run-benchmarks
make analyze
```

## Binaries

- `daq_acquire`: runs a configured acquisition scenario
- `daq_replay`: replays a previously recorded binary stream

## Example commands

Run a single scenario:

```bash
./build/daq_acquire --scenario baseline
```

Replay the first few messages from the baseline log:

```bash
./build/daq_replay --input data/generated/baseline_stream.bin --max-messages 10
```

## Outputs

Running the benchmark script generates:

- `data/generated/*_summary.json`
- `data/generated/*_metrics.csv`
- `data/generated/*_replay_summary.json`
- `data/generated/*_metrics.prom`
- `results/throughput_vs_time.png`
- `results/drop_rate_vs_time.png`
- `results/scenario_summary.json`
- `results/BENCHMARK_REPORT.md`

## Performance targets

This repo is designed to illustrate a few core tradeoffs:

- low queue contention helps when there are many fast producers
- batching improves storage efficiency but can increase tail latency
- overload protection should degrade gracefully instead of failing open
- durability and latency are always in tension under slow-consumer conditions

The included stress scenarios show how the system behaves when traffic bursts or when the writer path becomes artificially slow.

## Testing

```bash
make test
```

## Notes

The project stays local-first. It simulates data sources directly in process, which keeps the repo easy to run on a laptop while still surfacing the timing, batching, and backpressure decisions that matter in a real acquisition service.
