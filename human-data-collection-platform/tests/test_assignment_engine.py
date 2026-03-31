from app.services.assignment_engine import choose_next_task


def test_choose_seed_task_first_for_annotator():
    tasks = [
        {"id": 1, "status": "open", "priority": 50, "seed_task": False},
        {"id": 2, "status": "open", "priority": 20, "seed_task": True},
        {"id": 3, "status": "open", "priority": 99, "seed_task": False},
    ]
    chosen = choose_next_task(tasks, set(), "annotator")
    assert chosen["id"] == 2


def test_reviewer_only_gets_pending_review():
    tasks = [
        {"id": 1, "status": "open", "priority": 50, "seed_task": True},
        {"id": 2, "status": "pending_review", "priority": 10, "seed_task": False},
    ]
    chosen = choose_next_task(tasks, set(), "reviewer")
    assert chosen["id"] == 2
