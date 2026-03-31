from app.db import Base, SessionLocal, engine
from app.services.tasks import create_task

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    task = create_task(
        db,
        name="Invoice portal demo",
        description="Demo task used for local development.",
        instruction="Log into the portal and inspect the latest invoice details.",
        start_url="https://example.com/login",
        dry_run=True,
    )
    print(f"Created task {task.id}")
finally:
    db.close()
