from latdiag.analysis import compare_releases, summarize
from latdiag.io import read_events


def test_summarize_and_compare_flags_regression():
    baseline = read_events("samples/captures/release_v110.jsonl")
    candidate = read_events("samples/captures/release_v120.jsonl")

    summary = summarize(candidate)
    assert "scheduler_delay" in summary
    assert summary["scheduler_delay"].p99_us >= 280

    findings = compare_releases(baseline, candidate, threshold_pct=10.0)
    assert findings
    assert findings[0].event_type == "interrupt" or findings[0].event_type in {"scheduler_delay", "syscall_latency"}
