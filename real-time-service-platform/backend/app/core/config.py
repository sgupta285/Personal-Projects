from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "real-time-service-platform"
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./service_platform.db"
    redis_url: str = "redis://localhost:6379/0"
    rate_limit_capacity: int = 50
    rate_limit_refill_per_second: int = 10
    circuit_breaker_failure_threshold: int = 3
    circuit_breaker_recovery_timeout: int = 15
    downstream_base_latency_ms: int = 40
    downstream_jitter_ms: int = 25


@lru_cache
def get_settings() -> Settings:
    return Settings()
