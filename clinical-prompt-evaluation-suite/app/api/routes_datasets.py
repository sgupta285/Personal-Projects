from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import DatasetCreate, DatasetResponse
from app.services.dataset_service import create_dataset

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("/", response_model=list[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    return db.query(models.Dataset).order_by(models.Dataset.created_at.desc()).all()


@router.post("/", response_model=DatasetResponse)
def create_dataset_route(payload: DatasetCreate, db: Session = Depends(get_db)):
    return create_dataset(db, payload)
