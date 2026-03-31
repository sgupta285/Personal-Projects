from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas import (
    AgreementReport,
    AnalyticsOverview,
    BiasReport,
    DatasetCreate,
    DatasetRead,
    ExperimentRunCreate,
    ExperimentRunRead,
    PreferenceExampleCreate,
    PreferenceExampleRead,
    PreferenceRead,
    PreferenceSubmission,
    PromptSensitivityReport,
    RewardTargetRead,
    SearchResult,
    SnapshotCreate,
    SnapshotRead,
)
from app.services.analytics import AnalyticsService
from app.services.mlflow_tracker import ExperimentTracker
from app.services.repository import PreferenceLabRepository
from app.services.retrieval import PreferenceExampleRetriever
from app.services.reward_targets import METHOD, compute_reward_targets
from app.services.versioning import build_snapshot_manifest

router = APIRouter()
repository = PreferenceLabRepository()
analytics = AnalyticsService(repository)
retriever = PreferenceExampleRetriever(repository)
tracker = ExperimentTracker()


@router.get('/health')
def health() -> dict[str, str]:
    return {'status': 'ok'}


@router.post('/datasets', response_model=DatasetRead)
def create_dataset(payload: DatasetCreate) -> dict:
    return repository.create_dataset(payload.name, payload.description, payload.task_family)


@router.get('/datasets', response_model=list[DatasetRead])
def list_datasets() -> list[dict]:
    return repository.list_datasets()


@router.post('/examples', response_model=PreferenceExampleRead)
def create_example(payload: PreferenceExampleCreate) -> dict:
    try:
        repository.get_dataset(payload.dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    example = repository.create_example(
        dataset_id=payload.dataset_id,
        prompt_text=payload.prompt_text,
        task_type=payload.task_type,
        context=payload.context,
        metadata=payload.metadata,
        candidates=[candidate.model_dump() for candidate in payload.candidates],
    )
    return example


@router.get('/examples', response_model=list[PreferenceExampleRead])
def list_examples(dataset_id: int | None = None) -> list[dict]:
    return repository.list_examples(dataset_id=dataset_id)


@router.get('/examples/{example_id}', response_model=PreferenceExampleRead)
def get_example(example_id: int) -> dict:
    try:
        return repository.get_example(example_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post('/preferences', response_model=PreferenceRead)
def submit_preference(payload: PreferenceSubmission) -> dict:
    try:
        example = repository.get_example(payload.example_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    candidate_ids = {candidate['id'] for candidate in example['candidates']}
    if set(payload.ranking) - candidate_ids:
        raise HTTPException(status_code=400, detail='Ranking contains candidate IDs not present in the example.')
    preference = repository.submit_preference(
        example_id=payload.example_id,
        annotator_id=payload.annotator_id,
        ranking=payload.ranking,
        notes=payload.notes,
        metadata=payload.metadata,
    )
    targets = compute_reward_targets(repository, payload.example_id)
    repository.upsert_reward_target(payload.example_id, METHOD, targets)
    return preference


@router.get('/preferences', response_model=list[PreferenceRead])
def list_preferences(dataset_id: int | None = None) -> list[dict]:
    return repository.list_preferences(dataset_id=dataset_id)


@router.get('/reward-targets/{example_id}', response_model=RewardTargetRead)
def get_reward_target(example_id: int) -> dict:
    try:
        target = repository.get_reward_target(example_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        'example_id': target['example_id'],
        'method': target['method'],
        'targets': target['targets'],
    }


@router.post('/snapshots', response_model=SnapshotRead)
def create_snapshot(payload: SnapshotCreate) -> dict:
    try:
        repository.get_dataset(payload.dataset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    manifest = build_snapshot_manifest(repository, payload.dataset_id, payload.selection_filter)
    return repository.create_snapshot(payload.dataset_id, payload.version_name, manifest)


@router.get('/snapshots', response_model=list[SnapshotRead])
def list_snapshots(dataset_id: int | None = None) -> list[dict]:
    return repository.list_snapshots(dataset_id=dataset_id)


@router.post('/experiments', response_model=ExperimentRunRead)
def create_experiment_run(payload: ExperimentRunCreate) -> dict:
    artifact = tracker.log_run(payload.name, payload.config, payload.metrics)
    metrics = dict(payload.metrics)
    metrics['artifact_path'] = str(artifact)
    return repository.create_experiment_run(
        dataset_id=payload.dataset_id,
        snapshot_id=payload.snapshot_id,
        name=payload.name,
        config=payload.config,
        metrics=metrics,
    )


@router.get('/experiments', response_model=list[ExperimentRunRead])
def list_experiment_runs(dataset_id: int | None = None) -> list[dict]:
    return repository.list_experiment_runs(dataset_id=dataset_id)


@router.get('/search', response_model=list[SearchResult])
def search_examples(dataset_id: int, query: str = Query(..., min_length=2), top_k: int = 5) -> list[dict]:
    return [row.__dict__ for row in retriever.search(dataset_id=dataset_id, query=query, top_k=top_k)]


@router.get('/analytics/overview', response_model=AnalyticsOverview)
def analytics_overview() -> dict:
    return analytics.overview()


@router.get('/analytics/agreement/{dataset_id}', response_model=AgreementReport)
def analytics_agreement(dataset_id: int) -> dict:
    return analytics.agreement_report(dataset_id)


@router.get('/analytics/bias/{dataset_id}', response_model=BiasReport)
def analytics_bias(dataset_id: int) -> dict:
    return analytics.bias_report(dataset_id)


@router.get('/analytics/prompt-sensitivity/{dataset_id}', response_model=PromptSensitivityReport)
def analytics_prompt_sensitivity(dataset_id: int) -> dict:
    return analytics.prompt_sensitivity_report(dataset_id)
