from __future__ import annotations

import time
from pathlib import Path

from censusviz.analysis import CensusAnalyzer


def timed(name: str, fn) -> tuple[str, float]:
    start = time.perf_counter()
    fn()
    return name, time.perf_counter() - start


def main() -> None:
    analyzer = CensusAnalyzer.from_local_data()
    results = [
        timed("weighted_summary", analyzer.weighted_national_summary),
        timed("state_top_income", lambda: analyzer.top_geographies("median_income", "state", 10)),
        timed("county_moe", lambda: analyzer.margin_of_error_bounds("county", "median_income")),
    ]
    Path("artifacts").mkdir(exist_ok=True)
    with open("artifacts/benchmark_results.txt", "w", encoding="utf-8") as handle:
        for name, elapsed in results:
            handle.write(f"{name}: {elapsed:.6f}s\n")
    print("artifacts/benchmark_results.txt")


if __name__ == "__main__":
    main()
