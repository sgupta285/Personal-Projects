# Low-Latency Matching Engine and Market Data Feed

A small but serious C++20 trading-infrastructure repo built around the ideas called out in the portfolio README: price-time-priority order matching, binary feed handling, cache-aware systems work, Linux profiling, and measurable latency discipline. The project is not pretending to be a production exchange, but it is structured like something a systems-minded engineer could actually discuss in detail, benchmark, and extend without rewriting everything from scratch.

## Why this repo exists

The source README describes a systems-level trading project focused on microsecond latency, price-time priority, binary protocol parsing, lock-free queues, memory layout, and Linux profiling. This repo turns that into a concrete build:

- a C++20 matching engine with a real order book
- a simplified ITCH-style binary parser
- a UDP market data publisher for book and execution events
- reusable low-latency utilities such as an SPSC queue and object pool
- Linux profiling helpers for perf-based analysis
- deterministic sample feeds and benchmark tooling

## What is included

### Core features

- price-time-priority matching for buy and sell orders
- limit and market order support
- order cancel support
- execution generation with resting and aggressive order identifiers
- best bid and best ask snapshot publication
- binary feed replay from a compact wire format
- UDP publication of book and trade events to support downstream listeners
- deterministic fixture generation for repeatable tests and benchmarks

### Tech stack

- **C++20** for the matching path and feed parsing
- **Linux sockets** for market data event publication
- **Python 3** for fixture generation and benchmark automation
- **CMake** for builds and test orchestration
- **Docker** for a portable build and run path
- **perf**-friendly profiling scripts for Linux investigation

## Architecture

```text
binary feed / csv orders
        │
        ├── feed_replayer_app
        │      └── ItchParser
        │
        └── matching_engine_app
               └── MatchingEngine
                       ├── OrderBook
                       ├── UDP publisher
                       └── recent execution cache
```

### Main components

#### `OrderBook`
Tracks active orders and enforces price-time priority. Orders are indexed by ID for fast cancel and grouped by price level for matching. The implementation keeps the code readable while still reflecting the engineering ideas from the source README: predictable data flow, hot-path simplicity, and explicit control over matching behavior.

#### `MatchingEngine`
Wraps the order book and is responsible for publishing execution reports and top-of-book snapshots. It is the place where order handling and market data fan-out meet.

#### `ItchParser`
Implements a compact binary wire format inspired by ITCH-style market data feeds. The parser operates directly on byte spans and avoids unnecessary intermediate allocations.

#### Low-latency utilities
The repo includes a single-producer single-consumer queue and a lightweight object pool. They are not deeply wired into every code path yet, but they are part of the repo because the source README explicitly calls out lock-free queues and allocator discipline as part of the build story.

## Repository layout

```text
.
├── apps/
│   ├── feed_replayer_app.cpp
│   └── matching_engine_app.cpp
├── data/
│   ├── itch_feed.bin
│   └── orders.csv
├── docs/
│   └── profiling.md
├── include/llmde/
│   ├── core/
│   ├── engine/
│   ├── feed/
│   └── io/
├── scripts/
│   ├── benchmark.py
│   ├── generate_itch_feed.py
│   ├── generate_orders.py
│   └── profile.sh
├── src/
│   ├── core/
│   ├── engine/
│   ├── feed/
│   └── io/
├── tests/
├── CMakeLists.txt
├── Dockerfile
└── docker-compose.yml
```

## Build and run

### Local build

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
```

### Run the matching engine on the sample CSV stream

```bash
python3 scripts/generate_orders.py
./build/matching_engine_app data/orders.csv
```

Example output looks like this:

```text
processed=20000 elapsed_us=... throughput_orders_per_sec=...
best_bid=... best_bid_qty=... best_ask=... best_ask_qty=...
```

### Replay the binary sample feed

```bash
python3 scripts/generate_itch_feed.py
./build/feed_replayer_app data/itch_feed.bin
```

## Testing

```bash
ctest --test-dir build --output-on-failure
```

The tests cover:

- price-time matching correctness
- partial fills
- cancel behavior
- binary add and cancel message parsing

## Benchmarking

```bash
python3 scripts/benchmark.py --runs 5
```

This benchmark script:

- regenerates the deterministic order stream
- runs the release binary multiple times
- reports average wall-clock runtime and raw engine output

It is intentionally lightweight. This repo is aimed at repo-readability and reproducibility first, with enough structure to support deeper profiling work on a Linux machine.

## Linux profiling workflow

The source README called out perf, flamegraphs, and hardware counters, so the repo includes a profiling helper and notes.

```bash
./scripts/profile.sh
```

That script will:

- generate the order fixture
- build the engine
- run `perf record`
- write a text report to `docs/perf-report.txt`

You can also run your own commands directly:

```bash
perf stat ./build/matching_engine_app data/orders.csv
perf record -g ./build/matching_engine_app data/orders.csv
perf report --stdio
```

## Market data output

The engine publishes two simple UDP payload types to `127.0.0.1:19001` by default:

- `EXEC|...` for trades
- `BOOK|...` for best bid and best ask snapshots

That keeps the engine easy to inspect with a simple local listener while staying consistent with the repo's market-data-feed framing.

## Design decisions

### Why a readable order book instead of a hyper-specialized one?

The source README emphasized production-minded performance work, but this repo also needs to be runnable and inspectable as a GitHub artifact. The implementation therefore favors a small, explicit order book that still demonstrates the key ideas: order indexing, price-level queues, price-time priority, and hot-path awareness.

### Why include lock-free and pooling utilities even though the sample engine is compact?

Because they are part of the system design described in the source material. They help show how the codebase would evolve toward a more aggressive latency target without making the basic engine impossible to read.

### Why a simplified binary feed?

Real FIX and full ITCH implementations are large and protocol-heavy. The portfolio README referenced binary parsing and zero-copy techniques, so the repo includes a compact ITCH-style wire format that lets the parser and feed replay path stay concrete.

## Reproducibility notes

- fixture generation is deterministic
- tests do not depend on external services
- Docker provides a portable build path
- benchmark output is simple enough to compare across runs and machines

## Limitations

- this is a single-symbol sample engine
- the UDP publisher is for local fan-out and inspection, not production multicast
- the price-level data structure is built for clarity and repeatability, not exchange-grade completeness
- the parser models ITCH-style ideas rather than implementing the full protocol surface

## Docker

```bash
docker build -t llmde .
docker run --rm llmde
```

or

```bash
docker compose up --build
```

