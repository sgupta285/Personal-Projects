from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import ActionLog, ActionStatus, Artifact, ArtifactType, RunStatus, TaskRun
from app.runtime.browser_tools import BrowserToolkit, DryRunBrowserToolkit
from app.runtime.permissions import PermissionPolicy
from app.schemas import PlannedAction

logger = logging.getLogger(__name__)


class TaskExecutor:
    def __init__(self) -> None:
        self.permission_policy = PermissionPolicy()

    async def execute_run(self, db: Session, run: TaskRun) -> TaskRun:
        run.status = RunStatus.running
        run.started_at = datetime.utcnow()
        db.commit()
        db.refresh(run)

        toolkit_cls = DryRunBrowserToolkit if run.dry_run else BrowserToolkit

        try:
            async with toolkit_cls(headless=run.headless) as browser:
                for index, action_dict in enumerate(run.planned_actions, start=1):
                    action = PlannedAction.model_validate(action_dict)
                    await self._execute_action(db, run, browser, index, action)

                run.status = RunStatus.completed
                run.summary = f"Completed {len(run.planned_actions)} planned actions."
                final_dom = await browser.dom_summary()
                self._store_artifact(
                    db,
                    run_id=run.id,
                    artifact_type=ArtifactType.json_trace,
                    path=f"run:{run.id}:dom-summary",
                    metadata_json=final_dom,
                )
        except Exception as exc:
            logger.exception("Run %s failed", run.id)
            run.status = RunStatus.failed
            run.error_message = str(exc)
            run.summary = "Run failed before all actions completed."
        finally:
            run.finished_at = datetime.utcnow()
            db.commit()
            db.refresh(run)

        return run

    async def _execute_action(
        self,
        db: Session,
        run: TaskRun,
        browser,
        sequence: int,
        action: PlannedAction,
    ) -> None:
        decision = self.permission_policy.check(action.permission, run.dry_run)
        action_log = ActionLog(
            run_id=run.id,
            sequence=sequence,
            action_name=action.name,
            permission=action.permission,
            params=action.params,
            status=ActionStatus.pending,
            started_at=datetime.utcnow(),
        )
        db.add(action_log)
        db.commit()
        db.refresh(action_log)

        if not decision.allowed:
            action_log.status = ActionStatus.blocked
            action_log.error_message = decision.reason
            action_log.finished_at = datetime.utcnow()
            db.commit()
            return

        try:
            tool = getattr(browser, action.name)
        except AttributeError as exc:
            action_log.status = ActionStatus.failed
            action_log.error_message = f"Unknown action tool: {action.name}"
            action_log.finished_at = datetime.utcnow()
            db.commit()
            raise RuntimeError(f"Unknown action tool: {action.name}") from exc

        try:
            result = await asyncio.wait_for(tool(**action.params), timeout=30)
            action_log.status = ActionStatus.success
            action_log.result = result

            screenshot_result = await browser.screenshot(name=f"run-{run.id}-step-{sequence}")
            screenshot_path = screenshot_result.get("path")
            action_log.screenshot_path = screenshot_path

            if screenshot_path:
                self._store_artifact(
                    db,
                    run_id=run.id,
                    artifact_type=ArtifactType.screenshot,
                    path=screenshot_path,
                    metadata_json={"step": sequence, "action": action.name},
                )

        except Exception as exc:
            action_log.status = ActionStatus.failed
            action_log.error_message = str(exc)
            raise
        finally:
            action_log.finished_at = datetime.utcnow()
            db.commit()

    def _store_artifact(
        self,
        db: Session,
        *,
        run_id: int,
        artifact_type: ArtifactType,
        path: str,
        metadata_json: dict,
    ) -> None:
        artifact = Artifact(
            run_id=run_id,
            artifact_type=artifact_type,
            path=path,
            metadata_json=metadata_json,
        )
        db.add(artifact)
        db.commit()
