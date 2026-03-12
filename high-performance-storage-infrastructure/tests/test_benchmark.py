import pandas as pd

from storageinfra.benchmark import run_default_benchmarks


def test_benchmark_outputs_have_expected_columns():
    raw_df, summary_df = run_default_benchmarks()
    assert {"scenario", "size_bytes", "concurrency", "latency_ms", "throughput_mb_s"}.issubset(raw_df.columns)
    assert {"scenario", "avg_latency_ms", "p95_latency_ms", "throughput_mb_s"}.issubset(summary_df.columns)
    assert len(raw_df) > 0
    assert len(summary_df) > 0
