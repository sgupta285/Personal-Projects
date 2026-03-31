from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.config import settings
from app.schemas import AdminMetrics, AssignmentOut, BulkTaskCreate, ResponseCreate, ResponseOut, ReviewCreate, ReviewOut, TaskOut, UserCreate, UserOut
from app.services.repository import Repository

app = FastAPI(title=settings.app_name)
repo = Repository()


@app.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.app_name}


@app.post('/api/users', response_model=UserOut)
def create_user(payload: UserCreate) -> UserOut:
    return repo.create_user(payload.model_dump())


@app.get('/api/users', response_model=list[UserOut])
def list_users() -> list[UserOut]:
    return repo.list_users()


@app.post('/api/tasks/bulk', response_model=list[TaskOut])
def create_tasks(payload: BulkTaskCreate) -> list[TaskOut]:
    return repo.create_tasks([task.model_dump() for task in payload.tasks])


@app.get('/api/tasks', response_model=list[TaskOut])
def list_tasks() -> list[TaskOut]:
    return repo.list_tasks()


@app.post('/api/assignments/next/{user_id}', response_model=AssignmentOut | None)
def assign_next_task(user_id: int) -> AssignmentOut | None:
    assignment = repo.assign_next_task(user_id)
    if assignment is None:
        return None
    return assignment


@app.post('/api/responses', response_model=ResponseOut)
def submit_response(payload: ResponseCreate) -> ResponseOut:
    try:
        return repo.submit_response(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get('/api/reviews/pending', response_model=list[ResponseOut])
def pending_reviews() -> list[ResponseOut]:
    return repo.list_pending_responses()


@app.post('/api/reviews', response_model=ReviewOut)
def create_review(payload: ReviewCreate) -> ReviewOut:
    try:
        return repo.create_review(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get('/api/admin/metrics', response_model=AdminMetrics)
def admin_metrics() -> AdminMetrics:
    return repo.admin_metrics()
