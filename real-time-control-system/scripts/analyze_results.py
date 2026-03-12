#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def settling_time(df: pd.DataFrame, tolerance_ratio: float = 0.05) -> float | None:
    final_setpoint = df["setpoint"].iloc[-1]
    tolerance = max(abs(final_setpoint) * tolerance_ratio, 1.0)
    within = (df["true_speed"] - final_setpoint).abs() <= tolerance
    stable_window = 20
    for idx in range(len(df) - stable_window):
        if within.iloc[idx: idx + stable_window].all():
            return float(df["time_s"].iloc[idx])
    return None


def max_overshoot(df: pd.DataFrame) -> float:
    max_speed = df["true_speed"].max()
    max_setpoint = df["setpoint"].max()
    if max_setpoint <= 0:
        return 0.0
    return float((max_speed - max_setpoint) / max_setpoint * 100.0)


def build_plots(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 5))
    plt.plot(df["time_s"], df["setpoint"], label="setpoint", linewidth=2)
    plt.plot(df["time_s"], df["true_speed"], label="true speed", linewidth=1.8)
    plt.plot(df["time_s"], df["filtered_measurement"], label="filtered measurement", alpha=0.8)
    plt.xlabel("Time (s)")
    plt.ylabel("Speed")
    plt.title("Control response")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "control_response.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.hist(df["jitter_ms"], bins=40)
    plt.xlabel("Jitter (ms)")
    plt.ylabel("Loop count")
    plt.title("Control loop jitter distribution")
    plt.tight_layout()
    plt.savefig(output_dir / "jitter_histogram.png", dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)
    df = pd.read_csv(input_path)
    build_plots(df, output_dir)

    summary = {
        "rows": int(len(df)),
        "mean_abs_error": float((df["setpoint"] - df["true_speed"]).abs().mean()),
        "rmse": float((((df["setpoint"] - df["true_speed"]) ** 2).mean()) ** 0.5),
        "settling_time_s": settling_time(df),
        "max_overshoot_pct": max_overshoot(df),
        "mean_abs_jitter_ms": float(df["jitter_ms"].abs().mean()),
        "max_abs_jitter_ms": float(df["jitter_ms"].abs().max()),
        "overruns": int(df["overrun"].sum()),
        "mean_sensor_delay_ms": float(df["sensor_delay_ms"].mean()),
    }

    (output_dir / "analysis_summary.json").write_text(json.dumps(summary, indent=2))
    pd.DataFrame([summary]).to_csv(output_dir / "timing_table.csv", index=False)


if __name__ == "__main__":
    main()
