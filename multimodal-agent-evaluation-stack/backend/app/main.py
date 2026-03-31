from __future__ import annotations

import uuid
from collections import Counter
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from .analysis import classify_failure
from .benchmarks import load_default_benchmarks, upsert_benchmark
from .config import settings
from .db import Base, engine, get_db
from .evaluators import dispatch_evaluator
from .mlflow_client import MLflowLogger
from .models import Benchmark, Evaluation, FailureAnalysis, Run
from .runner import generate_demo_run
from .schemas import (
    BenchmarkCreate,
    FailureModeSummary,
    SummaryReport,
    RunCreate,
)

mlflow_logger = MLflowLogger()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


def model_to_dict(model: Any) -> dict[str, Any]:
    payload = {}
    for column in model.__table__.columns:
        payload[column.name] = getattr(model, column.name)
    if "metadata" in payload and hasattr(model, "metadata_json"):
        payload["metadata"] = payload.pop("metadata")
    return payload


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@app.get("/benchmarks")
def list_benchmarks(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    items = db.execute(select(Benchmark).order_by(Benchmark.benchmark_id)).scalars().all()
    return [
        {
            "benchmark_id": item.benchmark_id,
            "name": item.name,
            "version": item.version,
            "task_type": item.task_type,
            "evaluator_type": item.evaluator_type,
            "instructions": item.instructions,
            "expected_tools": item.expected_tools,
            "expected_output": item.expected_output,
            "metadata": item.metadata_json,
            "created_at": item.created_at,
        }
        for item in items
    ]


@app.post("/benchmarks/load-defaults")
def load_defaults(db: Session = Depends(get_db)) -> dict[str, Any]:
    loaded = load_default_benchmarks(db, settings.default_benchmark_dir)
    return {"loaded": len(loaded), "benchmark_ids": [item.benchmark_id for item in loaded]}


@app.post("/benchmarks")
def create_benchmark(payload: BenchmarkCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    benchmark = upsert_benchmark(db, payload.model_dump())
    return {
        "benchmark_id": benchmark.benchmark_id,
        "name": benchmark.name,
        "version": benchmark.version,
        "task_type": benchmark.task_type,
        "evaluator_type": benchmark.evaluator_type,
        "instructions": benchmark.instructions,
        "expected_tools": benchmark.expected_tools,
        "expected_output": benchmark.expected_output,
        "metadata": benchmark.metadata_json,
        "created_at": benchmark.created_at,
    }


@app.get("/benchmarks/{benchmark_id}")
def get_benchmark(benchmark_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    benchmark = db.get(Benchmark, benchmark_id)
    if benchmark is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    return {
        "benchmark_id": benchmark.benchmark_id,
        "name": benchmark.name,
        "version": benchmark.version,
        "task_type": benchmark.task_type,
        "evaluator_type": benchmark.evaluator_type,
        "instructions": benchmark.instructions,
        "expected_tools": benchmark.expected_tools,
        "expected_output": benchmark.expected_output,
        "metadata": benchmark.metadata_json,
        "created_at": benchmark.created_at,
    }


@app.get("/runs")
def list_runs(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    items = db.execute(select(Run).order_by(Run.created_at.desc())).scalars().all()
    return [model_to_dict(item) for item in items]


@app.post("/runs")
def create_run(payload: RunCreate, db: Session = Depends(get_db)) -> dict[str, Any]:
    benchmark = db.get(Benchmark, payload.benchmark_id)
    if benchmark is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    run = Run(run_id=str(uuid.uuid4()), **payload.model_dump())
    db.add(run)
    db.commit()
    db.refresh(run)
    return model_to_dict(run)


@app.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return model_to_dict(run)


@app.post("/runs/demo/{benchmark_id}")
def create_demo_run(benchmark_id: str, mode: str = Query("success"), db: Session = Depends(get_db)) -> dict[str, Any]:
    benchmark = db.get(Benchmark, benchmark_id)
    if benchmark is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    payload = generate_demo_run(benchmark_id, mode=mode if mode in {"success", "failure", "rubric"} else "success")
    run = Run(**payload)
    db.add(run)
    db.commit()
    db.refresh(run)
    return model_to_dict(run)


@app.post("/runs/{run_id}/evaluate")
def evaluate_run(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    benchmark = db.get(Benchmark, run.benchmark_id)
    if benchmark is None:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    result = dispatch_evaluator(
        evaluator_type=benchmark.evaluator_type,
        expected_output=benchmark.expected_output,
        expected_tools=benchmark.expected_tools,
        actual_output=run.final_output,
        trajectory=run.trajectory,
    )

    evaluation = Evaluation(
        evaluation_id=str(uuid.uuid4()),
        run_id=run.run_id,
        benchmark_id=run.benchmark_id,
        evaluator_type=benchmark.evaluator_type,
        score=result.score,
        success=result.success,
        metrics=result.metrics,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    mlflow_logger.log_evaluation(model_to_dict(run), model_to_dict(evaluation))
    return model_to_dict(evaluation)


@app.post("/runs/{run_id}/analyze")
def analyze_run(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    run = db.get(Run, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    evaluation = db.execute(select(Evaluation).where(Evaluation.run_id == run_id).order_by(Evaluation.created_at.desc())).scalars().first()
    evaluation_payload = model_to_dict(evaluation) if evaluation else None
    result = classify_failure(model_to_dict(run), evaluation_payload)

    analysis = FailureAnalysis(
        analysis_id=str(uuid.uuid4()),
        run_id=run.run_id,
        benchmark_id=run.benchmark_id,
        failure_mode=result.failure_mode,
        rationale=result.rationale,
        signals=result.signals,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return model_to_dict(analysis)


@app.get("/reports/summary", response_model=SummaryReport)
def report_summary(db: Session = Depends(get_db)) -> SummaryReport:
    runs = db.execute(select(Run)).scalars().all()
    evaluations = db.execute(select(Evaluation)).scalars().all()

    total_runs = len(runs)
    total_evaluated_runs = len(evaluations)
    average_score = round(sum(item.score for item in evaluations) / total_evaluated_runs, 4) if evaluations else 0.0
    success_rate = round(sum(1 for item in evaluations if item.success) / total_evaluated_runs, 4) if evaluations else 0.0
    average_latency_ms = round(sum(item.total_latency_ms for item in runs) / total_runs, 2) if runs else 0.0
    average_cost_usd = round(sum(item.estimated_cost_usd for item in runs) / total_runs, 4) if runs else 0.0

    runs_by_model = dict(Counter(run.model_name for run in runs))
    runs_by_benchmark = dict(Counter(run.benchmark_id for run in runs))

    return SummaryReport(
        total_runs=total_runs,
        total_evaluated_runs=total_evaluated_runs,
        average_score=average_score,
        success_rate=success_rate,
        average_latency_ms=average_latency_ms,
        average_cost_usd=average_cost_usd,
        runs_by_model=runs_by_model,
        runs_by_benchmark=runs_by_benchmark,
    )


@app.get("/reports/failure-modes", response_model=FailureModeSummary)
def report_failure_modes(db: Session = Depends(get_db)) -> FailureModeSummary:
    analyses = db.execute(select(FailureAnalysis)).scalars().all()
    return FailureModeSummary(counts=dict(Counter(item.failure_mode for item in analyses)))
