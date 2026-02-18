from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Fraud Detection API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_cache_ttl: int = 300  # seconds
    redis_enabled: bool = True

    # Model
    model_path: str = "data/fraud_model.joblib"
    model_threshold: float = 0.5
    feature_count: int = 30

    # Circuit breaker
    cb_failure_threshold: int = 5
    cb_recovery_timeout: int = 30  # seconds
    cb_half_open_max_calls: int = 3

    # Rate limiting
    rate_limit_per_minute: int = 600

    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = False
    jaeger_host: str = "localhost"
    jaeger_port: int = 6831

    # Drift monitoring
    drift_window_size: int = 1000
    drift_psi_threshold: float = 0.2
    drift_check_interval: int = 60  # seconds

    class Config:
        env_file = ".env"
        env_prefix = "FRAUD_"


settings = Settings()
