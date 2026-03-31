from sqlalchemy import select

from app import models
from app.db import SessionLocal
from app.services.exports import export_run_to_excel


def main():
    db = SessionLocal()
    try:
        run = db.execute(select(models.EvaluationRun).order_by(models.EvaluationRun.id.desc())).scalar_one()
        item_results = db.execute(
            select(models.ItemEvaluationResult).where(models.ItemEvaluationResult.run_id == run.id)
        ).scalars().all()
        path = export_run_to_excel(run, item_results)
        print(path)
    finally:
        db.close()


if __name__ == "__main__":
    main()
