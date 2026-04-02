from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'production-service-api-platform'
    env: str = 'development'
    database_url: str = 'sqlite:///./data/app.db'
    redis_url: str = 'redis://localhost:6379/0'
    jwt_secret: str = 'change-me'
    jwt_algorithm: str = 'HS256'
    access_token_ttl_minutes: int = 60
    default_page_size: int = 20
    max_page_size: int = 100
    enable_redis: bool = False
    enable_open_telemetry: bool = False
    request_timeout_seconds: int = 10
    default_rate_limit_per_minute: int = 60
    default_daily_quota: int = 10_000


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
