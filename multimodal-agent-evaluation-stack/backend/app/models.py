from __future__ import annotations

from datetime import datetime
from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Benchmark(Base):
    __tablename__ = "benchmarks"

    benchmark_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    evaluator_type: Mapped[str] = mapped_column(String(50), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    expected_tools: Mapped[list] = mapped_column(JSON, default=list)
    expected_output: Mapped[dict] = mapped_column(JSON, default=dict)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Run(Base):
    __tablename__ = "runs"

    run_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    benchmark_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(100), nullable=False)
    inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    final_output: Mapped[dict] = mapped_column(JSON, default=dict)
    trajectory: Mapped[list] = mapped_column(JSON, default=list)
    screenshots: Mapped[list] = mapped_column(JSON, default=list)
    browser_state_refs: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    total_latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    success_claimed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Evaluation(Base):
    __tablename__ = "evaluations"

    evaluation_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    benchmark_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    evaluator_type: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FailureAnalysis(Base):
    __tablename__ = "failure_analysis"

    analysis_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    benchmark_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    failure_mode: Mapped[str] = mapped_column(String(100), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    signals: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
