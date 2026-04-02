from __future__ import annotations

import json
from pathlib import Path

from censusviz.analysis import CensusAnalyzer


def main() -> None:
    out_dir = Path("artifacts")
    out_dir.mkdir(exist_ok=True)

    analyzer = CensusAnalyzer.from_local_data()
    payload = {
        "summary": analyzer.weighted_national_summary(),
        "top_states_by_income": analyzer.top_geographies("median_income", "state", 5).to_dict("records"),
        "top_counties_by_home_value": analyzer.top_geographies("median_home_value", "county", 5).to_dict("records"),
    }

    with open(out_dir / "demo_report.json", "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(out_dir / "demo_report.json")


if __name__ == "__main__":
    main()
