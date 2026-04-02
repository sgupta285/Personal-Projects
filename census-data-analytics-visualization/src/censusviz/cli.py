from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analysis import CensusAnalyzer


def main() -> None:
    parser = argparse.ArgumentParser(description="Census analytics helper")
    parser.add_argument("command", choices=["summary", "top"], help="Command to run")
    parser.add_argument("--metric", default="median_income")
    parser.add_argument("--geography", default="state", choices=["state", "county"])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output", default="artifacts/cli_output.json")
    args = parser.parse_args()

    analyzer = CensusAnalyzer.from_local_data()
    Path("artifacts").mkdir(exist_ok=True)

    if args.command == "summary":
        payload = analyzer.weighted_national_summary()
    else:
        payload = analyzer.top_geographies(args.metric, args.geography, args.limit).to_dict("records")

    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(args.output)


if __name__ == "__main__":
    main()
