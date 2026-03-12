from __future__ import annotations

import json
from pathlib import Path
import shutil
import time

from storageinfra.cache import MemoryCache
from storageinfra.config import settings
from storageinfra.store import DelayProfile, LocalObjectStore


def _write_and_read(store: LocalObjectStore, payload: bytes, key: str) -> float:
    started = time.perf_counter()
    store.put_object(settings.bucket, key, payload)
    _ = store.get_object(settings.bucket, key)
    return (time.perf_counter() - started) * 1000


def run_resilience_suite() -> dict:
    settings.ensure_directories()
    suite_root = settings.store_root / "resilience_suite"
    if suite_root.exists():
        shutil.rmtree(suite_root)
    suite_root.mkdir(parents=True, exist_ok=True)

    payload = b"x" * 131072

    baseline_store = LocalObjectStore(suite_root / "baseline")
    baseline_ms = _write_and_read(baseline_store, payload, "baseline.bin")

    restart_store = LocalObjectStore(suite_root / "restart")
    restart_store.put_object(settings.bucket, "persist.bin", payload)
    restarted = restart_store.reset()
    restart_success = restarted.get_object(settings.bucket, "persist.bin") == payload

    throttled_store = LocalObjectStore(
        suite_root / "throttled",
        delay=DelayProfile(base_delay_ms=4.0),
    )
    throttled_ms = _write_and_read(throttled_store, payload, "throttled.bin")

    pressure_store = LocalObjectStore(
        suite_root / "pressure",
        delay=DelayProfile(base_delay_ms=0.0, pressure_threshold_bytes=200000, pressure_delay_ms=5.0),
    )
    pressure_ms = []
    for idx in range(4):
        pressure_ms.append(_write_and_read(pressure_store, payload, f"pressure-{idx}.bin"))

    cache = MemoryCache(capacity_bytes=1024 * 1024)
    hot_store = LocalObjectStore(suite_root / "cache")
    hot_store.put_object(settings.bucket, "hot.bin", payload)
    no_cache_started = time.perf_counter()
    for _ in range(10):
        hot_store.get_object(settings.bucket, "hot.bin")
    no_cache_ms = (time.perf_counter() - no_cache_started) * 1000

    cache_started = time.perf_counter()
    for _ in range(10):
        cached = cache.get("hot.bin")
        if cached is None:
            cache.set("hot.bin", hot_store.get_object(settings.bucket, "hot.bin"))
    cache_ms = (time.perf_counter() - cache_started) * 1000

    results = {
        "baseline_roundtrip_ms": round(baseline_ms, 3),
        "restart_recovery_success": restart_success,
        "throttled_roundtrip_ms": round(throttled_ms, 3),
        "pressure_roundtrip_ms": [round(item, 3) for item in pressure_ms],
        "hot_reads_no_cache_ms": round(no_cache_ms, 3),
        "hot_reads_with_cache_ms": round(cache_ms, 3),
        "cache_speedup_x": round(no_cache_ms / cache_ms, 2) if cache_ms else None,
    }

    output_path = settings.benchmark_dir / "resilience_results.json"
    output_path.write_text(json.dumps(results, indent=2))
    return results
