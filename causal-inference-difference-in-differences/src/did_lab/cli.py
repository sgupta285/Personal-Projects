from __future__ import annotations

import argparse
import json
from pathlib import Path

from did_lab.config import ProjectConfig
from did_lab.pipeline import build_sample_dataset, run_analysis, run_benchmark


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Difference-in-differences policy evaluation toolkit")
    parser.add_argument("--config", default="configs/default.yaml", help="Path to YAML or JSON config")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate-sample", help="Generate sample panel data")
    analyze = subparsers.add_parser("run-analysis", help="Run the policy evaluation workflow")
    analyze.add_argument("--data", default=None, help="Optional explicit path to panel data CSV")

    subparsers.add_parser("benchmark", help="Run Monte Carlo benchmark")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = ProjectConfig.from_file(args.config)

    if args.command == "generate-sample":
        output = build_sample_dataset(config.data)
        print(json.dumps({"sample_dataset": str(output)}, indent=2))
        return

    if args.command == "run-analysis":
        data_path = args.data or config.data.output_path
        if not Path(data_path).exists():
            build_sample_dataset(config.data)
        summary = run_analysis(data_path, config.analysis)
        print(json.dumps(summary, indent=2))
        return

    if args.command == "benchmark":
        summary = run_benchmark(config.benchmark, config.data, config.analysis)
        print(json.dumps(summary, indent=2))
        return


if __name__ == "__main__":
    main()
