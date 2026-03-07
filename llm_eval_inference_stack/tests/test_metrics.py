from app.eval.metrics import recall_at_k, reciprocal_rank


def test_recall_at_k_hit() -> None:
    assert recall_at_k(["d1", "d2", "d3"], "d2", 3) == 1.0


def test_recall_at_k_miss() -> None:
    assert recall_at_k(["d1", "d2", "d3"], "d4", 3) == 0.0


def test_reciprocal_rank() -> None:
    assert reciprocal_rank(["d9", "d2", "d3"], "d2") == 0.5
