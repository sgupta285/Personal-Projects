from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.services.exports import export_run_to_excel

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/runs/{run_id}/excel")
def export_run_excel(run_id: int, db: Session = Depends(get_db)):
    run = db.get(models.EvaluationRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found.")
    item_results = (
        db.query(models.ItemEvaluationResult)
        .filter(models.ItemEvaluationResult.run_id == run_id)
        .order_by(models.ItemEvaluationResult.dataset_item_id.asc())
        .all()
    )
    path = export_run_to_excel(run, item_results)
    return {"path": path, "items": len(item_results)}
