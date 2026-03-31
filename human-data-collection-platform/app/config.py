from pathlib import Path
import os

class Settings:
    app_name: str = os.getenv("APP_NAME", "Human Data Collection Platform")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_path: str = os.getenv("DATABASE_PATH", "./human_data_collection.db")
    enable_redis: bool = os.getenv("ENABLE_REDIS", "false").lower() == "true"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    require_review_for_all: bool = os.getenv("REQUIRE_REVIEW_FOR_ALL", "true").lower() == "true"

    @property
    def database_file(self) -> Path:
        return Path(self.database_path)

settings = Settings()
