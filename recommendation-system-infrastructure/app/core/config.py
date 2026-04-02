from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "reco-platform"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./data/app.db"
    redis_url: str = "redis://localhost:6379/0"
    mlflow_tracking_uri: str = "./artifacts/mlruns"
    model_dir: str = "./artifacts/models"
    offline_features_path: str = "./data/processed/offline_features.json"
    user_embeddings_path: str = "./artifacts/models/user_embeddings.npy"
    item_embeddings_path: str = "./artifacts/models/item_embeddings.npy"
    item_metadata_path: str = "./data/processed/item_features.json"
    ab_test_salt: str = "reco-platform-salt"
    cache_ttl_seconds: int = 120
    default_candidate_pool: int = 250
    default_top_k: int = 20

    @property
    def model_dir_path(self) -> Path:
        return Path(self.model_dir)


settings = Settings()
