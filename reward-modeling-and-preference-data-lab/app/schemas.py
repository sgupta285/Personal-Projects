from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class DatasetCreate(BaseModel):
    name: str = Field(min_length=3)
    description: str = ""
    task_family: str = Field(default="preference_ranking")


class DatasetRead(BaseModel):
    id: int
    name: str
    description: str
    task_family: str
    created_at: datetime


class CandidateCreate(BaseModel):
    label: str
    response_text: str
    model_name: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PreferenceExampleCreate(BaseModel):
    dataset_id: int
    prompt_text: str
    task_type: str = "ranking"
    context: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    candidates: list[CandidateCreate] = Field(min_length=2)


class PreferenceExampleRead(BaseModel):
    id: int
    dataset_id: int
    prompt_text: str
    task_type: str
    context: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime
    candidates: list[dict[str, Any]]


class PreferenceSubmission(BaseModel):
    example_id: int
    annotator_id: str
    ranking: list[int] = Field(min_length=2)
    notes: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class PreferenceRead(BaseModel):
    id: int
    example_id: int
    annotator_id: str
    winner_candidate_id: int | None
    ranking: list[int]
    notes: str
    metadata: dict[str, Any]
    created_at: datetime


class SnapshotCreate(BaseModel):
    dataset_id: int
    version_name: str
    selection_filter: dict[str, Any] = Field(default_factory=dict)


class SnapshotRead(BaseModel):
    id: int
    dataset_id: int
    version_name: str
    manifest: dict[str, Any]
    created_at: datetime


class ExperimentRunCreate(BaseModel):
    dataset_id: int
    snapshot_id: int | None = None
    name: str
    config: dict[str, Any] = Field(default_factory=dict)
    metrics: dict[str, Any] = Field(default_factory=dict)


class ExperimentRunRead(BaseModel):
    id: int
    dataset_id: int
    snapshot_id: int | None
    name: str
    config: dict[str, Any]
    metrics: dict[str, Any]
    created_at: datetime


class SearchResult(BaseModel):
    example_id: int
    prompt_text: str
    task_type: str
    similarity: float
    top_candidate_labels: list[str]


class AnalyticsOverview(BaseModel):
    datasets: int
    examples: int
    preferences: int
    snapshots: int
    experiments: int
    examples_per_task_type: dict[str, int]
    preferences_per_annotator: dict[str, int]


class AgreementReport(BaseModel):
    dataset_id: int
    total_examples_with_multiple_judgments: int
    exact_winner_agreement_rate: float
    pairwise_agreement_rate: float
    winner_distribution: dict[str, int]


class BiasReport(BaseModel):
    dataset_id: int
    model_win_rates: dict[str, float]
    position_bias_rate: float
    average_candidate_length_by_model: dict[str, float]


class PromptSensitivityPoint(BaseModel):
    prompt_cluster: str
    task_type: str
    average_margin: float
    examples: int


class PromptSensitivityReport(BaseModel):
    dataset_id: int
    segments: list[PromptSensitivityPoint]


class RewardTargetRead(BaseModel):
    example_id: int
    method: Literal["normalized_win_rate"]
    targets: dict[str, float]
