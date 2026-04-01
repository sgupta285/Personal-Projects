from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="production-ml-serving-infrastructure", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    database_url: str = Field(default="sqlite+pysqlite:///./ml_serving.db", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    mlflow_tracking_uri: str = Field(default="file:./mlruns", alias="MLFLOW_TRACKING_URI")
    model_path: str = Field(default="artifacts/models/current_model.pt", alias="MODEL_PATH")
    model_registry_path: str = Field(default="artifacts/model_registry/current.json", alias="MODEL_REGISTRY_PATH")
    request_batch_window_ms: int = Field(default=100, alias="REQUEST_BATCH_WINDOW_MS")
    request_max_batch_size: int = Field(default=32, alias="REQUEST_MAX_BATCH_SIZE")
    in_memory_cache_ttl_seconds: int = Field(default=120, alias="IN_MEMORY_CACHE_TTL_SECONDS")
    in_memory_cache_maxsize: int = Field(default=512, alias="IN_MEMORY_CACHE_MAXSIZE")
    redis_cache_ttl_seconds: int = Field(default=300, alias="REDIS_CACHE_TTL_SECONDS")
    feature_lookback_days: int = Field(default=30, alias="FEATURE_LOOKBACK_DAYS")
    enable_redis: bool = Field(default=False, alias="ENABLE_REDIS")
    enable_dynamic_batching: bool = Field(default=True, alias="ENABLE_DYNAMIC_BATCHING")
    enable_fallback_model: bool = Field(default=True, alias="ENABLE_FALLBACK_MODEL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @property
    def model_path_obj(self) -> Path:
        return Path(self.model_path)

    @property
    def model_registry_path_obj(self) -> Path:
        return Path(self.model_registry_path)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
