from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Any

from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import UsageEvent, UsageRollup
from app.models.schemas import Dimension, Interval


class UsageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def resolve_range(self, start_date: date | None, end_date: date | None) -> tuple[date, date]:
        today = date.today()
        end_resolved = end_date or today
        start_resolved = start_date or (end_resolved - timedelta(days=self.settings.default_lookback_days - 1))
        if start_resolved > end_resolved:
            raise ValueError("start_date cannot be after end_date")
        return start_resolved, end_resolved

    def list_workspaces(self) -> list[str]:
        stmt = select(UsageEvent.workspace_id).distinct().order_by(UsageEvent.workspace_id)
        return [row[0] for row in self.db.execute(stmt)]

    def fetch_summary(self, workspace_id: str, start_date: date | None, end_date: date | None, interval: Interval) -> dict[str, Any]:
        start_resolved, end_resolved = self.resolve_range(start_date, end_date)
        stmt = (
            select(UsageRollup)
            .where(
                and_(
                    UsageRollup.workspace_id == workspace_id,
                    UsageRollup.interval == interval,
                    UsageRollup.metric_family == "overview",
                    UsageRollup.group_value == "all",
                    UsageRollup.bucket_start >= datetime.combine(start_resolved, time.min),
                    UsageRollup.bucket_start <= datetime.combine(end_resolved, time.max),
                )
            )
            .order_by(UsageRollup.bucket_start)
        )
        rows = self.db.scalars(stmt).all()
        totals = {
            "request_units": sum(row.request_units for row in rows),
            "billable_units": sum(row.billable_units for row in rows),
            "total_cost_usd": round(sum(row.total_cost_usd for row in rows), 2),
            "avg_latency_ms": round(sum(row.avg_latency_ms for row in rows) / len(rows), 2) if rows else 0.0,
            "export_count": sum(row.export_count for row in rows),
        }
        return {
            "workspace_id": workspace_id,
            "interval": interval,
            "start_date": start_resolved.isoformat(),
            "end_date": end_resolved.isoformat(),
            "totals": totals,
            "time_series": [
                {
                    "bucket_start": row.bucket_start.isoformat(),
                    "request_units": row.request_units,
                    "billable_units": row.billable_units,
                    "total_cost_usd": round(row.total_cost_usd, 2),
                    "avg_latency_ms": round(row.avg_latency_ms, 2),
                    "export_count": row.export_count,
                }
                for row in rows
            ],
        }

    def fetch_breakdown(
        self,
        workspace_id: str,
        start_date: date | None,
        end_date: date | None,
        interval: Interval,
        dimension: Dimension,
        limit: int = 12,
    ) -> dict[str, Any]:
        start_resolved, end_resolved = self.resolve_range(start_date, end_date)
        stmt = (
            select(
                UsageRollup.group_value,
                func.sum(UsageRollup.request_units),
                func.sum(UsageRollup.billable_units),
                func.sum(UsageRollup.total_cost_usd),
                func.avg(UsageRollup.avg_latency_ms),
                func.sum(UsageRollup.export_count),
            )
            .where(
                and_(
                    UsageRollup.workspace_id == workspace_id,
                    UsageRollup.interval == interval,
                    UsageRollup.metric_family == dimension,
                    UsageRollup.bucket_start >= datetime.combine(start_resolved, time.min),
                    UsageRollup.bucket_start <= datetime.combine(end_resolved, time.max),
                )
            )
            .group_by(UsageRollup.group_value)
            .order_by(func.sum(UsageRollup.request_units).desc())
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return {
            "workspace_id": workspace_id,
            "dimension": dimension,
            "interval": interval,
            "rows": [
                {
                    "group_value": row[0],
                    "request_units": int(row[1] or 0),
                    "billable_units": int(row[2] or 0),
                    "total_cost_usd": round(float(row[3] or 0), 2),
                    "avg_latency_ms": round(float(row[4] or 0), 2),
                    "export_count": int(row[5] or 0),
                }
                for row in rows
            ],
        }

    def build_metric_catalog(self) -> dict[str, Any]:
        return {
            "intervals": ["hour", "day", "month"],
            "dimensions": ["feature", "endpoint", "region", "plan", "status_class"],
            "metrics": ["request_units", "billable_units", "total_cost_usd", "avg_latency_ms", "export_count"],
            "workspaces": self.list_workspaces(),
        }
