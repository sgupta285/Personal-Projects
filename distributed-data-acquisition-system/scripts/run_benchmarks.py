#!/usr/bin/env python3
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build" / "daq_acquire"
REPLAY = ROOT / "build" / "daq_replay"
CONFIG = ROOT / "config" / "scenarios.csv"
OUT = ROOT / "data" / "generated"

def load_scenarios() -> list[str]:
    with CONFIG.open() as fh:
        rows = list(csv.DictReader(fh))
    return [row["scenario"] for row in rows]

def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not BUILD.exists():
        raise SystemExit("build/daq_acquire not found. Run `make build` first.")

    for scenario in load_scenarios():
        subprocess.run(
            [str(BUILD), "--scenario", scenario, "--config", str(CONFIG), "--output-dir", str(OUT)],
            check=True,
        )
        stream = OUT / f"{scenario}_stream.bin"
        subprocess.run(
            [str(REPLAY), "--input", str(stream), "--max-messages", "5"],
            check=True,
        )

if __name__ == "__main__":
    run()
