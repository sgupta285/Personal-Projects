from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class ClinicalSummarySchema(BaseModel):
    member_id: str
    encounter_date: str
    requested_service: str
    primary_reason: str
    evidence_for_approval: list[str] = Field(default_factory=list)
    evidence_for_denial: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)


class DatasetItemCreate(BaseModel):
    item_key: str
    input_text: str
    expected_output: dict[str, Any]
    expected_keywords: list[str] = Field(default_factory=list)
    difficulty: str = "medium"
    split: str = "test"


class DatasetCreate(BaseModel):
    name: str
    workflow_name: str
    description: str | None = None
    items: list[DatasetItemCreate] = Field(default_factory=list)


class PromptVersionCreate(BaseModel):
    name: str
    workflow_name: str
    provider: str = "mock"
    model_name: str = "demo-model"
    system_prompt: str
    output_schema_version: str = "v1"
    temperature: float = 0.2
    notes: str | None = None


class EvaluationRunCreate(BaseModel):
    prompt_version_id: int
    dataset_id: int
    provider: str | None = None
    model_name: str | None = None


class DatasetResponse(BaseModel):
    id: int
    name: str
    workflow_name: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromptVersionResponse(BaseModel):
    id: int
    name: str
    workflow_name: str
    provider: str
    model_name: str
    output_schema_version: str
    temperature: float
    notes: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RunResponse(BaseModel):
    id: int
    status: str
    provider: str
    model_name: str
    aggregate_scores: dict[str, Any]
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
