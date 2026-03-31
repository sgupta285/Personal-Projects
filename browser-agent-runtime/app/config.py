from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite+pysqlite:///./browser_agent.db"
    redis_url: str = "redis://localhost:6379/0"
    artifact_dir: Path = Path("./artifacts")
    default_headless: bool = True
    default_dry_run: bool = True
    worker_poll_interval: int = Field(default=2, ge=1)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    return settings
