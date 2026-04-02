from typing import Any

from pydantic import BaseModel, Field


class ContextFeatures(BaseModel):
    hour_of_day: int = 12
    device_type: str = "web"


class RecommendationRequest(BaseModel):
    user_id: str
    item_id: str | None = None
    surface: str = Field(default="home", pattern="^(home|search|related_items)$")
    limit: int = 20
    context: ContextFeatures = ContextFeatures()


class RecommendationItem(BaseModel):
    item_id: str
    title: str
    category: str
    score: float
    reason: str
    experiment_variant: str
    features: dict[str, Any]


class RecommendationResponse(BaseModel):
    user_id: str
    surface: str
    variant: str
    candidates_considered: int
    items: list[RecommendationItem]


class AssignmentResponse(BaseModel):
    user_id: str
    experiment_name: str
    variant: str


class ExperimentEvent(BaseModel):
    user_id: str
    variant: str
    clicked: int
    converted: int


class ExperimentSummaryRequest(BaseModel):
    events: list[ExperimentEvent]
