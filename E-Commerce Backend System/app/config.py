from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "E-Commerce Backend API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/ecommerce.db"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_echo: bool = False

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = True
    redis_cache_ttl: int = 300
    redis_rate_limit_window: int = 60
    redis_rate_limit_max: int = 100

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_prefix = "ECOM_"


settings = Settings()
