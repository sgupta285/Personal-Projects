from __future__ import annotations

from typing import Any

from .config import settings


class MLflowLogger:
    def __init__(self) -> None:
        self.enabled = bool(settings.mlflow_tracking_uri)
        self._client = None
        if self.enabled:
            try:
                import mlflow
                mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
                mlflow.set_experiment(settings.mlflow_experiment_name)
                self._client = mlflow
            except Exception:
                self.enabled = False
                self._client = None

    def log_evaluation(self, run_payload: dict[str, Any], evaluation_payload: dict[str, Any]) -> None:
        if not self.enabled or self._client is None:
            return
        with self._client.start_run(run_name=run_payload.get("run_id")):
            self._client.log_param("benchmark_id", run_payload.get("benchmark_id"))
            self._client.log_param("model_name", run_payload.get("model_name"))
            self._client.log_param("prompt_version", run_payload.get("prompt_version"))
            self._client.log_metric("score", float(evaluation_payload.get("score", 0.0)))
            self._client.log_metric("total_latency_ms", float(run_payload.get("total_latency_ms", 0)))
            self._client.log_metric("estimated_cost_usd", float(run_payload.get("estimated_cost_usd", 0.0)))
            for key, value in evaluation_payload.get("metrics", {}).items():
                if isinstance(value, (int, float, bool)):
                    self._client.log_metric(key, float(value))
