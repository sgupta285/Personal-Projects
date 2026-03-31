from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "multimodal-agent-evaluation-stack"
    environment: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./agent_eval.db"
    mlflow_tracking_uri: str | None = None
    mlflow_experiment_name: str = "agent-evals"
    default_benchmark_dir: str = str((Path(__file__).resolve().parents[2] / "benchmarks").resolve())

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
