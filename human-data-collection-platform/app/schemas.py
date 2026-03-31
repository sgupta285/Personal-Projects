from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TaskType = Literal[
    "ranking",
    "classification",
    "pairwise_preference",
    "freeform_critique",
    "moderation_review",
]
UserRole = Literal["annotator", "reviewer", "admin", "researcher"]


class UserCreate(BaseModel):
    name: str
    email: str | None = None
    role: UserRole
    skill_level: str = "general"


class UserOut(UserCreate):
    id: int
    is_active: bool = True


class TaskCreate(BaseModel):
    task_type: TaskType
    priority: int = Field(default=50, ge=0, le=100)
    batch_name: str | None = None
    requires_review: bool = True
    seed_task: bool = False
    payload: dict[str, Any]
    gold: dict[str, Any] | None = None


class BulkTaskCreate(BaseModel):
    tasks: list[TaskCreate]


class TaskOut(BaseModel):
    id: int
    task_type: TaskType
    status: str
    priority: int
    batch_name: str | None = None
    requires_review: bool
    seed_task: bool
    payload: dict[str, Any]
    gold: dict[str, Any] | None = None


class AssignmentOut(BaseModel):
    id: int
    task_id: int
    user_id: int
    status: str
    task: TaskOut


class ResponseCreate(BaseModel):
    assignment_id: int
    response: dict[str, Any]
    time_spent_seconds: int = Field(default=0, ge=0)


class ResponseOut(BaseModel):
    id: int
    assignment_id: int
    task_id: int
    user_id: int
    response: dict[str, Any]
    quality_flags: dict[str, Any] | None = None
    time_spent_seconds: int


class ReviewCreate(BaseModel):
    response_id: int
    reviewer_id: int
    decision: Literal["approved", "rejected", "needs_rework"]
    score: float = Field(default=0, ge=0, le=1)
    notes: str = ""


class ReviewOut(BaseModel):
    id: int
    response_id: int
    reviewer_id: int
    decision: str
    score: float
    notes: str


class AdminMetrics(BaseModel):
    open_tasks: int
    in_progress_tasks: int
    pending_review_tasks: int
    completed_tasks: int
    total_responses: int
    total_reviews: int
    seed_task_accuracy: float
    average_review_score: float
    throughput_by_type: dict[str, int]
    agreement_summary: dict[str, Any]
