from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import EnqueueResponse, RunCreate, TaskCreate, TaskRead, TaskRunRead
from app.services.tasks import create_run, create_task, get_task, list_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(payload: TaskCreate, db: Session = Depends(get_db)) -> TaskRead:
    task = create_task(
        db,
        name=payload.name,
        description=payload.description,
        instruction=payload.instruction,
        start_url=payload.start_url,
        dry_run=payload.dry_run,
    )
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks_endpoint(db: Session = Depends(get_db)) -> list[TaskRead]:
    return list_tasks(db)


@router.get("/{task_id}", response_model=TaskRead)
def get_task_endpoint(task_id: int, db: Session = Depends(get_db)) -> TaskRead:
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/runs", response_model=EnqueueResponse, status_code=status.HTTP_201_CREATED)
def enqueue_task_run(task_id: int, payload: RunCreate, db: Session = Depends(get_db)) -> EnqueueResponse:
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    run = create_run(db, task=task, headless=payload.headless)
    return EnqueueResponse(task=task, run=run)


@router.get("/{task_id}/runs", response_model=list[TaskRunRead])
def list_task_runs(task_id: int, db: Session = Depends(get_db)) -> list[TaskRunRead]:
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.runs
