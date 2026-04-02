from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.schemas import BreakdownResponse, MetricCatalogResponse, SummaryResponse
from app.repositories.usage_repository import UsageRepository
from app.services.analytics import AnalyticsService
from app.services.reporting import report_builder

router = APIRouter()


def get_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(UsageRepository(db))


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metric-catalog", response_model=MetricCatalogResponse)
def metric_catalog(service: AnalyticsService = Depends(get_service)):
    return service.get_metric_catalog()


@router.get("/usage/summary", response_model=SummaryResponse)
def usage_summary(
    workspace_id: str = Query("acme-cloud"),
    start_date: date | None = None,
    end_date: date | None = None,
    interval: str = Query("day", pattern="^(hour|day|month)$"),
    service: AnalyticsService = Depends(get_service),
):
    try:
        return service.get_summary(workspace_id, start_date, end_date, interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/usage/breakdown", response_model=BreakdownResponse)
def usage_breakdown(
    workspace_id: str = Query("acme-cloud"),
    start_date: date | None = None,
    end_date: date | None = None,
    interval: str = Query("day", pattern="^(hour|day|month)$"),
    dimension: str = Query("feature", pattern="^(feature|endpoint|region|plan|status_class)$"),
    limit: int = Query(12, ge=1, le=50),
    service: AnalyticsService = Depends(get_service),
):
    try:
        return service.get_breakdown(workspace_id, start_date, end_date, interval, dimension, limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/usage/export.csv")
def export_csv(
    workspace_id: str = Query("acme-cloud"),
    start_date: date | None = None,
    end_date: date | None = None,
    interval: str = Query("day", pattern="^(hour|day|month)$"),
    service: AnalyticsService = Depends(get_service),
):
    summary = service.get_summary(workspace_id, start_date, end_date, interval)
    csv_bytes = report_builder.build_csv(summary["time_series"])
    return Response(
        csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{workspace_id}-{interval}-usage.csv"'},
    )


@router.get("/usage/export.pdf")
def export_pdf(
    workspace_id: str = Query("acme-cloud"),
    start_date: date | None = None,
    end_date: date | None = None,
    interval: str = Query("day", pattern="^(hour|day|month)$"),
    dimension: str = Query("feature", pattern="^(feature|endpoint|region|plan|status_class)$"),
    service: AnalyticsService = Depends(get_service),
):
    summary = service.get_summary(workspace_id, start_date, end_date, interval)
    breakdown = service.get_breakdown(workspace_id, start_date, end_date, interval, dimension, 10)
    pdf_bytes = report_builder.build_pdf(
        workspace_id=workspace_id,
        start_date=date.fromisoformat(summary["start_date"]),
        end_date=date.fromisoformat(summary["end_date"]),
        totals=summary["totals"],
        breakdown_rows=breakdown["rows"],
    )
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{workspace_id}-{interval}-usage.pdf"'},
    )
