from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    max_batch_size: int = 4
    batch_wait_ms: int = 120
    gpu_memory_budget_mb: int = 4096
    gpu_worker_count: int = 1
    cache_ttl_seconds: int = 300
    job_storage_path: str = "./data/jobs"
    redis_url: str = "redis://localhost:6379/0"
    enable_redis: bool = False

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')


settings = Settings()
