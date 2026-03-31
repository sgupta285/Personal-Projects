from __future__ import annotations

from pathlib import Path

import mlflow

from app.config import settings


def log_run_to_mlflow(run_name: str, params: dict, metrics: dict, tags: dict | None = None) -> None:
    Path(settings.mlflow_tracking_uri).mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("clinical-prompt-evaluation-suite")
    with mlflow.start_run(run_name=run_name):
        mlflow.log_params(params)
        mlflow.log_metrics({k: float(v) for k, v in metrics.items() if isinstance(v, (int, float))})
        for key, value in (tags or {}).items():
            mlflow.set_tag(key, value)
