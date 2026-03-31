from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

from app.config import settings


def export_run_to_excel(run, item_results) -> str:
    export_dir = Path(settings.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()

    summary_sheet = workbook.active
    summary_sheet.title = "Run Summary"
    summary_sheet.append(["Run ID", run.id])
    summary_sheet.append(["Status", run.status])
    summary_sheet.append(["Provider", run.provider])
    summary_sheet.append(["Model", run.model_name])
    for key, value in run.aggregate_scores.items():
        summary_sheet.append([key, value])

    results_sheet = workbook.create_sheet("Item Results")
    results_sheet.append(
        [
            "dataset_item_id",
            "validation_passed",
            "rubric_overall",
            "keyword_recall",
            "schema_adherence",
            "hallucination_risk",
            "latency_ms",
            "summary",
        ]
    )

    for result in item_results:
        results_sheet.append(
            [
                result.dataset_item_id,
                result.validation_passed,
                result.rubric_scores.get("overall"),
                result.metric_scores.get("keyword_recall"),
                result.metric_scores.get("schema_adherence"),
                result.metric_scores.get("hallucination_risk"),
                result.latency_ms,
                result.structured_output.get("summary", ""),
            ]
        )

    path = export_dir / f"run_{run.id}_report.xlsx"
    workbook.save(path)
    return str(path)
