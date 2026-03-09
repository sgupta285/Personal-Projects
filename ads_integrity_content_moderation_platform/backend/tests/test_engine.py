from worker.engine import combine_scores, decide_status


def test_combine_scores_caps_at_one():
    assert combine_scores(0.9, 0.95) <= 1.0


def test_decision_thresholds():
    assert decide_status(0.90) == "blocked"
    assert decide_status(0.70) == "in_review"
    assert decide_status(0.20) == "approved"
