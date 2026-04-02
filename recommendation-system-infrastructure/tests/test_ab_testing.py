from app.services.ab_testing import ExperimentService


def test_assignment_is_stable():
    service = ExperimentService()
    first = service.get_assignment("user_0010")
    second = service.get_assignment("user_0010")
    assert first == second
    assert first["variant"] in {"baseline", "neural_rerank"}
