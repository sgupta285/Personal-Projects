# Profiling Notes

This repository is meant to be profiled on Linux. The engine is small enough to understand end to end, but structured enough to show the same kinds of decisions that matter in a real low-latency path.

## Recommended flow

1. Build in release mode.
2. Generate a repeatable order stream.
3. Run `perf record` against the matching engine binary.
4. Inspect branch misses, cache misses, and call stacks.
5. Generate a flamegraph if you already have Brendan Gregg's scripts installed locally.

## Useful commands

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
python3 scripts/generate_orders.py
perf stat build/matching_engine_app data/orders.csv
perf record -g build/matching_engine_app data/orders.csv
perf report --stdio
```

## What to look for

- unexpected heap activity inside the matching path
- branch-heavy logic around level selection and queue cleanup
- cache misses when the book becomes fragmented
- parser overhead when replaying the binary market data sample
