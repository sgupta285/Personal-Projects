from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Restaurant Discovery Platform"
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-me"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./restaurant_discovery.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    booking_provider: str = "mock"
    places_provider: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
