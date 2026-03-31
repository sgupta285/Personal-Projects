from __future__ import annotations

from app.evaluators.heuristics import hallucination_risk, keyword_recall, schema_adherence
from app.evaluators.rubric import build_rubric_scores
from app.services.output_validation import validate_structured_output


def score_output(output: dict, input_text: str, expected_keywords: list[str]) -> dict:
    validation_passed, validation_issues, normalized_output = validate_structured_output(output)
    rubric_scores = build_rubric_scores(normalized_output, expected_keywords)
    metric_scores = {
        "schema_adherence": schema_adherence(validation_passed),
        "keyword_recall": keyword_recall(normalized_output, expected_keywords),
        "hallucination_risk": hallucination_risk(normalized_output, input_text),
    }
    metric_scores["composite"] = round(
        (
            metric_scores["schema_adherence"] * 0.35
            + metric_scores["keyword_recall"] * 0.35
            + metric_scores["hallucination_risk"] * 0.30
        ),
        4,
    )
    return {
        "validation_passed": validation_passed,
        "validation_issues": validation_issues,
        "normalized_output": normalized_output,
        "rubric_scores": rubric_scores,
        "metric_scores": metric_scores,
    }


def aggregate_run_scores(item_scores: list[dict]) -> dict:
    if not item_scores:
        return {}
    return {
        "avg_overall_rubric": round(sum(item["rubric_scores"]["overall"] for item in item_scores) / len(item_scores), 4),
        "avg_keyword_recall": round(sum(item["metric_scores"]["keyword_recall"] for item in item_scores) / len(item_scores), 4),
        "avg_schema_adherence": round(sum(item["metric_scores"]["schema_adherence"] for item in item_scores) / len(item_scores), 4),
        "avg_hallucination_risk": round(sum(item["metric_scores"]["hallucination_risk"] for item in item_scores) / len(item_scores), 4),
        "avg_composite": round(sum(item["metric_scores"]["composite"] for item in item_scores) / len(item_scores), 4),
        "items_scored": len(item_scores),
    }
