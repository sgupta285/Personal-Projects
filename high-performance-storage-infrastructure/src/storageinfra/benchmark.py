from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import hashlib
import time

import numpy as np
import pandas as pd

from storageinfra.cache import MemoryCache
from storageinfra.config import settings
from storageinfra.store import build_store


@dataclass(slots=True)
class Scenario:
    name: str
    size_bytes: int
    concurrency: int
    ops: int


def _payload(size_bytes: int, seed: int) -> bytes:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=size_bytes, dtype=np.uint8).tobytes()


def _stable_digest(payload: bytes) -> str:
    return hashlib.md5(payload).hexdigest()


def _upload_once(store, bucket: str, key: str, body: bytes) -> tuple[float, int]:
    started = time.perf_counter()
    store.put_object(bucket, key, body)
    elapsed = time.perf_counter() - started
    return elapsed, len(body)


def _download_once(store, bucket: str, key: str, cache: MemoryCache | None = None) -> tuple[float, int, bool]:
    cache_hit = False
    started = time.perf_counter()
    if cache is not None:
        cached = cache.get(key)
        if cached is not None:
            cache_hit = True
            body = cached
        else:
            body = store.get_object(bucket, key)
            cache.set(key, body)
    else:
        body = store.get_object(bucket, key)
    elapsed = time.perf_counter() - started
    return elapsed, len(body), cache_hit


def run_default_benchmarks() -> tuple[pd.DataFrame, pd.DataFrame]:
    settings.ensure_directories()
    scenarios = settings.load_scenarios()
    sizes = scenarios["sizes_bytes"]
    concurrencies = scenarios["concurrency_levels"]
    ops_per_level = scenarios["ops_per_level"]
    hot_count = scenarios["hot_object_count"]

    store = build_store()
    cache = MemoryCache(settings.cache_capacity_bytes) if settings.cache_mode == "memory" else None

    records: list[dict] = []
    rng = np.random.default_rng(settings.seed)

    for size_bytes in sizes:
        preload_keys = []
        preload_payload = _payload(size_bytes, seed=size_bytes)
        for idx in range(max(hot_count, ops_per_level)):
            key = f"seed-{size_bytes}-{idx}.bin"
            store.put_object(settings.bucket, key, preload_payload)
            preload_keys.append(key)

        for concurrency in concurrencies:
            upload_keys = [f"upload-{size_bytes}-{concurrency}-{i}.bin" for i in range(ops_per_level)]
            upload_bodies = [_payload(size_bytes, seed=size_bytes + i + concurrency) for i in range(ops_per_level)]

            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                for key, body, result in zip(
                    upload_keys,
                    upload_bodies,
                    executor.map(lambda args: _upload_once(*args), [(store, settings.bucket, k, b) for k, b in zip(upload_keys, upload_bodies)]),
                ):
                    elapsed, byte_count = result
                    records.append(
                        {
                            "scenario": "upload",
                            "size_bytes": size_bytes,
                            "concurrency": concurrency,
                            "object_key": key,
                            "latency_ms": elapsed * 1000,
                            "bytes": byte_count,
                            "cache_hit": False,
                        }
                    )

            if cache is not None:
                cache.clear()
            cold_keys = preload_keys[:ops_per_level]
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                for key, result in zip(
                    cold_keys,
                    executor.map(lambda k: _download_once(store, settings.bucket, k, None), cold_keys),
                ):
                    elapsed, byte_count, cache_hit = result
                    records.append(
                        {
                            "scenario": "download_cold",
                            "size_bytes": size_bytes,
                            "concurrency": concurrency,
                            "object_key": key,
                            "latency_ms": elapsed * 1000,
                            "bytes": byte_count,
                            "cache_hit": cache_hit,
                        }
                    )

            if cache is not None:
                cache.clear()
            hot_keys = list(rng.choice(preload_keys[:hot_count], size=ops_per_level, replace=True))
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                for key, result in zip(
                    hot_keys,
                    executor.map(lambda k: _download_once(store, settings.bucket, k, cache), hot_keys),
                ):
                    elapsed, byte_count, cache_hit = result
                    records.append(
                        {
                            "scenario": "download_hot",
                            "size_bytes": size_bytes,
                            "concurrency": concurrency,
                            "object_key": key,
                            "latency_ms": elapsed * 1000,
                            "bytes": byte_count,
                            "cache_hit": cache_hit,
                        }
                    )

    raw_df = pd.DataFrame(records)
    effective_latency_s = raw_df["latency_ms"].clip(lower=0.2) / 1000
    raw_df["throughput_mb_s"] = (raw_df["bytes"] / (1024 * 1024)) / effective_latency_s
    summary_df = (
        raw_df.groupby(["scenario", "size_bytes", "concurrency"], as_index=False)
        .agg(
            operations=("object_key", "count"),
            avg_latency_ms=("latency_ms", "mean"),
            p95_latency_ms=("latency_ms", lambda s: float(np.percentile(s, 95))),
            throughput_mb_s=("throughput_mb_s", "mean"),
            cache_hit_rate=("cache_hit", "mean"),
            total_bytes=("bytes", "sum"),
        )
        .sort_values(["scenario", "size_bytes", "concurrency"])
    )

    raw_path = settings.benchmark_dir / "raw_results.csv"
    summary_path = settings.benchmark_dir / "summary.csv"
    summary_json_path = settings.benchmark_dir / "summary.json"
    raw_df.to_csv(raw_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    summary_json_path.write_text(summary_df.to_json(orient="records", indent=2))

    return raw_df, summary_df
