from app.services.output_validation import validate_structured_output


def test_validate_structured_output_success():
    payload = {
        "member_id": "M-1",
        "encounter_date": "2026-01-01",
        "requested_service": "MRI",
        "primary_reason": "Persistent pain",
        "evidence_for_approval": [],
        "evidence_for_denial": [],
        "risk_flags": [],
        "follow_up_questions": [],
        "summary": "Short summary of the case with supporting details.",
        "confidence": 0.82,
    }
    passed, issues, normalized = validate_structured_output(payload)
    assert passed is True
    assert issues == []
    assert normalized["member_id"] == "M-1"


def test_validate_structured_output_failure():
    payload = {"member_id": "M-1"}
    passed, issues, _ = validate_structured_output(payload)
    assert passed is False
    assert any("requested_service" in issue for issue in issues)
