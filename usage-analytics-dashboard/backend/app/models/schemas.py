from datetime import datetime, date
from typing import Literal

from pydantic import BaseModel, Field


Interval = Literal["hour", "day", "month"]
Dimension = Literal["feature", "endpoint", "region", "plan", "status_class"]


class DateRangeParams(BaseModel):
    workspace_id: str = Field(default="acme-cloud")
    start_date: date | None = None
    end_date: date | None = None
    interval: Interval = "day"


class TimeSeriesPoint(BaseModel):
    bucket_start: datetime
    request_units: int
    billable_units: int
    total_cost_usd: float
    avg_latency_ms: float
    export_count: int


class SummaryResponse(BaseModel):
    workspace_id: str
    interval: Interval
    start_date: date
    end_date: date
    totals: dict[str, float | int]
    time_series: list[TimeSeriesPoint]


class BreakdownRow(BaseModel):
    group_value: str
    request_units: int
    billable_units: int
    total_cost_usd: float
    avg_latency_ms: float
    export_count: int


class BreakdownResponse(BaseModel):
    workspace_id: str
    dimension: Dimension
    interval: Interval
    rows: list[BreakdownRow]


class MetricCatalogResponse(BaseModel):
    intervals: list[str]
    dimensions: list[str]
    metrics: list[str]
    workspaces: list[str]
