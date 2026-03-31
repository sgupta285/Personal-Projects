from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import EvaluationRunCreate, RunResponse
from app.services.evaluation_service import create_run, run_evaluation

router = APIRouter(prefix="/runs", tags=["runs"])


@router.get("/", response_model=list[RunResponse])
def list_runs(db: Session = Depends(get_db)):
    return db.query(models.EvaluationRun).order_by(models.EvaluationRun.created_at.desc()).all()


@router.post("/", response_model=RunResponse)
def create_and_execute_run(payload: EvaluationRunCreate, db: Session = Depends(get_db)):
    prompt = db.get(models.PromptVersion, payload.prompt_version_id)
    dataset = db.get(models.Dataset, payload.dataset_id)
    if prompt is None or dataset is None:
        raise HTTPException(status_code=404, detail="Prompt version or dataset not found.")

    provider = payload.provider or prompt.provider
    model_name = payload.model_name or prompt.model_name
    run = create_run(db, prompt.id, dataset.id, provider, model_name)
    return run_evaluation(db, run)


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.get(models.EvaluationRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run
