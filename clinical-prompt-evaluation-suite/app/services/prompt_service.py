from sqlalchemy.orm import Session

from app import models
from app.schemas import PromptVersionCreate


def create_prompt_version(db: Session, payload: PromptVersionCreate) -> models.PromptVersion:
    prompt = models.PromptVersion(**payload.model_dump())
    db.add(prompt)
    db.commit()
    db.refresh(prompt)
    return prompt
