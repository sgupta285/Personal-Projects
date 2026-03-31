from __future__ import annotations

import time
from datetime import datetime

from sqlalchemy.orm import Session

from app import models
from app.services.experiment_service import log_run_to_mlflow
from app.services.llm_clients import GenerationRequest, get_provider
from app.services.scoring import aggregate_run_scores, score_output


def create_run(db: Session, prompt_version_id: int, dataset_id: int, provider: str, model_name: str) -> models.EvaluationRun:
    run = models.EvaluationRun(
        prompt_version_id=prompt_version_id,
        dataset_id=dataset_id,
        provider=provider,
        model_name=model_name,
        status="queued",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def run_evaluation(db: Session, run: models.EvaluationRun) -> models.EvaluationRun:
    prompt = db.get(models.PromptVersion, run.prompt_version_id)
    dataset = db.get(models.Dataset, run.dataset_id)
    if prompt is None or dataset is None:
        raise ValueError("Prompt version or dataset not found.")

    provider = get_provider(run.provider)
    item_summaries = []

    run.status = "running"
    db.add(run)
    db.commit()

    for item in list(dataset.items):
        started = time.perf_counter()
        request = GenerationRequest(
            system_prompt=prompt.system_prompt,
            input_text=item.input_text,
            provider=run.provider,
            model_name=run.model_name,
            temperature=prompt.temperature,
        )
        output = provider.generate_structured_output(request)
        scoring = score_output(output, item.input_text, item.expected_keywords)
        latency_ms = int((time.perf_counter() - started) * 1000)

        result = models.ItemEvaluationResult(
            run_id=run.id,
            dataset_item_id=item.id,
            raw_output=output,
            structured_output=scoring["normalized_output"],
            validation_passed=scoring["validation_passed"],
            rubric_scores=scoring["rubric_scores"],
            metric_scores=scoring["metric_scores"],
            evaluator_notes=scoring["validation_issues"],
            latency_ms=latency_ms,
        )
        db.add(result)
        item_summaries.append(scoring)

    aggregate = aggregate_run_scores(item_summaries)
    run.aggregate_scores = aggregate
    run.status = "completed"
    run.completed_at = datetime.utcnow()
    db.add(run)
    db.commit()
    db.refresh(run)

    log_run_to_mlflow(
        run_name=f"run-{run.id}",
        params={
            "provider": run.provider,
            "model_name": run.model_name,
            "prompt_version_id": prompt.id,
            "dataset_id": dataset.id,
            "workflow_name": dataset.workflow_name,
        },
        metrics=aggregate,
        tags={"status": run.status},
    )
    return run
