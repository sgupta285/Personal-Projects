from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.db import get_db
from app.schemas import PromptVersionCreate, PromptVersionResponse
from app.services.prompt_service import create_prompt_version

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/", response_model=list[PromptVersionResponse])
def list_prompt_versions(db: Session = Depends(get_db)):
    return db.query(models.PromptVersion).order_by(models.PromptVersion.created_at.desc()).all()


@router.post("/", response_model=PromptVersionResponse)
def create_prompt_version_route(payload: PromptVersionCreate, db: Session = Depends(get_db)):
    return create_prompt_version(db, payload)
