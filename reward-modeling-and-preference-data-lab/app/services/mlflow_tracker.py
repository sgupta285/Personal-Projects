from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings


class ExperimentTracker:
    """
    Lightweight tracker that writes experiment payloads to disk.

    If MLflow is installed and MLFLOW_TRACKING_URI is configured, this class also
    emits the same payload to MLflow. The starter template keeps the dependency
    optional so the repo remains easy to run in a clean local environment.
    """

    def __init__(self) -> None:
        self.artifact_dir = Path(settings.artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def log_run(self, run_name: str, config: dict[str, Any], metrics: dict[str, Any]) -> Path:
        import json

        destination = self.artifact_dir / f"{run_name.replace(' ', '_').lower()}.json"
        payload = {"run_name": run_name, "config": config, "metrics": metrics}
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        self._log_with_mlflow_if_available(run_name, config, metrics)
        return destination

    @staticmethod
    def _log_with_mlflow_if_available(run_name: str, config: dict[str, Any], metrics: dict[str, Any]) -> None:
        if not settings.mlflow_tracking_uri:
            return
        try:
            import mlflow  # type: ignore
        except Exception:
            return
        mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
        with mlflow.start_run(run_name=run_name):
            mlflow.log_params({key: str(value) for key, value in config.items()})
            mlflow.log_metrics({key: float(value) for key, value in metrics.items() if isinstance(value, (int, float))})
