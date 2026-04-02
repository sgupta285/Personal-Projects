from __future__ import annotations

from censusviz.analysis import CensusAnalyzer


def main() -> None:
    analyzer = CensusAnalyzer.from_local_data()
    summary = analyzer.weighted_national_summary()
    assert summary["population_total"] > 300_000_000
    assert summary["weighted_median_income"] > 50_000
    top = analyzer.top_geographies("median_income", "state", 3)
    assert len(top) == 3
    print("smoke test passed")


if __name__ == "__main__":
    main()
