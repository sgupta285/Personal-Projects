from app.services.quality import detect_response_anomalies, score_seed_task, simple_agreement


def test_seed_task_scoring_matches_expected_label():
    result = score_seed_task({"instruction": "Classify"}, {"label": "billing"}, {"key": "label", "label": "billing"})
    assert result["score"] == 1.0
    assert result["matched"] is True


def test_anomaly_detection_flags_too_fast_and_too_short():
    result = detect_response_anomalies({"label": "a"}, 1)
    assert result["flagged"] is True
    assert result["suspiciously_fast"] is True


def test_simple_agreement_finds_majority():
    result = simple_agreement(["Billing", "billing", "shipping"])
    assert result["majority"] == "billing"
    assert result["agreement_rate"] == 0.6667
