from storageinfra.resilience import run_resilience_suite


def test_resilience_suite_reports_restart_success():
    results = run_resilience_suite()
    assert results["restart_recovery_success"] is True
    assert results["cache_speedup_x"] >= 1.0
