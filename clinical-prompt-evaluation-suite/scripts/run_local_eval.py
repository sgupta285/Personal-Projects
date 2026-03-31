from sqlalchemy import select

from app import models
from app.db import Base, SessionLocal, engine
from app.services.evaluation_service import create_run, run_evaluation


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        prompt = db.execute(select(models.PromptVersion).where(models.PromptVersion.name == "baseline-utilization-summary")).scalar_one()
        dataset = db.execute(select(models.Dataset).where(models.Dataset.name == "clinical-note-summarization-demo")).scalar_one()
        run = create_run(db, prompt.id, dataset.id, prompt.provider, prompt.model_name)
        run = run_evaluation(db, run)
        print(f"Completed run {run.id}")
        print(run.aggregate_scores)
    finally:
        db.close()


if __name__ == "__main__":
    main()
