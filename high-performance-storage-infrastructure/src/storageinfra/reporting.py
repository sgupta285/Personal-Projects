from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

from storageinfra.config import settings


def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.0f} MB"
    return f"{size_bytes / 1024:.0f} KB"


def write_reports(raw_df: pd.DataFrame, summary_df: pd.DataFrame, resilience: dict) -> None:
    settings.ensure_directories()

    summary = {
        "best_upload_throughput_mb_s": round(float(summary_df[summary_df["scenario"] == "upload"]["throughput_mb_s"].max()), 2),
        "best_download_hot_throughput_mb_s": round(float(summary_df[summary_df["scenario"] == "download_hot"]["throughput_mb_s"].max()), 2),
        "fastest_p95_ms": round(float(summary_df["p95_latency_ms"].min()), 2),
        "average_hot_cache_hit_rate": round(float(summary_df[summary_df["scenario"] == "download_hot"]["cache_hit_rate"].mean()), 3),
        "restart_recovery_success": resilience["restart_recovery_success"],
        "cache_speedup_x": resilience["cache_speedup_x"],
    }
    (settings.report_dir / "executive_summary.json").write_text(json.dumps(summary, indent=2))

    report_text = f"""# Performance Report

## Overview

This report summarizes the local benchmark run for the MinIO-style storage infrastructure project. The generated run uses the local object-store backend so the repository stays reproducible without external services, while preserving the same benchmark shape used for real MinIO runs.

## Key findings

- Best observed upload throughput: **{summary['best_upload_throughput_mb_s']} MB/s**
- Best observed hot-download throughput: **{summary['best_download_hot_throughput_mb_s']} MB/s**
- Fastest p95 latency across grouped scenarios: **{summary['fastest_p95_ms']} ms**
- Average hot-object cache hit rate: **{summary['average_hot_cache_hit_rate']:.1%}**
- Restart recovery success: **{summary['restart_recovery_success']}**
- Cache speedup on repeated hot reads: **{summary['cache_speedup_x']}x**

## Interpretation

The benchmark shows the expected pattern for object storage systems. Moderate concurrency improves throughput materially, but p95 latency starts to rise more quickly once the workload moves beyond the easiest scaling range. Repeated reads of a small hot object set benefit significantly from caching, which is why the project keeps a cache layer in the design even though the object store is the durable system of record.

The resilience checks also behave as expected. A restart against the same persisted backing directory preserves data, while injected delay and simulated pressure increase round-trip time enough to be visible in the benchmark artifacts.

## Output files

- `data/benchmarks/raw_results.csv`
- `data/benchmarks/summary.csv`
- `data/benchmarks/summary.json`
- `data/benchmarks/resilience_results.json`
- `data/reports/dashboard.html`
- `data/reports/throughput_by_concurrency.png`
- `data/reports/latency_p95_by_size.png`
"""
    (settings.report_dir / "performance_report.md").write_text(report_text)

    findings_text = f"""# Findings

## Overview

This project benchmarks an object-storage stack with a MinIO-first deployment model, a cache layer for hot reads, and a local simulation backend for fast reproducibility.

## Architecture

- object store abstraction supporting local filesystem mode and MinIO mode
- in-memory cache for hot object access patterns
- concurrent benchmark runner covering upload, cold download, and hot download paths
- resilience suite for restart recovery, throttling, and simulated disk pressure
- report generation layer that exports CSV, JSON, HTML, and PNG artifacts

## Methodology

The benchmark evaluates multiple object sizes and concurrency levels. Upload and download workloads are separated so throughput and latency can be compared without conflating write and read contention. A dedicated hot-read scenario is used to quantify cache value.

## Findings and results

The generated benchmark run reached **{summary['best_upload_throughput_mb_s']} MB/s** at its best upload point and **{summary['best_download_hot_throughput_mb_s']} MB/s** at its best cached hot-read point. The average hot-read cache hit rate across grouped scenarios was **{summary['average_hot_cache_hit_rate']:.1%}**, and the repeated-read resilience check showed a **{summary['cache_speedup_x']}x** speedup with caching enabled.

Moderate concurrency improved throughput more than single-threaded execution, but the p95 latency curves show the familiar tradeoff: past a certain point, more concurrency raises tail latency faster than it increases useful throughput.

## Limitations

- The included generated run uses the local backend rather than a live MinIO container.
- The Grafana dashboard assets are configuration files, not a live hosted dashboard.
- Redis is represented in the deployment topology, but the default runnable path uses an in-memory cache for simplicity.

## Future improvements

- add a true Redis cache client path
- benchmark larger multipart uploads
- add long-running soak tests with persistent volumes
- compare single-node MinIO against a distributed deployment
"""
    (settings.root_dir / "docs/FINDINGS.md").write_text(findings_text)

    plot_df = summary_df.copy()
    plot_df["size_label"] = plot_df["size_bytes"].map(_format_size)

    fig = px.line(
        plot_df[plot_df["scenario"] == "upload"],
        x="concurrency",
        y="throughput_mb_s",
        color="size_label",
        markers=True,
        title="Upload throughput by concurrency",
    )
    fig.write_html(settings.report_dir / "dashboard.html", include_plotlyjs="cdn")

    plt.figure(figsize=(8, 5))
    upload_plot = plot_df[plot_df["scenario"] == "upload"]
    for size_label, group in upload_plot.groupby("size_label"):
        plt.plot(group["concurrency"], group["throughput_mb_s"], marker="o", label=size_label)
    plt.title("Upload throughput by concurrency")
    plt.xlabel("Concurrency")
    plt.ylabel("Throughput (MB/s)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(settings.report_dir / "throughput_by_concurrency.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    latency_plot = plot_df[plot_df["scenario"] != "download_hot"]
    for size_label, group in latency_plot.groupby("size_label"):
        plt.plot(group["concurrency"], group["p95_latency_ms"], marker="o", label=size_label)
    plt.title("P95 latency by size")
    plt.xlabel("Concurrency")
    plt.ylabel("P95 latency (ms)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(settings.report_dir / "latency_p95_by_size.png", dpi=160)
    plt.close()
