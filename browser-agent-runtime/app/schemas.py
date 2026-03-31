from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models import ActionStatus, ArtifactType, RunStatus, TaskStatus


PermissionName = Literal["read_only", "navigation", "form_fill", "submission"]


class TaskCreate(BaseModel):
    name: str = Field(min_length=3, max_length=200)
    description: str | None = None
    instruction: str = Field(min_length=5)
    start_url: str | None = None
    dry_run: bool = True


class TaskRead(BaseModel):
    id: int
    name: str
    description: str | None
    instruction: str
    start_url: str | None
    dry_run: bool
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlannedAction(BaseModel):
    name: str
    permission: PermissionName
    params: dict[str, Any] = Field(default_factory=dict)


class RunCreate(BaseModel):
    headless: bool = True


class ActionLogRead(BaseModel):
    id: int
    sequence: int
    action_name: str
    permission: str
    status: ActionStatus
    params: dict[str, Any]
    result: dict[str, Any] | None
    error_message: str | None
    screenshot_path: str | None
    started_at: datetime | None
    finished_at: datetime | None

    model_config = {"from_attributes": True}


class ArtifactRead(BaseModel):
    id: int
    artifact_type: ArtifactType
    path: str
    metadata_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskRunRead(BaseModel):
    id: int
    task_id: int
    status: RunStatus
    dry_run: bool
    headless: bool
    planned_actions: list[dict[str, Any]]
    summary: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
    actions: list[ActionLogRead] = Field(default_factory=list)
    artifacts: list[ArtifactRead] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class EnqueueResponse(BaseModel):
    task: TaskRead
    run: TaskRunRead
