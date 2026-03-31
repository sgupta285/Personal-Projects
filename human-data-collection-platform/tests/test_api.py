from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module
from app.config import settings


def setup_module(module):
    db_path = Path(settings.database_path)
    if db_path.exists():
        db_path.unlink()
    main_module.repo = main_module.Repository()


client = TestClient(main_module.app)


def test_end_to_end_annotation_flow():
    user = client.post(
        "/api/users",
        json={"name": "Alicia", "email": "annotator@example.com", "role": "annotator", "skill_level": "general"},
    )
    reviewer = client.post(
        "/api/users",
        json={"name": "Riley", "email": "reviewer@example.com", "role": "reviewer", "skill_level": "senior"},
    )
    assert user.status_code == 200
    assert reviewer.status_code == 200

    task_payload = {
        "tasks": [
            {
                "task_type": "classification",
                "priority": 90,
                "batch_name": "test-batch",
                "requires_review": True,
                "seed_task": True,
                "payload": {"instruction": "Classify", "text": "Refund requested"},
                "gold": {"key": "label", "label": "billing"},
            }
        ]
    }
    created = client.post("/api/tasks/bulk", json=task_payload)
    assert created.status_code == 200
    task_id = created.json()[0]["id"]

    assignment = client.post(f"/api/assignments/next/{user.json()['id']}")
    assert assignment.status_code == 200
    assignment_id = assignment.json()["id"]
    assert assignment.json()["task_id"] == task_id

    response = client.post(
        "/api/responses",
        json={"assignment_id": assignment_id, "response": {"label": "billing"}, "time_spent_seconds": 12},
    )
    assert response.status_code == 200
    assert response.json()["quality_flags"]["seed_score"]["score"] == 1.0

    pending = client.get("/api/reviews/pending")
    assert pending.status_code == 200
    response_id = pending.json()[0]["id"]

    review = client.post(
        "/api/reviews",
        json={"response_id": response_id, "reviewer_id": reviewer.json()['id'], "decision": "approved", "score": 0.95, "notes": "Looks good."},
    )
    assert review.status_code == 200

    metrics = client.get("/api/admin/metrics")
    assert metrics.status_code == 200
    body = metrics.json()
    assert body["completed_tasks"] == 1
    assert body["total_responses"] == 1
    assert body["total_reviews"] == 1
