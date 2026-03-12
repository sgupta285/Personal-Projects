# Tuning Notes

## Multipart and object sizing

For MinIO-backed runs, the benchmark keeps object sizes in a practical local range to make repeated test runs cheap. In a larger deployment, multipart upload thresholds should be raised for multi-megabyte assets so the client can parallelize transfer work without creating too many tiny parts.

## Concurrency

The biggest improvement in the generated benchmark usually comes from moving from a single client thread to moderate concurrency. Past that point, latency tends to rise faster than throughput. That is a sign that the bottleneck is shifting from client wait time to backend write amplification or local disk contention.

## Cache thresholds

The hot-object cache is deliberately capped. A cache that absorbs the hottest keys gives most of the latency benefit without letting object reads crowd out the benchmark process itself. The repo defaults to 64 MB, which is enough for repeated access to the hot object set used in the local runs.

## Benchmark hygiene

- warm up before comparing scenarios
- keep object sizes fixed when comparing concurrency
- separate upload and download tests
- report p50 and p95 latency, not only averages
- rerun after configuration changes to confirm a real gain
