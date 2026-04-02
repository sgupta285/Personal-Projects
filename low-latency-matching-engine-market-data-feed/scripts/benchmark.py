from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
ENGINE = BUILD / "matching_engine_app"
INPUT = ROOT / "data" / "orders.csv"


def ensure_inputs() -> None:
    subprocess.run(["python3", str(ROOT / "scripts" / "generate_orders.py")], check=True)


def run_once() -> dict[str, float | str]:
    started = time.perf_counter()
    proc = subprocess.run([str(ENGINE), str(INPUT)], capture_output=True, text=True, check=True)
    wall = time.perf_counter() - started
    summary = proc.stdout.strip().splitlines()[0]
    return {"wall_seconds": wall, "summary": summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()

    ensure_inputs()
    results = [run_once() for _ in range(args.runs)]
    output = {
        "runs": args.runs,
        "avg_wall_seconds": sum(float(r["wall_seconds"]) for r in results) / len(results),
        "samples": results,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
