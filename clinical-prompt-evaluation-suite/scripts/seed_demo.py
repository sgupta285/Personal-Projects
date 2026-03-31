from pathlib import Path

from sqlalchemy import select

from app import models
from app.db import Base, SessionLocal, engine
from app.schemas import PromptVersionCreate
from app.services.dataset_service import import_dataset_from_json
from app.services.prompt_service import create_prompt_version


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing_dataset = db.execute(
            select(models.Dataset).where(models.Dataset.name == "clinical-note-summarization-demo")
        ).scalar_one_or_none()
        if existing_dataset is None:
            import_dataset_from_json(db, Path("data/sample_clinical_dataset.json"))

        prompt_payload = PromptVersionCreate(
            name="baseline-utilization-summary",
            workflow_name="utilization-review-summary",
            provider="mock",
            model_name="demo-model",
            system_prompt=(
                "You are assisting an operations team with structured clinical note summarization. "
                "Do not diagnose or recommend treatment. "
                "Extract only what is supported by the note and populate follow_up_questions when details are missing."
            ),
            notes="Seeded baseline prompt version for demo evaluation runs.",
        )
        existing_prompt = db.execute(
            select(models.PromptVersion).where(models.PromptVersion.name == prompt_payload.name)
        ).scalar_one_or_none()
        if existing_prompt is None:
            create_prompt_version(db, prompt_payload)
    finally:
        db.close()

    print("Seed complete.")


if __name__ == "__main__":
    main()
