from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Reward Modeling and Preference Data Lab"
    api_prefix: str = "/api"
    debug: bool = True
    database_url: str = "sqlite:///./preference_lab.db"
    artifact_dir: str = "artifacts"
    mlflow_tracking_uri: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
