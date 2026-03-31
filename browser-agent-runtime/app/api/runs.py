from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import TaskRunRead
from app.services.tasks import create_run, get_run

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/{run_id}", response_model=TaskRunRead)
def get_run_endpoint(run_id: int, db: Session = Depends(get_db)) -> TaskRunRead:
    run = get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post("/{run_id}/replay", response_model=TaskRunRead, status_code=status.HTTP_201_CREATED)
def replay_run_endpoint(run_id: int, db: Session = Depends(get_db)) -> TaskRunRead:
    original = get_run(db, run_id)
    if not original:
        raise HTTPException(status_code=404, detail="Run not found")
    replay = create_run(db, task=original.task, headless=original.headless)
    return replay
