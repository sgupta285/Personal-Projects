from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Usage Analytics Dashboard"
    app_env: str = "development"
    database_url: str = f"sqlite+pysqlite:///{(Path(__file__).resolve().parents[3] / 'data' / 'processed' / 'usage_analytics.db').as_posix()}"
    redis_url: str | None = None
    cache_ttl_seconds: int = 300
    default_lookback_days: int = 30
    allow_sqlite_fallback: bool = True

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
