from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models import RunStatus, Task, TaskRun, TaskStatus
from app.runtime.planner import RuleBasedPlanner
from app.services.queue import enqueue_run


planner = RuleBasedPlanner()


def create_task(
    db: Session,
    *,
    name: str,
    description: str | None,
    instruction: str,
    start_url: str | None,
    dry_run: bool,
) -> Task:
    task = Task(
        name=name,
        description=description,
        instruction=instruction,
        start_url=start_url,
        dry_run=dry_run,
        status=TaskStatus.draft,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return (
        db.query(Task)
        .options(joinedload(Task.runs).joinedload(TaskRun.actions), joinedload(Task.runs).joinedload(TaskRun.artifacts))
        .filter(Task.id == task_id)
        .first()
    )


def list_tasks(db: Session) -> list[Task]:
    return db.query(Task).order_by(Task.created_at.desc()).all()


def create_run(db: Session, *, task: Task, headless: bool) -> TaskRun:
    planned_actions = [action.model_dump() for action in planner.build_plan(task.instruction, task.start_url)]
    run = TaskRun(
        task_id=task.id,
        dry_run=task.dry_run,
        headless=headless,
        status=RunStatus.queued,
        planned_actions=planned_actions,
    )
    task.status = TaskStatus.queued
    db.add(run)
    db.commit()
    db.refresh(run)
    enqueue_run(run.id)
    return run


def get_run(db: Session, run_id: int) -> TaskRun | None:
    return (
        db.query(TaskRun)
        .options(joinedload(TaskRun.actions), joinedload(TaskRun.artifacts))
        .filter(TaskRun.id == run_id)
        .first()
    )
