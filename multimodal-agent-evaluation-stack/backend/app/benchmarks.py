from __future__ import annotations

import json
from pathlib import Path
from sqlalchemy.orm import Session

from .models import Benchmark


def load_benchmark_file(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def upsert_benchmark(db: Session, payload: dict) -> Benchmark:
    benchmark = db.get(Benchmark, payload["benchmark_id"])
    if benchmark is None:
        benchmark = Benchmark(
            benchmark_id=payload["benchmark_id"],
            name=payload["name"],
            version=payload["version"],
            task_type=payload["task_type"],
            evaluator_type=payload["evaluator_type"],
            instructions=payload["instructions"],
            expected_tools=payload.get("expected_tools", []),
            expected_output=payload.get("expected_output", {}),
            metadata_json=payload.get("metadata", {}),
        )
        db.add(benchmark)
    else:
        benchmark.name = payload["name"]
        benchmark.version = payload["version"]
        benchmark.task_type = payload["task_type"]
        benchmark.evaluator_type = payload["evaluator_type"]
        benchmark.instructions = payload["instructions"]
        benchmark.expected_tools = payload.get("expected_tools", [])
        benchmark.expected_output = payload.get("expected_output", {})
        benchmark.metadata_json = payload.get("metadata", {})
    db.commit()
    db.refresh(benchmark)
    return benchmark


def load_default_benchmarks(db: Session, benchmark_dir: str) -> list[Benchmark]:
    results: list[Benchmark] = []
    for path in sorted(Path(benchmark_dir).glob("*.json")):
        payload = load_benchmark_file(path)
        results.append(upsert_benchmark(db, payload))
    return results
