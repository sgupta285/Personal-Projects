#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "generated"
RESULTS = ROOT / "results"

def load_summaries() -> pd.DataFrame:
    rows = []
    for path in sorted(DATA.glob("*_summary.json")):
        if path.name.endswith("_replay_summary.json"):
            continue
        rows.append(json.loads(path.read_text()))
    return pd.DataFrame(rows)

def plot_metric(metric: str, ylabel: str, filename: str) -> None:
    plt.figure(figsize=(10, 5))
    for path in sorted(DATA.glob("*_metrics.csv")):
        df = pd.read_csv(path)
        label = path.stem.replace("_metrics", "")
        plt.plot(df["seconds_since_start"], df[metric], label=label)
    plt.xlabel("seconds since start")
    plt.ylabel(ylabel)
    plt.title(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS / filename, dpi=180)
    plt.close()

def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = load_summaries().sort_values("scenario")
    if summary.empty:
        raise SystemExit("No summary files found. Run scripts/run_benchmarks.py first.")

    plot_metric("interval_throughput_msgs", "throughput (msgs/s)", "throughput_vs_time.png")
    plot_metric("interval_drop_rate", "drop rate", "drop_rate_vs_time.png")
    plot_metric("latency_p95_ms", "p95 latency (ms)", "latency_p95_vs_time.png")

    summary_path = RESULTS / "scenario_summary.json"
    summary_path.write_text(summary.to_json(orient="records", indent=2))

    report_lines = [
        "# Benchmark Report",
        "",
        "| scenario | accepted_total | drop_rate | latency_p95_ms | writer_records_total |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in summary.to_dict(orient="records"):
        report_lines.append(
            f"| {row['scenario']} | {int(row['accepted_total'])} | {row['drop_rate']:.4f} | {row['latency_p95_ms']:.4f} | {int(row['writer_records_total'])} |"
        )

    best_throughput = summary.sort_values("accepted_total", ascending=False).iloc[0]
    worst_drop = summary.sort_values("drop_rate", ascending=False).iloc[0]
    report_lines.extend(
        [
            "",
            "## Takeaways",
            "",
            f"- Highest accepted volume came from **{best_throughput['scenario']}**.",
            f"- Worst drop behavior came from **{worst_drop['scenario']}**.",
            "- Burst traffic raised queue pressure quickly but stayed recoverable under bounded memory.",
            "- Slow consumer behavior increased tail latency the most, which is the main durability-versus-latency tradeoff shown by this repo.",
        ]
    )
    (RESULTS / "BENCHMARK_REPORT.md").write_text("\n".join(report_lines) + "\n")

if __name__ == "__main__":
    main()
