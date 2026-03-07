from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LLM Evaluation and Inference Stack"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    default_backend: str = "hf-local"
    default_model: str = "sshleifer/tiny-gpt2"
    mlflow_tracking_uri: str = "file:./artifacts/mlruns"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    log_level: str = "INFO"
    retrieval_corpus_path: str = "data/sample/retrieval_corpus.jsonl"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
