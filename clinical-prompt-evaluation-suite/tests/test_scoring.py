from app.services.scoring import aggregate_run_scores, score_output


def test_score_output_produces_metrics():
    payload = {
        "member_id": "M-1",
        "encounter_date": "2026-01-01",
        "requested_service": "MRI",
        "primary_reason": "Persistent pain",
        "evidence_for_approval": ["failed conservative therapy"],
        "evidence_for_denial": [],
        "risk_flags": ["Fall risk"],
        "follow_up_questions": ["Clarify duration of symptoms."],
        "summary": "Persistent pain after conservative therapy with fall risk.",
        "confidence": 0.77,
    }
    result = score_output(payload, "Failed conservative therapy with fall risk.", ["failed conservative therapy", "fall risk"])
    assert result["validation_passed"] is True
    assert result["metric_scores"]["keyword_recall"] == 1.0
    assert result["rubric_scores"]["overall"] >= 4.0


def test_aggregate_run_scores():
    items = [
        {
            "rubric_scores": {"overall": 4.5},
            "metric_scores": {
                "keyword_recall": 1.0,
                "schema_adherence": 1.0,
                "hallucination_risk": 1.0,
                "composite": 1.0,
            },
        },
        {
            "rubric_scores": {"overall": 4.0},
            "metric_scores": {
                "keyword_recall": 0.5,
                "schema_adherence": 1.0,
                "hallucination_risk": 0.8,
                "composite": 0.76,
            },
        },
    ]
    aggregate = aggregate_run_scores(items)
    assert aggregate["items_scored"] == 2
    assert aggregate["avg_overall_rubric"] == 4.25
