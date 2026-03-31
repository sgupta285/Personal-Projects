from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class TrajectoryStep(BaseModel):
    step_index: int
    tool_name: str
    action: str
    observation: str | None = None
    latency_ms: int = 0
    success: bool = True
    screenshot_ref: str | None = None
    state_ref: str | None = None


class BenchmarkCreate(BaseModel):
    benchmark_id: str
    name: str
    version: str
    task_type: str
    evaluator_type: Literal["exact_match", "rubric"]
    instructions: str
    expected_tools: list[str] = Field(default_factory=list)
    expected_output: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BenchmarkRead(BenchmarkCreate):
    created_at: datetime


class RunCreate(BaseModel):
    benchmark_id: str
    model_name: str
    prompt_version: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    final_output: dict[str, Any] = Field(default_factory=dict)
    trajectory: list[TrajectoryStep] = Field(default_factory=list)
    screenshots: list[str] = Field(default_factory=list)
    browser_state_refs: list[str] = Field(default_factory=list)
    status: str = "completed"
    total_latency_ms: int = 0
    estimated_cost_usd: float = 0.0
    success_claimed: bool = False


class RunRead(RunCreate):
    run_id: str
    created_at: datetime


class EvaluationRead(BaseModel):
    evaluation_id: str
    run_id: str
    benchmark_id: str
    evaluator_type: str
    score: float
    success: bool
    metrics: dict[str, Any]
    created_at: datetime


class FailureAnalysisRead(BaseModel):
    analysis_id: str
    run_id: str
    benchmark_id: str
    failure_mode: str
    rationale: str
    signals: dict[str, Any]
    created_at: datetime


class SummaryReport(BaseModel):
    total_runs: int
    total_evaluated_runs: int
    average_score: float
    success_rate: float
    average_latency_ms: float
    average_cost_usd: float
    runs_by_model: dict[str, int]
    runs_by_benchmark: dict[str, int]


class FailureModeSummary(BaseModel):
    counts: dict[str, int]
